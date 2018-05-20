from django import forms

from .models import RoomReservation
from aputils.widgets import TimePicker, DatePicker


class RoomReservationForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(RoomReservationForm, self).__init__(*args, **kwargs)

    # These fields are required for clean to be called
    req_keys = ['group', 'date', 'start', 'end', 'room', 'group_size', 'frequency', 'reason']
    for key in req_keys:
      self.fields[key].required = True

    self.fields['group'].widget.attrs['placeholder'] = 'Group making reservation (will be displayed on TV)'
    self.fields['start'].widget = TimePicker()
    self.fields['end'].widget = TimePicker()
    self.fields['date'].widget = DatePicker()

  class Meta:
    model = RoomReservation
    fields = ['group', 'date', 'start', 'end', 'room', 'group_size', 'frequency', 'reason']
