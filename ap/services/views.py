from datetime import datetime, date
from dateutil import parser
from sets import Set
from collections import OrderedDict, defaultdict
import random
import json

from django.db.models import Q
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.template.defaulttags import register
from django.shortcuts import render, redirect

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Count, F
from django.contrib import messages
from braces.views import GroupRequiredMixin

from rest_framework_bulk import (
    BulkModelViewSet,
)

from rest_framework.renderers import JSONRenderer

from .serializers import (
    UpdateWorkerSerializer,
    ServiceSlotWorkloadSerializer,
    ServiceActiveSerializer,
    WorkerIDSerializer,
    WorkerAssignmentSerializer,
    AssignmentPinSerializer,
    ServiceCalendarSerializer,
    ServiceTimeSerializer,
    ExceptionActiveSerializer,
)
from .service_scheduler import ServiceScheduler
from .forms import ServiceRollForm, ServiceAttendanceForm, AddExceptionForm, SingleTraineeServicesForm, ServiceCategoryAnalyzerForm
from .models import (
    Prefetch,
    Assignment,
    Service,
    ServiceSlot,
    Worker,
    Category,
    WeekSchedule,
    WorkerGroup,
    SeasonalServiceSchedule,
    Sum,
    ServiceAttendance,
    ServiceRoll,
    ServiceException
)

from aputils.trainee_utils import trainee_from_user
from aputils.utils import timeit, memoize
from aputils.decorators import group_required

from leaveslips.models import GroupSlip
from accounts.models import Trainee
from houses.models import House
from terms.models import Term, FIRST_WEEK, LAST_WEEK
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


def flip_gender(p):
    return 'B' if random.random() < p else 'S'


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


def hydrate_worker_list(allworkers_cache, workers):
  result = set()
  for w in workers:
    result.add(allworkers_cache[w.id])
  return result


@timeit
def hydrate(services, cws):

  workers_cache = WorkersCache(cws)

  for s in services:
    for slot in s.serviceslots:
      # blow away cache
      wg = slot.worker_group

      # If gender restrictions are either all brother/all sister, trim out half the gender by coin flip
      # https://developers.google.com/optimization/assignment/compare_mip_cp#assignment-with-allowed-groups-of-workers
      # TODO(see link about avoiding this coin flip using MIP groups)
      if slot.gender == 'X' and slot.workers_required > 1:
        # naively do 50/50, will calculate based on training population ratio later on
        gender = flip_gender(0.5)
        workers = workers_cache.get(wg.id, gender)
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

  # TODO: time conflict checking for services on same day and time
  # Only happens if we allow more than one services a day

  # Build service frequency db for all the workers

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


@timeit
def trim_service_exceptions(services, exceptions, pinned_assignments):
  s_w_tb, block_conflicting_services = build_trim_table(services, exceptions, pinned_assignments)

  # print 'Bloocked!!!!!!!!!!!', block_conflicting_services
  # go through all exceptions and delete workers out of hydrated services
  for s in services:
    # print 'exception service', s

    for slot in s.serviceslots:
      # Removing exceptions
      # if service mentioned in exception
      if s in s_w_tb:
        ws = s_w_tb[s]
        # print 'EXCEPTIONS!!!!!', s, s.serviceslots
        # remove all trainees in ts from all the serviceslots.workers.trainee
        for w in ws:
          # print 'checking worker exception', w, a.workers
          # loop through all trainees listed in exception
          if w in slot.workers:
            # remove worker
            slot.workers.remove(w)
            # print 'removing worker!!!!!!!!!!!1', w, slot.workers

      # Removing pinned assignments
      for w, weekday in block_conflicting_services:
        if weekday == s.weekday and w in slot.workers:
          conflict_ss = block_conflicting_services[(w, s.weekday)]
          if conflict_ss:
            # print 'trying to remove', s, w, slot.workers
            slot.workers.remove(w)
            # print 'removing worker!!!!!!!!!!!1 whole day block', w, slot.workers
          else:
            for conflict_s in conflict_ss:
              if conflict_s.check_time_conflict(s) and w in slot.workers:
                slot.workers.remove(w)
                # print 'removing working!!!!!!!!!!! partial day block', w, slot.workers


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


@timeit
@group_required(['training_assistant', 'service_schedulers'])
def services_view(request, run_assign=False, generate_leaveslips=False):
  # status, soln = 'OPTIMAL', [(1, 2), (3, 4)]
  user = request.user
  trainee = trainee_from_user(user)
  if request.GET.get('week_schedule'):
    current_week = request.GET.get('week_schedule')
    current_week = int(current_week)
    current_week = current_week if current_week < LAST_WEEK else LAST_WEEK
    current_week = current_week if current_week > FIRST_WEEK else FIRST_WEEK
    cws = WeekSchedule.get_or_create_week_schedule(trainee, current_week)
  else:
    ct = Term.current_term()
    current_week = ct.term_week_of_date(date.today())
    cws = WeekSchedule.get_or_create_current_week_schedule(trainee)
  week_start, week_end = cws.week_range

  workers = Worker.objects.select_related('trainee').all().order_by('trainee__firstname', 'trainee__lastname')

  if generate_leaveslips:
    assign_leaveslips(service_scheduler=trainee, cws=cws)
    message = "Successfully generated leave slips."
    messages.add_message(request, messages.SUCCESS, message)
    return redirect('services:services_view')
  elif run_assign:
    # Preassign designated services here
    save_designated_assignments(cws)
    # clear all non-pinned assignments and save new ones
    # Do this first so that proper work count could be set
    # The Django implementation produces a SQL query for each delete item =(
    # Source : https://code.djangoproject.com/ticket/9519
    # Need a better solution for this (maybe sometime in the future when we update Django)
    Assignment.objects.filter(week_schedule=cws, pin=False).delete()
    assign(cws)
    return HttpResponseRedirect(reverse_lazy('services:services_view') + '?week_schedule=' + str(current_week))

  # For Review Tab
  categories = Category.objects.prefetch_related(
      Prefetch('services', queryset=Service.objects.order_by('weekday', 'start')),
      Prefetch('services__serviceslot_set', queryset=ServiceSlot.objects.filter(assignments__week_schedule=cws).annotate(workers_count=Count('assignments__workers')).order_by('-worker_group__assign_priority')),
      Prefetch('services__serviceslot_set', queryset=ServiceSlot.objects.filter(~Q(Q(assignments__isnull=False) & Q(assignments__week_schedule=cws))).filter(workers_required__gt=0), to_attr='unassigned_slots'),
      Prefetch('services__serviceslot_set__assignments', queryset=Assignment.objects.filter(week_schedule=cws)),
      Prefetch('services__serviceslot_set__assignments__workers', queryset=Worker.objects.select_related('trainee').order_by('trainee__gender', 'trainee__firstname', 'trainee__lastname'))
  ).distinct()

  # For Services Tab
  service_categories = Category.objects.filter(services__designated=False).prefetch_related(
      Prefetch('services', queryset=Service.objects.filter(designated=False).order_by('weekday', 'start')),
      Prefetch('services__serviceslot_set', queryset=ServiceSlot.objects.all().order_by('-worker_group__assign_priority'))
  ).distinct()

  # For Designated Tab
  designated_categories = Category.objects.filter(services__designated=True).prefetch_related(
      Prefetch('services', queryset=Service.objects.filter(designated=True).order_by('weekday', 'start')),
      Prefetch('services__serviceslot_set', queryset=ServiceSlot.objects.all().order_by('-worker_group__assign_priority'))
  ).distinct()

  worker_assignments = Worker.objects.select_related('trainee').prefetch_related(Prefetch('assignments',
                                                                                          queryset=Assignment.objects.filter(week_schedule=cws).select_related('service', 'service_slot', 'service__category').order_by('service__weekday'),
                                                                                          to_attr='week_assignments'))

  exceptions = ServiceException.objects.all().prefetch_related('workers', 'services').select_related('schedule')

  # Getting all services to be displayed for calendar
  services = Service.objects.filter(active=True).prefetch_related('serviceslot_set', 'worker_groups').order_by('start', 'end')
  # .filter(Q(day__isnull=True) | Q(day__range=(week_start, week_end)))

  # attach services directly to trainees for easier template traversal
  for worker in worker_assignments:
    service_db = {}
    for a in worker.week_assignments:
      service_db.setdefault(a.service.category, []).append((a.service, a.service_slot.name))
    worker.services = service_db

  # Make workers_bb
  lJRender = JSONRenderer().render
  workers_bb = lJRender(WorkerIDSerializer(workers, many=True).data)
  services_bb = lJRender(ServiceCalendarSerializer(services, many=True).data)

  ctx = {
      'workers': workers,
      'workers_bb': workers_bb,
      'exceptions': exceptions,
      'categories': categories,
      'service_categories': service_categories,
      'designated_categories': designated_categories,
      'services_bb': services_bb,
      'report_assignments': worker_assignments,
      'cws': cws,
      'current_week': current_week,
      'prev_week': (current_week - 1),
      'next_week': (current_week + 1)
  }
  return render(request, 'services/services_view.html', ctx)


def generate_report(request, house=False):
  user = request.user
  trainee = trainee_from_user(user)
  current_week = request.GET.get('week_schedule', None)
  if current_week:
    current_week = int(current_week)
    cws = WeekSchedule.get_or_create_week_schedule(trainee, current_week)
  else:
    cws = WeekSchedule.get_or_create_current_week_schedule(trainee)
  week_start, week_end = cws.week_range

  order = [
      'Breakfast Prep',
      'Breakfast Cleanup',
      'Lunch Prep',
      'Lunch Cleanup',
      'Sack Lunch',
      'Supper Prep',
      'Supper Cleanup',
      'Supper Delivery',
      'Dust Mopping',
      'Restroom Cleaning',
      'Space Cleaning',
      'Chairs',
  ]
  ordering = dict([reversed(o) for o in enumerate(order)])
  categories = Category.objects.filter(~Q(name='Designated Services')).prefetch_related(
      Prefetch('services', queryset=Service.objects.order_by('weekday'))
  ).distinct()
  categories = sorted(categories, key=lambda c: ordering.get(c.name, float('inf')))

  worker_assignments = Worker.objects.select_related('trainee').prefetch_related(
      Prefetch('assignments', queryset=Assignment.objects.filter(week_schedule=cws).select_related('service', 'service_slot', 'service__category').order_by('service__weekday'), to_attr='week_assignments'))\
      .order_by('trainee__lastname', 'trainee__firstname')

  schedulers = list(Trainee.objects.filter(groups__name='service_schedulers').exclude(groups__name='dev').values_list('firstname', 'lastname'))
  schedulers = ", ".join("%s %s" % tup for tup in schedulers)

  # attach services directly to trainees for easier template traversal
  for worker in worker_assignments:
    service_db = {}
    designated_list = []
    for a in worker.week_assignments:
      if a.service.category.name == "Designated Services":
        designated_list.append(a.service)
      else:
        service_db.setdefault(a.service.category, []).append((a.service, a.service_slot.name))
      # re-order so service dates in box are in ascending order
      for cat, services in service_db.items():
        service_db[cat] = sorted(services, key=lambda s: (s[0].weekday + 6) % 7)
    worker.services = service_db
    worker.designated_services = designated_list

  ctx = {
      'columns': 2,
      'pagesize': 'letter',
      'orientation': 'landscape',
      'wkstart': str(week_start),
      'categories': categories,
      'worker_assignments': worker_assignments,
      'encouragement': cws.encouragement,
      'schedulers': schedulers,
      'page_title': 'FTTA Service Schedule'
  }

  if house:
    ctx['houses'] = House.objects.filter(Q(gender="B") | Q(gender="S"))
    return render(request, 'services/services_report_house.html', ctx)

  if request.POST.get('encouragement') is not None:
    if cws is None:
      print "no current week schedule"
    else:
      cws.encouragement = request.POST.get('encouragement')
      cws.save()

  return render(request, 'services/services_report_base.html', ctx)


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


def generate_signin(request, k=False, r=False, o=False):
  user = request.user
  trainee = trainee_from_user(user)
  current_week = request.GET.get('week_schedule', None)
  if current_week:
    current_week = int(current_week)
    cws = WeekSchedule.get_or_create_week_schedule(trainee, current_week)
  else:
    cws = WeekSchedule.get_or_create_current_week_schedule(trainee)
  week_start, week_end = cws.week_range
  # cws_assign = Assignment.objects.filter(week_schedule=cws).order_by('service__weekday', 'service__start')

  cws_assign = Assignment.objects.filter(week_schedule=cws).order_by('service__weekday')
  cws_assign = cws_assign.annotate(day=7 + F('service__weekday') - 1).annotate(weekday=F('day') % 7).order_by('weekday', 'service__start')

  ctx = {'wkstart': week_start}

  # All prep and cleanups are combined into onto one sign in sheet
  # first sorts for all assignment objects with preps and cleanups
  # get their serivce id then loop through each service id to all the assignments with the same service but different service slots
  # do it first for tuesday-LD then for monday because of the weekday choices assignment
  if k:
    kitchen = []
    kitchen_assignments = Assignment.objects.filter(week_schedule=cws).filter(Q(service__name__contains='Prep') | Q(service__name__contains='Cleanup'))
    assignments = kitchen_assignments.distinct('service')
    for s in cws_assign.filter(id__in=assignments).values('service'):
      assigns = sorted(cws_assign.filter(service__pk=s['service']), key=lambda a: a.service_slot.role)
      kitchen.append(merge_assigns(assigns))
    kitchen = zip(kitchen[::4], kitchen[1::4], kitchen[2::4], kitchen[3::4])
    ctx['kitchen'] = kitchen
    return render(request, 'services/signinsheetsk.html', ctx)

  # Restroom cleanups are separated by gender
  elif r:
    restroom_assignments = cws_assign.filter(service__name__contains='Restroom')
    restroom_b = restroom_assignments.filter(service_slot__gender='B')
    restroom_s = restroom_assignments.filter(service_slot__gender='S')

    restroom = [restroom_b, restroom_s]
    ctx['restroom'] = restroom
    return render(request, 'services/signinsheetsr.html', ctx)

  # All other sign-in reports
  elif o:
    cws_assign = cws_assign.filter(service__designated=False)
    # delivery = cws_assign.filter(service__name__contains='Delivery')
    chairs = cws_assign.filter(service__name__contains='Chairs')
    dust = cws_assign.filter(service__name__contains='Dust')
    lunch = cws_assign.filter(service__name__contains='Sack')
    space = cws_assign.filter(service__name__contains='Space Cleaning')
    supper = cws_assign.filter(service__name__contains='Supper Delivery')
    others = [chairs, dust, space, supper]

    lunches = defaultdict(list)
    for l in lunch:
      lunches[l.service.weekday].append(l)
    # get day, assignments pairs sorted by monday last
    items = sorted(lunches.items(), key=lambda i: (i[0] + 6) % 7)
    for i, item in enumerate(items[::2]):
      index = i * 2
      others.append(items[index][1] + items[index + 1][1] if index + 1 < len(items) else [])
    ctx['others'] = others
    return render(request, 'services/signinsheetso.html', ctx)


# API Views

class UpdateWorkersViewSet(BulkModelViewSet):
  queryset = Worker.objects.all()
  serializer_class = UpdateWorkerSerializer

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class ServiceSlotWorkloadViewSet(BulkModelViewSet):
  queryset = ServiceSlot.objects.all()
  serializer_class = ServiceSlotWorkloadSerializer

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class ServiceActiveViewSet(BulkModelViewSet):
  queryset = Service.objects.all()
  serializer_class = ServiceActiveSerializer

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class ServiceTimeViewSet(BulkModelViewSet):
  queryset = Service.objects.all()
  serializer_class = ServiceTimeSerializer

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class AssignmentViewSet(BulkModelViewSet):
  queryset = Assignment.objects.all()
  serializer_class = WorkerAssignmentSerializer

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class AssignmentPinViewSet(BulkModelViewSet):
  queryset = Assignment.objects.all()
  serializer_class = AssignmentPinSerializer

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class ExceptionActiveViewSet(BulkModelViewSet):
  queryset = ServiceException.objects.all()
  serializer_class = ExceptionActiveSerializer


class ServiceHours(GroupRequiredMixin, UpdateView):
  model = ServiceAttendance
  template_name = 'services/service_hours.html'
  form_class = ServiceAttendanceForm
  group_required = ['designated_service']
  service = None
  designated_assignmnets = None
  service_id = 0  # from ajax
  week = 0  # from ajax

  def get_object(self, queryset=None):
    term = Term.current_term()
    worker = trainee_from_user(self.request.user).worker
    self.designated_assignmnets = worker.assignments.all().filter(service__designated=True)
    try:
      self.week = self.kwargs['week']
    except KeyError:
      self.week = term.term_week_of_date(datetime.now().date())

    # get service
    try:
      self.service_id = self.kwargs['service_id']
    except KeyError:
      self.service_id = self.designated_assignmnets[0].service.id

    self.service = Service.objects.get(id=self.service_id)

    # get the existing object or created a new one
    service_attendance, created = ServiceAttendance.objects.get_or_create(worker=worker, term=term, week=self.week, designated_service=self.service)
    return service_attendance

  def get_form_kwargs(self):
    kwargs = super(ServiceHours, self).get_form_kwargs()
    kwargs['worker'] = trainee_from_user(self.request.user).worker
    return kwargs

  def form_valid(self, form):
    self.update_service_roll(service_attendance=self.get_object(), data=self.request.POST.copy())
    return super(ServiceHours, self).form_valid(form)

  def update_service_roll(self, service_attendance, data):
    start_list = data.pop('start_datetime')
    end_list = data.pop('end_datetime')
    task_list = data.pop('task_performed')
    ServiceRoll.objects.filter(service_attendance=service_attendance).delete()

    for index in range(len(start_list)):
      sr = ServiceRoll()
      sr.service_attendance = service_attendance
      sr.start_datetime = parser.parse(start_list[index])
      sr.end_datetime = parser.parse(end_list[index])
      sr.task_performed = task_list[index]
      sr.save()

  def get_context_data(self, **kwargs):
    ctx = super(ServiceHours, self).get_context_data(**kwargs)
    ctx['button_label'] = 'Submit'
    ctx['page_title'] = 'Designated Service Hours'
    service_roll_forms = []
    service_rolls = ServiceRoll.objects.filter(service_attendance=self.get_object()).order_by('start_datetime')
    if service_rolls.count() == 0:
      service_roll_forms.append(ServiceRollForm())
    else:
      for sr in service_rolls:
        service_roll_forms.append(ServiceRollForm(instance=sr))
    ctx['service_roll_forms'] = service_roll_forms
    return ctx


class ServiceHoursTAView(GroupRequiredMixin, TemplateView):
  template_name = 'services/service_hours_ta_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    context = super(ServiceHoursTAView, self).get_context_data(**kwargs)
    term = Term.current_term()
    week = 0
    designated_services = Service.objects.filter(category__name__icontains='designated')  # designates services
    week = self.request.GET.get('week', term.term_week_of_date(datetime.now().date()))
    services = self.request.GET.getlist('services', [])
    if services:
      if -1 not in services:
        designated_services = designated_services.filter(id__in=services)
    else:
      designated_services = designated_services.filter(id=designated_services.first().id)
    context['designated_services'] = self.get_services_dict(term, week, designated_services)
    context['week_range'] = [str(i) for i in range(20)]
    context['weekinit'] = str(week)
    context['page_title'] = "Service Hours Report"
    context['services_qs'] = Service.objects.filter(category__name__icontains='designated')
    return context

  def get_services_dict(self, term, week, service_ids=[]):
    designated_services = Service.objects.filter(category__name__icontains='designated')  # designates services
    services = []
    if service_ids:
      designated_services = designated_services.filter(id__in=service_ids)
    for ds in designated_services:
      workers = []
      worker_ids = ds.assignments.values_list('workers', flat=True).distinct('workers')
      for worker in Worker.objects.filter(id__in=worker_ids):  # filter out None values
        try:
          serv_att = worker.serviceattendance_set.get(term=term, week=week, designated_service=ds)
          workers.append({
            'full_name': worker.full_name,
            'service_rolls': serv_att.serviceroll_set.order_by('start_datetime').values(),
            'total_hours': serv_att.get_service_hours()
          })
        except ObjectDoesNotExist:
          continue
      services.append({
        'name': ds.name,
        'workers': workers
      })
    return services


class DesignatedServiceViewer(GroupRequiredMixin, TemplateView):
  template_name = 'services/designated_services_viewer.html'
  group_required = ['training_assistant', 'service_schedulers']

  def get_context_data(self, **kwargs):
    context = super(DesignatedServiceViewer, self).get_context_data(**kwargs)
    designated_services = Service.objects.filter(designated=True)
    services = []
    for w in Worker.objects.all().values('id', 'trainee__firstname', 'trainee__lastname', 'trainee__gender', 'trainee__current_term', 'trainee__team__type'):
      services.append({
          'worker': w,
          'service_name': '',

      })

    for s in designated_services:
      for wg in s.worker_groups.all():
        for w in wg.workers.all():
          dic = [x for x in services if x['worker']['id'] == w.id][0]
          if dic['service_name']:
            dic['service_name'] = dic['service_name'] + ", " + s.name
          else:
            dic['service_name'] = s.name

    context['designated_services'] = services
    context['page_title'] = "Designated Service Trainees"
    return context


class ExceptionView(GroupRequiredMixin, FormView):
  model = ServiceException
  template_name = 'services/services_add_exception.html'
  form_class = AddExceptionForm
  success_url = reverse_lazy('services:services_view')
  group_required = ['service_schedulers']

  def form_valid(self, form):
    trainees = form.cleaned_data.get('workers')
    exc = form.save(commit=False)
    exc.save()
    exc.workers.clear()
    for t in trainees:
      exc.workers.add(t.worker)
    for s in form.cleaned_data.get('services'):
      exc.services.add(s)
    exc.save()
    return HttpResponseRedirect(self.success_url)


class AddExceptionView(ExceptionView, CreateView):
  def get_context_data(self, **kwargs):
    ctx = super(AddExceptionView, self).get_context_data(**kwargs)
    ctx['exceptions'] = ServiceException.objects.all()
    ctx['button_label'] = 'Add Exception'
    return ctx


class UpdateExceptionView(ExceptionView, UpdateView):
  def get_context_data(self, **kwargs):
    ctx = super(UpdateExceptionView, self).get_context_data(**kwargs)
    ctx['exceptions'] = ServiceException.objects.exclude(id=self.object.id)
    ctx['form'] = self.get_modified_form(self.object)
    ctx['button_label'] = 'Update Exception'
    return ctx

  def get_modified_form(self, obj):
    # populate ExceptionForm with trainee ids (instead of worker ids)
    # This is because Trainee select form uses trainee ids instead of worker ids
    data = {}
    data.update(obj.__dict__)
    data['schedule'] = SeasonalServiceSchedule.objects.filter(id=obj.schedule_id).first()
    data['service'] = Service.objects.filter(id=obj.service_id).first()
    data['services'] = [s for s in obj.services.all()]
    data['workers'] = [w.trainee for w in obj.workers.all()]
    return AddExceptionForm(data)


class SingleTraineeServicesViewer(GroupRequiredMixin, FormView):
  template_name = 'services/single_trainee_services_viewer.html'
  group_required = ['training_assistant', 'service_schedulers']
  form_class = SingleTraineeServicesForm

  def get_success_url(self):
    if 'trainee_id' in self.kwargs:
      trainee_id = self.kwargs['trainee_id']
      return reverse('services:trainee_services_viewer', kwargs={'trainee_id': trainee_id})
    else:
      return reverse('services:single_trainee_services_viewer')

  def get_initial(self):
    """
    Returns the initial data to use for forms on this view.
    """
    initial = super(SingleTraineeServicesViewer, self).get_initial()

    trainee_id = self.kwargs.get('trainee_id', None)
    if trainee_id:
      initial['trainee_id'] = Trainee.objects.get(id=trainee_id)
    else:
      initial['trainee_id'] = Trainee.objects.filter(is_active=True).first()
    return initial

  def get_context_data(self, **kwargs):
    trainee_id = self.kwargs.get('trainee_id', None)
    if trainee_id:
      trainee = Trainee.objects.get(id=trainee_id)
    else:
      trainee = Trainee.objects.filter(is_active=True).first()
    context = super(SingleTraineeServicesViewer, self).get_context_data(**kwargs)
    context['page_title'] = "Single Trainee Services Viewer"
    context['trainee'] = trainee

    history = trainee.worker.service_history
    history = self.reformat(history)
    context['history'] = json.dumps(history)

    return context

  def reformat(self, data):
    ws = list(set([d['week_schedule__id'] for d in data]))  # already ordered
    new_data = []
    for w in ws:
      alist = []
      for d in data:
        if d['week_schedule__id'] == w:
          alist.append({'service': d['service__name'], 'weekday': d['service__weekday'], 'designated': d['service__designated']})
      if len(alist) > 0:
        start_date = WeekSchedule.objects.get(id=w).start
        week = Term.current_term().term_week_of_date(start_date)
        new_data.append({'week': week, 'assignments': alist})
    return new_data


class ServiceCategoryAnalyzer(FormView):
  template_name = 'services/service_category_analyzer.html'
  form_class = ServiceCategoryAnalyzerForm

  def get_success_url(self):
    if 'category_id' in self.kwargs:
      category_id = self.kwargs['category_id']
      return reverse('services:service_category_analyzer_selected', kwargs={'category_id': category_id})
    else:
      return reverse('services:service_category_analyzer')

  def get_initial(self):
    """
    Returns the initial data to use for forms on this view.
    """
    initial = super(ServiceCategoryAnalyzer, self).get_initial()

    category_id = self.kwargs.get('category_id', None)
    if category_id:
      initial['category_id'] = Category.objects.get(id=category_id)
    else:
      initial['category_id'] = Category.objects.exclude(name="Designated Services").first()
    return initial

  def get_context_data(self, **kwargs):
    category_id = self.kwargs.get('category_id', None)
    if category_id:
      category = Category.objects.get(id=category_id)
    else:
      category = Category.objects.exclude(name="Designated Services").first()
    context = super(ServiceCategoryAnalyzer, self).get_context_data(**kwargs)
    context['page_title'] = "Service Category Analyzer"
    context['category'] = category
    return context

'''

  services.worker_groups

  # Make network nodes for services
  # Service.name : serviceslot_set.role x serviceslot_set.workers_required

  services.serviceslot_set.worker_group.workers

  {
    servicename: service
  }

  {
    workerid: worker
  }


  {
    servicename: {
      workers: [
        worker1,
        worker2
      ],
      role: worker,
      workers_required: 3,
      workload: 3
    },
    day: Monday
  }

  worker = {
    history: [],
    service_cap: 3,
    service_needed: 3
  }

'''
