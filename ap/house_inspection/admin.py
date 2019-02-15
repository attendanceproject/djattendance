# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Inspectors

# Register your models here.

class InspectorsAdmin(admin.ModelAdmin):
	list_display = ('last_name', 'first_name')
	search_fields = ('last_name', 'first_name')
	list_per_page = 25
admin.site.register(Inspectors, InspectorsAdmin)