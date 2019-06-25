from django.contrib import admin

from aputils.admin_utils import FilteredSelectMixin
from accounts.models import Trainee

from .models import Event, Schedule
from .forms import EventForm, BaseScheduleForm


class EventAdmin(FilteredSelectMixin, admin.ModelAdmin):
  form = EventForm
  search_fields = ['pk', 'name', 'description', 'code', 'start', 'end']
  list_filter = ('code', 'type', 'class_type', 'monitor', 'weekday', 'chart')
  registered_filtered_select = [('schedules', Schedule), ]
  save_as = True
  list_display = ("pk", "name", "code", "description", "type", "start", "end", "day", "weekday", "chart")


# Works without mixin b/c relationship is explicitly defined
class ScheduleAdmin(admin.ModelAdmin):
  form = BaseScheduleForm
  save_as = True
  list_display = ("pk", "name", "comments", "priority", "term", "season", "weeks", "is_deleted")
  registered_filtered_select = [('trainees', Trainee), ('events', Event)]
  search_fields = ["pk", "name", "comments"]


admin.site.register(Event, EventAdmin)
admin.site.register(Schedule, ScheduleAdmin)
