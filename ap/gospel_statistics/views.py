# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Import for generate
import os
from datetime import *
from StringIO import StringIO
from zipfile import ZipFile

from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from accounts.models import Trainee
from aputils.decorators import group_required
from aputils.utils import render_to_pdf, timeit_inline
from teams.models import Team
from terms.models import Term

from .models import GospelPair, GospelStat

# ctx[cols] = attributes
attributes = [
    'Tracts Distributed', 'Bibles Distributed', 'Contacted (>30 sec)', 'Led to Pray', 'Baptized',
    '2nd Appointment', 'Regular Appointment', 'Minutes on the Gospel', 'Minutes in Appointment',
    'Bible Study', 'Small Groups', 'District Meeting (New Student)', 'Conference'
]

_attributes = [
    'tracts_distributed', 'bibles_distributed', 'contacted_30_sec', 'led_to_pray', 'baptized',
    'second_appointment', 'regular_appointment', 'minutes_on_gospel', 'minutes_in_appointment',
    'bible_study', 'small_group', 'district_meeting', 'conference'
]

_att_len = len(_attributes)

ctx = dict()
for i in _attributes:
  ctx[i] = 0

C_TERM = Term.current_term()


class GospelStatisticsView(TemplateView):
  template_name = "gospel_statistics/gospel_statistics.html"

  @staticmethod
  def get_stats_list(gospel_pairs, current_week):
    data = []
    stats = GospelStat.objects.filter(gospelpair__in=gospel_pairs, week=current_week).values(*_attributes)
    for p in gospel_pairs:
      entry = dict()
      entry['gospel_pair'] = p
      try:
        stat = stats.get(gospelpair=p)
        for _att in _attributes:
          entry[_att] = stat.get(_att)
      except ObjectDoesNotExist:
        for _att in _attributes:
          entry[_att] = 0
      data.append(entry)
    return data

  @staticmethod
  def get_all_stats_list(gospel_pairs):
    data = []
    stats = GospelStat.objects.filter(gospelpair__in=gospel_pairs)
    for p in gospel_pairs:
      entry = dict()
      entry['gospel_pair'] = p
      totals = stats.filter(gospelpair=p).aggregate(*[Sum(_att) for _att in _attributes])
      for _att in _attributes:
        entry[_att] = totals.get(_att + "__sum")
      data.append(entry)
    return data

  def post(self, request, *args, **kwargs):
    # Retreive the updated stat values
    list_of_pairs = request.POST.getlist('pairs')
    list_of_stats = request.POST.getlist('inputs')
    current_week = C_TERM.term_week_of_date(date.today())
    if 'week' in self.kwargs:
      current_week = self.kwargs['week']
    start_index = 0
    end_index = _att_len
    for i in list_of_pairs:
      pair = GospelPair.objects.filter(id=i)
      stats = GospelStat.objects.filter(gospelpair=pair, week=current_week)
      if stats.exists():
        target_values = dict(zip(_attributes, list_of_stats[start_index:end_index]))
        stats.update(**target_values)
        start_index += _att_len
        end_index += _att_len
    # Fix returning to current week instead of remaining in selected week
    return redirect(reverse('gospel_statistics:gospel-statistics-view') + str(current_week))

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    ctx = super(GospelStatisticsView, self).get_context_data(**kwargs)
    team = current_user.team
    ctx['page_title'] = 'Team Statistics'
    ctx['team'] = team
    ctx['gospel_pairs'] = GospelPair.objects.filter(team=team, term=C_TERM)
    ctx['cols'] = attributes
    ctx['current'] = []
    ctx['atts'] = _attributes
    week = C_TERM.term_week_of_date(date.today())
    if 'week' in self.kwargs:
      week = self.kwargs['week']
    ctx['week'] = week
    # Current week stat
    ctx['current'] = self.get_stats_list(ctx['gospel_pairs'], week)
    # All 20 week stat
    ctx['all_stat'] = self.get_all_stats_list(ctx['gospel_pairs'])
    return ctx


class GenerateReportView(GroupRequiredMixin, TemplateView):
  template_name = "gospel_statistics/generate_report.html"
  # Need to check
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = {
      'page_title': 'Generate Report',
      'attributes': attributes,
      'campuses': Team.objects.filter(type='CAMPUS'),
      'communities': Team.objects.filter(type='COM'),
      'weeks': range(20)
    }
    return ctx

  def post(self, request, *args, **kwargs):
    ctx = super(GenerateReportView, self).get_context_data(**kwargs)
    teams_id = request.POST.getlist('teams')
    teams = Team.objects.filter(id__in=teams_id)
    weeks = []
    weeks = request.POST.getlist('weeks')
    # 1 = Full Report, 2 = Week & Total, 3 = Total Only
    report_type = int(request.POST.get('report_type'))
    ctx['reporttype'] = report_type
    # save_type = request.POST.get('save_type')
    if len(teams) < 1:
      return render(request, "gospel_statistics/generate_report.html", self.get_context_data())

    # Generate Report here
    in_memory = StringIO()
    zfile = ZipFile(in_memory, "a")

    term_stats = GospelStat.objects.filter(gospelpair__term=C_TERM).prefetch_related('gospelpair')
    for team in teams:
      code = team.code
      team_stats = term_stats.filter(gospelpair__team=team)
      gospelpairs = GospelPair.objects.filter(team=team, term=C_TERM)
      if report_type < 2:
        t = timeit_inline("type 2 %s" % team)
        t.start()
        # Each Pair
        pairs = []
        for pair in gospelpairs:
          pair_total = [0] * _att_len
          names = ''
          for trainee in pair.trainees.all():
            if len(names) > 0:
              names += ', '
            names += trainee.firstname + ' ' + trainee.lastname
          one_pair = [[names] + attributes]
          pair_stats = team_stats.filter(gospelpair=pair).values_list(*_attributes)
          for week in weeks:
            stats = pair_stats.filter(week=week)
            one = list(stats.first())
            one_pair.append(['Week ' + week] + one)
            for i, _att in enumerate(one):
              pair_total[i] += _att
            one_pair.append(['GP Total'] + pair_total)
            pairs.append(one_pair)
        ctx['pairs'] = pairs
        t.end()

      if report_type < 3:
        t = timeit_inline("type 3 %s" % team)
        t.start()
        # pair_total
        weekly = []
        weekly_total = ['Weekly Total'] + [0] * _att_len
        all_stats = team_stats.filter(gospelpair__in=gospelpairs).values_list(*_attributes)
        for week in weeks:
          one_week = all_stats.filter(gospelpair__in=gospelpairs, week=week)
          for every in one_week:
            weeklys = ['Week ' + week] + list(every)
          weekly.append(weeklys)
          totals = one_week.aggregate(*[Sum(_att) for _att in _attributes])
          for i, _att in enumerate(_attributes):
            weekly_total[i + 1] = totals.get(_att + "__sum")
          weekly.append(weekly_total)
        ctx['weekly'] = weekly
        t.end()

      # Total
      t = timeit_inline("team totals")
      t.start()
      totals = [0] * _att_len
      aggr = team_stats.aggregate(*[Sum(_att) for _att in _attributes])
      for i, _att in enumerate(_attributes):
        totals[i] = aggr.get(_att + "__sum")
      total = [['All ' + code + ' GP Pair Totals Added Together'] + totals]
      t.end()

      t = timeit_inline("term totals")
      t.start()
      term_totals = [0] * _att_len
      aggr = term_stats.aggregate(*[Sum(_att) for _att in _attributes])
      for i, _att in enumerate(_attributes):
        term_totals[i] = aggr.get(_att + "__sum")
      t.end()

      total.append(['FTTA Grand Total (Campus/Community Teams)'] + term_totals)
      # Fix next two append
      # total.append([code+' Average Across Weeks ('+str(len(weeks))+' Week Range)']+[])
      # total.append(['FTTA Total Average Across Weeks ('+str(len(weeks))+' Week Range)']+[])
      averages = ["{0:.2f}".format(each / max(1, float(len(gospelpairs)))) for each in totals]
      total.append([code + ' GP Pair Team Average'] + averages)
      ctx['total'] = total
      ctx['page_title'] = 'Gospel Statistics Report'
      ctx['attributes'] = attributes
      ctx['weeks'] = range(20)
      ctx['team'] = team.name
      ctx['term'] = C_TERM
      ctx['stats'] = GospelStat.objects.filter(gospelpair__in=gospelpairs)
      # Make it downloadable
      # return render(request, 'gospel_statistics/gospel_statistics_report_base.html', ctx)
      t = timeit_inline("pdf generation")
      t.start()
      pdf_file = render_to_pdf('gospel_statistics/gospel_statistics_report_base.html', ctx)
      path = team.name + '.pdf'

      with open(path, 'w+') as f:
        f.write(pdf_file.content)
      zfile.write(path)
      os.remove(path)
      t.end()
    # fix for Linux zip files read in Windows
    for zf in zfile.filelist:
      zf.create_system = 0

    zfile.close()
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=Gospel_Statistics_Report.zip'
    in_memory.seek(0)
    response.write(in_memory.read())
    return response
    # return render(request, "gospel_statistics/generate_report.html", self.get_context_data())


class NewGospelPairView(TemplateView):
  template_name = "gospel_statistics/new_pair.html"

  @staticmethod
  def find_duplicate(query_set, m2m_field, ids):
    query = query_set.annotate(
        count=Count(m2m_field)).filter(count=len(ids))
    for _id in ids:
      query = query.filter(**{m2m_field: _id})
    return query

  def post(self, request, *args, **kwargs):
    current_team = self.request.user.team
    # Retrieve the selected trainees
    list_of_trainee_id = request.POST.getlist('inputs')
    # Do not create empty gospel pairs
    if not len(list_of_trainee_id):
      return redirect(reverse('gospel_statistics:gospel-statistics-view'))
    trainees = Trainee.objects.filter(id__in=list_of_trainee_id)
    gospelpair = GospelPair(team=current_team, term=C_TERM)
    gospelpair.save()
    gospelpair.trainees.set(trainees)
    duplicate_gps = self.find_duplicate(
        GospelPair.objects.filter(team=current_team, term=C_TERM).exclude(id=gospelpair.id),
        'trainees', list(trainees.values_list('id')))
    if duplicate_gps.exists():
      # Need to add an alert for duplicate gospel pair
      gospelpair.delete()
      return redirect(reverse('gospel_statistics:gospel-statistics-view'))

    # Create 20 week GospelStats for the new gospelpair
    for week in range(0, 20):
      GospelStat(gospelpair=gospelpair, week=week).save()
    return redirect(reverse('gospel_statistics:gospel-statistics-view'))

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    ctx = super(NewGospelPairView, self).get_context_data(**kwargs)
    ctx['page_title'] = 'New Gospel Pair'
    ctx['team'] = current_user.team
    ctx['members'] = Trainee.objects.filter(team=current_user.team)
    return ctx


def delete_pair(request):
  # Get the current pair
  current_id = request.POST['pair_id']
  pair = get_object_or_404(GospelPair, id=current_id)
  # Delete the pair
  # Add a warning for deleting a gospel pair
  pair.delete()
  return redirect(reverse('gospel_statistics:gospel-statistics-view'))


@group_required(['training_assistant'])
def TAGospelStatisticsView(request):
  # Campus trainees
  campus_pairs = GospelPair.objects.filter(team__type='CAMPUS')
  campus_trainees = campus_pairs.aggregate(Count('trainees')).get('trainees__count')

  campus_stats = GospelStat.objects.filter(gospelpair__team__type='CAMPUS')
  campus_totals = [0] * _att_len
  if campus_stats.exists():
    aggr = campus_stats.aggregate(*[Sum(_att) for _att in _attributes])
    for i, _att in enumerate(_attributes):
      campus_totals[i] = aggr.get(_att + '__sum')

  # Community trainees
  community_pairs = GospelPair.objects.filter(team__type='COM')
  community_trainees = community_pairs.aggregate(Count('trainees')).get('trainees__count')

  community_stats = GospelStat.objects.filter(gospelpair__team__type='COM')
  community_totals = [0] * _att_len
  if community_stats.exists():
    aggr = community_stats.aggregate(*[Sum(_att) for _att in _attributes])
    for i, _att in enumerate(_attributes):
      community_totals[i] = aggr.get(_att + '__sum')

  campus_average = []
  community_average = []
  for total in campus_totals:
    average = "{0:.2f}".format(total / max(float(campus_trainees), 1))
    campus_average.append(average)
  for total in community_totals:
    average = "{0:.2f}".format(total / max(float(community_trainees), 1))
    community_average.append(average)

  # ctx = GospelStat.objects.filter(gospelpair__in=pairs)
  ctx = {
    'page_title': 'Team Statistics Summary',
    'attributes': attributes,
    'campus_total': campus_totals,
    'community_total': community_totals,
    'campus_average': campus_average,
    'community_average': community_average,
  }
  return render(request, 'gospel_statistics/ta_gospel_statistics.html', context=ctx)
