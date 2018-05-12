import random
from datetime import date

from django.db import models

from accounts.models import User

""" dailybread models.py

This module displays a daily excerpt from the Word or the ministry every day.
It also allow users to submit portions.
"""


class Portion(models.Model):

  title = models.CharField(max_length=255)
  text = models.TextField()
  ref = models.CharField(max_length=255)
  submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  timestamp = models.TimeField(auto_now_add=True)
  approved = models.BooleanField(default=False)

  def get_absolute_url(self):
    return "/dailybread/%i/" % self.id

  @staticmethod
  def today():
    """ returns random daily portion for each day """
    portions = Portion.objects.filter(approved=True).values_list('id', flat=True)
    random.seed(date.today())
    try:
      return Portion.objects.get(id=random.choice(portions))
    except:
      return Portion()  # if it fails, return an empty Portion

  def __unicode__(self):
    try:
      return self.title
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
