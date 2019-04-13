from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput
from aputils.custom_fields import CSIMultipleChoiceField
from aputils.queryfilter import QueryFilterService
from aputils.widgets import (DatePicker, DatetimePicker,
                             MultipleSelectFullCalendar)
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django_select2.forms import ModelSelect2Widget
from services.models import (Assignment, Category, Qualification,
                             SeasonalServiceSchedule, Service,
                             ServiceAttendance, ServiceException, ServiceRoll,
                             Worker, WorkerGroup)


# This is written to improve query performance on admin backend
class WorkerPrejoinMixin(forms.ModelForm):
  workers = forms.ModelMultipleChoiceField(
      label='Workers',
      queryset=Worker.objects.select_related('trainee').all(),
      required=False,
      widget=admin.widgets.FilteredSelectMultiple('workers', is_stacked=False)
  )


class ServiceRollForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(ServiceRollForm, self).__init__(*args, **kwargs)
    self.fields['start_datetime'].required = True
    self.fields['end_datetime'].required = True

  class Meta:
    model = ServiceRoll
    fields = ["start_datetime", "end_datetime", "task_performed", ]
    widgets = {
      "start_datetime": DatetimePicker(),
      "end_datetime": DatetimePicker(),
      "task_performed": forms.Textarea()
    }


class ServiceAttendanceForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    worker = kwargs.pop('worker')
    super(ServiceAttendanceForm, self).__init__(*args, **kwargs)
    self.fields['designated_service'].queryset = worker.designated.all()
    self.fields['designated_service'].required = True
    self.fields['week'].required = False

  class Meta:
    model = ServiceAttendance
    fields = ["designated_service", "week", ]


class AddExceptionForm(forms.ModelForm):
  workers = forms.ModelMultipleChoiceField(
      queryset=Trainee.objects.all(),
      required=False,
      widget=TraineeSelect2MultipleInput(attrs={'id': 'id_trainees'}),
      label='Trainees to add to Exception',
  )

  def __init__(self, *args, **kwargs):
    super(AddExceptionForm, self).__init__(*args, **kwargs)
    self.fields['services'].widget.attrs['class'] = 'select-fk'
    self.fields['service'].widget.attrs['class'] = 'select-fk'

  class Meta:
    model = ServiceException
    fields = ['name', 'desc', 'tag', 'start', 'end', 'active', 'workers', 'services', 'schedule', 'workload', 'service', ]
    widgets = {
        'start': DatePicker(),
        'end': DatePicker(),
        'services': MultipleSelectFullCalendar(Service.objects.all(), 'services')
    }


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


class AssignmentAdminForm(WorkerPrejoinMixin, forms.ModelForm):
  class Meta:
    model = Assignment
    fields = '__all__'


class WorkGroupAdminForm(WorkerPrejoinMixin, forms.ModelForm):
  query_filters = CSIMultipleChoiceField(choices=QueryFilterService.get_choices(), required=False, label='Filters')

  class Meta:
    model = WorkerGroup
    fields = '__all__'


class ExceptionAdminForm(WorkerPrejoinMixin, forms.ModelForm):

  class Meta:
    model = ServiceException
    fields = '__all__'
    widgets = {
        'services': MultipleSelectFullCalendar(Service.objects.all(), 'services'),
    }


class QualificationForm(WorkerPrejoinMixin, forms.ModelForm):

  class Meta:
    model = Qualification
    exclude = []
    widgets = {
        'workers': admin.widgets.FilteredSelectMultiple('workers', is_stacked=False),
    }


class SingleTraineeServicesForm(forms.Form):
  trainee_id = forms.ModelChoiceField(
      queryset=Trainee.objects.filter(is_active=True),
      required=False,
      widget=ModelSelect2Widget(
          model=Trainee,
          search_fields=['firstname__icontains', 'lastname__icontains'],
      ),
  )


class ServiceCategoryAnalyzerForm(forms.Form):
  category_id = forms.ModelChoiceField(
    queryset=Category.objects.exclude(name="Designated Services"),
    required=False,
    widget=ModelSelect2Widget(
      model=Category,
      search_fields=['name__icontains'],
    ),
  )


class ServiceForm(forms.Form):
  # Add trainees to services and set them into groups
  designated_service = forms.ModelChoiceField(
    label='Services',
    queryset=Service.objects.filter(designated=True).exclude(name__contains='Prep'),
    required=True
  )

  workers = forms.ModelMultipleChoiceField(
    label='Trainees',
    queryset=Worker.objects.all(),
    required=True
  )

  groups = forms.ModelMultipleChoiceField(
    label='Groups',
    queryset=Group.objects.exclude(name__icontains='assistant'),
    required=False,
    help_text='Please contact an AP trainee, if you are unsure which group they need.'
  )

  def save(self, commit=True):
    designated_service_cleaned = self.cleaned_data['designated_service']
    workers_cleaned = self.cleaned_data['workers']
    groups_cleaned = self.cleaned_data['groups']

    # add to worke group, designated services should have only one worker group
    workergroup = designated_service_cleaned.worker_groups.all().first()
    workergroup.workers.add(*list(workers_cleaned))

    # add service to workers
    for w in workers_cleaned:
      w.designated.add(designated_service_cleaned)

    for group in groups_cleaned:
      group.user_set.add(*list(Trainee.objects.filter(worker__in=workers_cleaned)))

  def __init__(self, *args, **kwargs):
    super(ServiceForm, self).__init__(*args, **kwargs)
    self.fields['designated_service'].widget.attrs['class'] = 'select-fk'
    self.fields['workers'].widget.attrs['class'] = 'select-fk'
    self.fields['groups'].widget.attrs['class'] = 'select-fk'
