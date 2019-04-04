# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from accounts.models import User

# Create your models here.
class Conversation(models.Model):
  participants = models.ManyToManyField(User, null=True, blank=True)
