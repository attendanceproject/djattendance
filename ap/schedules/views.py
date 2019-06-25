import json

from accounts.models import Trainee
from aputils.decorators import group_required
from aputils.trainee_utils import trainee_from_user
from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from django.views.generic import CreateView, DeleteView, FormView, UpdateView
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from terms.models import Term
from attendance.models import Roll
from leaveslips.models import IndividualSlip

from .forms import EventForm, BaseScheduleForm, CreateScheduleForm, UpdateScheduleForm, AfternoonClassForm
from .models import Event, Schedule
from .serializers import (EventFilter, EventSerializer,
                          EventWithDateSerializer, ScheduleFilter,
                          ScheduleSerializer)
from .utils import should_split_schedule, split_schedule, afternoon_class_transfer

@group_required(['training_assistant', 'attendance_monitors'])
def assign_trainees_view(request, pk):
  if request.method == 'POST' and request.is_ajax():
    s = get_object_or_404(Schedule, pk=pk)
    s.assign_trainees()
    messages.success(request, 'Assigned trainees to schedule')
  return JsonResponse({'success': "True"})


@group_required(['training_assistant', 'attendance_monitors'])
def assign_team_schedules(request):
  ws = ','.join([str(x) for x in range(1, 19)])
  for s in Schedule.objects.filter(Q(weeks=ws) & ~Q(team_roll=None)):
    s.assign_trainees()
  return HttpResponse("Assigned trainees to team schedules")


@group_required(['training_assistant', 'attendance_monitors'])
def clear_team_schedules(request):
  ws = ','.join([str(x) for x in range(1, 19)])
  for s in Schedule.objects.filter(Q(weeks=ws) & ~Q(team_roll=None)):
    s.trainees.clear()
  return HttpResponse("Clear trainees from team schedules")


@group_required(['training_assistant', 'attendance_monitors'])
def clear_all_schedules(request):
  for s in Schedule.objects.all():
    s.trainees.clear()
  return HttpResponse("Cleared trainees from all schedules")


class EventDetail(generic.DetailView):
  model = Event
  context_object_name = "event"


class EventDelete(generic.DeleteView):
  model = Event
  success_url = reverse_lazy('schedules:event-create')


class TermEvents(generic.ListView):
  model = Event
  template_name = 'schedules/term_events.html'
  context_object_name = 'events'

  def get_queryset(self, **kwargs):
    return Event.objects.filter(term=Term.decode(self.kwargs['term']))

  def get_context_data(self, **kwargs):
    context = super(TermEvents, self).get_context_data(**kwargs)
    context['term'] = Term.decode(self.kwargs['term'])
    return context


class AllSchedulesView(generic.ListView):
  model = Schedule
  template_name = 'schedules/schedules_list.html'


#  API-ONLY VIEWS  #
class EventViewSet(viewsets.ModelViewSet):
  queryset = Event.objects.all()
  serializer_class = EventWithDateSerializer

  def get_queryset(self):
    if 'trainee' in self.request.GET:
      trainee = Trainee.objects.get(pk=self.request.GET.get('trainee'))
    else:
      user = self.request.user
      trainee = trainee_from_user(user)
    events = trainee.events
    return events

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class ScheduleViewSet(viewsets.ModelViewSet):
  queryset = Schedule.objects.all()
  serializer_class = ScheduleSerializer
  filter_backends = (DjangoFilterBackend,)
  filter_class = ScheduleFilter

  def get_queryset(self):
    trainee = trainee_from_user(self.request.user)
    schedule = Schedule.objects.filter(trainees=trainee)
    return schedule

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllEventViewSet(viewsets.ModelViewSet):
  queryset = Event.objects.all()
  serializer_class = EventSerializer
  filter_backends = (DjangoFilterBackend,)
  filter_class = EventFilter

  def get_queryset(self):
    try:
      week = int(self.request.GET.get('week', ''))
      day = int(self.request.GET.get('weekday', ''))
      date = Term.current_term().get_date(week, day)
      return Event.objects.filter(chart__isnull=False).filter(Q(weekday=day, day__isnull=True) | Q(day=date))
    except ValueError as e:
      print('%s (%s)' % (e.message, type(e)))
      return Event.objects.all()

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllScheduleViewSet(viewsets.ModelViewSet):
  queryset = Schedule.objects.all()
  serializer_class = ScheduleSerializer
  filter_backends = (DjangoFilterBackend,)
  filter_class = ScheduleFilter

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class EventCRUDMixin(GroupRequiredMixin):
  model = Event
  template_name = 'schedules/admin_form.html'
  form_class = EventForm
  group_required = ['attendance_monitors', 'training_assistant']


class EventAdminCreate(EventCRUDMixin, CreateView):
  def get_context_data(self, **kwargs):
    ctx = super(EventAdminCreate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Create Event'
    ctx['button_label'] = 'Create'
    return ctx


class EventAdminUpdate(EventCRUDMixin, UpdateView):
  def get_context_data(self, **kwargs):
    ctx = super(EventAdminUpdate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Update Event'
    ctx['button_label'] = 'Update'
    ctx['delete_button'] = True
    return ctx


class EventAdminDelete(EventCRUDMixin, DeleteView):
  success_url = reverse_lazy('schedules:admin-event-create')


class ScheduleCRUDMixin(GroupRequiredMixin):
  model = Schedule
  template_name = 'schedules/admin_form.html'
  form_class =  BaseScheduleForm
  group_required = [u'attendance_monitors', u'training_assistant']

  def form_invalid(self, form, **kwargs):
    context = self.get_context_data(form=form)
    form_data = form.data
    if 'Create' in form_data:
      context['action'] = 'create'
    elif 'Update' in form_data:
      context['action'] = 'update'
    elif 'Delete' in form_data:
      context['action'] = 'delete'

    error_data = json.loads(form.errors.as_json())
    errors_list = error_data['__all__']
    for error in errors_list:
      if error['code'] == 'invalidRolls':
        rolls_to_delete = error['message']
        roll_ids = [int(s) for s in rolls_to_delete[1:-1].split(',')]
        context['delete_rolls'] = Roll.objects.filter(id__in=roll_ids).order_by('trainee', 'date')
        break

    return self.render_to_response(context)

class ScheduleAdminCreate(ScheduleCRUDMixin, CreateView):
  form_class = CreateScheduleForm

  def get_context_data(self, **kwargs):
    ctx = super(ScheduleAdminCreate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Create Schedule'
    ctx['button_label'] = 'Create'
    return ctx

class ScheduleAdminUpdate(ScheduleCRUDMixin, UpdateView):
  form_class = UpdateScheduleForm

  def get_context_data(self, **kwargs):
    ctx = super(ScheduleAdminUpdate, self).get_context_data(**kwargs)
    ctx['button_label'] = 'Update'
    ctx['page_title'] = 'Update Schedule'
    ctx['delete_button'] = True
    ctx['split_button'] = True
    ctx['assign_trainees_button'] = True
    return ctx

  def form_valid(self, form):

    new_schedule = form.instance
    cur_schedule = Schedule.objects.get(id=new_schedule.id)

    new_set = new_schedule.trainees.all()
    current_set = cur_schedule.trainees.all()

    # If the trainee sets are identical, minor schedule update
    to_add = new_set.exclude(pk__in=current_set)
    to_delete = current_set.exclude(pk__in=new_set)

    if not to_add and not to_delete:
      return super(ScheduleAdminUpdate, self).form_valid(form)

    for t in to_delete:
      # trainee cannot be moved off of a schedule if there are rolls for events on that schedule
      t_events = t.rolls.order_by('event').distinct('event').values_list('event__id', flat=True)
      if cur_schedule.events.filter(id__in=t_events).exists():
        form._errors[NON_FIELD_ERRORS] = ErrorList(['Trainee(s) cannot be removed from schedule. Split the schedule.'])
        return super(ScheduleAdminUpdate, self).form_invalid(form)

    for t in to_add:
      # trainee cannot be moved onto a schedule if there are rolls for events on a schedule that it will overlap
      sch_event_set = cur_schedule.events.values('event__id', 'event__start', 'event__end')
      tr_event_set = t.rolls.order_by('event').distinct('event').values('event__id', 'event__start', 'event__end')
      for i in tr_event_set:
        for j in sch_event_set:
          if EventUtils.time_overlap(i['event__start'], i['event__end'], j['event__start'], j['event__end']):
            form._errors[NON_FIELD_ERRORS] = ErrorList(['Trainee(s) cannot be added to schedule. Split the schedule.'])
            return super(ScheduleAdminUpdate, self).form_invalid(form)
    if 'Delete' in form.data:
      obj_id = self.get_object().id
      Schedule.objects.get(pk=obj_id).delete()
      return redirect(reverse('schedules:admin-schedule-table'))

    return super(ScheduleAdminUpdate, self).form_valid(form)

def scheduleCRUD_delete_rolls(request):
  roll_ids = [int(string) for string in json.loads(request.POST.get('roll_ids'))]
  rolls = Roll.objects.filter(id__in=roll_ids)
  for leaveslip in IndividualSlip.objects.filter(rolls__in=rolls):
    old_status = str(leaveslip.status)
    leaveslip.status = 'D'
    leaveslip.comments = 'Automatically denied now due to rolls change from schedule changes. // Previous status is: ' + old_status + '. // Prior comments: ' + str(leaveslip.comments) +'.'
    leaveslip.save()
  rolls.delete()
  rolls = Roll.objects.filter(id__in=roll_ids)
  if not rolls.exists():
    return JsonResponse({"message": "Deletion success"})

  return JsonResponse({"message": "Deletion failure"})

@group_required(['training_assistant', 'attendance_monitors'])
def split_schedules_view(request, pk, week):
  if request.method == 'POST' and request.is_ajax():
    schedule = Schedule.objects.get(id=pk)
    if should_split_schedule(schedule, int(week)):
      curr, first_half, second_half = split_schedule(schedule, int(week))
      if second_half is not None:
        return JsonResponse({'success': second_half.get_absolute_url()})
      else:
        return JsonResponse({'failed': 'failed'})
  return HttpResponse(status=204)


# this class uses AfternoonClassForm with three inputs, trainees_id, event, and week
# uses function in utils called afternoon_class_transfer that moves traines onto the chosen schedule for the event
# returns string to indicate whether the transfer was successful or not
# there may be loopholes not found in certain circumnstancs --- Benji
class AfternoonClassChange(FormView):
  template_name = 'schedules/afternoon_class.html'
  form_class = AfternoonClassForm
  success_url = reverse_lazy('schedules:afternoon-class-change')

  def get_context_data(self, **kwargs):
    ctx = super(AfternoonClassChange, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Afternoon Classes Changes'
    return ctx

  def get_form_kwargs(self):

    afternoon_classes = Event.objects.filter(class_type='AFTN', weekday=3, monitor='AM').order_by('name')
    afternoon_classes = [(ev.id, ev.name) for ev in afternoon_classes if ev.schedules.filter(trainee_select='GP').count() == 0]
    afternoon_classes.insert(0, ('', '---'))

    kwargs = super(AfternoonClassChange, self).get_form_kwargs()
    kwargs['event_choices'] = afternoon_classes
    return kwargs

  def form_valid(self, form):
    data = dict(form.data.iterlists())
    start_week = int(data['week'][0])
    trainees_ids = data['trainees']
    event_id = int(data['event'][0])
    mess = afternoon_class_transfer(trainees_ids, event_id, int(start_week))
    messages.success(self.request, mess)
    return super(AfternoonClassChange, self).form_valid(form)

