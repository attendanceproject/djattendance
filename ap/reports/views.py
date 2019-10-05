import copy
import csv
import json
import os
from collections import Counter
from datetime import datetime
from StringIO import StringIO
from zipfile import ZipFile

from accounts.models import Trainee
from aputils.eventutils import EventUtils
from aputils.utils import render_to_pdf
from attendance.models import Roll
from braces.views import GroupRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView
from leaveslips.models import GroupSlip
from localities.models import Locality
from terms.models import Term

from .utils import Stash

stash = Stash()


# input view for generating generic attendance report
class GenerateAttendanceReport(GroupRequiredMixin, TemplateView):
  template_name = 'reports/generate_attendance_report.html'
  group_required = ['training_assistant']


# initial attendance report base that results in may ajax queries being generated
# according to list fed of trainee ids, localities, and teams
# this is done to bypass nginex timeout and to run more synchronous operations
# on computing the attendance record for trainees
# client requests to server would become easier to implement
# rather than running parallel processing via the backend
class AttendanceReport(GroupRequiredMixin, TemplateView):
  template_name = 'reports/attendance_report.html'
  group_required = ['training_assistant']

  def post(self, request, *args, **kwargs):
    # below is used to resolve duplicate city names for localities, eg: Richmond, Canada vs Richmond, VA
    # using foreign key links from the trainees ensures that we don't pull localities or teams that don't have any trainees
    context = self.get_context_data()
    trainees = Trainee.objects.exclude(type="S")
    context['trainee_ids'] = list(trainees.order_by('lastname').values_list('pk', flat=True))
    locality_ids = set(trainees.values_list('locality__id', flat=True).distinct())
    localities = [{'id': loc_id, 'name': Locality.objects.get(pk=loc_id).city.name} for loc_id in locality_ids]
    teams = list(set(trainees.values_list('team__code', flat=True)))

    # for localities with duplicate names, process it here
    try:
      dup_locality = Locality.objects.get(city__name='Richmond', city__state='VA')
      for locality in localities:
        if locality['id'] == dup_locality.id:
          locality['name'] = "Richmond, VA"
    except (Locality.DoesNotExist, KeyError):
      pass

    # set stash instance for optmized runtime
    stash.set_records(list())
    stash.set_localities(copy.deepcopy(localities))
    stash.set_teams(copy.deepcopy(teams))

    # use the headers field in stash for input adjustments, not a priority
    stash.set_headers(['unexcused_absences_percentage', 'tardy_percentage', 'classes_missed_percentage', 'sickness_percentage'])

    context['localities'] = localities
    context['dictLocalities'] = json.dumps(dict([(x["id"], x["name"]) for x in localities]))
    context['teams'] = teams

    request.session['date_from'] = request.POST.get("date_from")
    request.session['date_to'] = request.POST.get("date_to")

    return super(AttendanceReport, self).render_to_response(context)


def date_to_str(date):
  month = str(date.month)
  day = str(date.day)
  year = str(date.year)

  if len(month) < 2:
    month = '0' + month
  if len(day) < 2:
    day = '0' + day

  return month + '_' + day + '_' + year


def generate_csv(request):
  in_memory = StringIO()
  cfile = csv.writer(in_memory)

  date_from = datetime.strptime(request.session.get("date_from"), '%m/%d/%Y').date()
  date_to = datetime.strptime(request.session.get("date_to"), '%m/%d/%Y').date()
  all_trainees = copy.deepcopy(stash.get_records())

  # Change this list if want to add or remove fields
  fields = ['name', 'ta', 'term', 'gender', 'unexcused_absences_percentage', 'tardy_percentage',
            'sickness_percentage', 'classes_missed_percentage']

  cfile.writerow(tuple(fields))
  for each in sorted(all_trainees, key=lambda each: each['name']):
    trainee = tuple([each[field] for field in fields])
    cfile.writerow(trainee)

  path = 'Attendance_Report_' + date_to_str(date_from) + '_to_' + date_to_str(date_to) + '.csv'

  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename=' + path
  in_memory.seek(0)
  response.write(in_memory.read())

  return response


def generate_zip(request):
  date_from = datetime.strptime(request.session.get("date_from"), '%m/%d/%Y').date()
  date_to = datetime.strptime(request.session.get("date_to"), '%m/%d/%Y').date()
  localities = stash.get_localities()
  teams = stash.get_teams()

  # we're using a deep copy because we'll modify and adjust them for teams and for localities
  # for locality files we don't need to render which locality the trainee is from
  # for team files we don't need to render which team the trainee is on
  records_duplicate = copy.deepcopy(stash.get_records())
  date_range = [date_from, date_to]
  in_memory = StringIO()
  zfile = ZipFile(in_memory, "a")

  # first create dictionary object and set values used across all localities
  context = dict()
  context['date_range'] = date_range
  context['averages'] = stash.get_averages()

  # for each locality, grab only the trainees that are from that locality
  # filter using locality ID instead of name due to potential duplicates
  # create pdf file for locality, write it to the zip file
  for locality in localities:
    locality_trainees = [record for record in records_duplicate if record["sending_locality"] == locality["id"]]
    context['trainee_records'] = locality_trainees
    context['locality'] = locality["name"]

    pdf_file = render_to_pdf("reports/template_report.html", context)
    path = locality["name"] + '.pdf'

    with open(path, 'w+') as f:
      f.write(pdf_file.content)
    zfile.write(path)
    os.remove(path)

  # clear the dictionary object and set values used across all teams
  context = dict()
  context['date_range'] = date_range
  context['averages'] = stash.get_averages()

  # because the records use locality ids, we'll need to change those ids to names
  for record in records_duplicate:
    locality_id = record['sending_locality']
    locality_name = filter(lambda locality: locality['id'] == locality_id, localities)
    record['sending_locality'] = locality_name[0]['name']

  # for each team, grab only the trainees that serve on that team
  for team in teams:
    team_trainees = [record for record in records_duplicate if record["team"] == team]
    context['trainee_records'] = team_trainees
    context['team'] = team

    pdf_file = render_to_pdf("reports/template_report.html", context)
    path = team + '.pdf'

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


# given a list or rolls and groupslips, return rolls that are not excused by groupslips
def rolls_excused_by_groupslips(rolls, groupslips):
  unexcused_rolls = rolls
  for group_slip in groupslips:

    # majority of groupslips are on the same date
    if group_slip['start'].date() == group_slip['end'].date():
      unexcused_rolls = unexcused_rolls.exclude(event__start__gte=group_slip['start'].time(), event__end__lte=group_slip['end'].time())

    # to cover multi day groupslips for conference or other events
    else:
      potentials_rolls = unexcused_rolls.filter(date__range=[group_slip['start'].date(), group_slip['end'].date()])
      if potentials_rolls.count() == 0:
        continue
      for r in potentials_rolls:
        r_start = datetime.combine(r.date, r.event.start)
        r_end = datetime.combine(r.date, r.event.end)
        if group_slip['start'] <= r_start and group_slip['end'] >= r_end:
          unexcused_rolls = unexcused_rolls.exclude(id=r.pk)

  return unexcused_rolls


# computing the attendance record per trainee
# could potentially explore more optimized runtine by reducing duplicate computation
def attendance_report_trainee(request):

  date_from = datetime.strptime(request.session.get("date_from"), '%m/%d/%Y').date()
  date_to = datetime.strptime(request.session.get("date_to"), '%m/%d/%Y').date()
  t_id = int(request.GET["traineeId"])
  res = dict()

  trainee = Trainee.objects.get(pk=t_id)
  res["trainee_id"] = t_id
  res["name"] = trainee.lastname + ", " + trainee.firstname
  res["sending_locality"] = trainee.locality.id
  res["term"] = trainee.current_term
  res["team"] = trainee.team.code
  res["ta"] = trainee.TA.full_name
  res["gender"] = trainee.gender

  ct = Term.objects.get(current=True)
  if date_from < ct.start:
    date_from = ct.start
  if date_to > ct.end:
    date_to = ct.end

  rolls = Roll.objects.filter(trainee=trainee, date__gte=date_from, date__lte=date_to).exclude(status='P').exclude(event__monitor=None)

  start_datetime = datetime.combine(date_from, datetime.min.time())
  end_datetime = datetime.combine(date_to, datetime.max.time())
  group_slips = GroupSlip.objects.filter(status='A', start__gte=start_datetime, end__lte=end_datetime, trainees=trainee).values('start', 'end')

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

  # CALCULATE %TARDY
  total_possible_rolls_count = max(1,sum(count[ev] for ev in count if ev.monitor is not None))
  tardy_rolls = rolls.exclude(status='A').filter(~(Q(leaveslips__does_not_count=True) & Q(leaveslips__status='A')))
  tardy_rolls = rolls_excused_by_groupslips(tardy_rolls, group_slips.filter(does_not_count=True))

  res["tardy_percentage"] = str(round(tardy_rolls.count() / float(total_possible_rolls_count) * 100, 2)) + "%"

  # CALCULATE %CLASSES MISSED
  possible_class_rolls_count = max(1,sum(count[ev] for ev in count if ev.monitor == 'AM' and ev.type == 'C'))
  missed_classes = rolls.filter(event__monitor='AM', event__type='C')

  # currently counts rolls excused by individual and group slips
  # comment this part out to not count those rolls
  # exclude absent rolls excused by individual slips
  # missed_classes = missed_classes.exclude(leaveslips__status='A')

  missed_classes = missed_classes.filter(~(Q(leaveslips__does_not_count=True) & Q(leaveslips__status='A')))

  # exclude absent rolls excused by group slips
  missed_classes = rolls_excused_by_groupslips(missed_classes, group_slips.filter(does_not_count=True))

  res["classes_missed_percentage"] = str(round(missed_classes.count() / float(possible_class_rolls_count) * 100, 2)) + "%"

  # CALCULATE %SICKNESS
  rolls_covered_by_sickness = Roll.objects.filter(trainee=trainee, leaveslips__status='A', leaveslips__type='SICK', date__gte=date_from, date__lte=date_to).distinct()

  res["sickness_percentage"] = str(round(rolls_covered_by_sickness.count() / float(total_possible_rolls_count) * 100, 2)) + "%"

  # CALCULATE UNEXCUSED ABSENCES
  unexcused_absences = rolls.filter(status='A')
  unexcused_absences = unexcused_absences.exclude(leaveslips__status='A')
  unexcused_absences = rolls_excused_by_groupslips(unexcused_absences, group_slips)
  res["unexcused_absences_percentage"] = str(round(unexcused_absences.count() / float(total_possible_rolls_count) * 100, 2)) + "%"

  stash.append_records(res)
  return JsonResponse(res)


#         # get number of LS summaries
#         if "Number of LS" in items_for_query:
#           rtn_data[trainee.full_name]['Number of LS'] = Discipline.objects.filter(trainee=trainee).count()

#         group_slips_for_trainee = pgsq.query.filter(trainees=trainee).values('start', 'end', 'type')

#         trainee_rolls = qs_rolls.query.filter(trainee=trainee)
#         pickled_trainee_rolls = pickle.dumps(trainee_rolls)
#         pickled_trainee_query = pickle.loads(pickled_trainee_rolls)
#         qs_trainee_rolls = Roll.objects.all()
#         qs_trainee_rolls.query = pickled_trainee_query

#         if "Classes Missed" in items_for_query:
#           rtn_data[trainee.full_name]['Classes Missed'] = qs_trainee_rolls.query.filter(status='A', event__type='C').count()

#         absent_rolls_covered_in_group_slips = Roll.objects.none()
#         tardy_rolls_covered_in_group_slips = Roll.objects.none()

#         # DEALING WITH GROUP SLIPS FOR SPECIAL EXCUSED ABSENCES (next 45 lines of code)
#         # get rolls for special group slips; this is needed later for excluding these rolls from individual slips that cover these same rolls
#         rolls_covered_in_conference_group_slips = Roll.objects.none()
#         rolls_covered_in_fellowship_group_slips = Roll.objects.none()
#         rolls_covered_in_gospel_group_slips = Roll.objects.none()
#         rolls_covered_in_night_out_group_slips = Roll.objects.none()
#         rolls_covered_in_other_group_slips = Roll.objects.none()
#         rolls_covered_in_service_group_slips = Roll.objects.none()
#         rolls_covered_in_team_trip_group_slips = Roll.objects.none()

#         # necessary to do this due to slip.events function not working properly....
#         # Calculate for excused absences that can be covered by a group slip - conference, fellowship, gospel, night out, other, service, team trip
#         #t = timeit_inline("Group Slip Absences for Trainee")
#         #t.start()
#         for slip in group_slips_for_trainee:
#           #t = timeit_inline("Get rolls in slip for group slips")
#           #t.start()
#           rolls_in_slip = qs_trainee_rolls.query.filter(event__start__gte=slip['start'], event__end__lte=slip['end'], status='A')
#           #t.end()
#           #t = timeit_inline("Get absent rolls in slip for group slips")
#           t.start()
#           #absent_rolls_covered_in_group_slips = absent_rolls_covered_in_group_slips | rolls_in_slip
#           #t.end()
#           #t = timeit_inline("Get tardy rolls in slip for group slips")
#           #t.start()
#           tardy_rolls_covered_in_group_slips = tardy_rolls_covered_in_group_slips | qs_trainee_rolls.query.filter(event__start__gte=slip['start'], event__end__lte=slip['end'], status__in=['T', 'U', 'L'])
#           #t.end()
#           #t = timeit_inline("Add special type absent rolls to list")
#           #t.start()
#           if 'Absences - Excused - Conference' in items_for_query and slip['type'] == 'CONF':
#             rolls_covered_in_conference_group_slips = rolls_covered_in_conference_group_slips | rolls_in_slip
#           if 'Absences - Excused - Fellowship' in items_for_query and slip['type'] == 'FWSHP':
#             rolls_covered_in_fellowship_group_slips = rolls_covered_in_fellowship_group_slips | rolls_in_slip
#           if 'Absences - Excused - Gospel' in items_for_query and slip['type'] == 'GOSP':
#             rolls_covered_in_gospel_group_slips = rolls_covered_in_gospel_group_slips | rolls_in_slip
#           if 'Absences - Excused - Night Out' in items_for_query and slip['type'] == 'NIGHT':
#             rolls_covered_in_night_out_group_slips = rolls_covered_in_night_out_group_slips | rolls_in_slip
#           if 'Absences - Excused - Other' in items_for_query and slip['type'] == 'OTHER':
#             rolls_covered_in_other_group_slips = rolls_covered_in_other_group_slips | rolls_in_slip
#           if 'Absences - Excused - Service' in items_for_query and slip['type'] == 'SERV':
#             rolls_covered_in_service_group_slips = rolls_covered_in_service_group_slips | rolls_in_slip
#           if 'Absences - Excused - Team Trip' in items_for_query and slip['type'] == 'TTRIP':
#             rolls_covered_in_team_trip_group_slips = rolls_covered_in_team_trip_group_slips | rolls_in_slip
#           #t.end()

#         #t = timeit_inline("Get count of special absent rolls")
#         #t.start()
#         # add count of absent rolls covered by group slips to special excused absences count; deal with individual slips after this block of code
#         if 'Absences - Excused - Conference' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Conference'] = rolls_covered_in_conference_group_slips.count()
#         if 'Absences - Excused - Fellowship' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Fellowship'] = rolls_covered_in_fellowship_group_slips.count()
#         if 'Absences - Excused - Gospel' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Gospel'] = rolls_covered_in_gospel_group_slips.count()
#         if 'Absences - Excused - Night Out' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Night Out'] = rolls_covered_in_night_out_group_slips.count()
#         if 'Absences - Excused - Other' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Other'] = rolls_covered_in_other_group_slips.count()
#         if 'Absences - Excused - Service' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Service'] = rolls_covered_in_service_group_slips.count()
#         if 'Absences - Excused - Team Trip' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Excused - Team Trip'] = rolls_covered_in_team_trip_group_slips.count()
#         #t.end()
#         #t.end()


#         t = timeit_inline("Individual Slip Absence for Trainee")
#         t.start()
#         # DEALING WITH INDIVIDUAL SLIPS FOR SPECIAL EXCUSED ABSENCES (next 91 lines of code)
#         primary_indv_slip_filter = IndividualSlip.objects.filter(rolls__in=qs_trainee_rolls.query, rolls__status__contains='A', status__in=['A', 'S'])
#         pickled_indv_slip_filter = pickle.dumps(primary_indv_slip_filter)

#         # qs_rolls is the queryset of all pertinent rolls related to the filtered trainees in the date range that are tardies or absences
#         pickled_indv_slip_filter_qs = pickle.loads(pickled_indv_slip_filter)
#         indv_slip_qs = IndividualSlip.objects.all()
#         indv_slip_qs.query = pickled_indv_slip_filter_qs

#         if 'Absences - Total' in items_for_query:
#           rtn_data[trainee.full_name]['Absences - Total'] = qs_trainee_rolls.query.filter(status='A').count()
#         if 'Absences - Excused' in items_for_query:
#           # get all absent rolls excused by individual leave slips (exclude rolls covered in group slips, in case a trainee has both a group and individual leave slip for the same roll)
#           indv_slips = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused'] += indv_slips.values_list('rolls').count()

#           # get all absent rolls excused by groups slips
#           rtn_data[trainee.full_name]['Absences - Excused'] += absent_rolls_covered_in_group_slips.count()

#         if 'Absences - Unexcused' in items_for_query:
#           if 'Absences - Total' in rtn_data[trainee.full_name] and 'Absences - Excused' in rtn_data[trainee.full_name]:
#             # save time by not needing to query again
#             rtn_data[trainee.full_name]['Absences - Unexcused'] = rtn_data[trainee.full_name]['Absences - Total'] - rtn_data[trainee.full_name]['Absences - Excused']
#           else:
#             # get all rolls where trainee is absent and minus those excused by group and individual leave slips
#             rtn_data[trainee.full_name]['Absences - Unexcused'] = qs_trainee_rolls.query.filter(status='A').count() - \
#                 absent_rolls_covered_in_group_slips.count()

#             # exclude rolls covered in group leave slips
#             indv_slips = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
#             rtn_data[trainee.full_name]['Absences - Unexcused'] -= indv_slips.values_list('rolls').count()

#         if 'Absences - Unexcused and Sickness' in items_for_query:
#           # get rolls for absences that are excused with type sick
#           indv_slips_sickness = indv_slip_qs.query.filter(type="SICK")
#           rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] += indv_slips_sickness.values_list('rolls').count()
#           if 'Absences - Unexcused' in rtn_data[trainee.full_name]:
#             # get rolls for unexcused absences
#             rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] += rtn_data[trainee.full_name]['Absences - Unexcused']
#           else:
#             # get all rolls where trainee is absent and minus those excused by group and individual leave slips
#             rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] = qs_trainee_rolls.query.filter(status='A').count() - \
#                 absent_rolls_covered_in_group_slips.count()

#             indv_slips = indv_slip_qs.query.exclude(rolls__in=absent_rolls_covered_in_group_slips)
#             rtn_data[trainee.full_name]['Absences - Unexcused and Sickness'] -= indv_slips.values_list('rolls').count()

#         if 'Absences - Excused - Conference' in items_for_query:
#           conference_slips = indv_slip_qs.query.filter(type="CONF").exclude(rolls__in=rolls_covered_in_conference_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused - Conference'] += conference_slips.values_list('rolls').count()
#         if 'Absences - Excused - Family Emergency' in items_for_query:
#           fam_emerg_slips = indv_slip_qs.query.filter(type="EMERG")
#           rtn_data[trainee.full_name]['Absences - Excused - Family Emergency'] += fam_emerg_slips.values_list('rolls').count()
#         if 'Absences - Excused - Fellowship' in items_for_query:
#           fellowship_slips = indv_slip_qs.query.filter(type="FWSHP").exclude(rolls__in=rolls_covered_in_fellowship_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused - Fellowship'] += fellowship_slips.values_list('rolls').count()
#         if 'Absences - Excused - Funeral' in items_for_query:
#           funeral_slips = indv_slip_qs.query.filter(type="FUNRL")
#           rtn_data[trainee.full_name]['Absences - Excused - Funeral'] += funeral_slips.values_list('rolls').count()
#         if 'Absences - Excused - Gospel' in items_for_query:
#           gospel_slips = indv_slip_qs.query.filter(type="GOSP").exclude(rolls__in=rolls_covered_in_gospel_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused - Gospel'] += gospel_slips.values_list('rolls').count()
#         if 'Absences - Excused - Grad School/Job Interview' in items_for_query:
#           intv_slips = indv_slip_qs.query.filter(type="INTVW")
#           rtn_data[trainee.full_name]['Absences - Excused - Grad School/Job Interview'] += intv_slips.values_list('rolls').count()
#         if 'Absences - Excused - Graduation' in items_for_query:
#           grad_slips = indv_slip_qs.query.filter(type="GRAD")
#           rtn_data[trainee.full_name]['Absences - Excused - Graduation'] += grad_slips.values_list('rolls').count()
#         if 'Absences - Excused - Meal Out' in items_for_query:
#           meal_out_slips = indv_slip_qs.query.filter(type="MEAL")
#           rtn_data[trainee.full_name]['Absences - Excused - Meal Out'] += meal_out_slips.values_list('rolls').count()
#         if 'Absences - Excused - Night Out' in items_for_query:
#           night_out_slips = indv_slip_qs.query.filter(type="NIGHT")
#           rtn_data[trainee.full_name]['Absences - Excused - Night Out'] += night_out_slips.values_list('rolls').count()
#         if 'Absences - Excused - Other' in items_for_query:
#           other_slips = indv_slip_qs.query.filter(type="OTHER").exclude(rolls__in=rolls_covered_in_other_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused - Other'] += other_slips.values_list('rolls').count()
#         if 'Absences - Excused - Service' in items_for_query:
#           service_slips = indv_slip_qs.query.filter(type="SERV").exclude(rolls__in=rolls_covered_in_service_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused - Service'] += service_slips.values_list('rolls').count()
#         if 'Absences - Excused - Sickness' in items_for_query:
#           sick_slips = indv_slip_qs.query.filter(type="SICK")
#           rtn_data[trainee.full_name]['Absences - Excused - Sickness'] += sick_slips.values_list('rolls').count()
#         if 'Absences - Excused - Special' in items_for_query:
#           special_slips = indv_slip_qs.query.filter(type="SPECL")
#           rtn_data[trainee.full_name]['Absences - Excused - Special'] += special_slips.values_list('rolls').count()
#         if 'Absences - Excused - Wedding' in items_for_query:
#           wedding_slips = indv_slip_qs.query.filter(type="WED")
#           rtn_data[trainee.full_name]['Absences - Excused - Wedding'] += wedding_slips.values_list('rolls').count()
#         if 'Absences - Excused - Team Trip' in items_for_query:
#           team_trip_slips = indv_slip_qs.query.filter(type="TTRIP").exclude(rolls__in=rolls_covered_in_team_trip_group_slips)
#           rtn_data[trainee.full_name]['Absences - Excused - Team Trip'] += team_trip_slips.values_list('rolls').count()

#         t.end()

#         t = timeit_inline("Tardy for Trainee")
#         t.start()
#         # TARDIES FILTER
#         if 'Tardies - Total' in items_for_query:
#           late_tardies = qs_trainee_rolls.query.filter(status='T').count()
#           uniform_tardies = qs_trainee_rolls.query.filter(status='U').count()
#           left_class_tardies = qs_trainee_rolls.query.filter(status='L').count()
#           rtn_data[trainee.full_name]['Tardies - Total'] = late_tardies + uniform_tardies + left_class_tardies
#         if 'Tardies - Uniform' in items_for_query:
#           if 'uniform_tardies' in locals():
#             rtn_data[trainee.full_name]['Tardies - Uniform'] = uniform_tardies
#           else:
#             rtn_data[trainee.full_name]['Tardies - Uniform'] = qs_trainee_rolls.query.filter(status='U').count()
#         if 'Tardies - Left Class' in items_for_query:
#           if 'left_class_tardies' in locals():
#             rtn_data[trainee.full_name]['Tardies - Left Class'] = left_class_tardies
#           else:
#             rtn_data[trainee.full_name]['Tardies - Left Class'] = qs_trainee_rolls.query.filter(status='L').count()
#         if 'Tardies - Late' in items_for_query:
#           if 'late_tardies' in locals():
#             rtn_data[trainee.full_name]['Tardies - Late'] = late_tardies
#           else:
#             rtn_data[trainee.full_name]['Tardies - Late'] = qs_trainee_rolls.query.filter(status='T').count()
#         if 'Tardies - Excused' in items_for_query or 'Tardies - Unexcused' in items_for_query:
#           indv_slips = IndividualSlip.objects.filter(rolls__in=qs_trainee_rolls.query, rolls__status__in=['T', 'U', 'L'], status__in=['A', 'S']).exclude(rolls__in=tardy_rolls_covered_in_group_slips)
#           if 'Tardies - Excused' in items_for_query:
#             # individual slips
#             rtn_data[trainee.full_name]['Tardies - Excused'] += indv_slips.values_list('rolls').count()
#             # group slips
#             rtn_data[trainee.full_name]['Tardies - Excused'] += tardy_rolls_covered_in_group_slips.count()
#           if 'Tardies - Unexcused' in items_for_query:
#             if 'Tardies - Total' in rtn_data[trainee.full_name]:
#               rtn_data[trainee.full_name]['Tardies - Unexcused'] += rtn_data[trainee.full_name]['Tardies - Total']
#               # individual slips
#               rtn_data[trainee.full_name]['Tardies - Unexcused'] -= indv_slips.values_list('rolls').count()
#               # group slips
#               rtn_data[trainee.full_name]['Tardies - Unexcused'] -= tardy_rolls_covered_in_group_slips.count()
#             else:
#               late_tardies = qs_trainee_rolls.query.filter(status='T').count()
#               uniform_tardies = qs_trainee_rolls.query.filter(status='U').count()
#               left_class_tardies = qs_trainee_rolls.query.filter(status='L').count()
#               rtn_data[trainee.full_name]['Tardies - Unexcused'] += late_tardies + uniform_tardies + left_class_tardies
#               # individual slips
#               rtn_data[trainee.full_name]['Tardies - Unexcused'] -= indv_slips.values_list('rolls').count()
#               # group slips
#               rtn_data[trainee.full_name]['Tardies - Unexcused'] -= tardy_rolls_covered_in_group_slips.count()
#         t.end()
