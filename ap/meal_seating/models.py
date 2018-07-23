from django.db import models

""" meal_seating models.py

This module prints the bi-weekly meal seating list for the FTTA and FTTMA
brothers and sisters, and also for short-termers.
"""


class Table(models.Model):

  name = models.CharField(max_length=10)
  capacity = models.IntegerField(null=True)
  LOCATIONS = (
    ('W', 'West Cafeteria'),
    ('M', 'Main Cafeteria'),
    ('S', 'South Cafeteria'),
    ('SE', 'Southeast Cafeteria'),
  )
  GENDERS = (
    ('B', 'Brother'),
    ('S', 'Sister'),
  )

  location = models.CharField(max_length=2, choices=LOCATIONS, default='M')
  gender = models.CharField(max_length=1, choices=GENDERS)

  def getCapacity(self):
    return self.capacity

  def __unicode__(self):
    try:
      return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class TraineeExclusion(models.Model):
  trainee = models.IntegerField()
