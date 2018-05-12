from django.db import models


from datetime import datetime, timedelta

'''
Service swap -> check qualification mismatch but maybe lax on schedule conflict exception checking
'''


class Assignment(models.Model):
  """
  Defines a relationship between a worker and a service instance
  """

  week_schedule = models.ForeignKey('WeekSchedule', related_name='assignments', blank=True, on_delete=models.SET_NULL, null=True)

  service = models.ForeignKey('Service', related_name='assignments', null=True, on_delete=models.SET_NULL)
  # Get role + workload
  service_slot = models.ForeignKey('ServiceSlot', related_name='assignments', default=None, null=True, on_delete=models.SET_NULL)

  workers = models.ManyToManyField('Worker', related_name="assignments", blank=True)

  @property
  def workers_needed(self):
    return self.service_slot.workers_required - self.workers.count()

  def get_worker_list(self):
    return self.workers.all()

  # boolean determines if assignment made should be pinned, not altered by
  # flow algo, taken out of graph, trainee need services decremented (safest way to do it)
  # Maybe cost of edge 0?
  pin = models.BooleanField(default=False)

  # For AV/Piano, workload would be 0, no effect on services needed
  # For Shuttle, could be 1 as real service
  workload = models.PositiveSmallIntegerField(default=1)

  last_modified = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    try:
      return '%s assignment for %s' % (self.service, self.week_schedule)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  @staticmethod
  def get_assignments_to_worker(worker):
    return Assignment.objects.filter(workers=worker).all()

  def worker_list(self):
    return ', '.join([w.trainee.full_name for w in self.workers.all()])

  @property
  def startdatetime(self):
    start = self.week_schedule.start
    d = start + timedelta(self.service.weekday - 1)
    if self.service.weekday is 0:
      d += timedelta(7)
    return datetime.combine(d, self.service.start)

  @property
  def enddatetime(self):
    start = self.week_schedule.start
    d = start + timedelta(self.service.weekday - 1)
    if self.service.weekday is 0:
      d += timedelta(7)
    return datetime.combine(d, self.service.end)
