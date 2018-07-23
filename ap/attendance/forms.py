from accounts.models import Trainee
from aputils.widgets import DatePicker
from attendance.models import Roll
from django import forms
from django.db.models import Max
from schedules.models import Event


class RollAdminForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    trainee = None
    if 'trainee' in kwargs:
      trainee = kwargs.pop('trainee')
    super(RollAdminForm, self).__init__(*args, **kwargs)

    if trainee is not None:
      event_qs = Event.objects.none()
      for s in trainee.schedules.all():
        event_qs = event_qs | s.events.all()
      self.fields['event'].queryset = event_qs

    self.fields['event'].widget.attrs['class'] = 'select-fk'
    self.fields['trainee'].widget.attrs['class'] = 'select-fk'
    self.fields['submitted_by'].widget.attrs['class'] = 'select-fk'
    self.fields['date'].widget = DatePicker()

  def clean(self):
    cleaned_data = self.cleaned_data
    data_date = cleaned_data['date']
    data_event = cleaned_data['event']
    data_trainee = cleaned_data['trainee']
    data_submitted_by = cleaned_data['submitted_by']
    AMS = Trainee.objects.filter(groups__name='attendance_monitors')

    # Date needs to match the event weekday
    if not data_date.weekday() == data_event.weekday:  # 0 is Monday
      raise forms.ValidationError("Date selected does not match Event selected!!")

    # Roll date and event needs to match schedule week
    sched = data_event.schedules.filter(trainees__in=[data_trainee])
    pr = sched.aggregate(Max('priority'))['priority__max']
    if not sched.get(priority=pr).active_in_week(data_event.week_from_date(data_date)):
      raise forms.ValidationError("Event is not active for date selected!!")

    if data_trainee.self_attendance:
      if data_submitted_by.id != data_trainee.id and data_submitted_by not in AMS:
        raise forms.ValidationError("This is an invalid submitted_by!!")

    return cleaned_data

  class Meta:
    model = Roll
    fields = "__all__"
