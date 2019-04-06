from django import forms
from django.contrib import admin
from .models import Class, ClassFile
from schedules.models import Schedule

from aputils.admin_utils import FilteredSelectMixin


class ClassForm(forms.ModelForm):
  schedules = forms.ModelMultipleChoiceField(
      label='Schedules',
      queryset=Schedule.objects.all(),
      required=False,
      widget=admin.widgets.FilteredSelectMultiple("schedules", is_stacked=False),
  )

  class Meta:
    model = Class
    fields = '__all__'


class ClassAdmin(FilteredSelectMixin, admin.ModelAdmin):
  exclude = ['type']
  form = ClassForm
  registered_filtered_select = [('schedules', Schedule), ]
  save_as = True
  list_display = ("name", "code", "description", "type", "start", "end", "day", "weekday", "chart", "av_code")
  search_fields = ('name', 'code', 'description', 'type', 'weekday', 'av_code')

  # Automatically type class event objects saved.
  def save_model(self, request, obj, form, change):
    obj.type = 'C'
    obj.save()


class ClassFileAdmin(admin.ModelAdmin):
  list_display = ('label', 'for_class', 'file')
  list_filter = ('label', 'for_class', 'file')
  search_fields = ('label', 'for_class', 'file')

  class Meta:
    model = ClassFile
    fields = '__all__'


admin.site.register(Class, ClassAdmin)
admin.site.register(ClassFile, ClassFileAdmin)
