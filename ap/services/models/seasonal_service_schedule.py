from django.db import models

""" services models.py

The services model defines both weekly and permanent (designated) services in the

Data Models:
  - Category: This is a broad category that contains specific services. For
  example,Cleanup is a category that contains services such as Tuesday
  Breakfast Cleanup or Saturday Lunch Cleanup. Guard contains Guards A, B, C,
  and D.

  - Service: This refers to a specific service that repeats on a weekly basis.
  I.e. Tuesday Breakfast Prep is a service. It repeats every week. A specific
  instance of that service is defined in the service scheduler module as a
  service Instance.

  - SeasonalServiceSchedule: This is a period in which services are active and generally
  changes with the schedule of the training. Most of the time, the regular
  FTTA schedule will be in effect, but there are exceptions such as Service
  Week and the semiannual training.
"""

class SeasonalServiceSchedule(models.Model):
  """
  Defines a service period such as Pre-Training, FTTA regular week, etc.
  """

  name = models.CharField(max_length=200)
  description = models.TextField(blank=True, null=True)
  active = models.BooleanField(default=True)

  def __unicode__(self):
    try:
      return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
