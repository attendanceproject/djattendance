# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from announcements.notifications import get_announcements, get_popups

from .models import Conversation

class MessagingView(TemplateView):
  template_name = "messaging/inbox.html"

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    ctx = super(MessagingView, self).get_context_data(**kwargs)
    ctx['page_title'] = 'View Read Notifications'
    notifications = get_announcements(self.request)
    for notification in notifications:
      tag, content = notification
      messages.add_message(self.request, tag, content)
    ctx['popups'] = get_popups(self.request)
    return ctx
