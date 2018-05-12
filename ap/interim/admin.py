# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from interim.models import InterimIntentions, InterimItinerary


class InterimItineraryInline(admin.TabularInline):
  model = InterimItinerary


class InterimIntentionsInline(admin.ModelAdmin):
  inlines = [
    InterimItineraryInline,
  ]


admin.site.register(InterimIntentions, InterimIntentionsInline)
