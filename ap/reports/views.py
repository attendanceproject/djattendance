import copy
import json
import os
import pickle

from collections import OrderedDict, Counter
from datetime import datetime
from StringIO import StringIO
from zipfile import ZipFile

from aputils.utils import render_to_pdf, timeit, timeit_inline
from aputils.eventutils import EventUtils
from braces.views import GroupRequiredMixin, LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from accounts.models import Trainee
from terms.models import Term
from attendance.models import Roll
from leaveslips.models import GroupSlip, IndividualSlip
from localities.models import Locality
from schedules.models import Event, Schedule
from lifestudies.models import Discipline
from teams.models import Team

from .forms import ReportGenerateForm


class GenerateAttendanceReport(TemplateView):
  template_name = 'reports/generate_attendance_report.html'


class AttendanceReport(TemplateView):
  template_name = 'reports/attendance_report.html'

  def post(self, request, *args, **kwargs):

    context = self.get_context_data()
    context['trainees'] = list(Trainee.objects.filter(is_active=True).values_list('pk', flat=True))
    context['date_from'] = request.POST.get("date_from")
    context['date_to'] = request.POST.get("date_to")

    return super(AttendanceReport, self).render_to_response(context)

def attendance_report_trainee(request):
  data = request.GET

  res = dict()

  t_id = int(data['t_id'])
  trainee = Trainee.objects.get(pk=t_id)
  res['trainee_id'] = t_id
  res['firstname'] = trainee.firstname
  res['lastname'] = trainee.lastname
  res['sending_locality'] = trainee.locality.id
  res['team'] = trainee.team.code
  res['ta'] = trainee.TA.full_name
  res['gender'] = trainee.gender

  rolls = Roll.objects.filter(trainee=trainee).exclude(status='P').exclude(event__monitor=None)
  if trainee.self_attendance:
    rolls = rolls.filter(submitted_by=trainee)

  date_from = datetime.strptime(data['date_from'], '%m/%d/%Y').date()
  date_to = datetime.strptime(data['date_to'], '%m/%d/%Y').date()
  ct = Term.objects.get(current=True)
  if date_from < ct.start:
    date_from = ct.start
  if date_to > ct.end:
    date_to = ct.end

  week_from = ct.reverse_date(date_from)[0]
  week_to = ct.reverse_date(date_to)[0]
  weeks = range(week_from, week_to)
  w_tb = EventUtils.collapse_priority_event_trainee_table(weeks, trainee.active_schedules, [trainee])
  count = Counter()
  for kv in w_tb:
    for ev, t in w_tb[kv].items():
      if ev in count:
        count[ev] += 1
      else:
        count[ev] = 1

  total_rolls_for_trainee = sum(count[ev] for ev in count if ev.monitor is not None)
  tardy_rolls_count = rolls.exclude(status='A').count()
  res['% Tardy'] = str(round(tardy_rolls_count / float(total_rolls_for_trainee) * 100, 2)) + "%"

  return JsonResponse(res)


def zip_attendance_report(request):
  return None



class ReportCreateView(LoginRequiredMixin, GroupRequiredMixin, FormView):
  template_name = 'reports/reports.html'
  group_required = [u'training_assistant']

  # success_url = reverse_lazy('reports:generate-reports')
  success_url = reverse_lazy('reports:report-generated')
  form_class = ReportGenerateForm


class GeneratedReport(LoginRequiredMixin, GroupRequiredMixin, ListView):
  template_name = 'reports/generated_report.html'
  group_required = [u'training_assistant']

  def clean_empty(self, d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (self.clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, self.clean_empty(v)) for k, v in d.items()) if v}

  @timeit
  def post(self, request, *args, **kwargs):
    data = dict(request.POST.iterlists())
    final_data_locality = dict()  # {LOCALITY_NAME: {TRAINEE_NAME: {% Unex. Abs.: 10, % Sickness: 5, ...}, TRAINEE_NAME: ...}, LOCALITY_NAME: ...}
    final_data_team = dict()
    rtn_data = dict()  # {TRAINEE_NAME: {% Unex. Abs.: 10, % Sickness: 5, ...}, TRAINEE_NAME: ...}
    date_data = dict()
    date_from = datetime.strptime(data['date_from'][0], '%m/%d/%Y')
    date_to = datetime.strptime(data['date_to'][0], '%m/%d/%Y')
    date_data['date_from'] = str(date_from)
    date_data['date_to'] = str(date_to)

    number_of_days_covered = abs((date_to - date_from).days)

    total_rolls_in_a_week = Schedule.objects.filter(name='Generic Group Events')[0].events.all()

    total_rolls_in_report_for_one_trainee = int(float(number_of_days_covered) / 7 * total_rolls_in_a_week.count())

    # Assuming PSRP and Monday Night Revival are classes too, then we should have 12 classes in a week
    num_classes_in_report_for_one_trainee = int(float(number_of_days_covered) / 7 * 12)

    # filtered_trainees = Trainee.objects.filter(current_term__in=[1])
    filtered_trainees = Trainee.objects.filter(is_active=True)

    # averages of fields
    average_unexcused_absences_percentage = float(0)
    average_sickness_percentage = float(0)
    average_tardy_percentage = float(0)
    average_classes_missed_percentage = float(0)

    # number of trainees needed for calculating averages
    num_trainees = filtered_trainees.count()
    t = timeit_inline("Initial Pickling")
    t.start()

    # We only want to pickle non-present rolls
    filtered_rolls = Roll.objects.filter(trainee__in=filtered_trainees, date__range=[date_from, date_to]).exclude(status='P')
    pickled_rolls = pickle.dumps(filtered_rolls)

    # qs_rolls is the queryset of all pertinent rolls related to the filtered trainees in the date range
    pickled_query = pickle.loads(pickled_rolls)
    qs_rolls = Roll.objects.all()
    qs_rolls.query = pickled_query

    # get all group slips in report's time range with the specified trainees that have been approved, this is needed because groupslip start and end fields are datetime fields and the input is only a date field
    start_datetime = datetime.combine(date_from, datetime.min.time())
    end_datetime = datetime.combine(date_to, datetime.max.time())

    qs_group_slips = GroupSlip.objects.filter(status__in=['A', 'S'], start__gte=start_datetime, end__lte=end_datetime)
    t.end()
    # filtered_trainees = filtered_trainees.filter(firstname="David")  # Test line

    localities = Locality.objects.all()
    for locality in localities:
      if str(locality.city) == "Richmond, VA":
        final_data_locality["Richmond VA"] = {}
      else:
        final_data_locality[locality.city.name] = {}
    final_data_locality['N/A'] = {}

    teams = Team.objects.all()
    for team in teams:
      final_data_team[team.code] = {}

    for trainee in filtered_trainees:
      #print trainee.full_name
      if trainee.full_name not in rtn_data:
        rtn_data[trainee.full_name] = OrderedDict()
      rtn_data[trainee.full_name]["Term"] = trainee.current_term
      if trainee.locality is not None:
        if str(trainee.locality.city) == "Richmond, VA":
          rtn_data[trainee.full_name]["Sending Locality"] = "Richmond VA"
        else:
          rtn_data[trainee.full_name]["Sending Locality"] = trainee.locality.city.name
      else:
        rtn_data[trainee.full_name]["Sending Locality"] = 'N/A'
      rtn_data[trainee.full_name]["Team"] = trainee.team.code
      rtn_data[trainee.full_name]["ta"] = trainee.TA.full_name
      rtn_data[trainee.full_name]["Gender"] = trainee.gender

      qs_trainee_rolls = qs_rolls.query.filter(trainee=trainee)
      if trainee.self_attendance:
        qs_trainee_rolls = qs_trainee_rolls.filter(submitted_by=trainee)

      t = timeit_inline("Tardies")
      t.start()

      try:
        tardy_rolls_count = qs_trainee_rolls.exclude(status='A')
        rtn_data[trainee.full_name]["% Tardy"] = str(round(tardy_rolls_count.count() / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"

        average_tardy_percentage += float(rtn_data[trainee.full_name]["% Tardy"][:-1])
      except ZeroDivisionError:
        rtn_data[trainee.full_name]["% Tardy"] = "N/A"
      t.end()

      t = timeit_inline("Missed Classes")
      t.start()
      # this should come down to about twelve, including all the main, 1st year and 2nd year classes and afternoon class
      class_events = Event.objects.filter(monitor='AM', type='C').exclude(class_type=None)
      trainee_missed_classes = qs_trainee_rolls.filter(event__in=class_events, status='A')

      try:
        rtn_data[trainee.full_name]["% Classes Missed"] = str(round(trainee_missed_classes.count() / float(num_classes_in_report_for_one_trainee) * 100, 2)) + "%"
        average_classes_missed_percentage += float(rtn_data[trainee.full_name]["% Classes Missed"][:-1])
      except ZeroDivisionError:
        rtn_data[trainee.full_name]["% Classes Missed"] = "N/A"
      t.end()

      # dealing with '% sickness' now, need information on individual leave slips
      primary_indv_slip_filter = IndividualSlip.objects.filter(trainee=trainee, rolls__in=qs_trainee_rolls, status__in=['A', 'S'])
      t = timeit_inline("Leave slipped Rolls")
      t.start()
      try:
        rtn_data[trainee.full_name]["% Sickness"] = str(round(primary_indv_slip_filter.filter(type="SICK").count() / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
        average_sickness_percentage += float(rtn_data[trainee.full_name]["% Sickness"][:-1])
      except ZeroDivisionError:
        rtn_data[trainee.full_name]["% Sickness"] = "N/A"

      t.end()

      t = timeit_inline("Unexcused Absences")
      t.start()

      # first get all absent rolls for this trainee. This will be: (ROLLS_ABSENT - ROLLS_EXCUSED_BY_INDIVIDUAL_LEAVE_SLIPS - ROLLS_EXCUSED_BY_GROUP_LEAVE_SLIPS) / ALL_ROLLS
      unexcused_absences = qs_trainee_rolls.filter(status='A')

      # remove absences with an approved or sister approved individual leaveslip
      unexcused_absences = unexcused_absences.exclude(leaveslips__status__in=['A', 'S'])

      # start to remove absences excused by groupleaveslips
      group_slips_for_trainee = qs_group_slips.filter(trainees=trainee).values('start', 'end')
      for group_slip in group_slips_for_trainee:

        # majority of groupslips are on the same date
        if group_slip['start'].date() == group_slip['end'].date():
          unexcused_absences = unexcused_absences.exclude(event__start__gte=group_slip['start'].time(), event__end__lte=group_slip['end'].time())

        # to cover multi day groupslips for conference or other events
        else:
          potentials_rolls = unexcused_absences.filter(date__range=[group_slip['start'].date(), group_slip['end'].date()])
          if potentials_rolls.count() == 0:
            continue
          for r in potentials_rolls:
            r_start = datetime.combine(r.date, r.event.start)
            r_end = datetime.combine(r.date, r.event.end)
            if group_slip['start'] <= r_start and group_slip['end'] >= r_end:
              unexcused_absences = unexcused_absences.exclude(id=r.pk)

      try:
        rtn_data[trainee.full_name]["% Unex. Abs."] = str(round(unexcused_absences.count() / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
        average_unexcused_absences_percentage += float(rtn_data[trainee.full_name]["% Unex. Abs."][:-1])
      except ZeroDivisionError:
        rtn_data[trainee.full_name]["% Unex. Abs."] = "N/A"
      t.end()

    average_unexcused_absences_percentage = round(average_unexcused_absences_percentage / num_trainees, 2)
    average_sickness_percentage = round(average_sickness_percentage / num_trainees, 2)
    average_tardy_percentage = round(average_tardy_percentage / num_trainees, 2)
    average_classes_missed_percentage = round(average_classes_missed_percentage / num_trainees, 2)
    averages = {}
    averages["Average % Tardy"] = str(average_tardy_percentage) + "%"
    averages["Average % Classes Missed"] = str(average_classes_missed_percentage) + "%"
    averages["Average % Sickness"] = str(average_sickness_percentage) + "%"
    averages["Average % Unex. Abs."] = str(average_unexcused_absences_percentage) + "%"
    t = timeit_inline("Building Context")

    t.start()
    loc_data = []
    team_data = []
    for trainee in filtered_trainees:

      final_data_locality[rtn_data[trainee.full_name]["Sending Locality"]][trainee.full_name] = rtn_data[trainee.full_name]
      if rtn_data[trainee.full_name]["Sending Locality"] not in loc_data:
        loc_data.append(rtn_data[trainee.full_name]["Sending Locality"])

      final_data_team[rtn_data[trainee.full_name]["Team"]][trainee.full_name] = rtn_data[trainee.full_name]
      if rtn_data[trainee.full_name]["Team"] not in team_data:
        team_data.append(rtn_data[trainee.full_name]["Team"])

    final_data_locality = self.clean_empty(final_data_locality)
    final_data_team = self.clean_empty(final_data_team)

    context = {
      'loc_data': final_data_locality,
      'team_data': final_data_team,
      'date_data': date_data,
      'averages': averages
    }

    ctx = {'trainee_data': json.dumps(self.clean_empty(rtn_data))}
    ctx['loc_data'] = json.dumps(loc_data)
    ctx['team_data'] = json.dumps(team_data)
    ctx['date_data'] = {'date_from': date_from, 'date_to': date_to}
    ctx['averages'] = json.dumps(averages)
    t.end()

    in_memory = StringIO()
    zfile = ZipFile(in_memory, "a")

    for ld in list(context['loc_data']):
      ld_ctx = copy.deepcopy(context)
      ld_ctx.pop('team_data')
      for none_ld in list(ld_ctx['loc_data']):
        if none_ld != ld:
          print none_ld
          ld_ctx['loc_data'].pop(none_ld)

      pdf_file = render_to_pdf("reports/template_report.html", ld_ctx)
      path = ld + '.pdf'

      with open(path, 'w+') as f:
        f.write(pdf_file.content)
      zfile.write(path)
      os.remove(path)

    for ld in list(context['team_data']):
      ld_ctx = copy.deepcopy(context)
      ld_ctx.pop('loc_data')
      for none_ld in list(ld_ctx['team_data']):
        if none_ld != ld:
          print none_ld
          ld_ctx['team_data'].pop(none_ld)

      pdf_file = render_to_pdf("reports/template_report.html", ld_ctx)
      path = ld + '.pdf'

      with open(path, 'w+') as f:
        f.write(pdf_file.content)
      zfile.write(path)
      os.remove(path)

    # fix for Linux zip files read in Windows
    for zf in zfile.filelist:
      zf.create_system = 0

    zfile.close()
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=Attendance_Report.zip'
    in_memory.seek(0)
    response.write(in_memory.read())

    return response

    # # prints report instead of serving zip file
    # response = render(request, "reports/generated_report.html", ctx)


class ReportFilterView(LoginRequiredMixin, GroupRequiredMixin, FormView):
  template_name = 'reports/reports_filtered.html'
  group_required = [u'training_assistant']

  # success_url = reverse_lazy('reports:generate-reports')
  success_url = reverse_lazy('reports:report-filtered-generated')
  form_class = ReportGenerateForm

class GeneratedFilteredReport(LoginRequiredMixin, GroupRequiredMixin, ListView):
  template_name = 'reports/generated_filtered_report.html'
  group_required = [u'training_assistant']

  def clean_empty(self, d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (self.clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, self.clean_empty(v)) for k, v in d.items()) if v}

  @timeit
  def post(self, request, *args, **kwargs):
    data = dict(request.POST.iterlists())
    # print str(data)
    rtn_data = dict()  # {TRAINEE_NAME: {Absences - Total: 10, Tardies - Total: 5, ...}, TRAINEE_NAME: ...}
    final_data_locality = dict()  # {LOCALITY_NAME: {TRAINEE_NAME: {% Unex. Abs.: 10, % Sickness: 5, ...}, TRAINEE_NAME: ...}, LOCALITY_NAME: ...}
    final_data_team = dict()
    date_data = dict()
    date_from = datetime.strptime(data['date_from'][0], '%m/%d/%Y')
    date_to = datetime.strptime(data['date_to'][0], '%m/%d/%Y')
    date_data['date_from'] = str(date_from)
    date_data['date_to'] = str(date_to)
    delta = date_to - date_from

    filtered_trainees = Trainee.objects.all()

    if 'gender' in data.keys():
      gender = data['gender']

    if "Male" not in gender:
      filtered_trainees = filtered_trainees.filter(gender="S")
    elif "Female" not in gender:
      filtered_trainees = filtered_trainees.filter(gender="B")
    elif "Male" not in gender and "Female" not in gender:
      filtered_trainees = Trainee.objects.none()
      return rtn_data

    terms_filter = []
    # Return trainees only for the terms requested by report
    if 'term' in data.keys():
      terms_filter = [int(s) for s in data['term'] if s.isdigit()]

    if 'general_report' in data.keys():
      t = timeit_inline("Initial Pickling")
      t.start()
      filtered_trainees = filtered_trainees.filter(current_term__in=terms_filter)
      filtered_rolls = Roll.objects.filter(trainee__in=filtered_trainees, date__range=[date_from, date_to]).exclude(status='P')
      pickled_rolls = pickle.dumps(filtered_rolls)

      # get all group slips in report's time range with the specified trainees that have been approved.
      filtered_group_slips = GroupSlip.objects.filter(start__gte=date_from, end__lte=date_to, trainees__in=filtered_trainees, status__in=['A', 'S'])
      pickled_group_slips = pickle.dumps(filtered_group_slips)

      items_for_query = data['general_report']
      print str(items_for_query)

      # qs_rolls is the queryset of all pertinent rolls related to the filtered trainees in the date range that are tardies or absences
      pickled_query = pickle.loads(pickled_rolls)
      qs_rolls = Roll.objects.all()
      qs_rolls.query = pickled_query

      pickled_group_slips_query = pickle.loads(pickled_group_slips)
      pgsq = GroupSlip.objects.all()
      pgsq.query = pickled_group_slips_query
      t.end()

      localities = Locality.objects.all()
      for locality in localities:
        if str(locality.city) == "Richmond, VA":
          final_data_locality["Richmond VA"] = {}
        else:
          final_data_locality[locality.city.name] = {}
      final_data_locality['N/A'] = {}

      teams = Team.objects.all()
      for team in teams:
        final_data_team[team.code] = {}

      for trainee in filtered_trainees:
        rtn_data[trainee.full_name] = {}
        
        rtn_data[trainee.full_name] = OrderedDict()
        rtn_data[trainee.full_name]["Term"] = trainee.current_term
        if trainee.locality is not None:
          if str(trainee.locality.city) == "Richmond, VA":
            rtn_data[trainee.full_name]["Sending Locality"] = "Richmond VA"
          else:
            rtn_data[trainee.full_name]["Sending Locality"] = trainee.locality.city.name
        else:
          rtn_data[trainee.full_name]["Sending Locality"] = 'N/A'
        rtn_data[trainee.full_name]["Team"] = trainee.team.code
        rtn_data[trainee.full_name]["ta"] = trainee.TA.full_name
        rtn_data[trainee.full_name]["Gender"] = trainee.gender
        for item in items_for_query:
          rtn_data[trainee.full_name][item] = 0

        # get number of LS summaries
        if "Number of LS" in items_for_query:
          rtn_data[trainee.full_name]['Number of LS'] = Discipline.objects.filter(trainee=trainee).count()

        group_slips_for_trainee = pgsq.query.filter(trainees=trainee).values('start', 'end', 'type')

        trainee_rolls = qs_rolls.query.filter(trainee=trainee)
        pickled_trainee_rolls = pickle.dumps(trainee_rolls)
        pickled_trainee_query = pickle.loads(pickled_trainee_rolls)
        qs_trainee_rolls = Roll.objects.all()
        qs_trainee_rolls.query = pickled_trainee_query

        if "Classes Missed" in items_for_query:
          rtn_data[trainee.full_name]['Classes Missed'] = qs_trainee_rolls.query.filter(status='A', event__type='C').count()

        absent_rolls_covered_in_group_slips = Roll.objects.none()
        tardy_rolls_covered_in_group_slips = Roll.objects.none()

        # DEALING WITH GROUP SLIPS FOR SPECIAL EXCUSED ABSENCES (next 45 lines of code)
        # get rolls for special group slips; this is needed later for excluding these rolls from individual slips that cover these same rolls
        rolls_covered_in_conference_group_slips = Roll.objects.none()
        rolls_covered_in_fellowship_group_slips = Roll.objects.none()
        rolls_covered_in_gospel_group_slips = Roll.objects.none()
        rolls_covered_in_night_out_group_slips = Roll.objects.none()
        rolls_covered_in_other_group_slips = Roll.objects.none()
        rolls_covered_in_service_group_slips = Roll.objects.none()
        rolls_covered_in_team_trip_group_slips = Roll.objects.none()

        # necessary to do this due to slip.events function not working properly....
        # Calculate for excused absences that can be covered by a group slip - conference, fellowship, gospel, night out, other, service, team trip
        #t = timeit_inline("Group Slip Absences for Trainee")
        #t.start()
        for slip in group_slips_for_trainee:
          #t = timeit_inline("Get rolls in slip for group slips")
          #t.start()
          rolls_in_slip = qs_trainee_rolls.query.filter(event__start__gte=slip['start'], event__end__lte=slip['end'], status='A')
          #t.end()
          #t = timeit_inline("Get absent rolls in slip for group slips")
          t.start()
          #absent_rolls_covered_in_group_slips = absent_rolls_covered_in_group_slips | rolls_in_slip
          #t.end()
          #t = timeit_inline("Get tardy rolls in slip for group slips")
          #t.start()
          tardy_rolls_covered_in_group_slips = tardy_rolls_covered_in_group_slips | qs_trainee_rolls.query.filter(event__start__gte=slip['start'], event__end__lte=slip['end'], status__in=['T', 'U', 'L'])
          #t.end()
          #t = timeit_inline("Add special type absent rolls to list")
          #t.start()
          if 'Absences - Excused - Conference' in items_for_query and slip['type'] == 'CONF':
            rolls_covered_in_conference_group_slips = rolls_covered_in_conference_group_slips | rolls_in_slip
          if 'Absences - Excused - Fellowship' in items_for_query and slip['type'] == 'FWSHP':
            rolls_covered_in_fellowship_group_slips = rolls_covered_in_fellowship_group_slips | rolls_in_slip
          if 'Absences - Excused - Gospel' in items_for_query and slip['type'] == 'GOSP':
            rolls_covered_in_gospel_group_slips = rolls_covered_in_gospel_group_slips | rolls_in_slip
          if 'Absences - Excused - Night Out' in items_for_query and slip['type'] == 'NIGHT':
            rolls_covered_in_night_out_group_slips = rolls_covered_in_night_out_group_slips | rolls_in_slip
          if 'Absences - Excused - Other' in items_for_query and slip['type'] == 'OTHER':
            rolls_covered_in_other_group_slips = rolls_covered_in_other_group_slips | rolls_in_slip
          if 'Absences - Excused - Service' in items_for_query and slip['type'] == 'SERV':
            rolls_covered_in_service_group_slips = rolls_covered_in_service_group_slips | rolls_in_slip
          if 'Absences - Excused - Team Trip' in items_for_query and slip['type'] == 'TTRIP':
            rolls_covered_in_team_trip_group_slips = rolls_covered_in_team_trip_group_slips | rolls_in_slip
          #t.end()

        #t = timeit_inline("Get count of special absent rolls")
        #t.start()
        # add count of absent rolls covered by group slips to special excused absences count; deal with individual slips after this block of code
        if 'Absences - Excused - Conference' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Conference'] = rolls_covered_in_conference_group_slips.count()
        if 'Absences - Excused - Fellowship' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Fellowship'] = rolls_covered_in_fellowship_group_slips.count()
        if 'Absences - Excused - Gospel' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Gospel'] = rolls_covered_in_gospel_group_slips.count()
        if 'Absences - Excused - Night Out' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Night Out'] = rolls_covered_in_night_out_group_slips.count()
        if 'Absences - Excused - Other' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Other'] = rolls_covered_in_other_group_slips.count()
        if 'Absences - Excused - Service' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Service'] = rolls_covered_in_service_group_slips.count()
        if 'Absences - Excused - Team Trip' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Excused - Team Trip'] = rolls_covered_in_team_trip_group_slips.count()
        #t.end()
        #t.end()


        t = timeit_inline("Individual Slip Absence for Trainee")
        t.start()
        # DEALING WITH INDIVIDUAL SLIPS FOR SPECIAL EXCUSED ABSENCES (next 91 lines of code)
        primary_indv_slip_filter = IndividualSlip.objects.filter(rolls__in=qs_trainee_rolls.query, rolls__status__contains='A', status__in=['A', 'S'])
        pickled_indv_slip_filter = pickle.dumps(primary_indv_slip_filter)

        # qs_rolls is the queryset of all pertinent rolls related to the filtered trainees in the date range that are tardies or absences
        pickled_indv_slip_filter_qs = pickle.loads(pickled_indv_slip_filter)
        indv_slip_qs = IndividualSlip.objects.all()
        indv_slip_qs.query = pickled_indv_slip_filter_qs

        if 'Absences - Total' in items_for_query:
          rtn_data[trainee.full_name]['Absences - Total'] = qs_trainee_rolls.query.filter(status='A').count()
        if 'Absences - Excused' in items_for_query:
          # get all absent rolls excused by individual leave slips (exclude rolls covered in group slips, in case a trainee has both a group and individual leave slip for the same roll)
          indv_slips = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused'] += indv_slips.values_list('rolls').count()

          # get all absent rolls excused by groups slips
          rtn_data[trainee.full_name]['Absences - Excused'] += absent_rolls_covered_in_group_slips.count()

        if 'Absences - Unexcused' in items_for_query:
          if 'Absences - Total' in rtn_data[trainee.full_name] and 'Absences - Excused' in rtn_data[trainee.full_name]:
            # save time by not needing to query again
            rtn_data[trainee.full_name]['Absences - Unexcused'] = rtn_data[trainee.full_name]['Absences - Total'] - rtn_data[trainee.full_name]['Absences - Excused']
          else:
            # get all rolls where trainee is absent and minus those excused by group and individual leave slips
            rtn_data[trainee.full_name]['Absences - Unexcused'] = qs_trainee_rolls.query.filter(status='A').count() - \
                absent_rolls_covered_in_group_slips.count()

            # exclude rolls covered in group leave slips
            indv_slips = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
            rtn_data[trainee.full_name]['Absences - Unexcused'] -= indv_slips.values_list('rolls').count()

        if 'Absences - Unexcused and Sickness' in items_for_query:
          # get rolls for absences that are excused with type sick
          indv_slips_sickness = indv_slip_qs.query.filter(type="SICK")
          rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] += indv_slips_sickness.values_list('rolls').count()
          if 'Absences - Unexcused' in rtn_data[trainee.full_name]:
            # get rolls for unexcused absences
            rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] += rtn_data[trainee.full_name]['Absences - Unexcused']
          else:
            # get all rolls where trainee is absent and minus those excused by group and individual leave slips
            rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] = qs_trainee_rolls.query.filter(status='A').count() - \
                absent_rolls_covered_in_group_slips.count()

            indv_slips = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
            rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] -= indv_slips.values_list('rolls').count()

        if 'Absences - Excused - Conference' in items_for_query:
          conference_slips = indv_slip_qs.query.filter(type="CONF").exclude(rolls__in=rolls_covered_in_conference_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused - Conference'] += conference_slips.values_list('rolls').count()
        if 'Absences - Excused - Family Emergency' in items_for_query:
          fam_emerg_slips = indv_slip_qs.query.filter(type="EMERG")
          rtn_data[trainee.full_name]['Absences - Excused - Family Emergency'] += fam_emerg_slips.values_list('rolls').count()
        if 'Absences - Excused - Fellowship' in items_for_query:
          fellowship_slips = indv_slip_qs.query.filter(type="FWSHP").exclude(rolls__in=rolls_covered_in_fellowship_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused - Fellowship'] += fellowship_slips.values_list('rolls').count()
        if 'Absences - Excused - Funeral' in items_for_query:
          funeral_slips = indv_slip_qs.query.filter(type="FUNRL")
          rtn_data[trainee.full_name]['Absences - Excused - Funeral'] += funeral_slips.values_list('rolls').count()
        if 'Absences - Excused - Gospel' in items_for_query:
          gospel_slips = indv_slip_qs.query.filter(type="GOSP").exclude(rolls__in=rolls_covered_in_gospel_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused - Gospel'] += gospel_slips.values_list('rolls').count()
        if 'Absences - Excused - Grad School/Job Interview' in items_for_query:
          intv_slips = indv_slip_qs.query.filter(type="INTVW")
          rtn_data[trainee.full_name]['Absences - Excused - Grad School/Job Interview'] += intv_slips.values_list('rolls').count()
        if 'Absences - Excused - Graduation' in items_for_query:
          grad_slips = indv_slip_qs.query.filter(type="GRAD")
          rtn_data[trainee.full_name]['Absences - Excused - Graduation'] += grad_slips.values_list('rolls').count()
        if 'Absences - Excused - Meal Out' in items_for_query:
          meal_out_slips = indv_slip_qs.query.filter(type="MEAL")
          rtn_data[trainee.full_name]['Absences - Excused - Meal Out'] += meal_out_slips.values_list('rolls').count()
        if 'Absences - Excused - Night Out' in items_for_query:
          night_out_slips = indv_slip_qs.query.filter(type="NIGHT")
          rtn_data[trainee.full_name]['Absences - Excused - Night Out'] += night_out_slips.values_list('rolls').count()
        if 'Absences - Excused - Other' in items_for_query:
          other_slips = indv_slip_qs.query.filter(type="OTHER").exclude(rolls__in=rolls_covered_in_other_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused - Other'] += other_slips.values_list('rolls').count()
        if 'Absences - Excused - Service' in items_for_query:
          service_slips = indv_slip_qs.query.filter(type="SERV").exclude(rolls__in=rolls_covered_in_service_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused - Service'] += service_slips.values_list('rolls').count()
        if 'Absences - Excused - Sickness' in items_for_query:
          sick_slips = indv_slip_qs.query.filter(type="SICK")
          rtn_data[trainee.full_name]['Absences - Excused - Sickness'] += sick_slips.values_list('rolls').count()
        if 'Absences - Excused - Special' in items_for_query:
          special_slips = indv_slip_qs.query.filter(type="SPECL")
          rtn_data[trainee.full_name]['Absences - Excused - Special'] += special_slips.values_list('rolls').count()
        if 'Absences - Excused - Wedding' in items_for_query:
          wedding_slips = indv_slip_qs.query.filter(type="WED")
          rtn_data[trainee.full_name]['Absences - Excused - Wedding'] += wedding_slips.values_list('rolls').count()
        if 'Absences - Excused - Team Trip' in items_for_query:
          team_trip_slips = indv_slip_qs.query.filter(type="TTRIP").exclude(rolls__in=rolls_covered_in_team_trip_group_slips)
          rtn_data[trainee.full_name]['Absences - Excused - Team Trip'] += team_trip_slips.values_list('rolls').count()

        t.end()

        t = timeit_inline("Tardy for Trainee")
        t.start()
        # TARDIES FILTER
        if 'Tardies - Total' in items_for_query:
          late_tardies = qs_trainee_rolls.query.filter(status='T').count()
          uniform_tardies = qs_trainee_rolls.query.filter(status='U').count()
          left_class_tardies = qs_trainee_rolls.query.filter(status='L').count()
          rtn_data[trainee.full_name]['Tardies - Total'] = late_tardies + uniform_tardies + left_class_tardies
        if 'Tardies - Uniform' in items_for_query:
          if 'uniform_tardies' in locals():
            rtn_data[trainee.full_name]['Tardies - Uniform'] = uniform_tardies
          else:
            rtn_data[trainee.full_name]['Tardies - Uniform'] = qs_trainee_rolls.query.filter(status='U').count()
        if 'Tardies - Left Class' in items_for_query:
          if 'left_class_tardies' in locals():
            rtn_data[trainee.full_name]['Tardies - Left Class'] = left_class_tardies
          else:
            rtn_data[trainee.full_name]['Tardies - Left Class'] = qs_trainee_rolls.query.filter(status='L').count()
        if 'Tardies - Late' in items_for_query:
          if 'late_tardies' in locals():
            rtn_data[trainee.full_name]['Tardies - Late'] = late_tardies
          else:
            rtn_data[trainee.full_name]['Tardies - Late'] = qs_trainee_rolls.query.filter(status='T').count()
        if 'Tardies - Excused' in items_for_query or 'Tardies - Unexcused' in items_for_query:
          indv_slips = IndividualSlip.objects.filter(rolls__in=qs_trainee_rolls.query, rolls__status__in=['T', 'U', 'L'], status__in=['A', 'S']).exclude(rolls__in=tardy_rolls_covered_in_group_slips)
          if 'Tardies - Excused' in items_for_query:
            # individual slips
            rtn_data[trainee.full_name]['Tardies - Excused'] += indv_slips.values_list('rolls').count()
            # group slips
            rtn_data[trainee.full_name]['Tardies - Excused'] += tardy_rolls_covered_in_group_slips.count()
          if 'Tardies - Unexcused' in items_for_query:
            if 'Tardies - Total' in rtn_data[trainee.full_name]:
              rtn_data[trainee.full_name]['Tardies - Unexcused'] += rtn_data[trainee.full_name]['Tardies - Total']
              # individual slips
              rtn_data[trainee.full_name]['Tardies - Unexcused'] -= indv_slips.values_list('rolls').count()
              # group slips
              rtn_data[trainee.full_name]['Tardies - Unexcused'] -= tardy_rolls_covered_in_group_slips.count()
            else:
              late_tardies = qs_trainee_rolls.query.filter(status='T').count()
              uniform_tardies = qs_trainee_rolls.query.filter(status='U').count()
              left_class_tardies = qs_trainee_rolls.query.filter(status='L').count()
              rtn_data[trainee.full_name]['Tardies - Unexcused'] += late_tardies + uniform_tardies + left_class_tardies
              # individual slips
              rtn_data[trainee.full_name]['Tardies - Unexcused'] -= indv_slips.values_list('rolls').count()
              # group slips
              rtn_data[trainee.full_name]['Tardies - Unexcused'] -= tardy_rolls_covered_in_group_slips.count()
        t.end()

    for trainee in filtered_trainees:
      #print str(trainee.full_name)
      #print str(rtn_data[trainee.full_name])
      final_data_locality[rtn_data[trainee.full_name]["Sending Locality"]][trainee.full_name] = rtn_data[trainee.full_name]
      final_data_team[rtn_data[trainee.full_name]["Team"]][trainee.full_name] = rtn_data[trainee.full_name]


    final_data_locality = self.clean_empty(final_data_locality)
    final_data_team = self.clean_empty(final_data_team)
    

    loc_data = []
    team_data = []
    for trainee in filtered_trainees:

      final_data_locality[rtn_data[trainee.full_name]["Sending Locality"]][trainee.full_name] = rtn_data[trainee.full_name]
      if rtn_data[trainee.full_name]["Sending Locality"] not in loc_data:
        loc_data.append(rtn_data[trainee.full_name]["Sending Locality"])

      final_data_team[rtn_data[trainee.full_name]["Team"]][trainee.full_name] = rtn_data[trainee.full_name]
      if rtn_data[trainee.full_name]["Team"] not in team_data:
        team_data.append(rtn_data[trainee.full_name]["Team"])

    #final_data_locality = self.clean_empty(final_data_locality)
    #final_data_team = self.clean_empty(final_data_team)

    #print str(rtn_data)
    #print str(final_data_team)
    #print str(final_data_locality)
    
    context = {
      'loc_data': final_data_locality,
      'team_data': final_data_team,
      'date_data': date_data
      #'averages': averages
    }

    ctx = {'trainee_data': json.dumps(self.clean_empty(rtn_data))}
    ctx['loc_data'] = json.dumps(loc_data)
    ctx['team_data'] = json.dumps(team_data)
    ctx['date_data'] = {'date_from': date_from, 'date_to': date_to}
    #ctx['averages'] = json.dumps(averages)
    t.end()

    in_memory = StringIO()
    zfile = ZipFile(in_memory, "a")

    for ld in list(context['loc_data']):
      ld_ctx = copy.deepcopy(context)
      ld_ctx.pop('team_data')
      for none_ld in list(ld_ctx['loc_data']):
        if none_ld != ld:
          #print none_ld
          ld_ctx['loc_data'].pop(none_ld)

      print str(ld_ctx)
      #pdf_file = render_to_pdf("reports/template_report.html", ld_ctx)
      #locality_trainees = ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]]

      #for lt in locality_trainees:
      #  ld_ctx_0 = dict(ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]].items()[0:len(ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]])/4])
      #  ld_ctx_1 = dict(ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]].items()[len(ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]])/4:len(ld_ctx['loc_data'])/4 * 2])
      #  ld_ctx_2 = dict(ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]].items()[len(ld_ctx['loc_data'])/4 * 2:len(ld_ctx['loc_data'])/4 * 3])
      #  ld_ctx_3 = dict(ld_ctx['loc_data'][ld_ctx['loc_data'].keys()[0]].items()[len(ld_ctx['loc_data'])/4 * 3:len(ld_ctx['loc_data'])/4 * 4])

      #print "************************************************************************************************"
      #print str(ld_ctx_0)
      #print str(ld_ctx_1)
      #print str(ld_ctx_2)
      #print str(ld_ctx_3)
      #print "************************************************************************************************"

      #pdf_file0 = render_to_pdf("reports/template_report.html", ld_ctx_0)
      #pdf_file1 = render_to_pdf("reports/template_report.html", ld_ctx_1)
      #pdf_file2 = render_to_pdf("reports/template_report.html", ld_ctx_2)
      #pdf_file3 = render_to_pdf("reports/template_report.html", ld_ctx_3)
      pdf_file = render_to_pdf("reports/template_report.html", ld_ctx)
      path = ld + '.pdf'

      with open(path, 'w+') as f:
        f.write(pdf_file.content)
        #f.write(pdf_file0.content)
        #f.write(pdf_file1.content)
        #f.write(pdf_file2.content)
        #f.write(pdf_file3.content)
      zfile.write(path)
      os.remove(path)

    for ld in list(context['team_data']):
      ld_ctx = copy.deepcopy(context)
      ld_ctx.pop('loc_data')
      for none_ld in list(ld_ctx['team_data']):
        if none_ld != ld:
          #print none_ld
          ld_ctx['team_data'].pop(none_ld)

      print str(ld_ctx)

      #ld_ctx_0 = dict(ld_ctx['loc_data'].items()[0:len(ld_ctx['loc_data'])/4])
      #ld_ctx_1 = dict(ld_ctx['loc_data'].items()[len(ld_ctx['loc_data'])/4:len(ld_ctx['loc_data'])/4 * 2])
      #ld_ctx_2 = dict(ld_ctx['loc_data'].items()[len(ld_ctx['loc_data'])/4 * 2:len(ld_ctx['loc_data'])/4 * 3])
      #ld_ctx_3 = dict(ld_ctx['loc_data'].items()[len(ld_ctx['loc_data'])/4 * 3:len(ld_ctx['loc_data'])/4 * 4])

      #print "************************************************************************************************"
      #print str(ld_ctx_0)
      #print str(ld_ctx_1)
      #print str(ld_ctx_2)
      #print str(ld_ctx_3)
      #print "************************************************************************************************"

      #pdf_file0 = render_to_pdf("reports/template_report.html", ld_ctx_0)
      #pdf_file1 = render_to_pdf("reports/template_report.html", ld_ctx_1)
      #pdf_file2 = render_to_pdf("reports/template_report.html", ld_ctx_2)
      #pdf_file3 = render_to_pdf("reports/template_report.html", ld_ctx_3)
      pdf_file = render_to_pdf("reports/template_report.html", ld_ctx)
      path = ld + '.pdf'

      with open(path, 'w+') as f:
        f.write(pdf_file.content)
        #f.write(pdf_file0.content)
        #f.write(pdf_file1.content)
        #f.write(pdf_file2.content)
        #f.write(pdf_file3.content)
      zfile.write(path)
      os.remove(path)

    # fix for Linux zip files read in Windows
    for zf in zfile.filelist:
      zf.create_system = 0
    zfile.close()
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=Attendance_Report.zip'
    in_memory.seek(0)
    response.write(in_memory.read())
    return response

    #print str(final_data_team)
    #print str(final_data_locality)
    """
    context = {
      'data': rtn_data,
      'locality_data': final_data_locality,
      'team_data': final_data_team,
      'date_data': date_data
    }

    return render(request, "reports/generated_filtered_report.html", context=context)
    """

