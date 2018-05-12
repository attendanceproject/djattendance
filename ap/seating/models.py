from django.db import models

from terms.models import Term
from accounts.models import Trainee

""" seating/models.py

Chart: contains seats and trainees

Seat: intermediate model between Charts and Trainees M2M relationship

Partial: a subsection of a Chart
"""


class ChartManager(models.Manager):

  def get_queryset(self):
    return super(ChartManager, self).get_queryset().filter(term=Term.current_term())


class ChartAllManager(models.Manager):

  def get_queryset(self):
    return super(ChartAllManager, self).get_queryset()


class Chart(models.Model):
  """ Defines a seating chart, with trainees associated to seats"""
  objects = ChartManager()
  objects_all = ChartAllManager()

  name = models.CharField(max_length=100)
  desc = models.CharField(max_length=255, null=True, blank=True)

  term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True)

  height = models.PositiveSmallIntegerField()
  width = models.PositiveSmallIntegerField()

  trainees = models.ManyToManyField(Trainee, through='Seat')

  def __unicode__(self):
    try:
      return self.term.__unicode__() + ' ' + self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class Seat(models.Model):
  """ Intermediate model to relate a Trainee to a seating Chart """
  trainee = models.ForeignKey(Trainee, null=True, on_delete=models.SET_NULL)
  chart = models.ForeignKey(Chart, on_delete=models.SET_NULL, null=True)

  # coordinates
  x = models.PositiveSmallIntegerField()
  y = models.PositiveSmallIntegerField()

  def __unicode__(self):
    try:
      return "%s in %s @ (%s, %s)" % (self.trainee, self.chart, self.x, self.y )
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class Partial(models.Model):
  """ Defines a subset of a seating chart. Mainly used for entering roll """
  chart = models.ForeignKey(Chart, on_delete=models.SET_NULL, null=True)

  """ Section name eg. A, B... """
  section_name = models.CharField(max_length=5)

  # upper and lower bounds on x and y axis
  x_lower = models.PositiveSmallIntegerField()
  x_upper = models.PositiveSmallIntegerField()
  y_lower = models.PositiveSmallIntegerField()
  y_upper = models.PositiveSmallIntegerField()

  class Meta:
    ordering = ('chart', 'section_name')

  def __unicode__(self):
    try:
      return "%s - Section %s from (%s, %s) to (%s, %s)" % (self.chart, self.section_name, self.x_lower, self.y_lower, self.x_upper, self.y_upper)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
