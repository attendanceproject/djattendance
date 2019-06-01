import csv
import json
from collections import defaultdict
from datetime import date, datetime

from accounts.models import Trainee
from aputils.decorators import group_required
from aputils.trainee_utils import trainee_from_user
from aputils.utils import timeit
from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import F, Q, Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from houses.models import House
from rest_framework.renderers import JSONRenderer
from rest_framework_bulk import BulkModelViewSet
from terms.models import FIRST_WEEK, LAST_WEEK, Term

from .forms import (AddExceptionForm, ServiceAttendanceForm,
                    ServiceCategoryAnalyzerForm, ServiceForm, ServiceRollForm,
                    SingleTraineeServicesForm)
from .models import (Assignment, Category, Prefetch, SeasonalServiceSchedule,
                     Service, ServiceAttendance, ServiceException, ServiceRoll,
                     ServiceSlot, WeekSchedule, Worker)
from .serializers import (AssignmentPinSerializer, ExceptionActiveSerializer,
                          ServiceActiveSerializer, ServiceCalendarSerializer,
                          ServiceSlotWorkloadSerializer, ServiceTimeSerializer,
                          UpdateWorkerSerializer, WorkerAssignmentSerializer,
                          WorkerIDSerializer)
from .utils import (SERVICE_CHECKS, assign, assign_leaveslips, merge_assigns,
                    save_designated_assignments)


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

  pre_assignments = Assignment.objects.filter(week_schedule=cws, service__isnull=False).select_related(
      'service',
      'service_slot',
      'service__category'
  ).order_by('service__weekday')

  worker_assignments = Worker.objects.select_related('trainee').prefetch_related(
      Prefetch('assignments', queryset=pre_assignments, to_attr='week_assignments')
  )

  exceptions = ServiceException.objects.all().prefetch_related('workers', 'services').select_related('schedule')

  # Getting all services to be displayed for calendar
  services = Service.objects.filter(active=True).prefetch_related('serviceslot_set', 'worker_groups').order_by('start', 'end')

  for worker in worker_assignments:
    worker.workload = sum(a.workload for a in worker.week_assignments)
    worker.checks = [
        c.check(worker.week_assignments) for c in SERVICE_CHECKS
    ]
    # attach services directly to trainees for easier template traversal
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
      'next_week': (current_week + 1),
      'service_checks': SERVICE_CHECKS,
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
    ctx['houses'] = House.objects.filter(id__in=Trainee.objects.values_list('house', flat=True))
    return render(request, 'services/services_report_house.html', ctx)

  if request.POST.get('encouragement') is not None:
    if cws is None:
      print "no current week schedule"
    else:
      cws.encouragement = request.POST.get('encouragement')
      cws.save()

  return render(request, 'services/services_report_base.html', ctx)


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
    # Add empty dicts until len(kitchen) is a multiple of 4 so zip() doesn't cut off any service printouts
    if (len(kitchen) % 4) != 0:
      for i in range(0, 4 - (len(kitchen) % 4)):
        kitchen.append([])
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
    # Add empty tuples of (None,[]) (DUMMY VALUE) until len(items) is a multiple of 2 so no service printouts get cut off
    items = sorted(lunches.items(), key=lambda i: (i[0] + 6) % 7)
    if (len(items) % 2) != 0:
      for i in range(0, 2 - (len(items) % 2)):
        items.append((None, []))
    for i, item in enumerate(items[::2]):
      index = i * 2
      if len(items) == 1:
        others.append(items[index][1])
      else:
        others.append(items[index][1] + items[index + 1][1] if index + 1 < len(items) else [])
    ctx['others'] = filter(lambda x: x, others)  # remove empty querysets
    return render(request, 'services/signinsheetso.html', ctx)


def changeWeek(request):

  user = request.user
  trainee = trainee_from_user(user)
  service_db = {}
  designated_list = []

  if request.is_ajax():
    week_id = request.GET['week']
    current_week = int(week_id)
    current_week = current_week if current_week < LAST_WEEK else LAST_WEEK
    current_week = current_week if current_week > FIRST_WEEK else FIRST_WEEK
    cws = WeekSchedule.get_or_create_week_schedule(trainee, week_id)
  else:
    ct = Term.current_term()
    current_week = ct.term_week_of_date(date.today())
    cws = WeekSchedule.get_or_create_current_week_schedule(trainee)

  worker_assignments = Worker.objects.select_related('trainee').prefetch_related(Prefetch(
      'assignments',
      queryset=Assignment.objects.filter(week_schedule=cws).select_related('service').order_by('service__weekday'),
      to_attr='week_assignments')
  )

  # Find services related to the user
  for current_worker in worker_assignments:
    trainee = str(trainee)
    if trainee == current_worker.full_name:
      for a in current_worker.week_assignments:
        if a.service.category.name == "Designated Services":
          designated_list.append(a.service)
        else:
          # service_db.setdefault(a.service.name, []).append((a.service.weekday, a.service_slot.name))
          service_db.setdefault(a.service.name, a.service.weekday)

  service_data = json.dumps(service_db)
  return HttpResponse(service_data, content_type='application/json')


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


class ServiceHours(UpdateView):
  model = ServiceAttendance
  template_name = 'services/service_hours.html'
  form_class = ServiceAttendanceForm
  service = None
  w_designated_services = None
  service_id = 0  # from ajax
  week = 0  # from ajax

  def get_object(self, queryset=None):
    term = Term.current_term()
    worker = trainee_from_user(self.request.user).worker
    self.w_designated_services = worker.designated.all()
    self.week = self.kwargs.get('week', None)
    self.service_id = self.kwargs.get('service_id', None)
    if not self.week:
      self.week = term.term_week_of_date(datetime.now().date())

    if not self.service_id:
      self.service_id = self.w_designated_services.first().id

    self.service = Service.objects.get(id=self.service_id)

    # get the existing object or created a new one
    service_attendance = ServiceAttendance.objects.get_or_create(worker=worker, term=term, week=self.week, designated_service=self.service)[0]
    return service_attendance

  def get_form_kwargs(self):
    kwargs = super(ServiceHours, self).get_form_kwargs()
    kwargs['worker'] = trainee_from_user(self.request.user).worker
    return kwargs

  def dispatch(self, request, *args, **kwargs):
    if request.method == 'GET':
      kwarg_keys = self.kwargs.keys()
      if ('week' not in kwarg_keys) or ('service_id' not in kwarg_keys):
        self.get_object()  # gives values to self.service_id, self.week
        return redirect(reverse('services:designated_service_hours', kwargs={'service_id': self.service_id, 'week': self.week}))
    return super(ServiceHours, self).dispatch(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    service_roll_forms = self.get_service_roll_forms(self.request.POST)
    if all(f.is_valid() for f in service_roll_forms):
      service_attendance = self.get_object()
      ServiceRoll.objects.filter(service_attendance=service_attendance).delete()
      for srf in service_roll_forms:
        sr = srf.save(commit=False)
        sr.service_attendance = service_attendance
        sr.save()
      return redirect(reverse('services:designated_service_hours', kwargs={'service_id': self.kwargs['service_id'], 'week': self.kwargs['week']}))
    else:
      ctx = {'form': self.form_class(request.POST, worker=trainee_from_user(self.request.user).worker)}
      ctx['button_label'] = 'Submit'
      ctx['page_title'] = 'Designated Service Hours'
      ctx['service_roll_forms'] = service_roll_forms
      return super(ServiceHours, self).render_to_response(ctx)

  @staticmethod
  def get_service_roll_forms(data):
    start_list = data.getlist('start_datetime')
    end_list = data.getlist('end_datetime')
    task_list = data.getlist('task_performed')
    service_roll_forms = []
    for index in range(len(start_list)):
      temp = {}
      temp['start_datetime'] = start_list[index]
      temp['end_datetime'] = end_list[index]
      temp['task_performed'] = task_list[index]
      srf = ServiceRollForm(temp)
      service_roll_forms.append(srf)
    return service_roll_forms

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


class ServiceCategoryNotDoneViewer(FormView):
  template_name = 'services/service_category_not_done_viewer.html'
  form_class = ServiceCategoryAnalyzerForm

  def get_success_url(self):
    if 'category_id' in self.kwargs:
      category_id = self.kwargs['category_id']
      return reverse('services:service_category_not_done_viewer_selected', kwargs={'category_id': category_id})
    else:
      return reverse('services:service_category_not_done_viewer')

  def get_initial(self):
    initial = super(ServiceCategoryNotDoneViewer, self).get_initial()

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

    context = super(ServiceCategoryNotDoneViewer, self).get_context_data(**kwargs)
    context['page_title'] = "Have Not Done This Service Category This Term"
    context['category'] = category

    trainees = Trainee.objects.all()

    assignments = Assignment.objects.filter(service__category=Category.objects.filter(name=category)).prefetch_related('workers')
    for a in assignments:
      for w in a.workers.all():
        trainees = trainees.exclude(id=w.trainee.id)

    context['trainees'] = trainees
    context['count'] = trainees.count()
    context['brothers_count'] = trainees.filter(gender='B').count()
    context['sisters_count'] = trainees.filter(gender='S').count()

    return context


class ServiceCategoryCountsViewer(FormView):
  template_name = 'services/service_category_counts_viewer.html'
  form_class = ServiceCategoryAnalyzerForm

  def get_success_url(self):
    if 'category_id' in self.kwargs:
      category_id = self.kwargs['category_id']
      return reverse('services:service_category_counts_viewer_selected', kwargs={'category_id': category_id})
    else:
      return reverse('services:service_category_counts_viewer')

  def get_initial(self):
    initial = super(ServiceCategoryCountsViewer, self).get_initial()

    category_id = self.kwargs.get('category_id', None)
    if category_id:
      initial['category_id'] = Category.objects.get(id=category_id)
    else:
      initial['category_id'] = Category.objects.exclude(name="Designated Services").first()
    return initial

  def get_context_data(self, **kwargs):
    CURRENT_TERM = Term.current_term()
    category_id = self.kwargs.get('category_id', None)
    if category_id:
      category = Category.objects.get(id=category_id)
    else:
      category = Category.objects.exclude(name="Designated Services").first()

    context = super(ServiceCategoryCountsViewer, self).get_context_data(**kwargs)
    context['page_title'] = "Service Category Counts"
    context['category'] = category

    assignments = Assignment.objects.filter(week_schedule__start__gte=CURRENT_TERM.start).filter(service__category=category).prefetch_related('workers', 'week_schedule', 'service')
    count_list = []
    for a in assignments:
      for w in a.workers.all():
        if not any(d.get('id', None) == w.trainee.id for d in count_list):
          count_list.append({'id': w.trainee.id,
                             'full_name2': w.trainee.full_name2,
                             'times_done': 1,
                             'last_service': a.service.name,
                             'ws_of_last': a.week_schedule.start,
                             'wn_of_last': CURRENT_TERM.term_week_of_date(a.week_schedule.start),
                             'wd_of_last': a.service.weekday,
                             'start_time_of_last': a.service.start})
        else:
          t = filter(lambda person: person['id'] == w.trainee.id, count_list)
          t[0]['times_done'] += 1
          if (a.week_schedule.start > t[0]['ws_of_last']):
            t[0]['ws_of_last'] = a.week_schedule.start
            t[0]['wn_of_last'] = CURRENT_TERM.term_week_of_date(a.week_schedule.start)
            t[0]['wd_of_last'] = a.service.weekday
            t[0]['start_time_of_last'] = a.service.start
            t[0]['last_service'] = a.service.name
          elif (a.week_schedule.start == t[0]['ws_of_last'] and a.service.weekday > t[0]['wd_of_last']):
            t[0]['wd_of_last'] = a.service.weekday
            t[0]['start_time_of_last'] = a.service.start
            t[0]['last_service'] = a.service.name

    context['count_list'] = count_list

    return context


class DesignatedServiceAdderViewer(FormView):
  template_name = 'services/add_trainee_service_form.html'
  form_class = ServiceForm

  def get_success_url(self):
    return reverse('services:services_form')

  def form_valid(self, form):
    if form.is_valid():
      form.save()
      workers = form.cleaned_data.get('workers')
      service = form.cleaned_data.get('designated_service')
      ct = Term.current_term()
      week_range = range(0, ct.term_week_of_date(date.today()))
      for worker in workers:
        for week in week_range:
          sa, created = ServiceAttendance.objects.get_or_create(worker=worker, designated_service=service, term=ct, week=week)
          if created:
            sa.excused = True
            sa.save()
    return super(DesignatedServiceAdderViewer, self).form_valid(form)

  def get_context_data(self, **kwargs):
    context = super(DesignatedServiceAdderViewer, self).get_context_data(**kwargs)
    context['page_title'] = "Add Trainees to Designated Service"
    return context


class ImportGuestsView(GroupRequiredMixin, TemplateView):
  template_name = 'services/import_guests.html'
  group_required = ['training_assistant', 'service_schedulers']

  def get_context_data(self, **kwargs):
    context = super(ImportGuestsView, self).get_context_data(**kwargs)
    table_columns = [
      {"title": "First Name", "data": "First"},
      {"title": "Last Name", "data": "Last"},
      {"title": "House", "data": "House"},
      {"title": "Gender", "data": "Gender"}
    ]
    context['page_title'] = "Import Guest Workers"
    context['columns'] = json.dumps(table_columns)
    context['workers'] = Worker.objects.filter(trainee__type='S')
    return context


@group_required(['training_assistant', 'service_schedulers'])
def process_guests(request):
  if request.method == "POST":
    csv_file = request.FILES['fileinput']
    reader = csv.DictReader(csv_file)
    for row in reader:
      trainee = {
        'email': row['First'] + '.' + row['Last'] + '@ap.ftta.lan',
        'firstname': row['First'],
        'lastname': row['Last'],
        'gender': row['Gender'],
        'type': 'S',
        'current_term': 1,
        'is_active': True,
        'house': House.objects.get(name=row['House'])
      }
      t, created = Trainee.objects.get_or_create(**trainee)
      if created:
        Worker.objects.get_or_create(trainee=t, health=10, services_cap=2)
  return redirect(reverse('services:import-guests'))


@group_required(['training_assistant', 'service_schedulers'])
def deactivate_guest(request, pk):
  if request.method == "POST" and request.is_ajax():
    w = Worker.objects.get(pk=pk)
    w.trainee.delete()
    return JsonResponse({'success': True})
  return JsonResponse({'success': False})


@group_required(['training_assistant', 'service_schedulers'])
def bulk_deactivate_guests(request):
  if request.method == "POST" and request.is_ajax():
    for key, value in request.POST.iteritems():
      w = Worker.objects.get(pk=key)
      w.trainee.delete()
    return JsonResponse({'success': True})
  return JsonResponse({'success': False})