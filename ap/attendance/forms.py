from aputils.widgets import DatePicker
from attendance.models import Roll
from django import forms
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

  class Meta:
    model = Roll
    fields = "__all__"
