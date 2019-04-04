# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class MessagingView(TemplateView):
  template_name = "messaging/inbox.html"

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    ctx = super(MessagingView, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Inbox'
    return ctx
