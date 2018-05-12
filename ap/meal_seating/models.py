from django.db import models
from accounts.models import User, Trainee

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

  @staticmethod
  def seatinglist(genderlist, gender):
    tables = Table.objects.filter(gender = gender)
    traineenum = 0
    tablenum = 0
    totalcapacity = 0
    meal_list = []
    for x in Table.objects.all().filter(gender = gender).values("capacity"):
      totalcapacity += x["capacity"]
    if (len(genderlist) > totalcapacity):
      print "cannot seat " , len(genderlist) , " trainees. Current capacity is: " , totalcapacity
      return None
    else:
      for trainee in genderlist:
        meal_seating = {}
        if ( traineenum == tables[tablenum].capacity):
          tablenum += 1
          traineenum = 0
        meal_seating["first_name"] = trainee.firstname
        meal_seating["last_name"] = trainee.lastname
        meal_seating["table"] = tables[tablenum]
        meal_list.append(meal_seating)
        traineenum += 1
      return meal_list

class TraineeExclusion(models.Model):
  trainee = models.IntegerField()
