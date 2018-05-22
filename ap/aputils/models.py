from django.db import models

from django_countries.fields import CountryField
from django_countries import countries

from localflavor.us.models import USStateField

""" APUTILS models.py

The APUTILS model handles various miscellaneous data models that will be used
widely across other files.

Data Models:
  - Country: A standard country, used in cities.
  - City: A standard city anywhere in the world, used in localities and
  addresses
  - Address: A standard US address used for training residences, emergency
  contact information, and other things
  - Vehicle: Represents vehicles owned by trainees
  - EmergencyInfo: Emergency contact info for a trainee, used in accounts
"""


class City(models.Model):

  # the name of the city
  name = models.CharField(max_length=50)
  # optional for non-US cities
  state = USStateField(null=True, blank=True)
  # Country foreign key
  country = CountryField(default='US')

  ordering = ('country', 'state', 'name', )

  def __unicode__(self):
    try:
      city_str = self.name

      if self.country == 'US':
        city_str = city_str + ", " + str(self.state)
      else:
        city_str = city_str + ", " + str(dict(countries)[self.country])
      return city_str
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    verbose_name_plural = "cities"


class AddressManagerWithCity(models.Manager):
  def get_queryset(self):
    return super(AddressManagerWithCity, self).get_queryset().select_related('city')


class Address(models.Model):

  objects = AddressManagerWithCity()

  # line 1 of the address field
  address1 = models.CharField(max_length=150)

  # line 2 of the address field
  address2 = models.CharField(max_length=150, blank=True)

  # City foreign key
  city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

  zip_code = models.CharField(null=True, blank=True, max_length=30)

  # optional four-digit zip code extension
  zip4 = models.PositiveSmallIntegerField(null=True, blank=True)

  # optional details field
  details = models.CharField(max_length=150, null=True, blank=True)

  def __unicode__(self):
    try:
      return '%s, %s %s' % (
        (self.address1 + ", " + self.address2) if self.address2 else self.address1,
        self.city,
        self.zip_code
      )
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    verbose_name_plural = "addresses"


class HomeAddress(Address):
  trainee = models.ForeignKey('accounts.Trainee', on_delete=models.SET_NULL, null=True)


class Vehicle(models.Model):

  color = models.CharField(max_length=20, blank=True, null=True)

  # e.g. "Honda", "Toyota"
  make = models.CharField(max_length=30, blank=True, null=True)

  # e.g. "Accord", "Camry"
  model = models.CharField(max_length=30, blank=True, null=True)

  year = models.PositiveSmallIntegerField(blank=True, null=True)

  license_plate = models.CharField(max_length=25, blank=True, null=True)

  state = USStateField(blank=True)

  capacity = models.PositiveSmallIntegerField()

  user = models.ForeignKey('accounts.User', related_name='vehicles', blank=True, null=True, on_delete=models.SET_NULL)

  def __unicode__(self):
    try:
      return ('%s %s %s') % (self.color, self.make, self.model)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class EmergencyInfo(models.Model):

  name = models.CharField(max_length=255)

  # contact's relation to the trainee.
  relation = models.CharField(max_length=30)

  phone = models.CharField(max_length=15)

  phone2 = models.CharField(max_length=15, blank=True, null=True)

  address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

  trainee = models.OneToOneField('accounts.Trainee', blank=True, null=True)

  def __unicode__(self):
    try:
      return self.name + '(' + self.relation + ')'
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class QueryFilter(models.Model):
  name = models.CharField(max_length=255)
  description = models.CharField(max_length=255, blank=True, null=True)

  # Dictionary of all filters applied to query
  query = models.TextField()

  def __unicode__(self):
    try:
      return self.name
      # q = eval(self.query)
      # return '%s - %s' % (self.name, '(' + ','.join(['%s=%s' % (k, v) for k, v in q.items()]) + ')')
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
