from .models import XBApplication
from django.contrib import admin


class XBApplicationAdmin(admin.ModelAdmin):
  search_fields = ['trainee__firstname', 'trainee__lastname', 'pk']  # to search up trainees


admin.site.register(XBApplication, XBApplicationAdmin)
