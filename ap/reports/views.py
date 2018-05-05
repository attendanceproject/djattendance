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
from schedules.models import Event

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

  def post(self, request, *args, **kwargs):
    data = dict(request.POST.iterlists())
    # print str(data)
    rtn_data = dict()  # {TRAINEE_NAME: {% Unex. Abs.: 10, % Sickness: 5, ...}, TRAINEE_NAME: ...}
    date_data = dict()
    date_from = datetime.strptime(data['date_from'][0], '%m/%d/%Y')
    date_to = datetime.strptime(data['date_to'][0], '%m/%d/%Y')
    date_data['date_from'] = str(date_from)
    date_data['date_to'] = str(date_to)
    delta = date_to - date_from

    #filtered_trainees = Trainee.objects.filter(current_term__in=[1, 2, 3, 4])
    filtered_trainees = Trainee.objects.filter(current_term__in=[4])

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

    localities = Locality.objects.all()
    teams = Team.objects.all()

    for trainee in filtered_trainees:
      if trainee.full_name not in rtn_data:
        rtn_data[trainee.full_name] = OrderedDict()
      rtn_data[trainee.full_name]["Term"] = trainee.current_term
      if trainee.locality is not None:
        rtn_data[trainee.full_name]["Sending Locality"] = trainee.locality.city.name
      else:
        print "trainee " + trainee.full_name + " has no locality..."
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
        rtn_data[trainee.full_name]["% Tardy"] = str(round(qs_trainee_rolls.query.filter(status__in=['T','U','L']).count() / float(trainee_all_rolls.count()) * 100, 2)) + "%"
        average_tardy_percentage += float(rtn_data[trainee.full_name]["% Tardy"][:-1])
      except ZeroDivisionError:
        message = "Division by 0 error."
        rtn_data[trainee.full_name]["% Tardy"] = "N/A"
        #return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})

      class_events = Event.objects.filter(start=datetime.strptime('10:15', '%H:%M'), type='C').exclude(name="Session II") | Event.objects.filter(start=datetime.strptime('08:25', '%H:%M')).exclude(name="Session I").exclude(name="Study Roll").exclude(name="Study").exclude(name="End Study") | Event.objects.filter(name="PSRP")
      trainee_class_events = qs_trainee_rolls.query.filter(event__in=class_events)
      trainee_missed_classes = trainee_class_events.filter(status='A')

      print("trainee is: " + trainee.full_name)
      #print ("missed classes: " + str(trainee_missed_classes.count()))
      #print ("class events: " + str(trainee_class_events.count()))

      try:
        rtn_data[trainee.full_name]["% Classes Missed"] = str(round(trainee_missed_classes.count() / float(trainee_class_events.count()) * 100, 2)) + "%"
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
        rtn_data[trainee.full_name]["% Sickness"] = str(round(indv_slip_qs.query.filter(type="SICK").count() / float(trainee_all_rolls.count()) * 100, 2)) + "%"
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
      print "all absences: " + str(qs_trainee_rolls.query.filter(status='A').count())
      print "absent rolls in group slips: " + str(absent_rolls_covered_in_group_slips.count())
      print "absent rolls in indv slips: " + str(absent_rolls_covered_by_indv_leaveslips.count())
      try:
        rtn_data[trainee.full_name]["% Unex. Abs."] = str(round(unexcused_absences / float(trainee_all_rolls.count()) * 100, 2)) + "%"
        average_unexcused_absences_percentage += float(rtn_data[trainee.full_name]["% Unex. Abs."][:-1])
      except ZeroDivisionError:
        message = "Division by 0 error."
        rtn_data[trainee.full_name]["% Unex. Abs."] = "N/A"
        #return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})

    average_unexcused_absences_percentage = round(average_unexcused_absences_percentage / num_trainees, 2)
    average_sickness_percentage = round(average_sickness_percentage / num_trainees, 2)
    average_tardy_percentage = round(average_tardy_percentage / num_trainees, 2)
    average_classes_missed_percentage = round(average_classes_missed_percentage / num_trainees, 2)
    for trainee in filtered_trainees:
      rtn_data[trainee.full_name]["Average % Tardy"] = str(average_tardy_percentage) + "%"
      rtn_data[trainee.full_name]["Average % Classes Missed"] = str(average_classes_missed_percentage) + "%"
      rtn_data[trainee.full_name]["Average % Sickness"] = str(average_sickness_percentage) + "%"
      rtn_data[trainee.full_name]["Average % Unex. Abs."] = str(average_unexcused_absences_percentage) + "%"
    
    print str(rtn_data)

    context = {
      'data': rtn_data,
      'date_data': date_data
    }

    return render(request, "reports/generated_report.html", context=context)
