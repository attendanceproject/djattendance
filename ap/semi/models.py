# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from accounts.models import Trainee
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from terms.models import Term


def default_attendance():
  return {"tuesday": "N", "wednesday": "N", "thursday": "N", "friday": "N", "saturday": "N"}


class SemiAnnual(models.Model):

  trainee = models.ForeignKey(Trainee)

  term = models.ForeignKey(Term)

  attendance = JSONField(default=default_attendance())

  location = models.CharField(max_length=5, default='TC')

  comments = models.CharField(max_length=200, blank=True)

  class Meta:
    unique_together = ('trainee', 'term')

  def get_location_url(self):
    return reverse('semi:location', kwargs={'pk': self.id})
