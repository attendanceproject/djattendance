from collections import defaultdict, Counter

from ortools.linear_solver import pywraplp

from .constants import (
    MAX_PREPS_PER_WEEK,
    MAX_SERVICE_CATEGORY_PER_WEEK,
    MAX_SERVICES_PER_DAY,
    PREP
)
from .models import Assignment, Service, ServiceSlot
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

    def services_left(worker):
      return max(worker.services_cap -
                 self.assignments.get(worker.id, 0) -
                 self.exceptions.get(worker.id, 0), 0)
    t = timeit_inline("Creating worker list")
    t.start()
    workers = []
    worker_indices = defaultdict(set)
    worker_set = set()
    i = 0
    for service in self.services:
      for slot in service.serviceslots:
        for worker in slot.workers:
          if worker in worker_set:
            continue
          worker_set.add(worker)
          workers.append(worker)
          try:
            for w in worker:
              worker_indices[w].add(i)
          except TypeError:
            worker_indices[worker].add(i)
          i += 1
    worker_caps = []
    for worker in workers:
      cap = calculate_worker_value(worker, services_left, min)
      worker_caps.append(cap)
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
        task_size.append(slot.workers_required if slot.gender != 'X' else 1)
        day_constraints[service.weekday].append(num_tasks)
        category_constraints[service.category].append(num_tasks)
        if PREP in service.category.name:
          prep_constraints[PREP].append(num_tasks)
        num_tasks += 1
    t.end()
    self.tasks = tasks

    def sick_level_func(w):
      return float(max(10 - w.health, 1))

    cost = []
    t = timeit_inline("Creating cost")
    t.start()
    for i, worker in enumerate(workers):
      sick_level = calculate_worker_value(worker, sick_level_func, sum)
      freqs = calculate_worker_value(
          worker,
          lambda w: w.weighted_service_frequency,
          lambda s: sum(s, Counter())
      )

      c = []
      for service, slot in tasks:
        # frequency_value is an indicator of how often worker has done a particular service, specific to the weekday.
        frequency_value = 0
        if freqs.get(service.category):
          frequency_value = freqs.get(service.category).get(service.weekday, 0)
        c.append(frequency_value +
                 sick_level / 10 -
                 slot.worker_group.assign_priority)
      cost.append(c)
    t.end()
    self.workers = workers

    t = timeit_inline("Initializing worker, task grid")
    t.start()
    for i in range(num_workers):
      for j in range(num_tasks):
        slot = tasks[j][1]
        is_valid_choice = workers[i] in slot.workers
        if is_valid_choice:
          x[i, j] = solver.BoolVar('Bool %s, %s' % (workers[i], tasks[j][1]))
        else:
          x[i, j] = solver.IntVar(0, 0, '0: %i, %i' % (i, j))
    t.end()

    t = timeit_inline("Adding worker workload constraint")
    t.start()
    for i in range(num_workers):
      indices = worker_indices[workers[i]]
      solver.Add(solver.Sum(x[ind, j] for j in
                 range(num_tasks) for ind in indices) <= worker_caps[i])
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
        indices = worker_indices[workers[i]]
        solver.Add(solver.Sum(x[ind, j] for j in constrained_tasks
                   for ind in indices) <= MAX_SERVICES_PER_DAY)
    t.end()

    t = timeit_inline("Adding two task categories per week constraint")
    t.start()
    for _, constrained_tasks in category_constraints.items():
      for i in range(num_workers):
        indices = worker_indices[workers[i]]
        solver.Add(solver.Sum(x[ind, j] for j in constrained_tasks
                   for ind in indices) <= MAX_SERVICE_CATEGORY_PER_WEEK)
    t.end()

    t = timeit_inline("Adding one prep per week constraint")
    t.start()
    constrained_tasks = prep_constraints[PREP]
    for i in range(num_workers):
      indices = worker_indices[workers[i]]
      solver.Add(solver.Sum(x[ind, j] for j in constrained_tasks
                 for ind in indices) <= MAX_PREPS_PER_WEEK)
    t.end()

    t = timeit_inline("Minimizing unfilled services, service uniformity")
    t.start()
    diffs = []
    for j in range(num_tasks):
      worker_count = solver.Sum(x[i, j] for i in range(num_workers))
      diffs.append(task_size[j] - worker_count)
    c = solver.Sum(x[i, j] * cost[i][j]
                   for i in range(num_workers)
                   for j in range(num_tasks))
    solver.Minimize(1000 * solver.Sum(diffs) + c)
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
          try:
            assign_workers[(service, slot)].extend(worker)
          except TypeError:
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

    # manually add chair brothers because their service is a special case
    chairs = Service.objects.filter(name__contains='Chairs')
    chair_slots = ServiceSlot.objects.filter(role='*', service__in=chairs)
    for a in Assignment.objects.filter(week_schedule=cws, service__in=chairs,
                                       pin=False, service_slot__in=chair_slots):
      a.workers.add(*a.service_slot.worker_group.get_workers)


def calculate_worker_value(worker, value, aggregator):
  try:
    return aggregator([value(w) for w in worker])
  except TypeError:
    return value(worker)
