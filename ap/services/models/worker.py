from collections import Counter

from django.db import models
from django.db.models import Sum, Q
from django.utils.functional import cached_property

from week_schedule import WeekSchedule
from terms.models import Term


""" Service models.py

Data Models:
  - Worker: a service worker who can fill a role on a service (e.g. trainee, short-termer, LSM hosp.)
  - WorkerGroup: a group of service workers (which can be defined by the service schedulers)

Related Models:
  - services.Service: a weekly service recurring one per week
  - services.Category: a way to group services of similar types together (e.g. Restroom cleaning)
  - services.Period: refers to time of year this service is active (e.g. semiannual, service week, FTTA)

Abbreviations:
  sv = service
  inst = instance
"""


class Qualification(models.Model):
  """
  Defines an eligibility for workers to certain services.
  """
  name = models.CharField(max_length=100)
  desc = models.CharField(max_length=255)

  def __unicode__(self):
    try:
      return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class WorkerManager(models.Manager):
  def get_queryset(self, *args, **kwargs):
    return super(WorkerManager, self).get_queryset(*args, **kwargs).filter(trainee__is_active=True).select_related('trainee')


# Has exceptions
class Worker(models.Model):

  objects = WorkerManager()

  # Field put here so if trainee deleted will auto-delete worker model
  trainee = models.OneToOneField('accounts.Trainee')
  qualifications = models.ManyToManyField('Qualification', blank=True, related_name='workers')
  designated = models.ManyToManyField('Service', related_name='designated_workers', blank=True)  # Still needed?

  services_eligible = models.ManyToManyField('Service', related_name='workers_eligible', blank=True)

  # level from 0 to 10, 10 is healthy, 0 is dying
  health = models.PositiveIntegerField(default=10)

  services_cap = models.PositiveSmallIntegerField(default=3)

  # workload = models.PositiveIntegerField(default=3)  #history object
  # weeks = models.PositiveSmallIntegerField(default=1, blank=True, null=True)  #??? what does this do?

  last_modified = models.DateTimeField(auto_now=True)

  @property
  def full_name(self):
    return self.trainee.full_name

  # TODO: Add in service_history, id of all prev services?,
  @property
  def service_history(self):  # TODO: filter by term
    # returns dictionary
    return self.assignments.all().order_by('week_schedule__id', 'service__weekday', 'service__name').values('week_schedule__id', 'service__name', 'service__weekday', 'service__designated')

  # dictionary of all the types and freq
  @property
  def weighted_service_frequency(self):
    # cache results
    if not hasattr(self, '_service_freq'):
      self._services_freq = Counter()
      current_term = Term.current_term()
      for a in self.assignments.all():
        if a.week_schedule.start >= current_term.start:
          self._services_freq[a.service.category] += a.week_schedule.week / 10.0
    return self._services_freq

  # This is very inefficient. ...
  @property
  def services_count(self):
    # cache results
    if not hasattr(self, '_services_count'):
      cws = WeekSchedule.current_week_schedule()
      week_start, week_end = cws.week_range
      assignments_count = self.assignments.filter(week_schedule=cws).aggregate(Sum('workload')).get('workload__sum') if cws else 0
      exceptions_count = self.exceptions.filter(active=True, start__lte=week_start)\
          .filter(Q(end__isnull=True) | Q(end__gte=week_end))\
          .filter(Q(schedule=None) | Q(schedule__active=True))\
          .distinct().aggregate(Sum('workload')).get('workload__sum')
      self._services_count = (assignments_count or 0) + (exceptions_count or 0)
    return self._services_count

  @cached_property
  def services_needed(self):
    '''
      Calculates services needed for worker for current week_schedule
    '''
    return self.services_cap - self.services_count

  @property
  def avg_workload(self):
    return self.workload / float(self.weeks)

  @property
  def services_exempted(self):
    # TODO: support events in the future
    exemptions = set()
    for exception in self.exceptions:
      exemptions.add(exception.services.all())
    return exemptions

  def __unicode__(self):
    try:
      return self.trainee.full_name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    ordering = ['trainee__firstname', 'trainee__lastname']
