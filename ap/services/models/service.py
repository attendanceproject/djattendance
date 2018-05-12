from django.db import models

from schedules.constants import WEEKDAYS

from .constants import GENDER
from .constants import WORKER_ROLE_TYPES

from datetime import datetime, timedelta


class Category(models.Model):
  """
  Defines a service category such as Clean-up, Guard, Mopping, Chairs, etc.
  """
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True, null=True)

  def __unicode__(self):
    try:
      return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

# Should be able to define number and type of workers needed.
# Also allow volunteers, extras to be added


# TODO: Add service rolls
class Service(models.Model):
  class Meta:
    ordering = ['category', 'weekday', 'start']
  """
  Defines a weekly service, whether rotational (e.g. Tuesday Breakfast Clean-up)
  or designated (e.g. Attendance Project, Vehicle Maintenance, or Lights)

  Repeats weekly unless day is specified for a one-off service

  Each Service only covers one time slot (e.g. Tuesday Supper Cleanup)
  """

  # Name is made primary key so any changes would create a new service automatically.
  name = models.CharField(max_length=100, unique=True)
  # the event's shortcode, e.g. FMoC or Lights
  code = models.CharField(max_length=10)

  # Category groups all the individual services into one group for editting
  # e.g. Monday Breakfast Cleanup, Tuesday Breakfast Cleanup
  category = models.ForeignKey('Category', related_name="services", on_delete=models.SET_NULL, null=True)
  schedule = models.ManyToManyField('SeasonalServiceSchedule', related_name="services")

  active = models.BooleanField(default=True)
  designated = models.BooleanField(default=False)

  # Total number of workers required for this service
  # workers_required = models.PositiveSmallIntegerField(default=1)

  '''
  - Specifies types of worker groups and how many to choose from and
    what role to give them as well as gender roles
  - Also doubles to hold designated service workers.
  '''
  worker_groups = models.ManyToManyField('WorkerGroup', through='ServiceSlot')

  weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
  start = models.TimeField()
  end = models.TimeField()
  # Optional day creates a one-off service that doesn't repeat weekly
  day = models.DateField(blank=True, null=True)

  def calculated_date(self):
    if self.day:
      d = self.day
    else:
      d = datetime.today()
      d = d - timedelta(d.weekday()) + timedelta(self.weekday)
      # Shift Monday to week future since our week starts on Tuesday
      if self.weekday is 0:
        d += timedelta(7)
    return d.date()

  def calculated_date_from_week_start(self, date):
    if self.day:
      d = self.day
    else:
      d = date + timedelta(self.weekday)
      # Shift Monday to week future since our week starts on Tuesday
      if self.weekday is 0:
        d += timedelta(7)
    return d.date()

  @property
  def startdatetime(self):
    d = self.calculated_date()
    return datetime.combine(d, self.start)

  @property
  def enddatetime(self):
    d = self.calculated_date()
    return datetime.combine(d, self.end)

  @property
  def calculated_weekday(self):
    if self.weekday:
      return self.weekday
    else:
      # get weekday from date
      return self.day.weekday()

  last_modified = models.DateTimeField(auto_now=True)

  # checks for time conflicts between events. Returns True if conflict exists.
  def check_time_conflict(self, service):
    return (self.end >= service.start) and (service.end >= self.start)

  def __unicode__(self):
    try:
      return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


'''
TODO: Need a powerful editor for service worker groups for service schedulers
to categorize trainees as workers based on qualifications/criteria

e.g.
Instance: 3/25/2016 Saturday Dinner Cleanup
 -> workers through assignments (roles)
Service: Cleanup
ServiceSlot: Cleanup star
WorkerGroup: 1st term stars

'''


class ServiceSlot(models.Model):
  name = models.CharField(max_length=100)
  service = models.ForeignKey('Service', null=True, on_delete=models.SET_NULL)
  worker_group = models.ForeignKey('WorkerGroup', null=True, on_delete=models.SET_NULL)
  workers_required = models.PositiveSmallIntegerField(default=1)
  # on a scale of 1-12, with 12 being the most intense (workload
  # is potentially different for different roles depending within same service)
  # Maybe this should be used as service load to count off services instead...
  workload = models.PositiveSmallIntegerField(default=1)
  role = models.CharField(max_length=3, choices=WORKER_ROLE_TYPES, default='wor')
  # Optional gender requirement + qualification requirement
  gender = models.CharField(max_length=1, choices=GENDER, default='E')

  last_modified = models.DateTimeField(auto_now=True)

  def save(self, *args, **kwargs):
    # Check if related service is designated
    # if designated then we auto fill the workers_required to worker_group
    if self.service.designated:
      self.workers_required = self.worker_group.get_workers.count()
    super(ServiceSlot, self).save(*args, **kwargs)

  def __unicode__(self):
    try:
      return '%s, %s : %d x %s:%s (workload: %d)' % (
        self.service, self.worker_group, self.workers_required, self.role, self.gender, self.workload
      )
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    ordering = ['name']


# Stores history of graph json so assign algo doesn't have to be rerun to modify the graph
class GraphJson(models.Model):
  week_schedule = models.ForeignKey('WeekSchedule', related_name='graphs', null=True, on_delete=models.SET_NULL)
  json = models.TextField()

  status = models.CharField(max_length=100)

  date_created = models.DateTimeField(auto_now=True)
