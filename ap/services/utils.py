from collections import OrderedDict, Counter
from datetime import datetime
from itertools import combinations
from sets import Set

from django.db.models import Q, Count
from django.template.defaulttags import register

from accounts.models import User
from aputils.utils import memoize, timeit
from leaveslips.models import GroupSlip

from .models import (Assignment, Prefetch, SeasonalServiceSchedule, Service,
                     ServiceException, ServiceSlot, Sum, WorkerGroup)
from .service_scheduler import ServiceScheduler
from .constants import (
      MAX_PREPS_PER_WEEK,
      MAX_SERVICE_CATEGORY_PER_WEEK,
      MAX_SERVICES_PER_DAY,
      PREP,
)


'''
Pseudo-code for algo


-----
Hard-constraint

Get all the services without day (repeating services) + date falls within this coming week
Get all the workergroups + roles + count (related to services)

duplicate services node with multiple count for workergroups (single instance)

Get all workers?

Create edges based on worker.services_needed

check only 1 service per day, weekday
check conflicting services on same day -> flow into a single bottle-neck node

--------
Trim operation?
Apply exceptions to trim workers from services

All pre-assigned, take out of the graph (designated, shuttle, etc.), if
assignment counts as service, trim all other services that day

how to check for time conflict
All pinned assignments -> check time conflict but not count as +1 service?

All time conflict will be caused only by irregular services
(piano, AV, Shuttle, Outline Sisters)


------
special operation

to choose star assignments for duo star assignments
flip coin for brother/sister and create edges

-------
Soft-constraint (edges cost)

Calculate the cost for the edges

pull history, health

health (base weight of trainee -> sink)
history (+1 for each service already done before), more weight, closer to current date (3 weeks?)
(visualize it for SS) experience (-0.5 for each service already done before)
noise (+- noise for randomly in the cost run each time)? maybe optional

ServiceSlot.workload (base weight of each trainee -> service)




-------
star assignment -> maybe greedy trim star edges and then
randomly flip coins to ratio of brother/sister star ratio
and trim graph appropriately

(future dev) -> Maybe incorporate how constrained each star in the flipping
probabilities to bias less constrained stars
'''


class WorkersCache(object):
  def __init__(self, cws):
    self.workers_cache = {}
    workergroups = WorkerGroup.objects.prefetch_related('workers')
    for wg in workergroups:
      ws = wg.get_workers_prefetch_assignments(cws)
      self.workers_cache[wg.id] = ws

  @memoize
  def get(self, id, type):
    # print 'called cold cache', id, type
    if type == 'query':
      return self.workers_cache[id]
    elif type == 'set':
      return set(self.workers_cache[id])
    elif type == 'B':
      return set(self.workers_cache[id].filter(trainee__gender='B'))
    elif type == 'S':
      return set(self.workers_cache[id].filter(trainee__gender='S'))
    else:
      return None


@timeit
def hydrate(services, cws):

  workers_cache = WorkersCache(cws)
  for s in services:
    for slot in s.serviceslots:
      # blow away cache
      wg = slot.worker_group

      # https://developers.google.com/optimization/assignment/compare_mip_cp#assignment-with-allowed-groups-of-workers
      if slot.gender == 'X' and slot.workers_required > 1:
        workers = set()
        for gender, _ in User.GENDER:
          workers |= set(combinations(workers_cache.get(wg.id, gender), slot.workers_required))
        slot.workers = workers
      else:
        workers = workers_cache.get(wg.id, 'set')
        slot.workers = workers.copy()

  return services


def assign_leaveslips(service_scheduler, cws):
  assignments = Assignment.objects.filter(week_schedule=cws).select_related('service').prefetch_related('workers')
  # Delete old group leave slips
  GroupSlip.objects.filter(service_assignment__in=assignments).delete()
  timestamp = datetime.now()
  bulk_leaveslips_assignments = []
  bulk_groupslip_trainees = []
  for a in assignments.distinct('service'):
    gs = GroupSlip(type='SERV', status='A', trainee=service_scheduler, description=a.service, comments=a, start=a.startdatetime, end=a.enddatetime, submitted=timestamp, last_modified=timestamp, finalized=timestamp, service_assignment=a)
    bulk_leaveslips_assignments.append(gs)
  GroupSlip.objects.bulk_create(bulk_leaveslips_assignments)
  ThroughModel = GroupSlip.trainees.through
  bulk_groupSlips = GroupSlip.objects.filter(service_assignment__in=assignments)
  for gs in bulk_groupSlips:
    workers = set()
    sa = gs.service_assignment
    for a in assignments.filter(service=sa.service):
      workers |= set(a.workers.all())
    for worker in workers:
      bulk_groupslip_trainees.append(ThroughModel(groupslip_id=gs.id, trainee_id=worker.trainee.id))
  ThroughModel.objects.bulk_create(bulk_groupslip_trainees)
  bulk_groupSlips.annotate(num_trainees=Count('trainees')).filter(num_trainees=0).delete()


@timeit
def assign(cws):
  # get start date and end date of effective week
  week_start, week_end = cws.week_range

  # Gets services that are active with day null or day between week range
  css = SeasonalServiceSchedule.objects.filter(active=True)\
      .prefetch_related('services')

  # Get pinned assignments
  pinned_assignments = Assignment.objects.filter(week_schedule=cws, pin=True).select_related('service').prefetch_related('workers')

  # Load all active services onto memory
  services = Set()
  for ss in css:
    s = ss.services.filter(Q(day__isnull=True) | Q(day__range=(week_start, week_end)))\
        .filter(active=True)\
        .filter(designated=False)\
        .select_related()\
        .prefetch_related(Prefetch('serviceslot_set', queryset=ServiceSlot.objects.exclude(assignments__pin=True, assignments__week_schedule=cws).select_related('worker_group').prefetch_related('worker_group__workers').order_by('-worker_group__assign_priority', 'workers_required'), to_attr='serviceslots'),
                          'worker_groups__workers',
                          'worker_groups__workers__trainee')\
        .distinct()\
        .order_by('start', 'end')
    services.union_update(Set(s))
  print "#services", len(services)

  # Populate fields onto memory
  print "Populating fields onto memory"
  services = hydrate(services, cws)

  # Get all active exception in time period with active or no schedule constrains
  print "Fetching exceptions"
  ac = {}
  ec = {}
  exceptions = ServiceException.objects.filter(active=True, start__lte=week_end)\
      .filter(Q(end__isnull=True) | Q(end__gte=week_start))\
      .filter(Q(schedule=None) | Q(schedule__active=True))\
      .distinct()
  assignments_count_list = Assignment.objects.filter(week_schedule=cws).values('workers').annotate(count=Sum('workload'))
  exceptions_count_list = exceptions.values('workers').annotate(count=Sum('workload'))
  exceptions = exceptions.prefetch_related('services', 'workers', 'workers__trainee')

  for a in assignments_count_list:
    ac[a['workers']] = a['count']
  for e in exceptions_count_list:
    ec[e['workers']] = e['count']

  print "Trimming service exceptions"
  trim_service_exceptions(services, exceptions, pinned_assignments)

 # Build and solve graph
  scheduler = ServiceScheduler(services, ac, ec)
  status = scheduler.solve()
  print(status)
  scheduler.save(cws)


# Checks to see if there's a intersection between 2 time ranges
def is_overlap(a, b):
  # (StartA <= EndB) and (EndA >= StartB)
  return (a.calculated_weekday == b.calculated_weekday) and (a.start <= b.end) and (a.end >= b.start)


def sort_services(services):
  services = list(services)
  # in place stable sort
  services.sort(key=lambda x: (x.calculated_weekday, x.start, x.end))
  return services


def build_service_conflict_table(services):
  '''
  Only have to worry about service time overlap conflict if I assign trainees
  more than 1 service per day.
  '''

  # build a table of service mapping to other services in conflicting times/day
  c_tb = {}

  services = sort_services(services)
  len_l = len(services)

  # for each service, check to see if it overlaps with next service and keep checking
  # until no more overlaps and then move on to the next service. Build collision table 2-way
  for i in range(len_l - 1):
    j = i + 1
    while j < len_l and is_overlap(services[i], services[j]):
      # if overlap build 2-way table
      c_tb.setdefault(services[i], Set()).add(services[j])
      # reverse
      c_tb.setdefault(services[j], Set()).add(services[i])

      j += 1

  # Run time: if every item overlaps with every other item, O(n^2), if only ~1, O(n)
  return c_tb


@timeit
def build_trim_table(services, exceptions, pinned_assignments):
  # build exception table and then remove everyone in that table
  # {service: set([worker])}
  s_w_tb = {}
  # set([(w, weekday)])
  # block_whole_day = set()

  # {(w, weekday):set([services])}
  block_conflicting_services = OrderedDict()

  for e in exceptions:
    ws = e.workers.all()
    for s in e.services.all():
      for w in ws:
        s_w_tb.setdefault(s, Set()).add(w)
  # Add to exception table for pinned_assignments to be removed
  for a in pinned_assignments:
    s = a.service
    wholedayblock = a.workload > 0
    for w in a.workers.all():
      s_w_tb.setdefault(s, Set()).add(w)
      # add to block list
      if wholedayblock:
        # print 'whole day block', w, s.weekday
        # override conflict checking blocking b/c it's whole day
        block_conflicting_services[(w, s.weekday)] = True
      else:
        # print 'parital day block', w, s.weekday
        # only add blocking if no whole day blocking already
        if (w, s.weekday) not in block_conflicting_services:
          block_conflicting_services.setdefault((w, s.weekday), set()).add(s)
        else:
          if not block_conflicting_services[(w, s.weekday)]:
            block_conflicting_services.setdefault((w, s.weekday), set()).add(s)

  return (s_w_tb, block_conflicting_services)


def remove_hydrated_worker(slot, worker):
  slot.workers.remove(worker)
  for ws in slot.workers:
    try:
      if worker in ws:
        slot.workers.remove(ws)
    except TypeError:
      continue


@timeit
def trim_service_exceptions(services, exceptions, pinned_assignments):
  s_w_tb, block_conflicting_services = build_trim_table(services, exceptions, pinned_assignments)

  # go through all exceptions and delete workers out of hydrated services
  for s in services:

    for slot in s.serviceslots:
      # Removing exceptions
      # if service mentioned in exception
      if s in s_w_tb:
        ws = s_w_tb[s]
        # remove all trainees in ts from all the serviceslots.workers.trainee
        for w in ws:
          # loop through all trainees listed in exception
          if w in slot.workers:
            remove_hydrated_worker(slot, w)

      # Removing pinned assignments
      for w, weekday in block_conflicting_services:
        if weekday == s.weekday and w in slot.workers:
          conflict_ss = block_conflicting_services[(w, s.weekday)]
          if conflict_ss:
            remove_hydrated_worker(slot, w)
          else:
            for conflict_s in conflict_ss:
              if conflict_s.check_time_conflict(s) and w in slot.workers:
                remove_hydrated_worker(slot, w)


# Save all designated services as pinned assignments
# This is run before we start the regular assignment for rotational services
def save_designated_assignments(cws):
  '''
    Grab all services with designated=True and in active schedule
    For each designated service grab worker slots
    For each worker slots create Assignment with service=service, service_slot=slot, week_schedule=cws, workload=slot.workload, workers=slot.worker_group.get_workers

    Bulk saves solution in 4 db calls
  '''
  bulk_service_assignments = []
  bulk_assignment_workers = []
  services = Service.objects.filter(designated=True, active=True).prefetch_related('worker_groups').distinct()
  # Delete all outdated Assignments for designated services
  Assignment.objects.filter(service__in=services, week_schedule=cws).delete()
  for service in services:
    for slot in service.serviceslot_set.all():
      a = Assignment(service=service, service_slot=slot, week_schedule=cws, workload=slot.workload, pin=True)
      slot.save()
      bulk_service_assignments.append(a)
  Assignment.objects.bulk_create(bulk_service_assignments)

  ThroughModel = Assignment.workers.through
  assignments = Assignment.objects.filter(week_schedule=cws, pin=True, service__in=services).prefetch_related('service_slot', 'service_slot__worker_group', 'service_slot__worker_group__workers')
  for a in assignments:
    workers = set(a.service_slot.worker_group.get_workers.all())
    for worker in workers:
      bulk_assignment_workers.append(ThroughModel(assignment_id=a.id, worker_id=worker.id))
  ThroughModel.objects.bulk_create(bulk_assignment_workers)


@register.filter
def merge_assigns(assigns):
  non_stars = []
  stars = []
  star_assignment = None
  non_star_assignment = None
  assignments = []
  for a in assigns:
    if '*' in a.service_slot.role:
      star_assignment = a
      stars.extend(a.get_worker_list())
    else:
      non_star_assignment = a
      non_stars.extend(a.get_worker_list())
  if star_assignment:
    star_assignment.get_worker_list = lambda: stars
    assignments.append(star_assignment)
  if non_star_assignment:
    non_star_assignment.get_worker_list = lambda: non_stars
    assignments.append(non_star_assignment)
  return assignments


class ServiceCheck(object):
  def __init__(self, func, limit, name):
    self.func = func
    self.limit = limit
    self.name = name

  def check(self, assignments):
    assignment_acc = [
        self.func(a) for a in assignments
        if self.func(a)
    ]
    counts = Counter(assignment_acc)

    over_limit = False
    for _, count in counts.items():
      if count > self.limit:
        over_limit = True
    return over_limit

def assignment_day(assignment):
  return assignment.service.day

def assignment_cat(assignment):
  cat = assignment.service.category
  return cat if not assignment.service.designated else None

def assignment_prep(assignment):
  service = assignment.service
  return PREP if PREP in service.name and not "Breakfast" in service.name else None

SERVICE_CHECKS = [
    ServiceCheck(assignment_day, MAX_SERVICES_PER_DAY, '> {0} service/day'.format(MAX_SERVICES_PER_DAY)),
    ServiceCheck(assignment_cat, MAX_SERVICE_CATEGORY_PER_WEEK, '> {0} category/week'.format(MAX_SERVICE_CATEGORY_PER_WEEK)),
    ServiceCheck(assignment_prep, MAX_PREPS_PER_WEEK, '> {0} prep/week'.format(MAX_PREPS_PER_WEEK)),
]
