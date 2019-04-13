from datetime import timedelta

from accounts.models import Trainee
from aputils.eventutils import EventUtils
from aputils.models import QueryFilter
from aputils.utils import comma_separated_field_is_in_regex
from django.core.urlresolvers import reverse
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models import Q
from schedules.constants import WEEKDAYS
from seating.models import Chart
from teams.models import Team
from terms.models import Term


""" SCHEDULES models.py
This schedules module is for representing weekly trainee schedules.
Data Models
- Event:
  an event, such as class or study time, that trainees need to attend.
- WeeklyEvents:
- Schedule:
  a collection of events for one trainee. each trainee should have one
  schedule per term.
- ScheduleTemplate:
  a generic collection of events for one week that can be applied to a
  trainee or group of trainees.
"""


class Event(models.Model):
  '''
  Event - Only defines one particular event. i.e. Full Min (Tuesday morning, weekly)
  Can never be something like: Thursday/Saturday evening study
  '''
  # different colors assigned to each event type
  # Use this to display Rolls
  EVENT_TYPES = (
      ('C', 'Class'),
      ('S', 'Study'),
      ('R', 'Rest'),
      ('M', 'Meal'),
      ('H', 'House'),
      ('T', 'Team'),
      ('Y', 'YPC'),
      ('L', 'Church Meeting'),  # C is taken, so L for locality
      ('*', 'Special'),  # S is taken, so * for special
  )

  # This field determines if person can enter roll. Does not affect how it shows on their view
  MONITOR_TYPES = (
      ('AM', 'Attendance Monitor'),
      ('TM', 'Team Monitor'),
      ('HC', 'House Coordinator'),
      ('RF', 'RFID reader'),
  )

  CLASS_TYPE = (
      ('MAIN', 'Main'),
      ('1YR', '1st Year'),
      ('2YR', '2nd Year'),
      ('AFTN', 'Afternoon'),
  )

  # name of event, e.g. Full Ministry of Christ, or Lights Out
  name = models.CharField(max_length=255)

  # the event's shortcode, e.g. FMoC or Lights
  code = models.CharField(max_length=20)

  # used for A/V
  av_code = models.CharField(max_length=2, blank=True, default='')

  # a description of the event (optional)
  description = models.CharField(max_length=250, blank=True)

  # the type of event
  type = models.CharField(max_length=1, choices=EVENT_TYPES)

  # which type of class this is, e.g. Main, 1st year
  class_type = models.CharField(max_length=4, choices=CLASS_TYPE, blank=True, null=True)

  # who takes roll for this event
  monitor = models.CharField(max_length=2, choices=MONITOR_TYPES, blank=True, null=True)

  start = models.TimeField()

  end = models.TimeField()

  # Optional to catch one-off days, only happen once
  day = models.DateField(blank=True, null=True)

  weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS, verbose_name='Day of the week')

  # Reference to Chart
  # Optional field, not all Events have seating chart
  chart = models.ForeignKey(Chart, blank=True, null=True, on_delete=models.SET_NULL)

  # Unifies the way to get weekday from events with self.day or self.weekday
  def get_uniform_weekday(self):
    if not self.day:
      return self.weekday
    else:
      return self.day.weekday()

  @staticmethod
  def week_from_date(date):
    return Term.current_term().term_week_of_date(date)

  # the date of the event for a given week
  def date_for_week(self, week):
    start_date = Term.current_term().start
    event_week = start_date + timedelta(weeks=week)
    return event_week + timedelta(days=self.weekday)

  # checks for time conflicts between events. Returns True if conflict exists.
  def check_time_conflict(self, event):
    return (self.end > event.start) and (event.end > self.start)

  def __unicode__(self):
    try:
      if self.day:
        date = self.day
      else:
        date = self.get_weekday_display()
      return "ID %s: %s %s [%s - %s] %s" % (self.id, date, self.weekday, self.start.strftime('%H:%M'), self.end.strftime('%H:%M'), self.name)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  def get_absolute_url(self):
    return reverse('schedules:admin-event', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('schedules:admin-event-delete', kwargs={'pk': self.id})


class ScheduleManager(models.Manager):

  def get_queryset(self):
    return super(ScheduleManager, self).get_queryset().filter(term=Term.current_term())


class ScheduleAllManager(models.Manager):

  def get_queryset(self):
    return super(ScheduleAllManager, self).get_queryset()


class Schedule(models.Model):
  '''
  Schedules stack on top of each other to create a master schedule for each trainee
  Base schedules may include rising schedule, meal schedule, class schedule, night schedule
  Special schedules may include a specific campus's work schedule (UCLA, USC, OCC, PCC), ITERO, service week, Thanksgiving
  (e.g. Campus - CHAP - Chapman University - Orange, Class - General Class, Conference - Memorial Day Meals)
  A complete schedule would result from something like
  Rise + meal + class + UCLA work + UCLA study + night = schedule for UCLA trainee for a normal week
  Schedules can not be edited, only cloned + deactivated.
  All active schedules carry over from term to term -> 4th termres taken off,
  1st termers addee
  Deactivation governed by length of trainees attached to schedule
  It is done by taking trainees off schedules, this prevents human
  error of accidentally reactivating a schedule with a stale set of
  trainees attached to it
  '''

  objects = ScheduleManager()
  objects_all = ScheduleAllManager()

  # Add filter choices here.
  TRAINEE_FILTER = (
      ('MC', 'Main Classroom'),  # for all trainees
      ('FY', 'First Year'),
      ('SY', 'Second Year'),
      ('TE', 'Team'),
      ('YP', 'YP'),
      ('CH', 'Children'),
      ('MA', 'Manual'),
      ('GP', 'Group')
  )

  name = models.CharField(max_length=255)

  # Optional comments to describe schedule
  comments = models.CharField(max_length=250, blank=True)

  # which trainee this schedule belongs to
  trainees = models.ManyToManyField(Trainee, related_name="schedules", blank=True)

  # which events are on this schedule
  events = models.ManyToManyField(Event, blank=True, related_name="schedules")

  # For override calculation with services?, could -1
  priority = models.SmallIntegerField()

  # weeks schedule is active in selected season (e.g. [1,2,3,4,5,6,7,8,9,10])
  # max_length=50 fits exactly 1 to 20 with commas and no spaces
  weeks = models.CharField(validators=[validate_comma_separated_integer_list], max_length=50, default='0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19', blank=True, null=True)

  # Only active schedule used for term schedule calculation
  # active = models.BooleanField(default=True)

  # None means valid for both spring + fall
  season = models.CharField(max_length=6,
                            choices=(
                                ('Spring', 'Spring'),
                                ('Fall', 'Fall'),
                                ('All', 'All')
                            ),
                            default=None)

  # Choose auto fill trainees or manually selecting trainees
  # currently not used
  trainee_select = models.CharField(max_length=2, choices=TRAINEE_FILTER, default='MC')

  # Choose which team roll this schedule shows up on
  team_roll = models.ForeignKey(Team, related_name='schedules', blank=True, null=True, on_delete=models.SET_NULL)

  date_created = models.DateTimeField(auto_now=True)

  import_to_next_term = models.BooleanField(default=False, verbose_name='Auto import schedule to the following term')

  # If a change comes in part-term, a schedule may differ in different parts of the term.
  # Parent schedule points to a full-term version of the most-recent schedule, which can be
  # easily imported to the next term.
  # This is to keep historical data intact. See assign_trainees_to_schedule method
  parent_schedule = models.ForeignKey('self', related_name='parent', null=True, blank=True, on_delete=models.SET_NULL)

  # Is this already a parent schedule this term?
  is_parent_schedule = models.BooleanField(default=False)

  # trainee_set_locked means that the trainee set assigned to this schedule should not be
  # updated any more for this term--e.g., if a schedule was split due to trainees
  # switching teams or something similiar, then the first split of the schedule and the
  # parent schedule should not have their trainee set recalculated at risk of having
  # historical roll data lose meaning.
  trainee_set_locked = models.BooleanField(default=False)

  # is_locked means that for the rest of this term, the trainee set will not change.
  # If this schedule gets moved to the next term, then we should make sure to reset the
  # is_locked flag
  is_locked = models.BooleanField(default=False)

  term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL)

  query_filter = models.ForeignKey(QueryFilter, null=True, blank=True, on_delete=models.SET_NULL)

  # Hides "deleted" schedule but keeps it for the sake of record
  is_deleted = models.BooleanField(default=False)

  # Events in time range
  def events_in_range(self, start, end):
    evts = []
    for event in self.events.all():
      if event.end >= start and end >= event.start:
        evts.append(event)
    return evts

  # Whether the schedule has the week
  def active_in_week(self, week):
    weeks = [int(x) for x in self.weeks.split(',')]
    return week in weeks

  def active_in_period(self, period):
    weeks = [int(x) for x in self.weeks.split(',')]
    for week in weeks:
      if ((week + 1) // 2) == period:
        return True
    return False

  @property
  def start_date(self):
    weeks = [int(x) for x in self.weeks.split(',')]
    start_week = weeks[0]
    return Term.current_term().start + timedelta(weeks=start_week - 1)

  @property
  def end_date(self):
    weeks = [int(x) for x in self.weeks.split(',')]
    end_week = weeks[len(weeks) - 1]
    return Term.current_term().start + timedelta(weeks=end_week - 1)

  class Meta:
    ordering = ('priority', 'season')

  def __unicode__(self):
    try:
      return 'ID %s: [%s] %s - %s schedule' % (self.id, self.priority, self.name, self.season)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  @staticmethod
  def current_term_schedules():
    return Schedule.objects.filter(Q(season=Term.current_season()) | Q(season='All')).filter(is_deleted=False)

  # Gets all schedules with event of type in a week. Optionally for a team
  @staticmethod
  def get_all_schedules_by_type_in_weeks(type, weeks, team=None):
    active_schedules = Schedule.current_term_schedules()
    if team:
      active_schedules = active_schedules.filter(team=team)
    active_schedules = active_schedules.filter(events__type=type).distinct()
    wks_reg = comma_separated_field_is_in_regex(weeks)
    # Queries schedules with week defined
    active_schedules = active_schedules.filter(weeks__regex=wks_reg).order_by('priority')
    return active_schedules

  # Gets all schedules for selected trainees within a given list of weeks. Optionally for a team
  # Returns object type QuerySet
  @staticmethod
  def get_all_schedules_in_weeks_for_trainees(weeks, trainees, team=None):
    wks_reg = comma_separated_field_is_in_regex(weeks)
    # print wks_reg, trainees
    # Queries schedules with week defined
    active_schedules = Schedule.current_term_schedules()
    active_schedules = active_schedules.filter(is_deleted=False, weeks__regex=wks_reg, trainees__in=trainees).exclude(trainee_select='GP')
    if team:
      active_schedules = active_schedules.filter(team=team)

    active_schedules = active_schedules.distinct().order_by('priority')
    return active_schedules

  @staticmethod
  def get_roll_table_by_type_in_weeks(trainees, monitor, weeks, event_type):
    '''
      Grab all active schedules of trainees and collapse in order of priority.
      This saves us from recalculated shared schedule common among many trainees,
      We only need to collapse them once.

      get_all_schedules_in_weeks_for_trainees():
      --------------------------------------------------------
        Get all the schedules for all trainees (distinct) in order of inc. priorities


      collapse_priority_event_trainee_table():
      --------------------------------------------------------
        Go through all schedules and override conflicting events trainee roster list
      with trainee list that has higher priority

      Returns table {ev: set([trainee1, trainee2])} in order of increasing start/end time of ev


      export_typed_ordered_roll_list():
      --------------------------------------------------------
        Pull out all remaining events after priority-collapsing of type we are taking roll for

        Returns {event: Set([trainee1, trainee2])


      flip_roll_list():
      --------------------------------------------------------
        we flip the table
        Return object {trainee: [Events, ]}
    '''

    t_set = set(trainees)
    schedules = Schedule.get_all_schedules_in_weeks_for_trainees(weeks, trainees)
    w_tb = EventUtils.collapse_priority_event_trainee_table(weeks, schedules, t_set)
    event_trainee_tb = EventUtils.export_typed_ordered_roll_list(w_tb, monitor)
    if monitor == 'AM':
      event_trainee_tb = [ev_ts for ev_ts in event_trainee_tb if ev_ts[0].type == event_type]

    return EventUtils.flip_roll_list(event_trainee_tb)

  def save(self, *args, **kwargs):
    super(Schedule, self).save(*args, **kwargs)

  def _get_qf_trainees(self):
    if not self.query_filter:
      return Trainee.objects.all()
    query = eval(self.query_filter.query)
    if isinstance(query, dict):
      return Trainee.objects.filter(**query)
    else:
      return Trainee.objects.filter(query)

  """
  Suggest using this to populate query filters for teams
  for t in Team.objects.all():
    q = QueryFilter(name=t.name, query="{{'team__name': '{}'}}".format(t.name))
    q.save()
  """
  def assign_trainees(self):
    trainees = self._get_qf_trainees()
    if trainees:
      self.trainees.set(trainees)

  def get_assign_url(self):
    return reverse('schedules:assign-trainees', kwargs={'pk': self.id})

  def get_absolute_url(self):
    return reverse('schedules:admin-schedule', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('schedules:admin-schedule-delete', kwargs={'pk': self.id})

  def get_split__partial_url(self):
    return '/schedules/admin/schedules/split/%s/' % str(self.id)
