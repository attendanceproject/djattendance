from django.db import models
from aputils.models import Address
from aputils.utils import sorted_user_list_str

""" HOUSES models.py

This houses module is a utility model that define training housing.

Data Models:
    - House: a training house
    - Room: a room inside a training house (any type)
    - Bunk: a bunk (either lower of upper) in a given house
    - HCSurvey: a survey of the general atmosphere of the given house
    - HCGeneralComment: Each survey has (up to 2) HCGeneralComments
    - HCTraineeComment: Each survey has many HCTraineeComments, 1 per non-hc resident
    - HCRecommendation: HC recommending a resident trainee
"""

class HouseManager(models.Manager):
  # Only works for one-to-one relationships. Currently does not work for other types
  use_for_related_fields = True

  def get_queryset(self):
    return super(HouseManager, self).get_queryset().filter(used=True).order_by('name')

class InactiveHouseManager(models.Manager):
  def get_queryset(self):
    return super(InactiveHouseManager, self).get_queryset().filter(used=False).order_by('name')


class House(models.Model):

  objects = HouseManager()
  inactive = InactiveHouseManager()

  GENDER = (
    ('B', 'Brother'),
    ('S', 'Sister'),
    ('C', 'Couple')
  )

  # the common name for the house, e.g. 1329 Amberwick, 2102 Grace
  name = models.CharField(max_length=50)

  # the house's address (defined in the utils class)
  address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

  # a house can designated for either brothers, sisters, or a couple
  gender = models.CharField(max_length=1, choices=GENDER)

  # whether this house is actively used by the training
  used = models.BooleanField(default=True)

  def residents_list(self):
    return sorted_user_list_str(self.residents.filter(is_active=True))

  def get_hcs(self):
    return sorted_user_list_str(self.residents.filter(groups__name="HC"))

  #returns a query set of the empty bunks for this house
  def empty_bunk_count(self,position_list=[]):
    if len(position_list)==0:
      return Bunk.objects.filter(room__house=self).exclude(trainee__active=True).count()
    return Bunk.objects.filter(room__house=self,position__in=position_list).exclude(trainee__active=True).count()

  def __unicode__(self):
    try:
      return u'%s' % (self.name.strip(' '))
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class Room(models.Model):

  ROOM_TYPES = (
    ('LIV', 'Living Room'),
    ('DIN', 'Dining Room'),
    ('BED1', 'Bedroom A'),
    ('BED2', 'Bedroom B'),
    ('BED3', 'Bedroom C'),
    ('BED4', 'Bedroom D'),
    ('BED5', 'Bedroom E'),
    ('BED6', 'Bedroom F'),
    ('BED7', 'Bedroom G'),
    ('KIT', 'Kitchen'),
    ('BAT1', 'Bathroom A'),
    ('BAT2', 'Bathroom B'),
    ('BAT3', 'Bathroom C'),
    ('GAR', 'Garage'),
    ('PAT', 'Patio'),
    ('LAU', 'Laundry Room'),
    ('STA', 'Stairs'),
    ('HAL1', 'Hallway (downstairs)'),
    ('HAL2', 'Hallway (upstairs)'),
  )

  SIZES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
  )

  type = models.CharField(max_length=4, choices=ROOM_TYPES)

  # optional field for specifying the physical size of the room
  # useful mainly for hospitality/short-term assignments
  size = models.CharField(max_length=1, choices=SIZES, null=True, blank=True)

  # refers to number of beds
  capacity = models.SmallIntegerField(default=0)  # 0 if room is not a bedroom

  house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True)

  floor = models.SmallIntegerField(default=1)

  def __unicode__(self):
    try:
      return self.house.name + " " + self.get_type_display()
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class Bunk(models.Model):

  POSITION = (
    ('B', 'Bottom'),
    ('T', 'Top'),
    ('L', 'Queen-Left'),  # for couples
    ('R', 'Queen-Right'),
    ('S', 'Single')
  )

  LENGTH = (
    ('R', 'Regular'),
    ('L', 'Long')
  )

  FRAME_TYPES = (
    ('M', 'Metal'),
    ('C', 'Cot'),
    ('H', 'Wood Honey'),
    ('W', 'Wood Walnut'),
    ('WC', 'Wood Walnut Crown'),
    ('O', 'Wood Oak'),
    ('LV', 'Wood Light Vintage'),
  )

  # the bunk's number
  number = models.SmallIntegerField()

  # whether this is a top or bottom bunk
  position = models.CharField(max_length=1, choices=POSITION)

  # which bunk this bunk is linked to, if any
  link = models.OneToOneField('Bunk', null=True, blank=True)

  # which room this bunk is in
  room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)

  length = models.CharField(max_length=1, choices=LENGTH, default='R')

  # type of bed frame
  frame = models.CharField(max_length=2, choices=FRAME_TYPES, null=True, blank=True)

  # type of mattress
  mattress = models.CharField(max_length=50, null=True, blank=True)

  # whether bunk has a guardrail
  guardrail = models.NullBooleanField(blank=True)

  # whether bunk has a ladder
  ladder = models.NullBooleanField(blank=True)

  notes = models.TextField(blank=True, null=True)

  def __unicode__(self):
    try:
      return self.room.house.name + " Bunk " + str(self.number)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
