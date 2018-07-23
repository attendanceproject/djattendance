from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import Avg

from datetime import timedelta, date

from terms.models import Term

import services

from django.utils.functional import cached_property


# Has: assignments
class WeekSchedule(models.Model):
  class Meta:
    ordering = ['-start']

  """
  A service schedule for one week in the training.
  """

  start = models.DateField()  # should be the Tuesday of every week
  description = models.TextField(blank=True, null=True)

  # line of encouragement in the beginning
  encouragement = models.TextField(blank=True, null=True)

  # workload calculations
  workload_margin = models.PositiveSmallIntegerField(default=2)

  # exceptions inactive for just this week
  silenced_exceptions = models.ManyToManyField('ServiceException', blank=True, verbose_name='Exceptions to ignore this week')

  @property
  def week(self):
    return Term.current_term().term_week_of_date(self.start)

  # TODO
  # average workload for this schedule
  @property
  def avg_workload(self):
    return self.assignments.aggregate(avg_workload=Coalesce(Avg('workload'), 0))['avg_workload'] / services.models.Worker.objects.count()

  # Prevent from working way above the average trainee workload (standard of deviation)
  # avg_workload + margin = workload ceiling
  @property
  def workload_ceiling(self):
    return self.avg_workload + self.workload_margin

  # Info on scheduler who created the schedule and info on last modified
  scheduler = models.ForeignKey('accounts.Trainee', on_delete=models.SET_NULL, null=True)
  last_modified = models.DateTimeField(auto_now=True)

  @staticmethod
  def get_or_create_current_week_schedule(scheduler):
    ct = Term.current_term()
    current_week = ct.term_week_of_date(date.today())
    return WeekSchedule.get_or_create_week_schedule(scheduler, current_week)

  @staticmethod
  def get_or_create_week_schedule(scheduler, week_number):
    ct = Term.current_term()
    # service week starts on Tuesdays rather than Mondays
    start = ct.get_date(int(week_number), 1)
    if WeekSchedule.objects.filter(start=start).exists():
      week_schedule = WeekSchedule.objects.get(start=start)
    else:
      week_schedule = WeekSchedule(start=start, scheduler=scheduler)
      week_schedule.save()
    return week_schedule

  @cached_property
  def week_range(self):
    week_start = self.start
    week_end = self.start + timedelta(days=6)
    return (week_start, week_end)

  @staticmethod
  def latest_week_schedule():
    return WeekSchedule.objects.latest('start')

  @staticmethod
  def current_week_schedule():
    t = date.today()
    ct = Term.current_term()
    if ct.is_date_within_term(t):
      week = ct.term_week_of_date(t)
      # service week starts on Tuesdays rather than Mondays
      start = ct.startdate_of_week(week) + timedelta(days=1)
      if WeekSchedule.objects.filter(start=start).exists():
        return WeekSchedule.objects.get(start=start)
      else:
        return None

  def __unicode__(self):
    try:
      return 'Week Schedule - ' + str(self.start)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
