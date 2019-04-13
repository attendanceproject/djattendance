# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import (Answer, AnswerChoice, GospelTrip, NonTrainee, Question,
                     Section)


class AnswerAdmin(admin.ModelAdmin):
  list_display = ('pk', 'trainee', 'question')
  list_filter = ('gospel_trip', 'trainee', 'question')
  ordering = ('gospel_trip', 'question')
  search_fields = ('pk', 'trainee__firstname', 'trainee__lastname', 'gospel_trip__name', 'question__section__name')


admin.site.register(GospelTrip)
admin.site.register(Section)
admin.site.register(Question)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerChoice)
admin.site.register(NonTrainee)
