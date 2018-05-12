from django.db import models

""" ROOMS models.py

The ROOMS app represents rooms that are in the Training Center (TC). This is
used by other apps such as Room Reservation and Maintenance Requests.

Data Models:
    - Building: a building associated with a room
    - Inventory: an inventory of items associated with a room
    - Room: a room
"""

class Building(models.Model):
  name = models.CharField(max_length=3)

class Inventory(models.Model):
  green_chairs = models.IntegerField()
  clocks = models.IntegerField()
  frames = models.IntegerField()
  tissues = models.IntegerField()
  peach_chairs = models.IntegerField()
  tablet_chairs = models.IntegerField()
  computers = models.IntegerField()



class Room(models.Model):

  ROOM_TYPES = (
    ('Cr', 'Classroom'),
    ('FR', 'Fellowship Room'),
    ('SR', 'Study Room'),
    ('CA', 'Common Area'),
    ('Cf', 'Cafeteria'),
  )

  ACCESS_TYPES = (
    ('C', 'Common'),
    ('B', 'Brothers'),
    ('S', 'Sisters'),
    ('R', 'Restricted'),
  )

  BUILDING_CODES = (
    ('TC', 'Training Center'),
    ('MCC', 'Ministry Conference Center'),
  )

  # the room number/code e.g.EPC, W372
  code = models.CharField(max_length=6, primary_key=True)

  # the room's name, e.g. East Side Peach Chairs, or West Third Heavens
  name = models.CharField(max_length=30)

  # which floor of the TC this room is on
  floor = models.SmallIntegerField()

  # not sure if this is needed
  type = models.CharField(max_length=2, choices=ROOM_TYPES, blank=True)

  # the access of this room, e.g. brothers only, sisters only,
  access = models.CharField(max_length=1, choices=ACCESS_TYPES)

  # some rooms are in the system and have schedules, but cannot be reserved
  reservable = models.BooleanField(default=False)

  # building = models.CharField(max_length = 3, choices=BUILDING_CODES, default='TC')

  def __unicode__(self):
    try:
    	return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    ordering = ['name']
