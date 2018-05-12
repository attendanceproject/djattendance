from collections import defaultdict

from ortools.linear_solver import pywraplp

from .models import Worker, Assignment
from aputils.utils import timeit_inline


class ServiceScheduler(object):
  def __init__(self, services, assignments, exceptions):
    self.services = services
    self.assignments = assignments
    self.exceptions = exceptions

  def solve(self):
    # uses Mixed Integer Programming assignment algorithm as described here:
    # https://developers.google.com/optimization/assignment/assignment_mip
    solver = pywraplp.Solver('SolveAssignmentProblemMIP',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    self.solver = solver
    x = {}
    self.x = x
    day_constraints = defaultdict(list)
    category_constraints = defaultdict(list)
    prep_constraints = defaultdict(list)

    t = timeit_inline("Creating worker list")
    t.start()
    worker_caps = []
    workers = list(Worker.objects.all().prefetch_related('assignments').prefetch_related('assignments__service'))
    for w in workers:
      services_left = max(w.services_cap -
                          self.assignments.get(w.id, 0) -
                          self.exceptions.get(w.id, 0), 0)
      worker_caps.append(services_left)
    num_workers = len(workers)
    t.end()

    t = timeit_inline("Creating task list")
    t.start()
    tasks = []
    num_tasks = 0
    task_size = []
    for service in self.services:
      for slot in service.serviceslots:
        tasks.append((service, slot))
        task_size.append(slot.workers_required)
        day_constraints[service.weekday].append(num_tasks)
        category_constraints[service.category].append(num_tasks)
        if "Prep" in service.category.name:
          prep_constraints['Prep'].append(num_tasks)
        num_tasks += 1
    t.end()
    self.tasks = tasks

    cost = []
    t = timeit_inline("Creating cost")
    t.start()
    for i, w in enumerate(workers):
      freqs = w.service_frequency
      c = []
      sick_lvl = float(max(10 - w.health, 1))
      for service, slot in tasks:
        c.append(freqs.get(service.category, 0) + sick_lvl / 10)
      cost.append(c)
    t.end()
    self.workers = workers

    t = timeit_inline("Initializing worker, task grid")
    t.start()
    for i in range(num_workers):
      for j in range(num_tasks):
        if workers[i] not in tasks[j][1].workers:
          x[i, j] = solver.IntVar(0, 0, 'Int %i, %i' % (i, j))
        else:
          x[i, j] = solver.BoolVar('%s, %s' % (workers[i], tasks[j][1]))
    t.end()

    t = timeit_inline("Adding worker workload constraint")
    t.start()
    for i in range(num_workers):
      solver.Add(solver.Sum([x[i, j] for j in
                 range(num_tasks)]) <= worker_caps[i])
    t.end()

    t = timeit_inline("Adding task has correct amount of workers constraint")
    t.start()
    for j in range(num_tasks):
      c = task_size[j]
      solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) <= c)
    t.end()

    t = timeit_inline("Adding one task per day constraint")
    t.start()
    for day, constrained_tasks in day_constraints.items():
      for i in range(num_workers):
        solver.Add(solver.Sum(x[i, j] for j in constrained_tasks) <= 1)
    t.end()

    t = timeit_inline("Adding two task categories per week constraint")
    t.start()
    for day, constrained_tasks in category_constraints.items():
      for i in range(num_workers):
        solver.Add(solver.Sum(x[i, j] for j in constrained_tasks) <= 2)
    t.end()

    t = timeit_inline("Adding one prep per week constraint")
    t.start()
    for day, constrained_tasks in prep_constraints.items():
      for i in range(num_workers):
        solver.Add(solver.Sum(x[i, j] for j in constrained_tasks) <= 1)
    t.end()

    t = timeit_inline("Minimizing unfilled services, service uniformity")
    t.start()
    diffs = []
    for j in range(num_tasks):
      worker_count = solver.Sum([x[i, j] for i in range(num_workers)])
      diffs.append(task_size[j] - worker_count)
    c = solver.Sum([x[i, j] * cost[i][j]
                    for i in range(num_workers)
                    for j in range(num_tasks)])
    solver.Minimize(20 * solver.Sum(diffs) + c)
    t.end()

    t = timeit_inline("Solving MIP")
    t.start()
    status = solver.Solve()
    t.end()
    print('Total cost = ', self.solver.Objective().Value())
    return status

  def save(self, cws):
    assignments = []
    assign_workers = {}
    for service, slot in self.tasks:
      a = Assignment(service=service, service_slot=slot,
                     week_schedule=cws, workload=slot.workload)
      assignments.append(a)
      assign_workers[(service, slot)] = []
    Assignment.objects.bulk_create(assignments)

    for i, worker in enumerate(self.workers):
      for j, (service, slot) in enumerate(self.tasks):
        if self.x[i, j].solution_value() > 0:
          assign_workers[(service, slot)].append(worker)

    assignments = Assignment.objects.filter(week_schedule=cws, pin=False)\
                                    .select_related('service', 'service_slot')
    bulk = []
    ThroughModel = Assignment.workers.through
    for a in assignments:
      workers = assign_workers[(a.service, a.service_slot)]
      for worker in workers:
        bulk.append(ThroughModel(assignment_id=a.id, worker_id=worker.id))
    ThroughModel.objects.bulk_create(bulk)
