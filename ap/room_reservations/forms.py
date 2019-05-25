import datetime
from aputils.trainee_utils import is_TA
from aputils.widgets import DatePicker, TimePicker
from django import forms
from terms.models import Term
from .models import RoomReservation

class RoomReservationForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super(RoomReservationForm, self).__init__(*args, **kwargs)

    # These fields are required for clean to be called
    req_keys = ['group', 'date', 'start', 'end', 'room', 'frequency', 'reason']
    for key in req_keys:
      self.fields[key].required = True

    if is_TA(user):
      self.fields['reason'].required = False

    self.fields['group'].widget.attrs['placeholder'] = 'Group making reservation (will be displayed on TV)'
    self.fields['start']
    self.fields['end']
    self.fields['date']

  class Meta:
    model = RoomReservation
    fields = ['group', 'date', 'start', 'end', 'room', 'frequency', 'reason']
    widgets = {
      "start": TimePicker(),
      "end": TimePicker(),
      "date": DatePicker()
    }

  def clean(self):
    cleaned_data = self.cleaned_data
    data_date = cleaned_data['date']
    data_start = cleaned_data['start']
    data_end = cleaned_data['end']
    data_room = cleaned_data['room']
    data_frequency = cleaned_data['frequency']

    # If the cleaned data (from django - the inputted data when a user tries to make a new room reservation)
    # is not valid then raise an error.
    if not Term.current_term().is_date_within_term(data_date):
      raise forms.ValidationError("Given date is not a valid date within the term.")

    if data_start == data_end:
      raise forms.ValidationError("Given start and end times should not be the same.")

    if data_start > data_end:
      raise forms.ValidationError("Given start time should not be after the end time.")

    current_time = datetime.datetime.now().time()
    todays_date = datetime.date.today()
    if data_date <= todays_date and data_start < current_time:
      raise forms.ValidationError("The given reservation is being made in the past.")

    # Based on a first-come, first-serve principle, do not allow trainees to submit a pending room reservation
    # if there is already a pending room reservation waiting to be approved or denied.
    PendingRoomReservations = RoomReservation.objects.filter(status='P', room=data_room)  # pull Pending Room Reservations data
    if self.instance.id:
      PendingRoomReservations = PendingRoomReservations.exclude(id=self.instance.id)
    for r in PendingRoomReservations:
      if r.end > data_start and r.start < data_end and r.date.weekday() == data_date.weekday():
        if r.frequency == 'Once' and r.date < data_date:
          continue
        if r.date > data_date and data_frequency == 'Once':
          continue
        raise forms.ValidationError('There is a pending room reservation with "' + r.group + '" on ' + r.date.strftime("%m-%d-%Y") + ' from ' + r.start.strftime("%I:%M%p") + ' - ' + r.end.strftime("%I:%M%p.") + ' Please choose a different room or time.')

    # Logic with verbose error messages for checking room reservation conflicts.
    # ARR = ApprovedRoomReservation, NRR = NewRoomReservation
    ApprovedRoomReservations = RoomReservation.objects.filter(status='A', room=data_room)  # pull Approved Room Reservations data
    if self.instance.id:
      ApprovedRoomReservations = ApprovedRoomReservations.exclude(id=self.instance.id)
    for r in ApprovedRoomReservations:
      if r.end > data_start and r.start < data_end and r.date.weekday() == data_date.weekday():
        if r.frequency == 'Once':
          # if r.date < data_data, whether NRR is 'Once' or 'Term' having r.date there will never be an overlap.
          if r.date < data_date:
            continue
          # if r.date == data_date, raise an error regardless if NRR is 'Once' or 'Term' because they both overlap.
          elif r.date == data_date:
            raise forms.ValidationError('Overlap with "' + r.group + '" on ' + r.date.strftime("%m-%d-%Y") + ' from ' + r.start.strftime("%I:%M%p") + ' - ' + r.end.strftime("%I:%M%p."))
          # if r.date > data_date, raise an error if NRR is 'Term' because NRR would eventually overlap. 'Once' would be ok.
          elif r.date > data_date:
            if data_frequency == 'Once':
              continue
            raise forms.ValidationError('Given reservation will eventually overlap with "' + r.group + '" on ' + r.date.strftime("%m-%d-%Y") + ' from ' + r.start.strftime("%I:%M%p") + ' - ' + r.end.strftime("%I:%M%p."))
        elif r.frequency == 'Term':
          # if r.date < data_data, raise an error regardless if NRR is 'Once' or 'Term' because ARR will eventually overlap
          if r.date < data_date:
            raise forms.ValidationError('Overlap with "' + r.group + '" on ' + data_date.strftime("%A") + 's for the term from ' + r.start.strftime("%I:%M%p") + ' - ' + r.end.strftime("%I:%M%p."))
          # if r.date == data_date, raise an error regardless if NRR is 'Once' or 'Term' because they both overlap
          elif r.date == data_date:
            raise forms.ValidationError('Overlap with "' + r.group + '" on ' + r.date.strftime("%m-%d-%Y") + ' from ' + r.start.strftime("%I:%M%p") + ' - ' + r.end.strftime("%I:%M%p."))
          # if r.date > data_date, raise an error if NRR is 'Term' because NRR will eventually overlap. 'Once' would be ok.
          elif r.date > data_date:
            if data_frequency == 'Once':
              continue
            raise forms.ValidationError('Given reservation will eventually overlap with "' + r.group + '" on ' + r.date.strftime("%m-%d-%Y") + ' from ' + r.start.strftime("%I:%M%p") + ' - ' + r.end.strftime("%I:%M%p."))
    return cleaned_data
