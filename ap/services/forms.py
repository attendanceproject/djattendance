from django import forms

from services.models import Service, ServiceException, ServiceRoll, ServiceAttendance
from aputils.widgets import DatetimePicker, DatePicker, MultipleSelectFullCalendar
from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput


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
    service_ids = []
    for assignment in worker.assignments.all().filter(service__designated=True).exclude(service__name__contains='Breakfast'):
      service_ids.append(assignment.service.id)
    self.fields['designated_service'].queryset = Service.objects.filter(id__in=service_ids)
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

  class Meta:
    model = ServiceException
    fields = ['name', 'desc', 'tag', 'start', 'end', 'active', 'workers', 'services', 'schedule', 'workload', 'service', ]
    widgets = {
        'start': DatePicker(),
        'end': DatePicker(),
        'services': MultipleSelectFullCalendar(Service.objects.all(), 'services')
    }
