from django.contrib import admin
from django.conf.urls import url
from django.contrib.admin import SimpleListFilter
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms

from services.models import (
    Worker,
    Category,
    Service,
    SeasonalServiceSchedule,
    WeekSchedule,
    Qualification,
    WorkerGroup,
    Assignment,
    Trainee,
    ServiceSlot,
    ServiceException,
)

from aputils.admin_utils import FilteredSelectMixin
from aputils.widgets import MultipleSelectFullCalendar
from aputils.queryfilter import QueryFilterService
from aputils.custom_fields import CSIMultipleChoiceField


# This is written to improve query performance on admin backend
class WorkerPrejoinMixin(forms.ModelForm):
  workers = forms.ModelMultipleChoiceField(
      label='Workers',
      queryset=Worker.objects.select_related('trainee').all(),
      required=False,
      widget=admin.widgets.FilteredSelectMultiple('workers', is_stacked=False)
  )


class ReadonlyException(object):
  def name(self, instance):
      return instance.exception.name

  def start(self, instance):
    return instance.exception.start

  def end(self, instance):
    return instance.exception.end

  def active(self, instance):
    return instance.exception.active

  def workload(self, instance):
    return instance.exception.workload

  def workers(self, instance):
    return instance.exception.get_worker_list()


class WorkerExceptionInline(ReadonlyException, admin.TabularInline):
  model = ServiceException.workers.through
  # fields = ['exception__name']
  readonly_fields = ['name', 'start', 'end', 'active', 'workers']
  extra = 1

  suit_classes = 'suit-tab suit-tab-exception'


class WorkerAdmin(admin.ModelAdmin):
  inlines = [
      WorkerExceptionInline,
  ]
  list_display = ('trainee', 'health', 'services_cap')
  # list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
  ordering = ('trainee__firstname',)
  search_fields = ['trainee__email', 'trainee__firstname', 'trainee__lastname']
  list_filter = ('trainee__gender', 'trainee__current_term', 'trainee__team', 'trainee__house', 'health', 'services_cap')
  filter_horizontal = ('designated', 'services_eligible', 'qualifications')
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  fieldsets = (
      (None, {
          'classes': ('suit-tab', 'suit-tab-worker',),
          'fields': ('trainee', 'health', 'services_cap', 'qualifications', 'designated', 'services_eligible')
      }),
  )

  suit_form_tabs = (
      ('worker', 'General'),
      ('exception', 'Service Exceptions'),
  )

  def get_urls(self):
    urls = super(WorkerAdmin, self).get_urls()
    my_urls = [
        url(r'^import_trainees/$', self.import_trainees)
    ]
    return my_urls + urls

  def import_trainees(self, request):
    from django.http import HttpResponseRedirect
    # Deletes all worker instances of inactive trainees
    Worker.objects.filter(trainee__is_active=False).delete()
    # Gets all active trainees and check if any do not have worker affiliation, if not, create one
    ts = Trainee.objects.filter(worker__isnull=True, is_active=True)
    ws = []
    for t in ts:
      ws.append(Worker(trainee=t))

    Worker.objects.bulk_create(ws)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  class Meta:
    model = Worker
    fields = '__all__'


class SeasonalServiceScheduleForm(forms.ModelForm):
  services = forms.ModelMultipleChoiceField(
      label='Services',
      queryset=Service.objects.all(),
      required=False,
      widget=admin.widgets.FilteredSelectMultiple('services', is_stacked=False)
  )

  class Meta:
    model = SeasonalServiceSchedule
    exclude = []
    widgets = {
        'services': admin.widgets.FilteredSelectMultiple('services', is_stacked=False),
    }


class SeasonalServiceScheduleAdmin(FilteredSelectMixin, admin.ModelAdmin):
  form = SeasonalServiceScheduleForm
  registered_filtered_select = [('services', Service), ]

  list_display = ('name', 'description', 'active')
  ordering = ('name', 'active')
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  class Meta:
    model = SeasonalServiceSchedule
    fields = '__all__'


class WorkerGroupInline(admin.StackedInline):
  model = Service.worker_groups.through
  fields = ['name', 'gender', 'workers_required', 'workload', 'role', 'worker_group']
  extra = 1

  def worker_group(self, instance):
    return instance.worker_group.name
  worker_group.short_description = 'worker group'

  suit_classes = 'suit-tab suit-tab-workergroup'


class ServiceSlotAdmin(admin.ModelAdmin):
  list_display = ('service', 'worker_group', 'workers_required', 'role')
  list_filter = ('service', 'worker_group', 'service__category')
  ordering = ('service', 'worker_group',)
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  class Meta:
    model = Worker
    fields = '__all__'


class ServiceExceptionInline(ReadonlyException, admin.TabularInline):
  model = ServiceException.services.through
  # fields = ['exception__name']
  readonly_fields = ['name', 'start', 'end', 'active', 'workers']

  extra = 1
  suit_classes = 'suit-tab suit-tab-exception'


class ServiceInline(admin.StackedInline):
  model = Service
  fk_name = 'category'
  extra = 1


class CategoryAdmin(admin.ModelAdmin):

  list_display = ('name', 'description')
  ordering = ('name',)
  inlines = [ServiceInline, ]
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  class Meta:
    model = Category
    fields = '__all__'


class DesignatedServiceExceptionInline(ReadonlyException, admin.TabularInline):
  model = ServiceException
  fk_name = 'service'
  extra = 1

  suit_classes = 'suit-tab suit-tab-serviceexception'

  readonly_fields = ['name', 'start', 'end', 'active', 'workload', 'workers']

  exclude = ['tag', 'desc', 'services', 'schedule', ]


class ServiceAdmin(admin.ModelAdmin):
  inlines = [
      WorkerGroupInline,
      ServiceExceptionInline,
      DesignatedServiceExceptionInline,
      # ExceptionInline,
  ]

  # def get_queryset(self, request):
  #   service = super(ServiceAdmin, self).get_queryset(request)
  #   service = service.prefetch_related('service_exceptions', 'service_exceptions__workers', 'service_exceptions__workers__trainee')
  #   return service

  list_display = ('name', 'code', 'category', 'active', 'weekday', 'start', 'end', 'day')
  exclude = ('exceptions', )
  filter_horizontal = ('schedule', )
  list_filter = ('schedule', 'category', 'active', 'designated', 'weekday')
  # Allows django admin to duplicate record
  # save_as = True

  fieldsets = (
      (None, {
          'classes': ('suit-tab', 'suit-tab-service',),
          'fields': ('name', 'code', 'category', 'schedule',
                     'active', 'designated', 'weekday', 'start',
                     'end', 'day'
                     )
      }),
  )

  suit_form_tabs = (('service', 'General'),
                    ('workergroup', 'Worker Slots'),
                    ('exception', 'Exceptions from this service'),
                    ('serviceexception', 'Service-Related Exceptions'),
                    )

  class Meta:
    model = Service
    fields = '__all__'


class AssignmentAdminForm(WorkerPrejoinMixin, forms.ModelForm):
  class Meta:
    model = Assignment
    fields = '__all__'


class AssignmentAdmin(admin.ModelAdmin):
  form = AssignmentAdminForm
  list_display = ('id', 'week_schedule', 'service', 'service_slot', 'worker_list', 'workers_needed', 'pin')
  ordering = ('week_schedule', 'service')
  list_filter = ('week_schedule', 'service', 'service_slot', 'pin')
  save_as = True

  # def get_queryset(self, request):
  #   assignment = super(AssignmentAdmin, self).get_queryset(request)
  #   assignment = assignment.select_related('week_schedule', 'service', 'service_slot').prefetch_related('workers')
  #   return assignment

  class Meta:
    model = Assignment
    fields = '__all__'


class WorkGroupAdminForm(WorkerPrejoinMixin, forms.ModelForm):
  query_filters = CSIMultipleChoiceField(choices=QueryFilterService.get_choices(), required=False, label='Filters')

  class Meta:
    model = WorkerGroup
    fields = '__all__'


class WorkerGroupAdmin(admin.ModelAdmin):
  form = WorkGroupAdminForm
  list_display = ('name', 'description', 'active', 'worker_count')
  ordering = ('active', 'name')
  exclude = ('permissions',)
  readonly_fields = ['worker_count', 'get_worker_list']
  search_fields = ['name', 'description']
  list_filter = ('active', )
  # Allows django admin to duplicate record
  # save_as = True

  fieldsets = (
      (None, {
          'classes': ('suit-tab', 'suit-tab-general',),
          'fields': ('name', 'description', 'active', 'assign_priority', 'query_filters', 'workers')
      }),
      ('Preview', {
          'classes': ('suit-tab', 'suit-tab-preview',),
          'fields': ('worker_count', 'get_worker_list',)
      }),
  )

  suit_form_tabs = (('general', 'General'),
                    ('preview', 'Filter Preview'),)

  def worker_count(self, obj):
    return obj.get_workers.count()

  def get_worker_list(self, obj):
    return obj.get_worker_list()
  get_worker_list.short_description = "Trainees after Applying Filter"

  class Meta:
    model = WorkerGroup
    fields = '__all__'


# method for updating
@receiver(post_save, sender=Qualification)
def add_query_filter(sender, instance, **kwargs):
  QueryFilterService.addQ(instance.name, worker__qualifications__name=instance.name)

class ExceptionAdminForm(WorkerPrejoinMixin, forms.ModelForm):

  class Meta:
    model = ServiceException
    fields = '__all__'
    widgets = {
        'services': MultipleSelectFullCalendar(Service.objects.all(), 'services'),
    }


class ExceptionAdmin(admin.ModelAdmin):
  form = ExceptionAdminForm
  list_display = ('name', 'tag', 'desc', 'start', 'end', 'active')
  ordering = ('active', 'name')

  # filter_horizontal = ('workers', 'services')
  search_fields = ('name', 'desc',)
  list_filter = ('active', 'tag', 'start', 'end')
  # inlines = [
  #   ServiceInline,
  # ]

  # exclude = ('services',)

  class Meta:
    model = ServiceException
    fields = '__all__'


class QualificationForm(WorkerPrejoinMixin, forms.ModelForm):

  class Meta:
    model = Qualification
    exclude = []
    widgets = {
        'workers': admin.widgets.FilteredSelectMultiple('workers', is_stacked=False),
    }


class QualificationAdmin(FilteredSelectMixin, admin.ModelAdmin):
  form = QualificationForm
  registered_filtered_select = [('workers', Worker), ]
  # inlines = [

  # ]
  list_display = ('name', 'desc')
  ordering = ('name',)

  class Meta:
    model = Qualification
    fields = '__all__'


# class WorkerGroupInline(admin.StackedInline):
#     model = Service.worker_groups.through
#     fields = ['name', 'workers_required', 'workload', 'role', 'worker_group']
#     extra = 1
#     def worker_group(self, instance):
#         return instance.worker_group.name
#     worker_group.short_description = 'worker group'

#     suit_classes = 'suit-tab suit-tab-workergroup'


class CurrentSchedulerListFilter(SimpleListFilter):
  title = 'Scheduler'
  parameter_name = 'Scheduler'

  def lookups(self, request, model_admin):
    CHOICES = ()
    ss = Trainee.objects.filter(groups__name='service_schedulers')

    for s in ss:
      CHOICES += ((s.id, s.full_name),)

    return CHOICES

  def queryset(self, request, queryset):
    print 'chose!!!', self.value()
    print 'queryset', queryset.filter(scheduler__id=self.value())
    if self.value():
      return queryset.filter(scheduler__id=self.value())
    else:
      return queryset


class WeekScheduleAdmin(admin.ModelAdmin):
  list_display = ('start', 'scheduler', 'description', 'workload_margin', 'avg_workload', 'workload_ceiling')
  # list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
  ordering = ('-start',)
  search_fields = ['start', 'description']
  list_filter = (CurrentSchedulerListFilter,)
  # filter_horizontal = ('designated', 'services_eligible', 'qualifications')
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "scheduler":
            kwargs["queryset"] = Trainee.objects.filter(groups__name='service_schedulers')
        return super(WeekScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

  class Meta:
    model = WeekSchedule
    fields = '__all__'

# from seasonal_service_schedule import *
# from service import *
# from worker import *
# from workergroup import *
# from exception import *
# from assignment import *
# from week_schedule import *


admin.site.register(SeasonalServiceSchedule, SeasonalServiceScheduleAdmin)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceSlot, ServiceSlotAdmin)

admin.site.register(Qualification, QualificationAdmin)
admin.site.register(Worker, WorkerAdmin)

# admin.site.register(Worker, WorkerAdmin2)

admin.site.register(WorkerGroup, WorkerGroupAdmin)

admin.site.register(ServiceException, ExceptionAdmin)

admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(WeekSchedule, WeekScheduleAdmin)
