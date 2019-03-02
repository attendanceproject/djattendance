# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from interim.models import InterimIntentions, InterimItinerary
from terms.models import Term


class InterimItineraryInline(admin.TabularInline):
  model = InterimItinerary


class InterimIntentionsAdminWithInline(admin.ModelAdmin):
  list_display = ('pk', 'trainee', 'intent', 'post_training_intentions')
  list_filter = ('trainee__current_term', 'intent', 'post_training_intentions')
  search_fields = ('pk', 'trainee__firstname', 'trainee__lastname')
  ordering = ('trainee__firstname', )
  inlines = [
    InterimItineraryInline,
  ]

  def get_queryset(self, request):
    qs = super(InterimIntentionsAdminWithInline, self).get_queryset(request)
    if Term.current_term():
      return qs.filter(admin__term=Term.current_term())
    return qs


admin.site.register(InterimIntentions, InterimIntentionsAdminWithInline)
