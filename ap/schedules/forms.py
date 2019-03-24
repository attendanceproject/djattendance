from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput
from aputils.custom_fields import CSIMultipleChoiceField

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError

from terms.models import Term
from attendance.models import Roll

from .models import Event, Schedule
from .utils import validate_rolls_to_schedules


class EventForm(forms.ModelForm):
  schedules = forms.ModelMultipleChoiceField(
    label='Schedules',
    queryset=Schedule.objects.all(),
    required=False,
    widget=FilteredSelectMultiple("schedules", is_stacked=False))

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    self.fields['type'].widget.attrs['class'] = 'select-fk'
    self.fields['class_type'].widget.attrs['class'] = 'select-fk'
    self.fields['monitor'].widget.attrs['class'] = 'select-fk'
    self.fields['weekday'].widget.attrs['class'] = 'select-fk'
    self.fields['chart'].widget.attrs['class'] = 'select-fk'

  class Meta:
    model = Event
    exclude = []
    widgets = {
      'schedules': FilteredSelectMultiple("schedules", is_stacked=False),
    }

class BaseScheduleForm(forms.ModelForm):
  events = forms.ModelMultipleChoiceField(
    label='Events',
    queryset=Event.objects.all(),
    required=False,
    widget=FilteredSelectMultiple(
      "events", is_stacked=False)
  )

  weeks = CSIMultipleChoiceField(
    initial='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18',
    choices=Term.all_weeks_choices(),
    required=False,
    label='Weeks'
  )

  trainees = forms.ModelMultipleChoiceField(
    queryset=Trainee.objects.all(),
    label='Participating Trainees',
    required=False,
    widget=TraineeSelect2MultipleInput,
  )


  def __init__(self, *args, **kwargs):
    super(BaseScheduleForm, self).__init__(*args, **kwargs)
    self.fields['trainees'].widget.attrs['class'] = 'select-fk'
    self.fields['parent_schedule'].widget.attrs['class'] = 'select-fk'
    self.fields['term'].widget.attrs['class'] = 'select-fk'
    self.fields['term'].initial = Term.current_term()
    self.fields['season'].initial = 'All'
    self.fields['trainee_select'].initial = 'MA'
    self.fields['query_filter'].widget.attrs['class'] = 'select-fk'

  class Meta:
    model = Schedule
    exclude = []

class CreateScheduleForm(BaseScheduleForm):

  def clean(self):
    data = self.cleaned_data
    trainees = data['trainees']
    interested_schedules = Schedule.objects.filter(trainees__in=trainees).exclude(priority__gt=int(data['priority'])).exclude(trainee_select='GP')
    interested_eventsList = list(interested_schedules.values('events__id', 'events__start', 'events__end', 'events__weekday'))
    events = data['events']
    events_weekday = set(events.values_list('weekday', flat=True))
    event_ids = []

    for ev in interested_eventsList:
      if ev['events__weekday'] in events_weekday:
        for event in events:
          if event.start <= ev['events__start'] <= event.end or event.start <= ev['events__end'] <= event.end or (ev['events__start'] <= event.start and ev['events__end'] >= event.end):
            event_ids.append(ev['events__id'])
            break

    weeks = data['weeks']
    weeks = weeks.split(',')
    current_term = Term.current_term()
    start_date = current_term.startdate_of_week(int(weeks[0]))
    end_date = current_term.enddate_of_week(int(weeks[-1]))
    rolls = Roll.objects.filter(trainee__in=trainees, event__id__in=event_ids, date__range=[start_date, end_date]).values_list('id', flat=True)
    if rolls.exists():
      raise ValidationError('%(rolls)s', code='invalidRolls', params={'rolls': list(rolls)})

    return self.cleaned_data

# small hack for delete, we're giving two buttons to the same form and instead of using DeleteView
# we'll be using the same framework for rendering rolls deletion for both update and delete
class UpdateScheduleForm(BaseScheduleForm):

  def clean(self):
    rolls = Roll.objects.none()
    cleaned_data = self.cleaned_data

    if 'Update' in self.data:
      if 'weeks' in self.changed_data:
        changed_weeks = cleaned_data['weeks'].split(',')
        initial_weeks = self.initial['weeks'].split(',')
        min_val = int(min(changed_weeks[0], initial_weeks[0]))
        max_val = int(max(changed_weeks[-1], initial_weeks[-1])) + 1
        weeks = range(min_val, max_val)
      else:
        weeks = [int(s) for s in cleaned_data['weeks'].split(',')]

      t_set = set(cleaned_data['trainees'])
      if 'trainees' in self.changed_data:
        t_set = set(self.initial['trainees']) | t_set

      schedules = Schedule.get_all_schedules_in_weeks_for_trainees(weeks, t_set)
      schedules = list(schedules.exclude(id=self.instance.id))

      mock_schedule = {}
      mock_schedule['events'] = cleaned_data['events']
      mock_schedule['trainees'] = cleaned_data['trainees']
      mock_schedule['priority'] = cleaned_data['priority']
      mock_schedule['weeks'] = cleaned_data['weeks']
      schedules.append(mock_schedule)

    elif 'Delete' in self.data:

      weeks = [int(s) for s in cleaned_data['weeks'].split(',')]
      t_set = cleaned_data['trainees']
      schedules = Schedule.get_all_schedules_in_weeks_for_trainees(weeks, t_set)
      schedules = schedules.exclude(pk=self.instance.id)

    current_term = Term.current_term()
    start_date = current_term.startdate_of_week(weeks[0])
    end_date = current_term.enddate_of_week(weeks[-1])
    potential_rolls = Roll.objects.filter(trainee__in=t_set, date__range=[start_date, end_date])
    rolls = validate_rolls_to_schedules(schedules, t_set, weeks, potential_rolls)
    rolls = rolls.values_list('id', flat=True)

    if rolls.exists():
      raise ValidationError('%(rolls)s', code='invalidRolls', params={'rolls': list(rolls)})

    return self.cleaned_data

class AfternoonClassForm(forms.Form):

  trainees = forms.ModelMultipleChoiceField(
    queryset=Trainee.objects.all(),
    label='Trainees',
    required=True,
    widget=TraineeSelect2MultipleInput,
  )

  event = forms.ChoiceField(
    required=True,
    label='Transfer to'
  )

  week = forms.IntegerField(
    max_value=18,
    min_value=1,
    required=True,
    label='Starting from week'
  )

  def __init__(self, *args, **kwargs):
    event_choices = kwargs.pop('event_choices')
    super(AfternoonClassForm, self).__init__(*args, **kwargs)
    self.fields['event'].choices = event_choices
    self.fields['trainees'].widget.attrs['class'] = 'select-fk'