from datetime import datetime, time, date, timedelta
from pytz import timezone
import pytz

from django.db import models
from django.contrib.postgres.fields import HStoreField

from accounts.models import User, Trainee
from classes.models import Class
from schedules.models import Event


class Classnotes(models.Model):

  class Meta:
    ordering = ['-date_assigned']
    verbose_name = 'class notes'
    verbose_name_plural = 'class notes'

  CN_STATUS = (
    ('A', 'Approved'),
    ('P', 'Pending'),
    ('F', 'Marked for Fellowship'),
    ('U', 'Unsubmitted'),
  )

  CN_TYPE = (
    ('R', 'Regular'),
    ('S', 'Special')
  )

  # the date of the class doing the class notes for
  date = models.DateField(blank=True, null=True)
  comments = models.TextField(blank=True, null=True)
  # content of class note
  content = models.TextField(blank=True, null=True)

  date_assigned = models.DateTimeField(auto_now_add=True)
  date_due = models.DateTimeField(editable=False)
  date_submitted = models.DateTimeField(blank=True, null=True)

  event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.SET_NULL)

  # minWord Count
  minimum_words = models.PositiveSmallIntegerField(default=250)
  submitting_paper_copy = models.BooleanField(default=False)

  status = models.CharField(max_length=1, choices=CN_STATUS, default='U')
  type = models.CharField(max_length=1, choices=CN_TYPE, default='R')
  trainee = models.ForeignKey(Trainee, related_name='%(class)ss', on_delete=models.SET_NULL, null=True)

  def add_comments(self, comments):
    self.comments = comments
    self.save()
    return self

  def approved(self):
    return self.status == 'A'

  def pending(self):
    return self.status == 'P'

  def fellowship(self):
    return self.status == 'F'

  def unsubmitted(self):
    return self.status == 'U'

  def approve(self):
    self.status = 'A'
    self.save()
    return self

  def unapprove(self):
    self.status = 'P'
    self.save()
    return self

  def set_fellowship(self):
    self.status = 'F'
    self.save()
    return self

  def remove_fellowship(self):
    self.status = 'P'
    self.save()
    return self

  @property
  def due_in(self):
    today = date.today()
    due = datetime.date(self.date_due)
    # return (self.date_due - today).days
    delta = due - today
    return delta.days

  @property
  def past_due(self):
    return self.due_in < 0

  def clean(self, *args, **kwargs):
    """Custom validator for word count"""
    wc_list = self.content.split()
    # if len(wc_list) < self.minimum_words and self.submitting_paper_copy is False:
    #     raise ValidationError("Your word count is less than {count}".format(count=self.minimum_words))
    super(Classnotes, self).clean(*args, **kwargs)

  def save(self, **kwargs):
    """ Class notes are due 10 days after assigned """

    # only add days if it's the first time the model is saved
    if not self.id:
      d = timedelta(days=10)
      self.date_due = datetime.now() + d
    self.full_clean()
    super(Classnotes, self).save()

  def next(self):
    return Classnotes.objects.filter(date_submitted__gt=self.date_submitted, trainee=self.trainee).order_by('date_submitted').first()

  def prev(self):
    return Classnotes.objects.filter(date_submitted__lt=self.date_submitted, trainee=self.trainee).order_by('-date_submitted').first()

  def __unicode__(self):
    try:
      return "{name}'s class note for {classname} assigned on {date_assigned} Status: {status}".format(
          name=self.trainee.full_name,
          classname=self.event.name,
          date_assigned=timezone('US/Pacific').localize(self.date_assigned),
          status=self.status,
      )
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
