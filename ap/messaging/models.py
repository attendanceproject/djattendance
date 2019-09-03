# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from accounts.models import User

class Message(models.Model):
  text = models.TextField(null=True, blank=True)
  sent_by = models.ForeignKey(User, null=True, blank=True, related_name='sent')
  read_by = models.ManyToManyField(User, null=True, blank=True, related_name='read')
  time_sent = models.DateTimeField(editable=False)

  def save(self, *args, **kwargs):
    if not self.id:
      self.time_sent = timezone.now()
    return super(User, self).save(*args, **kwargs)

#Conversation is composed of multiple Message instances
class Conversation(models.Model):
  participants = models.ManyToManyField(User, null=True, blank=True)
  messages = models.ManyToManyField(Message, null=True, blank=True)
  time_created = models.DateTimeField(editable=False)

  def save(self, *args, **kwargs):
    if not self.id:
      self.time_created = timezone.now()
    return super(User, self).save(*args, **kwargs)
