import json
import dateutil.parser

from django.views.generic import TemplateView
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect
from rest_framework import filters
from rest_framework.renderers import JSONRenderer
from datetime import date, datetime, time, timedelta
from collections import OrderedDict
from .models import Roll
from .serializers import RollSerializer, RollFilter, AttendanceSerializer
from schedules.models import Schedule, Event
from schedules.constants import WEEKDAYS
from leaveslips.models import IndividualSlip, GroupSlip
from terms.models import Term
from accounts.models import Trainee, TrainingAssistant
from seating.models import Chart, Seat, Partial
from houses.models import House
from teams.models import Team
from rest_framework_bulk import (
    BulkModelViewSet
)

from accounts.serializers import TrainingAssistantSerializer, TraineeRollSerializer, TraineeForAttendanceSerializer
from schedules.serializers import AttendanceEventWithDateSerializer, EventWithDateSerializer
from leaveslips.serializers import IndividualSlipSerializer, GroupSlipSerializer
from seating.serializers import ChartSerializer, SeatSerializer, PartialSerializer
from terms.serializers import TermSerializer

from braces.views import GroupRequiredMixin

from ap.forms import TraineeSelectForm
from aputils.trainee_utils import trainee_from_user, is_trainee
from aputils.eventutils import EventUtils
from aputils.decorators import group_required
from copy import copy


# if the attendance monitors inputs rolls for a trainee on self attendance
# but the trainee doesn't input his/her own rolls, then the trainee shouldn't see these rolls
# unless AMs pull audit

def react_attendance_context(trainee):
  listJSONRenderer = JSONRenderer()
  trainees = Trainee.objects.all().prefetch_related('groups')
  events = trainee.events
  groupevents = trainee.groupevents
  rolls = Roll.objects.filter(trainee=trainee)
  main_rolls = [r.id for r in rolls if r.is_main_roll]
  rolls = rolls.filter(id__in=main_rolls)
  individualslips = IndividualSlip.objects.filter(trainee=trainee).prefetch_related('rolls')
  groupslips = GroupSlip.objects.filter(Q(trainees__in=[trainee])).distinct().prefetch_related('trainees')
  TAs = TrainingAssistant.objects.filter(groups__name='regular_training_assistant')
  term = [Term.current_term()]
  ctx = {
      'events_bb': listJSONRenderer.render(AttendanceEventWithDateSerializer(events, many=True).data),
      'groupevents_bb': listJSONRenderer.render(AttendanceEventWithDateSerializer(groupevents, many=True).data),
      'trainee_bb': listJSONRenderer.render(TraineeForAttendanceSerializer(trainee).data),
      'trainees_bb': listJSONRenderer.render(TraineeForAttendanceSerializer(trainees, many=True).data),
      'rolls_bb': listJSONRenderer.render(RollSerializer(rolls, many=True).data),
      'individualslips_bb': listJSONRenderer.render(IndividualSlipSerializer(individualslips, many=True).data),
      'groupslips_bb': listJSONRenderer.render(GroupSlipSerializer(groupslips, many=True).data),
      'TAs_bb': listJSONRenderer.render(TrainingAssistantSerializer(TAs, many=True).data),
      'term_bb': listJSONRenderer.render(TermSerializer(term, many=True).data),
      'trainee_select_form': TraineeSelectForm()
  }
  return ctx


class AttendanceView(TemplateView):
  def get_context_data(self, **kwargs):
    ctx = super(AttendanceView, self).get_context_data(**kwargs)
    current_url = resolve(self.request.path_info).url_name
    ctx['current_url'] = current_url
    return ctx


class AttendancePersonal(AttendanceView):
  template_name = 'attendance/attendance_react.html'

  def get_context_data(self, **kwargs):
    ctx = super(AttendancePersonal, self).get_context_data(**kwargs)
    listJSONRenderer = JSONRenderer()
    user = self.request.user
    trainee = trainee_from_user(user)
    if not trainee:
      trainee = Trainee.objects.filter(groups__name='attendance_monitors').first()
      ctx['actual_user'] = listJSONRenderer.render(TraineeForAttendanceSerializer(self.request.user).data)
    ctx.update(react_attendance_context(trainee))
    return ctx


# View for Class/Seat Chart Based Rolls
class RollsView(GroupRequiredMixin, AttendanceView):
  template_name = 'attendance/roll_class.html'
  context_object_name = 'context'
  group_required = [u'attendance_monitors', u'training_assistant']

  # TODO enforce DRY principle, currently used for robustness

  def get(self, request, *args, **kwargs):
    if not is_trainee(self.request.user):
      return redirect('home')

    context = self.get_context_data()
    return super(RollsView, self).render_to_response(context)

  def post(self, request, *args, **kwargs):

    context = self.get_context_data()
    return super(RollsView, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    lJRender = JSONRenderer().render
    ctx = super(RollsView, self).get_context_data(**kwargs)
    user = self.request.user
    trainee = trainee_from_user(user)

    if self.request.method == 'POST':
      selected_week = self.request.POST.get('week')
      event_id = self.request.POST.get('events')
      event = Event.objects.get(id=event_id)
      selected_date = event.date_for_week(int(selected_week))
      event.date = selected_date
      event.start_datetime = datetime.combine(event.date, event.start)
      event.end_datetime = datetime.combine(event.date, event.end)
    else:
      selected_date = date.today()
      selected_week = Event.week_from_date(selected_date)
      # try;
      events = trainee.immediate_upcoming_event(with_seating_chart=True)
      # TODO: - if trainee has no current event load other class that is occuring at the same time
      if len(events) > 0:
        event = events[0]
      else:
        event = None

    selected_week = int(selected_week)

    if event:
      chart = Chart.objects.filter(event=event).first()
      if chart:
        seats = Seat.objects.filter(chart=chart).select_related('trainee')
        partial = Partial.objects.filter(chart=chart).order_by('section_name')
        # Get roll with with for current event and today's date
        roll = Roll.objects.filter(event=event, date=selected_date)
        # TODO - Add group leave slips
        individualslips = IndividualSlip.objects.filter(rolls__in=roll, status='A')
        trainees = Trainee.objects.filter(schedules__events=event)
        schedules = Schedule.get_all_schedules_in_weeks_for_trainees([selected_week, ], trainees)

        w_tb = EventUtils.collapse_priority_event_trainee_table([selected_week, ], schedules, trainees)

        t_set = EventUtils.get_trainees_attending_event_in_week(w_tb, event, selected_week)

        for s in seats:
          if s.trainee in t_set:
            s.attending = True
          else:
            s.attending = False

        start_datetime = datetime.combine(selected_date, event.start)
        end_datetime = datetime.combine(selected_date, event.end)
        group_slip = GroupSlip.objects.filter(end__gte=start_datetime, start__lte=end_datetime, status='A').prefetch_related('trainees')
        print group_slip, start_datetime, end_datetime
        trainee_groupslip = set()
        for gs in group_slip:
          trainee_groupslip = trainee_groupslip | set(gs.trainees.all())

        ctx['event'] = event
        ctx['event_bb'] = lJRender(EventWithDateSerializer(event).data)
        ctx['attendance_bb'] = lJRender(RollSerializer(roll, many=True).data)
        ctx['individualslips_bb'] = lJRender(IndividualSlipSerializer(individualslips, many=True).data)
        ctx['trainee_groupslip_bb'] = lJRender(TraineeRollSerializer(trainee_groupslip, many=True).data)
        ctx['trainees_bb'] = lJRender(TraineeRollSerializer(trainees, many=True).data)
        ctx['chart'] = chart
        ctx['chart_bb'] = lJRender(ChartSerializer(chart, many=False).data)
        ctx['seats'] = seats
        ctx['seats_bb'] = lJRender(SeatSerializer(seats, many=True).data)
        ctx['partial'] = partial
        ctx['partial_bb'] = lJRender(PartialSerializer(partial, many=True).data)

    ctx['weekdays'] = WEEKDAYS
    ctx['date'] = selected_date
    ctx['week'] = selected_week
    ctx['day'] = selected_date.weekday()

    # ctx['leaveslips'] = chain(list(IndividualSlip.objects.filter(trainee=self.request.user.trainee).filter(events__term=Term.current_term())), list(GroupSlip.objects.filter(trainee=self.request.user.trainee).filter(start__gte=Term.current_term().start).filter(end__lte=Term.current_term().end)))

    return ctx


# Audit View
# according to PM, the audit functionality is to allow attendance monitors to easily audit 2nd year trainees who take their own attendancne
# two key things are recorded, mismatch frequency and absent-tardy discrepancy
# mismatch frequency is the record of how many times the trainee records present but the attendance monitor records otherwise, eg: tardy due to uniform or left class or abset
# absent-tardy discrepancy is the record of how many times the attendance monitor marks the trainee absent but the trainee marks a type of tardy
class AuditRollsView(GroupRequiredMixin, TemplateView):

  template_name = 'attendance/roll_audit.html'
  context_object_name = 'context'
  group_required = [u'attendance_monitors', u'training_assistant']

  def get(self, request, *args, **kwargs):
    if not is_trainee(self.request.user):
      return redirect('home')

    context = self.get_context_data()
    return super(AuditRollsView, self).render_to_response(context)

  def post(self, request, *args, **kwargs):
    context = self.get_context_data()
    return super(AuditRollsView, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    ctx = super(AuditRollsView, self).get_context_data(**kwargs)
    ctx['current_url'] = resolve(self.request.path_info).url_name
    ctx['user_gender'] = Trainee.objects.filter(id=self.request.user.id).values('gender')[0]
    ctx['current_period'] = Term.period_from_date(Term.current_term(), date.today())

    if self.request.method == 'POST':
      val = self.request.POST.get('id')[10:]
      if self.request.POST.get('state') == 'true':
        Trainee.objects.filter(pk=val).update(self_attendance=True)
      elif self.request.POST.get('state') == 'false':
        Trainee.objects.filter(pk=val).update(self_attendance=False)

    audit_log = []
    if self.request.method == 'GET':

      # filter for the selected gender
      trainees_secondyear = Trainee.objects.filter(current_term__gt=2)
      gen = self.request.GET.get('gender')
      if gen == "brothers":
        trainees_secondyear = trainees_secondyear.filter(gender='B')
      elif gen == "sisters":
        trainees_secondyear = trainees_secondyear.filter(gender='S')
      elif gen == "":
        trainees_secondyear = trainees_secondyear.none()

      # filter rolls for the selected period
      rolls_all = Roll.objects.none()
      for p in self.request.GET.getlist('period[]'):
        rolls_all = rolls_all | Roll.objects.filter(date__gte=Term.startdate_of_period(Term.current_term(), int(p)), date__lte=Term.enddate_of_period(Term.current_term(), int(p)))

      # audit trainees that are not attendance monitor
      # this treats an attendance monitor as a regular trainee, may need to reconsider for actual cases
      for t in trainees_secondyear.order_by('lastname'):
        mismatch = 0
        AT_discrepancy = 0
        details = []
        rolls = rolls_all.filter(trainee=t)
        roll_trainee = rolls.filter(submitted_by=t)  # rolls taken by trainee
        roll_am = rolls.filter(submitted_by__in=trainees_secondyear.filter(groups__name="attendance_monitors"))  # rolls taken by attendance monitor
        for r in roll_am.order_by('date'):
          self_status = roll_trainee.filter(event=r.event, date=r.date).values('status')
          r_stat_trainee = 'P'
          if self_status:
              r_stat_trainee = self_status[0]['status']

          # PM indicates that mismatch is only when trainee marks P and AM marks otherwise
          if r_stat_trainee == 'P' and r.status != 'P':
            mismatch += 1
            details.append("MF %d/%d %s" % (r.date.month, r.date.day, r.event.code))

          # PM indicates that AT discrepancy is only when AM marks A and trainee marks a type of T
          if r.status == 'A' and r_stat_trainee in set(['T', 'U', 'L']):
            AT_discrepancy += 1
            details.append("AT %d/%d %s" % (r.date.month, r.date.day, r.event.code))

        audit_log.append([t.gender, t.self_attendance, t, mismatch, AT_discrepancy, ", ".join(details)])

    if self.request.GET.get('ask'):
      ctx['audit_log'] = audit_log

    ctx['title'] = 'Audit Rolls'
    return ctx


class TableRollsView(GroupRequiredMixin, AttendanceView):
  template_name = 'attendance/roll_table.html'
  context_object_name = 'context'
  group_required = [u'attendance_monitors', u'training_assistant']

  def get(self, request, *args, **kwargs):
    context = self.get_context_data()
    return super(TableRollsView, self).render_to_response(context)

  def post(self, request, *args, **kwargs):
    context = self.get_context_data()
    return super(TableRollsView, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    ctx = super(TableRollsView, self).get_context_data(**kwargs)

    trainees = kwargs['trainees']

    current_term = Term.current_term()
    ctx['house'] = self.request.user.house
    ctx['team'] = self.request.user.team
    if self.request.method == 'POST':
      selected_week = int(self.request.POST.get('week'))
      selected_date = current_term.startdate_of_week(selected_week)

      house = self.request.POST.get('house')
      if house:
        trainees = Trainee.objects.filter(house__name=house)
        ctx['house'] = house
      team = self.request.POST.get('team')
      if team:
        trainees = Trainee.objects.filter(team__name=team)
        ctx['team'] = team

    else:
      selected_date = date.today()
    current_week = current_term.term_week_of_date(selected_date)
    start_date = current_term.startdate_of_week(current_week)
    end_date = current_term.enddate_of_week(current_week)
    start_datetime = datetime.combine(start_date, time())
    end_datetime = datetime.combine(end_date, time())

    event_type = kwargs['type']
    if event_type == "H":
      ctx['houses'] = House.objects.filter(used=True).order_by("name").exclude(name__in=['TC', 'MCC', 'COMMUTER'])
    elif event_type == "T":
      ctx['teams'] = Team.objects.all().order_by("type", "name").values("pk", "name")

    event_list, trainee_evt_list = Schedule.get_roll_table_by_type_in_weeks(trainees, event_type, [current_week, ])
    group_slip = GroupSlip.objects.filter(end__gte=start_datetime, start__lte=end_datetime, status='A').order_by('start', 'end').prefetch_related('trainees')
    group_slip_tbl = OrderedDict()
    event_groupslip_tbl = OrderedDict()
    for gs in group_slip:
      gs_start = group_slip_tbl.setdefault(gs.start, OrderedDict())
      gs_end = gs_start.setdefault(gs.end, set())
      gs_end.add(gs)
    for evt in event_list:
      for gs_start in group_slip_tbl:
        if gs_start > evt.start_datetime:
          break
        else:
          for gs_end in group_slip_tbl[gs_start]:
            if gs_end < evt.end_datetime:
              break
            else:
              for g in group_slip_tbl[gs_start][gs_end]:
                eg_set = event_groupslip_tbl.setdefault(evt, set(g.trainees.all()))
                eg_set |= set(g.trainees.all())

    rolls = Roll.objects.filter(event__in=event_list, date__gte=start_date, date__lte=end_date).select_related('trainee', 'event')
    # TODO - Add group leave slips
    rolls_withslips = rolls.filter(leaveslips__isnull=False, leaveslips__status="A")

    # trainees: [events,]
    # event.roll = roll
    # {trainee: OrderedDict({
    #   (event, date): roll
    # }),}
    roll_dict = OrderedDict()

    # Populate roll_dict from roll object for look up for building roll table
    for roll in rolls:
      r = roll_dict.setdefault(roll.trainee, OrderedDict())
      if roll in rolls_withslips:
        roll.leaveslip = True
      r[(roll.event, roll.date)] = roll

    # print trainee_evt_list, roll_dict, trainees, event_type

    # Add roll to each event from roll table
    for trainee in roll_dict:
      # Only update if trainee predefined
      if trainee in trainee_evt_list:
        evt_list = trainee_evt_list[trainee]
        if len(evt_list) <= 0:
          # delete empty column if all blocked out
          del trainee_evt_list[trainee]
        else:
          for i in range(0, len(evt_list)):
            ev = copy(evt_list[i])
            d = ev.start_datetime.date()
            # Add roll if roll exists for trainee
            if trainee in roll_dict and (ev, d) in roll_dict[trainee]:
              # if trainee is on self attendance (trainee.self_attendance=True),
              # only display rolls not submitted by the trainee and modify rolls that are not submitted by the trainee.
              if trainee.self_attendance and (trainee == roll_dict[trainee][(ev, d)].submitted_by):
                continue
              else:
                ev.roll = roll_dict[trainee][(ev, d)]
            evt_list[i] = ev

    ctx['event_type'] = event_type
    ctx['start_date'] = start_date
    ctx['term_start_date'] = current_term.start.strftime('%Y%m%d')
    ctx['current_week'] = current_week
    ctx['trainees'] = trainees
    ctx['trainees_event_list'] = trainee_evt_list
    ctx['event_list'] = event_list
    ctx['event_groupslip_tbl'] = event_groupslip_tbl
    ctx['week'] = Term.current_term().term_week_of_date(date.today())
    return ctx


# Class Rolls Table
class ClassRollsView(TableRollsView):
  def get_context_data(self, **kwargs):
    kwargs['trainees'] = Trainee.objects.all()
    kwargs['type'] = 'C'
    ctx = super(ClassRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "Class Rolls"
    return ctx


# Meal Rolls
class MealRollsView(TableRollsView):
  def get_context_data(self, **kwargs):
    kwargs['trainees'] = Trainee.objects.all()
    kwargs['type'] = 'M'
    ctx = super(MealRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "Meal Rolls"
    return ctx


# Study Rolls
class StudyRollsView(TableRollsView):
  def get_context_data(self, **kwargs):
    kwargs['trainees'] = Trainee.objects.all()
    kwargs['type'] = 'S'
    ctx = super(StudyRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "Study Rolls"
    return ctx


# House Rolls
class HouseRollsView(TableRollsView):
  group_required = [u'HC', u'attendance_monitors', u'training_assistant']

  def get_context_data(self, **kwargs):
    trainee = trainee_from_user(self.request.user)
    if trainee:
      house = trainee.house
    else:
      house = House.objects.first()
    if self.request.user.has_group(['attendance_monitors']):
      kwargs['trainees'] = Trainee.objects.filter(house=house)
    else:
      kwargs['trainees'] = Trainee.objects.filter(house=house).filter(Q(self_attendance=False, current_term__gt=2) | Q(current_term__lte=2))
    kwargs['type'] = 'H'
    ctx = super(HouseRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "House Rolls"
    return ctx


class RFIDRollsView(TableRollsView):
  def get_context_data(self, **kwargs):
    kwargs['trainees'] = Trainee.objects.all()
    kwargs['type'] = 'RF'
    ctx = super(RFIDRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "RFID Rolls"
    return ctx


# Team Rolls
class TeamRollsView(TableRollsView):
  group_required = [u'team_monitors', u'attendance_monitors', u'training_assistant']

  def get_context_data(self, **kwargs):
    trainee = trainee_from_user(self.request.user)
    if trainee:
      team = trainee.team
    else:
      team = Team.objects.first()
    if self.request.user.has_group(['attendance_monitors']):
      kwargs['trainees'] = Trainee.objects.filter(team=team)
    else:
      kwargs['trainees'] = Trainee.objects.filter(team=team).filter(Q(self_attendance=False, current_term__gt=2) | Q(current_term__lte=2))
    kwargs['type'] = 'T'
    ctx = super(TeamRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "Team Rolls"
    return ctx


# YPC Rolls
class YPCRollsView(TableRollsView):
  group_required = [u'ypc_monitors', u'attendance_monitors', u'training_assistant']

  def get_context_data(self, **kwargs):
    trainee = trainee_from_user(self.request.user)
    kwargs['trainees'] = Trainee.objects.filter(team__type__in=['YP', 'CHILD']).filter(Q(self_attendance=False, current_term__gt=2) | Q(current_term__lte=2))
    kwargs['type'] = 'Y'
    ctx = super(YPCRollsView, self).get_context_data(**kwargs)
    ctx['title'] = "YPC Rolls"
    return ctx


class RollViewSet(BulkModelViewSet):
  queryset = Roll.objects.all()
  serializer_class = RollSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = RollFilter

  def get_queryset(self):
    user = self.request.user
    trainee = trainee_from_user(user)
    roll = trainee.current_rolls
    return roll

  def allow_bulk_destroy(self, qs, filtered):
    return filtered
    # failsafe- to only delete if qs is filtered.
    # return not all(x in filtered for x in qs)


class AttendanceViewSet(BulkModelViewSet):
  queryset = Trainee.objects.all()
  serializer_class = AttendanceSerializer
  filter_backends = (filters.DjangoFilterBackend,)

  def get_queryset(self):
    trainee = Trainee.objects.get(pk=self.request.GET.get('trainee', self.request.user))
    return [trainee]

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllRollViewSet(BulkModelViewSet):
  queryset = Roll.objects.all()
  serializer_class = RollSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = RollFilter

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllAttendanceViewSet(BulkModelViewSet):
  queryset = Trainee.objects.all()
  serializer_class = AttendanceSerializer
  filter_backends = (filters.DjangoFilterBackend,)

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


def finalize(request):
  if not request.method == 'POST':
    return HttpResponseBadRequest('Request must use POST method')
  data = json.loads(request.body)
  trainee = get_object_or_404(Trainee, id=data['trainee']['id'])
  submitter = get_object_or_404(Trainee, id=data['submitter']['id'])
  period_start = dateutil.parser.parse(data['weekStart'])
  period_end = dateutil.parser.parse(data['weekEnd'])
  rolls_this_week = trainee.rolls.filter(date__gte=period_start, date__lte=period_end)
  if rolls_this_week.exists():
    rolls_this_week.update(finalized=True)
  else:
    # we need some way to differentiate between those who have finalized and who haven't if they have no rolls
    # add a dummy finalized present roll for this case
    event = trainee.events[0] if trainee.events else (Event.objects.first() if Event.objects else None)
    if not event:
      return HttpResponseServerError('No events found')
    roll = Roll(date=period_start, trainee=trainee, status='P', event=event, finalized=True, submitted_by=submitter)
    roll.save()
  listJSONRenderer = JSONRenderer()
  rolls = listJSONRenderer.render(RollSerializer(Roll.objects.filter(trainee=trainee), many=True).data)

  return JsonResponse({'rolls': json.loads(rolls)})


@group_required(('attendance_monitors',))
def rfid_signin(request, trainee_id):
  data = {}
  trainee = Trainee.objects.filter(rfid_tag=trainee_id).first()
  if trainee is None:
    data = {
        'ok': False,
        'errMsg': 'RFID tag is invalid'
    }
  else:
    events = filter(lambda x: x.monitor == 'RF', trainee.immediate_upcoming_event())
    if not events:
      data = {
          'ok': False,
          'errMsg': 'No event found for %s' % trainee
      }
    else:
      now = datetime.now()
      event = events[0]
      if (now - event.start_datetime) > timedelta(minutes=15):
        status = 'A'
      elif (now - event.start_datetime) > timedelta(minutes=0):
        status = 'T'
      else:
        status = 'P'
      roll = Roll(event=event, trainee=trainee, status=status, submitted_by=trainee, date=now)
      roll.save()
      data = {
          'ok': True,
          'trainee': trainee.full_name,
          'roll': status,
          'event': event.name,
          'now': now.isoformat()
      }

  return HttpResponse(json.dumps(data), content_type='application/json')


@group_required(('attendance_monitors',))
def rfid_finalize(request, event_id, event_date):
  event = get_object_or_404(Event, pk=event_id)
  date = datetime.strptime(event_date, "%Y-%m-%d").date()
  if not event.monitor == 'RF':
    return HttpResponseBadRequest('No event found')

  # mark trainees without a roll for this event absent
  rolls = event.roll_set.filter(date=date)
  trainees_with_roll = set([roll.trainee for roll in rolls])
  schedules = event.schedules.all()
  for schedule in schedules:
    trainees = schedule.trainees.all()
    for trainee in trainees:
      if trainee not in trainees_with_roll:
        roll = Roll(event=event, trainee=trainee, status='A', submitted_by=trainee, date=date, finalized=True)
        roll.save()

  # mark existing rolls as finalized
  rolls.update(finalized=True)

  # don't keep a record of present to save space
  rolls.filter(status='P', leaveslips__isnull=True).delete()

  return HttpResponse('Roll finalized')


@group_required(('attendance_monitors',))
def rfid_tardy(request, event_id, event_date):
  event = get_object_or_404(Event, pk=event_id)
  date = datetime.strptime(event_date, "%Y-%m-%d").date()
  if not event.monitor == 'RF':
    return HttpResponseBadRequest('No event found')
  event.roll_set.filter(date=date, status='T', leaveslips__isnull=True).delete()
  return HttpResponse('Roll tardies removed')
