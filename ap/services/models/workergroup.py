from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from accounts.models import Trainee
from services.models import Worker, WeekSchedule
from services.models import Qualification
import services
import json

from aputils.queryfilter import QueryFilterService

from django.db.models import Prefetch

from django.utils.functional import cached_property

'''
WorkerGroup inherits from django Group so service

designated service
 - permission
regular service
general groups
seasonal groups

View functions:
1st term worker group
sisters worker group

group -> run when add a trainee
validator/updater for workergroups

generic worker groups -> auto-generated

Service Worker Group Trainee Filter Picklist

'''


'''
Will either be a filter workergroup or manual workergroup

WorkerGroup can created via:

 - filter
  - http://ap.ftta.lan/api/trainees/term/2/?format=json&terms%5B%5D=2&terms%5B%5D=3&hc=false

 - manual assignment
 - doodle

Assignments may be
 - static
 - rotational
 - weekly manual assignment


Inherits from Group:
 - name          Required. 80 characters or fewer. Any characters are permitted. Example: 'Awesome Users'.
 - permissions   Many-to-many field to Permission:



?? TODO: make workgroup have types, (e.g. designated)

IMPORTANT!!!: For the sake of performance, make sure to make very few
workergroups that are shared among many services (no duplicates!),
b/c it's very expensive to fetch users from db using query

Using explicit worker definition is way faster (optimization-wise) than filters as they can be fetched in bulk in the beginning

'''
class WorkerGroup(models.Model):

  # Optional query_filter object. Only this filter or workers
  # manual assignments allowed at a time
  name = models.CharField(max_length=255)
  query_filters = models.TextField(blank=True, null=True)

  description = models.TextField(blank=True, null=True)

  active = models.BooleanField(default=True)

  workers = models.ManyToManyField(
    'Worker', related_name="workergroups", blank=True)

  # Algorithm will assign higher priority first
  assign_priority = models.PositiveSmallIntegerField(default=1)
  permission_groups = models.ManyToManyField(Group, related_name='service_group', blank=True)
  last_modified = models.DateTimeField(auto_now=True)

  @cached_property
  def get_workers(self):
    if not self.active:
      return Worker.objects.none()
    if not self.query_filters:
      # then it's a manual list of workers
      workers = self.workers
    else:
      workers = Worker.objects
      # Chain all the filters together to get the composite filter
      for name in self.query_filters.split(','):
        workers = workers.filter(QueryFilterService.get_query(name))
      # Return filtered result
      # return workers
    # Only return workers with nozero service cap
    return workers.filter(services_cap__gt=0).select_related('trainee')\
        .prefetch_related(Prefetch('assignments', queryset=services.models.Assignment.objects.order_by('week_schedule__start')),
                          'assignments__service', 'assignments__service_slot')

  def get_workers_prefetch_assignments(self, cws):
    pinned = services.models.Assignment.objects.filter(week_schedule=cws, pin=True)
    pinnedPrefetch = Prefetch(
        'assignments',
        queryset=pinned,
        to_attr='pinned_assignments'
    )
    return self.get_workers.prefetch_related(pinnedPrefetch)\
        .prefetch_related('assignments')\
        .prefetch_related(
            'assignments__service',
            'assignments__week_schedule'
    )

  def get_worker_ids(self):
    if not self.active:
      return []
    if not self.query_filters:
      # then it's a manual list of workers
      workers = self.workers
    else:
      workers = Worker.objects
      # Chain all the filters together to get the composite filter
      for name in self.query_filters.split(','):
        workers = workers.filter(QueryFilterService.get_query(name))
      # Return filtered result
      # return workers
    # Only return workers with nozero service cap
    cws = WeekSchedule.latest_week_schedule
    return workers.filter(services_cap__gt=0).values('id')


  @cached_property
  def get_workers_set(self):
    if not hasattr(self, '_worker_set'):
        self._worker_set = set(self.get_workers)

    return self._worker_set

  def get_worker_list(self):
    workers = self.get_workers
    return ', '.join([w.trainee.full_name for w in workers])

  def __unicode__(self):
    try:
      return "%s (%s)" % (self.name, self.description)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


# method for updating
@receiver(post_save, sender=Qualification)
def add_query_filter(sender, instance, **kwargs):
  QueryFilterService.addQ(instance.name, worker__qualifications__name=instance.name)