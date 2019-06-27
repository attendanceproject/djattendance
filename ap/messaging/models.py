# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from accounts.models import User

# Create your models here.
class Message(models.Model):
  text = models.TextField(null=True, blank=True)
  author = models.ForeignKey(User, null=True, blank=True, related_name='wrote')
  read = models.ManyToManyField(User, null=True, blank=True, related_name='read')

class Conversation(models.Model):
  participants = models.ManyToManyField(User, null=True, blank=True)
  messages = models.ManyToManyField(Message, null=True, blank=True)

