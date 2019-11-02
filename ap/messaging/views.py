# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from announcements.notifications import get_announcements, get_popups

from .models import Conversation
from accounts.models import User
from announcements.models import Announcement
from terms.models import Term

# All announcements page
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

    # Specify to only display the announcements pertaining to current user and term
    anns = Announcement.objects.filter(trainees_read=current_user, announcement_date__gte=Term.current_term().start, announcement_date__lte=datetime.today(), type='SERVE')
    anns_dict = dict()
    for i in anns:
      if i.announcement_date in anns_dict:
        anns_dict[i.announcement_date]=anns_dict[i.announcement_date]+[i.announcement]
      else:
        anns_dict[i.announcement_date]=[i.announcement]
    ctx['anns']=sorted(anns_dict.iteritems(), reverse=True)
    print ctx['anns']
    

    return ctx
