# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from accounts.models import Trainee
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from terms.models import Term
from semi.utils import REQUEST_STATUS
from aputils.utils import RequestMixin


def default_attendance():
  return {"tuesday": "", "wednesday": "", "thursday": "", "friday": "", "saturday": ""}


class SemiAnnual(models.Model, RequestMixin):

  trainee = models.ForeignKey(Trainee)

  term = models.ForeignKey(Term)

  attendance = JSONField(default=default_attendance())

  location = models.CharField(max_length=5, default='TC')

  other_location = models.CharField(max_length=200, blank=True)

  request_comments = models.TextField(max_length=1000, blank=True, null=True)

  ta_comments = models.TextField(max_length=500, blank=True, null=True)

  status = models.CharField(max_length=1, default='P', choices=REQUEST_STATUS)

  class Meta:
    unique_together = ('trainee', 'term')

  def get_location_url(self):
    return reverse('semi:location', kwargs={'pk': self.id})

  def get_trainee_requester(self):
    return self.trainee
