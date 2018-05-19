from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from .forms import ReportGenerateForm
from datetime import datetime
from accounts.models import Trainee
from lifestudies.models import Discipline
from leaveslips.models import IndividualSlip, GroupSlip
from attendance.models import Roll
from localities.models import Locality
from teams.models import Team
from schedules.models import Event, Schedule

from collections import OrderedDict
import pickle


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

  def post(self, request, *args, **kwargs):
    data = dict(request.POST.iterlists())
    #print str(data)
    final_data_locality = dict() #{LOCALITY_NAME: {TRAINEE_NAME: {% Unex. Abs.: 10, % Sickness: 5, ...}, TRAINEE_NAME: ...}, LOCALITY_NAME: ...}
    final_data_team = dict()
    rtn_data = dict()  # {TRAINEE_NAME: {% Unex. Abs.: 10, % Sickness: 5, ...}, TRAINEE_NAME: ...}
    date_data = dict()
    date_from = datetime.strptime(data['date_from'][0], '%m/%d/%Y')
    date_to = datetime.strptime(data['date_to'][0], '%m/%d/%Y')
    date_data['date_from'] = str(date_from)
    date_data['date_to'] = str(date_to)
    delta = date_to - date_from

    number_of_days_covered = abs((date_to - date_from).days)

    total_rolls_in_a_week = Schedule.objects.filter(name='Generic Group Events')[0].events.all()

    #print str("number of days covered: " + str(number_of_days_covered))
    #print str("total roll in a week: " + str(total_rolls_in_a_week.count()))

    total_rolls_in_report_for_one_trainee = int(float(number_of_days_covered) / 7 * total_rolls_in_a_week.count())

    #Assuming PSRP and Monday Night Revival are classes too, then we should have 12 classes in a week
    num_classes_in_report_for_one_trainee = int(float(number_of_days_covered) / 7 * 12)  
 
    #print str("total rolls for a trainee: " + str(total_rolls_in_report_for_one_trainee))

    #filtered_trainees = Trainee.objects.filter(current_term__in=[1])
    filtered_trainees = Trainee.objects.filter(current_term__in=[3])

    #averages of fields
    average_unexcused_absences_percentage = float(0)
    average_sickness_percentage = float(0)
    average_tardy_percentage = float(0)
    average_classes_missed_percentage = float(0)

    #number of trainees needed for calculating averages
    num_trainees = filtered_trainees.count()

    filtered_rolls = Roll.objects.filter(trainee__in=filtered_trainees, date__range=[date_from, date_to])
    pickled_rolls = pickle.dumps(filtered_rolls)

    # get all group slips in report's time range with the specified trainees that have been approved.
    filtered_group_slips = GroupSlip.objects.filter(start__gte=date_from, end__lte=date_to, trainees__in=filtered_trainees, status__in=['A', 'S'])
    pickled_group_slips = pickle.dumps(filtered_group_slips)

    # qs_rolls is the queryset of all pertinent rolls related to the filtered trainees in the date range
    pickled_query = pickle.loads(pickled_rolls)
    qs_rolls = Roll.objects.all()
    qs_rolls.query = pickled_query

    #qs_group_slips is the queryset of all group slips related to the filtered trainees in the date range that are approved
    pickled_group_slips_query = pickle.loads(pickled_group_slips)
    qs_group_slips = GroupSlip.objects.all()
    qs_group_slips.query = pickled_group_slips_query

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
      if trainee.full_name not in rtn_data:
        rtn_data[trainee.full_name] = OrderedDict()
      rtn_data[trainee.full_name]["Term"] = trainee.current_term
      if trainee.locality is not None:
        rtn_data[trainee.full_name]["Sending Locality"] = trainee.locality.city.name
      else:
        #print "trainee " + trainee.full_name + " has no locality..."
        rtn_data[trainee.full_name]["Sending Locality"] = 'N/A'
      rtn_data[trainee.full_name]["team"] = trainee.team.name
      rtn_data[trainee.full_name]["ta"] = trainee.TA.full_name
      rtn_data[trainee.full_name]["Gender"] = trainee.gender

      trainee_all_rolls = qs_rolls.query.filter(trainee=trainee)
      pickled_trainee_rolls = pickle.dumps(trainee_all_rolls)
      pickled_trainee_query = pickle.loads(pickled_trainee_rolls)
      qs_trainee_rolls = Roll.objects.all()
      qs_trainee_rolls.query = pickled_trainee_query

      try:
        if trainee.self_attendance:
          tardy_rolls_count = 0
          for roll in qs_trainee_rolls.query.filter(status__in=['T','U','L']):
            if roll.submitted_by == trainee:
              tardy_rolls_count += 1
          rtn_data[trainee.full_name]["% Tardy"] = str(round(tardy_rolls_count / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
        else:
          rtn_data[trainee.full_name]["% Tardy"] = str(round(qs_trainee_rolls.query.filter(status__in=['T','U','L']).count() / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
        average_tardy_percentage += float(rtn_data[trainee.full_name]["% Tardy"][:-1])
      except ZeroDivisionError:
        message = "Division by 0 error."
        rtn_data[trainee.full_name]["% Tardy"] = "N/A"
        #return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})

      class_events = Event.objects.filter(start=datetime.strptime('10:15', '%H:%M'), type='C').exclude(name="Session II") | Event.objects.filter(start=datetime.strptime('08:25', '%H:%M')).exclude(name="Session I").exclude(name="Study Roll").exclude(name="Study").exclude(name="End Study") | Event.objects.filter(name="PSRP")
      trainee_class_events = qs_trainee_rolls.query.filter(event__in=class_events)
      trainee_missed_classes = trainee_class_events.filter(status='A')

      #print("trainee is: " + trainee.full_name)
      #print ("missed classes: " + str(trainee_missed_classes.count()))
      #print ("class events: " + str(trainee_class_events.count()))

      try:
        if trainee.self_attendance:
          absent_class_rolls_count = 0
          for roll in trainee_missed_classes:
            if roll.submitted_by == trainee:
              absent_class_rolls_count += 1
          rtn_data[trainee.full_name]["% Classes Missed"] = str(round(absent_class_rolls_count / float(num_classes_in_report_for_one_trainee) * 100, 2)) + "%"
        else:
          rtn_data[trainee.full_name]["% Classes Missed"] = str(round(trainee_missed_classes.count() / float(num_classes_in_report_for_one_trainee) * 100, 2)) + "%"
          average_classes_missed_percentage += float(rtn_data[trainee.full_name]["% Classes Missed"][:-1])
      except ZeroDivisionError:
        message = "Division by 0 error."
        rtn_data[trainee.full_name]["% Classes Missed"] = "N/A"
        #return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})

      #dealing with '% sickness' now, need information on individual leave slips
      primary_indv_slip_filter = IndividualSlip.objects.filter(trainee=trainee, rolls__in=qs_trainee_rolls.query, rolls__status__contains='A', status__in=['A', 'S'])
      pickled_indv_slip_filter = pickle.dumps(primary_indv_slip_filter)
      pickled_indv_slip_filter_qs = pickle.loads(pickled_indv_slip_filter)
      indv_slip_qs = IndividualSlip.objects.all()
      indv_slip_qs.query = pickled_indv_slip_filter_qs

      try:
        rtn_data[trainee.full_name]["% Sickness"] = str(round(indv_slip_qs.query.filter(type="SICK").count() / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
        average_sickness_percentage += float(rtn_data[trainee.full_name]["% Sickness"][:-1])
      except ZeroDivisionError:
        message = "Division by 0 error."
        rtn_data[trainee.full_name]["% Sickness"] = "N/A"
        #return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})

      #get total unexcused absences. This will be: ROLLS_ABSENT - (ROLLS_EXCUSED_BY_INDIVIDUAL_LEAVE_SLIPS + ROLLS_EXCUSED_BY_GROUP_LEAVE_SLIPS) / ALL_ROLLS
      absent_rolls_covered_in_group_slips = Roll.objects.none()
      group_slips_for_trainee = qs_group_slips.query.filter(trainees=trainee)
      for group_slip in group_slips_for_trainee:
        rolls_in_slip = qs_trainee_rolls.query.filter(event__start__gte=group_slip.start, event__end__lte=group_slip.end, status='A')
        absent_rolls_covered_in_group_slips = absent_rolls_covered_in_group_slips | rolls_in_slip

      indv_leaveslips_with_absences = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
      absent_rolls_covered_by_indv_leaveslips = Roll.objects.none()
      for indv_leaveslip in indv_leaveslips_with_absences:
        absent_rolls_covered_by_indv_leaveslips = absent_rolls_covered_by_indv_leaveslips | indv_leaveslip.rolls.filter(status="A")

      #get total unexcused absences
      unexcused_absences = qs_trainee_rolls.query.filter(status='A').count() - absent_rolls_covered_in_group_slips.count() - absent_rolls_covered_by_indv_leaveslips.count()
      #print "all absences: " + str(qs_trainee_rolls.query.filter(status='A').count())
      #print "absent rolls in group slips: " + str(absent_rolls_covered_in_group_slips.count())
      #print "absent rolls in indv slips: " + str(absent_rolls_covered_by_indv_leaveslips.count())

      #excluding because they are covered by leaveslips:
      absent_rolls_to_exclude_from_self_attendance_calculation = []
      
      for roll in absent_rolls_covered_in_group_slips:
        absent_rolls_to_exclude_from_self_attendance_calculation.append(roll.id)

      for roll in absent_rolls_covered_by_indv_leaveslips:
        absent_rolls_to_exclude_from_self_attendance_calculation.append(roll.id)

      try:
        if trainee.self_attendance:
          for roll in qs_trainee_rolls.query.filter(status='A').exclude(id__in=absent_rolls_to_exclude_from_self_attendance_calculation):
            if roll.submitted_by != trainee:
              unexcused_absences -= 1
          rtn_data[trainee.full_name]["% Unex. Abs."] = str(round(unexcused_absences / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
        else:
          rtn_data[trainee.full_name]["% Unex. Abs."] = str(round(unexcused_absences / float(total_rolls_in_report_for_one_trainee) * 100, 2)) + "%"
          average_unexcused_absences_percentage += float(rtn_data[trainee.full_name]["% Unex. Abs."][:-1])
      except ZeroDivisionError:
        message = "Division by 0 error."
        rtn_data[trainee.full_name]["% Unex. Abs."] = "N/A"
        #return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})
      #print str(rtn_data[trainee.full_name])

    average_unexcused_absences_percentage = round(average_unexcused_absences_percentage / num_trainees, 2)
    average_sickness_percentage = round(average_sickness_percentage / num_trainees, 2)
    average_tardy_percentage = round(average_tardy_percentage / num_trainees, 2)
    average_classes_missed_percentage = round(average_classes_missed_percentage / num_trainees, 2)

    averages = {}
    for trainee in filtered_trainees:
      averages["Average % Tardy"] = str(average_tardy_percentage) + "%"
      averages["Average % Classes Missed"] = str(average_classes_missed_percentage) + "%"
      averages["Average % Sickness"] = str(average_sickness_percentage) + "%"
      averages["Average % Unex. Abs."] = str(average_unexcused_absences_percentage) + "%"
      if 'sending-locality' in data['report_by']:
        final_data_locality[rtn_data[trainee.full_name]["Sending Locality"]][trainee.full_name] = rtn_data[trainee.full_name]
      if 'team' in data['report_by']:
        final_data_team[rtn_data[trainee.full_name]["team"]][trainee.full_name] = rtn_data[trainee.full_name]
    


    if 'sending-locality' in data['report_by']:
      final_data_locality = self.clean_empty(final_data_locality)
    #  for each_locality in final_data_locality:
    #    if final_data_locality[each_locality] == {}:
    #      del final_data_locality[each_locality]

    if 'team' in data['report_by']:
      final_data_team = self.clean_empty(final_data_team)
    #  for each_team in final_data_team:
    #    if final_data_team[each_team] == {}:
    #      del final_data_team[each_team]
    
    #print str(final_data_locality)
    #print str(final_data_team)

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

    return render(request, "reports/generated_report.html", context=context)
