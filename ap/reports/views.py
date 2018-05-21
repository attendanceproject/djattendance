import pickle
from collections import OrderedDict
from datetime import datetime

from accounts.models import Trainee
from aputils.utils import timeit, timeit_inline
from attendance.models import Roll
from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from leaveslips.models import GroupSlip, IndividualSlip
from localities.models import Locality
from schedules.models import Event, Schedule
from teams.models import Team

from .forms import ReportGenerateForm


class ReportCreateView(LoginRequiredMixin, GroupRequiredMixin, FormView):
  template_name = 'reports/reports.html'
  group_required = [u'training_assistant']

  # success_url = reverse_lazy('reports:generate-reports')
  success_url = reverse_lazy('reports:report-generated')
  form_class = ReportGenerateForm

  LS_TYPES = {
      'CONF': 'Conference',
      'EMERG': 'Family Emergency',
      'FWSHP': 'Fellowship',
      'FUNRL': 'Funeral',
      'GOSP': 'Gospel',
      'INTVW': 'Grad School/Job Interview',
      'GRAD': 'Graduation',
      'MEAL': 'Meal Out',
      'NIGHT': 'Night Out',
      'OTHER': 'Other',
      'SERV': 'Service',
      'SICK': 'Sickness',
      'SPECL': 'Special',
      'WED': 'Wedding',
      'NOTIF': 'Notification Only',
      'TTRIP': 'Team Trip',
  }


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
    if 'sending-locality' in data['report_by']:
      localities = Locality.objects.all()
      for locality in localities:
        final_data_locality[locality.city.name] = {}
      final_data_locality['N/A'] = {}

    if 'team' in data['report_by']:
      teams = Team.objects.all()
      for team in teams:
        final_data_team[team.name] = {}

    for trainee in filtered_trainees:
      print trainee.full_name
      if trainee.full_name not in rtn_data:
        rtn_data[trainee.full_name] = OrderedDict()
      rtn_data[trainee.full_name]["Term"] = trainee.current_term
      if trainee.locality is not None:
        rtn_data[trainee.full_name]["Sending Locality"] = trainee.locality.city.name
      else:
        rtn_data[trainee.full_name]["Sending Locality"] = 'N/A'
      rtn_data[trainee.full_name]["team"] = trainee.team.name
      rtn_data[trainee.full_name]["ta"] = trainee.TA.full_name
      rtn_data[trainee.full_name]["Gender"] = trainee.gender

      qs_trainee_rolls = qs_rolls.query.filter(trainee=trainee)

      t = timeit_inline("Tardies")
      t.start()

      try:
        tardy_rolls_count = qs_trainee_rolls.exclude(status='A')
        if trainee.self_attendance:
          tardy_rolls_count = tardy_rolls_count.filter(submitted_by=trainee)

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
      if trainee.self_attendance:
        trainee_missed_classes = trainee_missed_classes.filter(submitted_by=trainee)

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

      t = timeit_inline("Unexcude Absences")
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
        
      if trainee.self_attendance:
        unexcused_absences = unexcused_absences.filter(submitted_by=trainee)

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
    for trainee in filtered_trainees:
      if 'sending-locality' in data['report_by']:
        final_data_locality[rtn_data[trainee.full_name]["Sending Locality"]][trainee.full_name] = rtn_data[trainee.full_name]
      if 'team' in data['report_by']:
        final_data_team[rtn_data[trainee.full_name]["team"]][trainee.full_name] = rtn_data[trainee.full_name]

    if 'sending-locality' in data['report_by']:
      final_data_locality = self.clean_empty(final_data_locality)

    if 'team' in data['report_by']:
      final_data_team = self.clean_empty(final_data_team)

    if 'sending-locality' in data['report_by'] and 'team' in data['report_by']:
      context = {
        'locality_data': final_data_locality,
        'team_data': final_data_team,
        'date_data': date_data,
        'averages': averages
      }
    elif 'sending-locality' in data['report_by']:
      context = {
        'locality_data': final_data_locality,
        'date_data': date_data,
        'averages': averages
      }
    elif 'team' in data['report_by']:
      context = {
        'team_data': final_data_team,
        'date_data': date_data,
        'averages': averages
      }
    t.end()
    return render(request, "reports/generated_report.html", context=context)
