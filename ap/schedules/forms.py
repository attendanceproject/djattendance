from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput
from aputils.custom_fields import CSIMultipleChoiceField

from django import forms
from django.db.models import Q
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError

from terms.models import Term
from attendance.models import Roll

from itertools import groupby
from operator import itemgetter

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

    ### The next set of code is to find and delete rolls if someone is inputting new events in the middle of the term.
    # The old solution of using "date__range=[start_date, end_date]" for the Roll.objects.filter only works with the assumption
    # that trainee events are continuous throughout the term. So in the case if a trainee event is every other week, then roll objects will need to be deleted
    # even if the selected week isn't chosen. E.g. Weeks 2,4,6,8 - so anything between 2 through 8 would be deleted, including weeks 3,4,7 even though they're not included.
    
    ### Put weeks chosen for an event in a group, then add them to a list.
    # This is based off of "https://docs.python.org/2.6/library/itertools.html#examples"
    # and explicitly copied from an answer "https://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list"
    # Order of the numbering matters for this solution (in our case, it's already ordered).
    week_ranges = []
    for k, g in groupby(enumerate(weeks), lambda (i,x):int(i)-int(x)):
      group = map(itemgetter(1), g)
      week_ranges.append((group[0], group[-1]))

    ### Use a Django Q function to dynamically filter the weeks
    # "https://stackoverflow.com/questions/44067134/django-query-an-unknown-number-of-multiple-date-ranges"
    # Basically instead of only being able to do "date__range" filter once, Q function allows us to dynamically create and 
    # filter from multiple date__ranges
    qs = [Q(date__range=[current_term.startdate_of_week(int(from_week)), current_term.enddate_of_week(int(to_week))]) for (from_week, to_week) in week_ranges]
    week_range_q = Q()
    for q in qs:
      week_range_q = week_range_q | q

    rolls = Roll.objects.filter(trainee__in=trainees, event__id__in=event_ids).values_list('id', flat=True)
    rolls = rolls.filter(week_range_q) # This filter is with the multiple date__range

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
        # gets only the changed weeks
        changed_weeks = set(cleaned_data['weeks'].split(','))
        initial_weeks = set(self.initial['weeks'].split(','))
        weeks_set = changed_weeks - initial_weeks | initial_weeks - changed_weeks
        weeks = [int(s) for s in weeks_set]

      else:
        weeks = [int(s) for s in cleaned_data['weeks'].split(',')]

      t_set = set(cleaned_data['trainees'])
      if 'trainees' in self.changed_data:
        # gets only the changed trainees
        t_set = (t_set - set(self.initial['trainees'])) | (set(self.initial['trainees']) - t_set)

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

    ### Put weeks chosen for an event in a group, then add them to a list.
    # there's a more extensive comment in CreateScheduleForm that uses the same code
    week_ranges = []
    for k, g in groupby(enumerate(weeks), lambda (i,x):int(i)-int(x)):
      group = map(itemgetter(1), g)
      week_ranges.append((group[0], group[-1]))

    ### Put weeks chosen for an event in a group, then add them to a list.
    # there's a more extensive comment in CreateScheduleForm that uses the same code
    qs = [Q(date__range=[current_term.startdate_of_week(int(from_week)), current_term.enddate_of_week(int(to_week))]) for (from_week, to_week) in week_ranges]
    week_range_q = Q()
    for q in qs:
      week_range_q = week_range_q | q

    potential_rolls = Roll.objects.filter(trainee__in=t_set).filter(week_range_q)
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