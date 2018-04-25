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
    rtn_data = dict()  # {TRAINEE_NAME: {Absences - Total: 10, Tardies - Total: 5, ...}, TRAINEE_NAME: ...}
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
      filtered_trainees = filtered_trainees.filter(current_term__in=terms_filter)
      filtered_rolls = Roll.objects.filter(trainee__in=filtered_trainees, date__range=[date_from, date_to]).exclude(status='P')
      pickled_rolls = pickle.dumps(filtered_rolls)

      # get all group slips in report's time range with the specified trainees that have been approved.
      filtered_group_slips = GroupSlip.objects.filter(start__gte=date_from, end__lte=date_to, trainees__in=filtered_trainees, status__in=['A', 'S'])
      pickled_group_slips = pickle.dumps(filtered_group_slips)

      items_for_query = data['general_report']

      # qs_rolls is the queryset of all pertinent rolls related to the filtered trainees in the date range that are tardies or absences
      pickled_query = pickle.loads(pickled_rolls)
      qs_rolls = Roll.objects.all()
      qs_rolls.query = pickled_query

      pickled_group_slips_query = pickle.loads(pickled_group_slips)
      pgsq = GroupSlip.objects.all()
      pgsq.query = pickled_group_slips_query

      for trainee in filtered_trainees:
        rtn_data[trainee.full_name] = {}
        for item in items_for_query:
          rtn_data[trainee.full_name][item] = 0

        # get number of LS summaries
        if "Number of LS" in items_for_query:
          rtn_data[trainee.full_name]['Number of LS'] = Discipline.objects.filter(trainee=trainee).count()

        group_slips_for_trainee = pgsq.query.filter(trainees=trainee)

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
        for slip in group_slips_for_trainee:
          rolls_in_slip = qs_trainee_rolls.query.filter(event__start__gte=slip.start, event__end__lte=slip.end, status='A')
          absent_rolls_covered_in_group_slips = absent_rolls_covered_in_group_slips | rolls_in_slip
          tardy_rolls_covered_in_group_slips = tardy_rolls_covered_in_group_slips | qs_trainee_rolls.query.filter(event__start__gte=slip.start, event__end__lte=slip.end, status__in=['T', 'U', 'L'])
          if 'Absences - Excused - Conference' in items_for_query and slip.type == 'CONF':
            rolls_covered_in_conference_group_slips = rolls_covered_in_conference_group_slips | rolls_in_slip
          if 'Absences - Excused - Fellowship' in items_for_query and slip.type == 'FWSHP':
            rolls_covered_in_fellowship_group_slips = rolls_covered_in_fellowship_group_slips | rolls_in_slip
          if 'Absences - Excused - Gospel' in items_for_query and slip.type == 'GOSP':
            rolls_covered_in_gospel_group_slips = rolls_covered_in_gospel_group_slips | rolls_in_slip
          if 'Absences - Excused - Night Out' in items_for_query and slip.type == 'NIGHT':
            rolls_covered_in_night_out_group_slips = rolls_covered_in_night_out_group_slips | rolls_in_slip
          if 'Absences - Excused - Other' in items_for_query and slip.type == 'OTHER':
            rolls_covered_in_other_group_slips = rolls_covered_in_other_group_slips | rolls_in_slip
          if 'Absences - Excused - Service' in items_for_query and slip.type == 'SERV':
            rolls_covered_in_service_group_slips = rolls_covered_in_service_group_slips | rolls_in_slip
          if 'Absences - Excused - Team Trip' in items_for_query and slip.type == 'TTRIP':
            rolls_covered_in_team_trip_group_slips = rolls_covered_in_team_trip_group_slips | rolls_in_slip

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

    if 'general_item' in data.keys():
      for trainee in filtered_trainees:
        rtn_data[trainee.full_name] = {}
        for general_item in data['general_item']:
          if general_item == "Gender":
            rtn_data[trainee.full_name]["Gender"] = trainee.gender
          elif general_item == "Term":
            rtn_data[trainee.full_name]["Term"] = trainee.current_term
          elif general_item == "Sending Locality":
            if trainee.locality is not None:
              rtn_data[trainee.full_name]["Sending Locality"] = trainee.locality.city.name
            else:
              rtn_data[trainee.full_name]["Sending Locality"] = 'N/A'
          elif general_item == "Team":
            rtn_data[trainee.full_name]["team"] = trainee.team.name
          elif general_item == "TA":
            rtn_data[trainee.full_name]["ta"] = trainee.TA.full_name

    context = {
      'data': rtn_data,
      'date_data': date_data
    }

    return render(request, "reports/generated_report.html", context=context)
