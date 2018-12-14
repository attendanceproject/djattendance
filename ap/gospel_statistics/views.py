# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import *

from accounts.models import Trainee
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponse
from terms.models import Term
from aputils.decorators import group_required
from braces.views import GroupRequiredMixin

from .models import GospelPair, GospelStat
from teams.models import Team

# Import for generate
import os
from aputils.utils import render_to_pdf
from zipfile import ZipFile
from StringIO import StringIO

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
ctx = dict()
for i in _attributes:
  ctx[i] = 0

C_TERM = Term.current_term()


def get_week():
  for i in range(0, 20):
    if C_TERM.startdate_of_week(i) <= date.today() \
      and C_TERM.enddate_of_week(i) >= date.today():
      return i


class GospelStatisticsView(TemplateView):
  template_name = "gospel_statistics/gospel_statistics.html"

  @staticmethod
  def get_stats_list(gospel_pairs, gospel_statistics, current_week):
    data = []
    for p in gospel_pairs:
      entry = dict()
      entry['gospel_pair'] = p
      stat = gospel_statistics.filter(gospelpair=p, week=current_week)[0]
      for i in _attributes:
        entry[i] = eval('stat.' + i)
      data.append(entry)
    return data

  @staticmethod
  def get_all_stats_list(gospel_pairs, gospel_statistics):
    data = []
    for p in gospel_pairs:
      entry = dict()
      entry['gospel_pair'] = p
      for i in _attributes:
        entry[i] = 0
      stats = gospel_statistics.filter(gospelpair=p)
      # Aggregate all the stats from all the different weeks
      for stat in stats:
        entry[_attributes[0]] += stat.tracts_distributed
        entry[_attributes[1]] += stat.bibles_distributed
        entry[_attributes[2]] += stat.contacted_30_sec
        entry[_attributes[3]] += stat.led_to_pray
        entry[_attributes[4]] += stat.baptized
        entry[_attributes[5]] += stat.second_appointment
        entry[_attributes[6]] += stat.regular_appointment
        entry[_attributes[7]] += stat.minutes_on_gospel
        entry[_attributes[8]] += stat.minutes_in_appointment
        entry[_attributes[9]] += stat.bible_study
        entry[_attributes[10]] += stat.small_group
        entry[_attributes[11]] += stat.district_meeting
        entry[_attributes[12]] += stat.conference
      data.append(entry)
    return data

  def post(self, request, *args, **kwargs):
    # Retreive the updated stat values
    list_of_pairs = request.POST.getlist('pairs')
    list_of_stats = request.POST.getlist('inputs')
    current_week = get_week()
    if 'week' in self.kwargs:
      current_week = self.kwargs['week']
    index = 0
    for i in list_of_pairs:
      pair = GospelPair.objects.filter(id=i)
      stat = GospelStat.objects.filter(gospelpair=pair, week=current_week)[0]
      ## Why doesn't this work?
      # for i in range(13):
      #  eval('stat.'+_attributes[i]+' = list_of_stats['+str(index+i)+']')
      stat.tracts_distributed = list_of_stats[index]
      stat.bibles_distributed = list_of_stats[index + 1]
      stat.contacted_30_sec = list_of_stats[index + 2]
      stat.led_to_pray = list_of_stats[index + 3]
      stat.baptized = list_of_stats[index + 4]
      stat.second_appointment = list_of_stats[index + 5]
      stat.regular_appointment = list_of_stats[index + 6]
      stat.minutes_on_gospel = list_of_stats[index + 7]
      stat.minutes_in_appointment = list_of_stats[index + 8]
      stat.bible_study = list_of_stats[index + 9]
      stat.small_group = list_of_stats[index + 10]
      stat.district_meeting = list_of_stats[index + 11]
      stat.conference = list_of_stats[index + 12]
      stat.save()
      index += 13
    ## Fix returning to current week instead of remaining in selected week
    return redirect(reverse('gospel_statistics:gospel-statistics-view') + str(current_week))

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    ctx = super(GospelStatisticsView, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Team Statistics'
    ctx['team'] = current_user.team
    ctx['gospel_pairs'] = GospelPair.objects.filter(team=current_user.team, term=C_TERM)
    ctx['cols'] = attributes
    ctx['current'] = []
    ctx['atts'] = _attributes
    week = get_week()
    if 'week' in self.kwargs:
      week = self.kwargs['week']
    ctx['week'] = week
    # Current week stat
    ctx['current'] = self.get_stats_list(ctx['gospel_pairs'], GospelStat.objects.filter(gospelpair__in=ctx['gospel_pairs']), week)
    # All 20 week stat
    ctx['all_stat'] = self.get_all_stats_list(ctx['gospel_pairs'], GospelStat.objects.filter(gospelpair__in=ctx['gospel_pairs']))
    return ctx

class GenerateReportView(GroupRequiredMixin, TemplateView):
  template_name = "gospel_statistics/generate_report.html"
  ## Need to check
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = {
      'page_title': 'Generate Report',
      'attributes': attributes,
      'campuses': Team.objects.filter(type='CAMPUS'),
      'communities': Team.objects.filter(type='COM'),
      'weeks': [i for i in range(20)]
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
    ctx['reporttype']=report_type
    save_type = request.POST.get('save_type')
    if len(teams) < 1:
      return render(request, "gospel_statistics/generate_report.html", self.get_context_data())

    ## Generate Report here
    in_memory = StringIO()
    zfile = ZipFile(in_memory, "a")
    for team in teams:
      code = team.code
      gospelpairs = GospelPair.objects.filter(team=team, term=C_TERM)
      if report_type < 2:
        # Each Pair
        pairs = []
        for pair in gospelpairs:
          pair_total = [0 for i in range(len(_attributes))]
          names = ''
          for trainee in pair.trainees.all():
            if len(names) > 0:
              names += ', '
            names += trainee.firstname+' '+trainee.lastname
          one_pair = [[names]+attributes]
          for week in weeks:
            one = GospelStat.objects.filter(gospelpair=pair, week=week)[0]
            one_pair.append(['Week '+week]+[eval('one.'+att) for att in _attributes])
            for i in range(len(_attributes)):
              pair_total[i]+=eval('one.'+_attributes[i])
          one_pair.append(['GP Total']+pair_total)
          pairs.append(one_pair)
        ctx['pairs'] = pairs
  
      if report_type < 3:
        # Weekly
        weekly = []
        weekly_total = ['Weekly Total']+[0 for i in range(len(_attributes))]
        for week in weeks:
          one_week = GospelStat.objects.filter(gospelpair__in=gospelpairs, week=week)
          weeklys = ['Week '+week]+[0 for i in range(len(_attributes))]
          for every in one_week:
            for i in range(len(_attributes)):
              val = eval('every.'+_attributes[i])
              weeklys[i+1] += val
              weekly_total[i+1] += val
          weekly.append(weeklys)
        weekly.append(weekly_total)
        ctx['weekly'] = weekly
      
      # Total
      stats = GospelStat.objects.filter(gospelpair__in=gospelpairs)
      totals = [0 for i in range(len(_attributes))]
      for stat in stats:
        for i in range(len(_attributes)):
          totals[i] += eval('stat.'+_attributes[i])
      total = [['All '+code+' GP Pair Totals Added Together']+totals]
      all_pairs = GospelPair.objects.filter(term=C_TERM)
      alls = GospelStat.objects.filter(gospelpair__in=all_pairs)
      grand = [0 for i in range(len(_attributes))]
      for each in alls:
        for i in range(len(_attributes)):
          grand[i] += eval('each.'+_attributes[i])

      total.append(['FTTA Grand Total (Campus/Community Teams)']+grand)
      ## Fix next two append
      #total.append([code+' Average Across Weeks ('+str(len(weeks))+' Week Range)']+[])
      #total.append(['FTTA Total Average Across Weeks ('+str(len(weeks))+' Week Range)']+[])
      total.append([code+' GP Pair Team Average']+["{0:.2f}".format(each/max(1,float(len(gospelpairs)))) for each in totals])
      ctx['total'] = total
      ctx['page_title'] = 'Gospel Statistics Report'
      ctx['attributes'] = attributes
      ctx['weeks'] = [i for i in range(20)]
      ctx['team'] = team.name
      ctx['term'] = C_TERM
      ctx['stats'] = GospelStat.objects.filter(gospelpair__in=gospelpairs)
      ## Make it downloadable
      #return render(request, 'gospel_statistics/gospel_statistics_report_base.html', ctx)
      pdf_file = render_to_pdf('gospel_statistics/gospel_statistics_report_base.html', ctx)
      path = team.name+'.pdf'

      with open(path, 'w+') as f:
        f.write(pdf_file.content)
      zfile.write(path)
      os.remove(path)

    # fix for Linux zip files read in Windows
    for zf in zfile.filelist:
      zf.create_system = 0

    zfile.close()
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=Gospel_Statistics_Report.zip'
    in_memory.seek(0)
    response.write(in_memory.read())

    return response
    #return render(request, "gospel_statistics/generate_report.html", self.get_context_data())

class NewGospelPairView(TemplateView):
  template_name = "gospel_statistics/new_pair.html"

  def post(self, request, *args, **kwargs):
    current_team = self.request.user.team
    # Retrieve the selected trainees
    list_of_trainee_id = request.POST.getlist('inputs')
    # Do not create empty gospel pairs
    if len(list_of_trainee_id) == 0:
        return redirect(reverse('gospel_statistics:gospel-statistics-view'))
    list_of_trainees = []
    for each in list_of_trainee_id:
      list_of_trainees.extend(Trainee.objects.filter(id=each))
    # Create a new empty gospel pair
    gospelpair = GospelPair(team=current_team, term=C_TERM)
    gospelpair.save()
    # Add the trainees
    for each in list_of_trainees:
      gospelpair.trainees.add(each)
    # Check for duplicate
    for each in GospelPair.objects.filter(team=current_team, term=C_TERM):
      if each.id is not gospelpair.id and set(each.trainees.all()) == set(gospelpair.trainees.all()):
        ## Need to add an alert for duplicate gospel pair
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
  pair = GospelPair(id=current_id)
  # Delete the pair
  ## Add a warning for deleting a gospel pair
  pair.delete()
  return redirect(reverse('gospel_statistics:gospel-statistics-view'))


@group_required(['training_assistant'])
def TAGospelStatisticsView(request):
  # Campus trainees
  campus = Team.objects.filter(type='CAMPUS')
  campus_pairs = GospelPair.objects.filter(team__in=campus)
  campus_trainees=0
  for i in campus_pairs:
    campus_trainees+=len(i.trainees.all())
  campus_all = GospelStat.objects.filter(gospelpair__in=campus_pairs)
  campus_total = [0 for i in range(len(_attributes))]
  if len(campus_all)>0:
    for index in range(len(campus_all)):
      for i in range(len(_attributes)):
        campus_total[i]+=eval('campus_all['+str(index)+'].'+_attributes[i])

  # Community trainees
  community = Team.objects.filter(type='COM')
  community_pairs = GospelPair.objects.filter(team__in=community)
  community_all = GospelStat.objects.filter(gospelpair__in=community_pairs)
  community_trainees=0
  for i in community_pairs:
    community_trainees+=len(i.trainees.all())
  community_total = []
  community_total = [0 for i in range(len(_attributes))]
  if len(community_all)>0:
    for index in range(len(community_all)):
      for i in range(len(_attributes)):
        community_total[i]+=eval('community_all['+str(index)+'].'+_attributes[i])

  campus_average = []
  community_average = []
  for i in campus_total:
    campus_average.append("{0:.2f}".format(i/max(float(campus_trainees),1)))
  for i in community_total:
    community_average.append("{0:.2f}".format(i/max(float(community_trainees),1)))

  #ctx = GospelStat.objects.filter(gospelpair__in=pairs)
  ctx = {
    'page_title': 'Team Statistics Summary',
    'attributes': attributes,
    'campus_total': campus_total,
    'community_total': community_total,
    'campus_average': campus_average,
    'community_average': community_average,
  }
  return render(request, 'gospel_statistics/ta_gospel_statistics.html', context=ctx)
