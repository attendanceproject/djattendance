from django.db import models

from django_countries import countries

from aputils.models import City

""" LOCALITIES models.py

The Localities module is a utility module underlying other apps. In particular,
both trainees are related to localities (as being sent from), and teams are
related to localities (as serving in).

Data Models:
  - Locality: a local church
"""


class Locality(models.Model):

  city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

  def __unicode__(self):
    try:
      city_str = self.city.name
      if self.city.country == 'US':
        city_str = city_str + ", " + str(self.city.state)
      else:
        city_str = city_str + ", " + str(dict(countries)[self.city.country])
      return city_str
      #Changed the unicode function to match that of City.
      #Properly returns city,country for international localities.
      #return self.city.name + ", " + str(self.city.state)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    verbose_name_plural = 'localities'
    ordering = ('city__name', 'city__state')
