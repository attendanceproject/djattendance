# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from accounts.models import User

# Create your models here.
class Conversation(models.Model):
  ## Add a field that indicates which object it is linked to
  participants = models.ManyToManyField(User, null=True, blank=True)
  
class Message(models.Model):
  conversation = models.ForeignKey(GospelPair, blank=True, null=True, on_delete=models.CASCADE)
  sent_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
  read_by = models.ManyToManyField(User, null=True, blank=True)
  text = models.TextField(null=True, blank=True)
  time_sent = models.DateTimeField(auto_now_add=True)
