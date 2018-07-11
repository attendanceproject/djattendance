from collections import OrderedDict
from datetime import date, datetime, timedelta

from aputils.eventutils import EventUtils
from aputils.models import Address
from attendance.utils import Period
from badges.models import Badge
from dateutil import parser
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        Group, PermissionsMixin)
from django.contrib.postgres.fields import JSONField
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from houses.models import Bunk, House
from localities.models import Locality
from teams.models import Team
from terms.models import Term


""" accounts models.py
The user accounts module takes care of user accounts and
utilizes/extends Django's auth system to handle user authentication.

USER ACCOUNTS
  Because we want to use the user's email address as the unique
  identifier, we have chosen to implement a custom User model,

  Types:
    Trainee: Regular, Short-term, Commuter
    TA

  User accounts are all merged into one model for the sake of db performance
  Since the User table sits at the center of AP, constantly prefetching/pre-joining
  tables every time user is accessed is cost-prohibitive and difficult to maintain

  Other notes:
    - every Trainee is also a service worker, so those user accounts also
    have a ServiceWorker profile that contains information needed for the
    ServiceScheduler algorithm
    - before coming to the FTTA, a trainee may have come to short-term.
    These trainees will have a Short-Term profile at that time, and later
    also have a Trainee  profile when they come for the full-time.

  The merging of all tables also allow user to have multiple roles at different times in
  their life cycle, and also allows a clean transition between roles
  (e.g. a Short-termer who becomes a Trainee and then later a TA can keep the same
  account throughout).
"""


class APUserManager(BaseUserManager):

  def create_user(self, email, password=None):
    """ Creates a user, given an email and a password (optional) """
    if not email:
      raise ValueError("Users must have an email address")

    user = self.model(email=APUserManager.normalize_email(email))
    user.set_password(password)
    user.save(using=self._db)

    return user

  def create_superuser(self, email, password):
    """ Creates a super user, given an email and password (required) """
    user = self.create_user(email)
    user.set_password(password)

    user.is_admin = True
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self.db)

    for g in Group.objects.all():
      g.user_set.add(user)

    return user


class UserMeta(models.Model):
  # ---------------Personal Information------------------
  phone = models.CharField(max_length=25, null=True, blank=True)
  home_phone = models.CharField(max_length=25, null=True, blank=True)
  work_phone = models.CharField(max_length=25, null=True, blank=True)

  maidenname = models.CharField(verbose_name=u'maiden name',
                                max_length=30,
                                blank=True, null=True
                                )

  # refers to the user's home address, not their training residence
  address = models.ForeignKey(Address, blank=True, verbose_name='home address', on_delete=models.SET_NULL, null=True)

  college = models.CharField(max_length=50, null=True, blank=True)
  major = models.CharField(max_length=50, null=True, blank=True)
  degree = models.CharField(max_length=30, null=True, blank=True)

  emergency_name = models.CharField(max_length=100, null=True, blank=True)
  emergency_address = models.CharField(max_length=250, null=True, blank=True)
  emergency_phone = models.CharField(max_length=25, null=True, blank=True)
  emergency_phone2 = models.CharField(max_length=25, null=True, blank=True)

  # ---------------Trainee specific--------------
  # is_married refers to the status, is_couple is True if both parties are in the
  # training
  is_married = models.BooleanField(default=False)
  is_couple = models.BooleanField(default=False)

  GOSPEL_PREFS = (
      ('CP', 'Campus'),
      ('YP', 'Young People'),
      ('CM', 'Community'),
      ('CH', 'Children'),
      ('ID', 'Internet Defense Confirmation Project')
  )
  gospel_pref1 = models.CharField(max_length=2, choices=GOSPEL_PREFS, null=True, blank=True)
  gospel_pref2 = models.CharField(max_length=2, choices=GOSPEL_PREFS, null=True, blank=True)

  bunk = models.ForeignKey(Bunk, on_delete=models.SET_NULL, null=True, blank=True)

  readOT = models.BooleanField(default=False)
  readNT = models.BooleanField(default=False)

  # ---------------Trainee Assistant specific--------------
  services = models.ManyToManyField('services.Service', related_name='worker_meta', blank=True)
  houses = models.ManyToManyField(House, related_name='residents_meta', blank=True)

  user = models.OneToOneField('User', related_name='meta', null=True, blank=True)


class User(AbstractBaseUser, PermissionsMixin):
  """ A basic user account, containing all common user information.
  This is a custom-defined User, but inherits from Django's classes
  to integrate with Django's other provided User tools/functionality
  AbstractBaseUser provides Django's basic authentication backend.
  PermissionsMixin provides compatibility with Django's built-in permissions system.
  """

  USER_TYPES = (
      ('T', 'Training Assistant'),
      ('R', 'Regular (full-time)'),  # a regular full-time trainee
      ('S', 'Short-term (long-term)'),  # a 'short-term' long-term trainee
      ('C', 'Commuter')
  )

  type = models.CharField(max_length=1, choices=USER_TYPES)

  email = models.EmailField(verbose_name=u'email address',
                            max_length=255,
                            unique=True,
                            db_index=True
                            )

  # Necessary until we are no longer importing from a CSV file.
  office_id = models.IntegerField(blank=True, null=True)

  rfid_tag = models.IntegerField(blank=True, null=True)
  # optional username to get wiki to work
  username = models.CharField(
      _('username'),
      max_length=30,
      unique=True,
      blank=True,
      null=True,
      help_text=_('Required. 30 characters or fewer. Letters, digits and '
                  '@/./+/-/_ only.'),
      validators=[
          validators.RegexValidator(r'^[\w.@+-]+$',
                                    _('Enter a valid username. '
                                      'This value may contain only letters, numbers '
                                      'and @/./+/-/_ characters.'),
                                    'invalid'
                                    ),
      ],
      error_messages={
          'unique': _("A user with that username already exists."),
      }
  )

  badge = models.ForeignKey(Badge, blank=True, on_delete=models.SET_NULL, null=True)

  # All user data
  firstname = models.CharField(verbose_name=u'first name', max_length=30)
  lastname = models.CharField(verbose_name=u'last name', max_length=30)
  middlename = models.CharField(verbose_name=u'middle name', max_length=30, blank=True, null=True)
  nickname = models.CharField(max_length=30, blank=True, null=True)

  GENDER = (
      ('B', 'Brother'),
      ('S', 'Sister')
  )

  LRHAND = (
      ('L', 'left'),
      ('R', 'right')
  )

  gender = models.CharField(max_length=1, choices=GENDER)
  lrhand = models.CharField(max_length=1, choices=LRHAND, default='R')
  date_of_birth = models.DateField(null=True)

  @property
  def age(self):
    today = date.today()
    dob = self.date_of_birth
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)

  # Custom query manager
  objects = APUserManager()

  def get_absolute_url(self):
    return "/users/%s/" % urlquote(self.username)

  # First name first
  @property
  def full_name(self):
    fullname = '%s %s' % (self.firstname, self.lastname)
    return fullname.strip()

  # Last name first
  @property
  def full_name2(self):
    fullname = '%s, %s' % (self.lastname, self.firstname)
    return fullname.strip()

  def get_short_name(self):
    return self.firstname

  def get_full_name(self):
    return self.full_name

  def email_user(self, subject, message, from_email=None):
    send_mail(subject, message, from_email, [self.email])

  def HC_status(self):
    return self.groups.filter(name='HC').exists()

  def has_group(self, groups=[]):
    return self.groups.filter(name__in=groups).exists()

  def is_designated_grader(self):
    return self.groups.filter(name='exam_graders').exists()

  def __unicode__(self):
    try:
      return "%s, %s <%s>" % (self.lastname, self.firstname, self.email)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  # TODO(import2): permissions -- many to many role_type

  # ---------------Trainee specific--------------
  # Terms_attended can exist for every user but curent_term does not necessarily make sense for a TA for example
  terms_attended = models.ManyToManyField(Term, blank=True)
  current_term = models.IntegerField(default=1, null=True, blank=True)

  date_begin = models.DateField(null=True, blank=True)
  date_end = models.DateField(null=True, blank=True)

  TA = models.ForeignKey('self', related_name='training_assistant', null=True, blank=True, on_delete=models.SET_NULL)
  mentor = models.ForeignKey('self', related_name='mentee', null=True, blank=True, on_delete=models.SET_NULL)

  locality = models.ForeignKey(Locality, null=True, blank=True, on_delete=models.SET_NULL)

  team = models.ForeignKey(Team, null=True, blank=True, related_name='members', on_delete=models.SET_NULL)

  house = models.ForeignKey(House, null=True, blank=True, related_name='residents', on_delete=models.SET_NULL)

  # flag for trainees taking their own attendance
  # this will be false for 1st years and true for 2nd with some exceptions.
  self_attendance = models.BooleanField(default=False)

  def get_outstanding_discipline(self):
    o_discipline = []
    for discipline in self.discipline_set.all():
      if not discipline.is_completed():
        o_discipline.append(discipline)
    return o_discipline

  class Meta:
    ordering = ['lastname', 'firstname']


class TraineeManager(models.Manager):
  # Only works for one-to-one relationships. Currently does not work for other types
  use_for_related_fields = True

  def get_queryset(self):
    return super(TraineeManager, self).get_queryset().filter(models.Q(type='R') | models.Q(type='S') | models.Q(type='C'))\
        .filter(is_active=True)


class InactiveTraineeManager(models.Manager):
  def get_queryset(self):
    return super(InactiveTraineeManager, self).get_queryset().filter(models.Q(type='R') | models.Q(type='S') | models.Q(type='C')).filter(is_active=False)


class Trainee(User):

  class Meta:
    proxy = True
    ordering = ['firstname', 'lastname']

  objects = TraineeManager()
  inactive = InactiveTraineeManager()

  # for groupslips, create a schedule named 'Group Events' filled with group events (located in static/react/scripts/testdata/groupevents.js)
  @property
  def group_schedule(self):
    return self.schedules.filter(trainee_select='GP').order_by('priority')

  @property
  def active_schedules(self):
    return self.schedules.filter(
        Q(is_deleted=False) &
        (Q(season=Term.current_season()) | Q(season='All')) &
        ~Q(trainee_select='GP')
    ).order_by('priority')

  # rolls for current term
  @property
  def current_rolls(self):
    c_term = Term.current_term()
    rolls = self.rolls.filter(date__gte=c_term.start, date__lte=c_term.end)
    if self.self_attendance:
      rolls = rolls.filter(submitted_by=self)
    return rolls

  def __unicode__(self):
    try:
      return "%s %s" % (self.firstname, self.lastname)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  def get_attendance_record(self, period=None):
    from leaveslips.models import GroupSlip
    c_term = Term.current_term()
    rolls = self.rolls.exclude(status='P').filter(date__gte=c_term.start, date__lte=c_term.end).order_by('event', 'date').distinct('event', 'date').prefetch_related('event')
    ind_slips = self.individualslips.filter(status__in=['A', 'S'])
    att_record = []  # list of non 'present' events
    excused_timeframes = []  # list of groupslip time ranges
    excused_rolls = []  # prevents duplicate rolls

    def attendance_record(att, start, end, event):
      return {
          'attendance': att,
          'start': start,
          'end': end,
          'event': event,
      }

    def reformat(slip):
      s = str(datetime.combine(slip['rolls__date'], slip['rolls__event__start'])).replace(' ', 'T')
      e = str(datetime.combine(slip['rolls__date'], slip['rolls__event__end'])).replace(' ', 'T')
      return (s, e)

    group_slips = GroupSlip.objects.filter(trainees=self, status__in=['A', 'S'])

    # TODO: It doesn't cover trainees who are also a team monitor
    if self.self_attendance:
      rolls = rolls.filter(submitted_by=self)
    else:
      rolls = rolls.exclude(submitted_by=self)
    rolls = rolls.order_by('event__id', 'date').distinct('event__id', 'date')  # may not need to order

    if period is not None:
      # works without period, but makes calculate_summary really slow
      p = Period(c_term)
      start_date = p.start(period)
      end_date = p.end(period)
      startdt = datetime.combine(start_date, datetime.min.time())
      enddt = datetime.combine(end_date, datetime.min.time())
      rolls = rolls.filter(date__gte=start_date, date__lte=end_date)  # rolls for current period
      ind_slips = ind_slips.filter(rolls__in=[d['id'] for d in rolls.values('id')])
      group_slips = group_slips.filter(start__lte=enddt, end__gte=startdt)

    rolls = rolls.values('event__id', 'event__start', 'event__end', 'event__name', 'status', 'date')
    ind_slips = ind_slips.values('rolls__event__id', 'rolls__event__start', 'rolls__event__end', 'rolls__date', 'rolls__event__name', 'id')
    excused_timeframes = group_slips.values('start', 'end')

    # first, individual slips
    for slip in ind_slips:
      if slip['rolls__event__id'] is None:
        continue
      start, end = reformat(slip)
      att_record.append(attendance_record(
          'E',
          start,
          end,
          slip['rolls__event__id']
      ))
      excused_rolls.append((slip['rolls__event__id'], slip['rolls__date']))

    for roll in rolls:
      excused = False
      for excused_roll in excused_rolls:
        if roll['event__id'] == excused_roll[0] and roll['date'] == excused_roll[1]:  # Check if roll is excused using the roll's event and the roll's date
          excused = True
          break
      if excused is False:
        if roll['status'] == 'A':  # absent rolls
          att_record.append(attendance_record(
              'A',
              str(roll['date']) + 'T' + str(roll['event__start']),
              str(roll['date']) + 'T' + str(roll['event__end']),
              roll['event__id']
          ))
        else:  # tardy rolls
          att_record.append(attendance_record(
              'T',
              str(roll['date']) + 'T' + str(roll['event__start']),
              str(roll['date']) + 'T' + str(roll['event__end']),
              roll['event__id']
          ))
    # now, group slips
    for record in att_record:
      if record['event'] is None:
        continue
      if record['attendance'] != 'E':
        start_dt = parser.parse(record['start'])
        end_dt = parser.parse(record['end'])
        for tf in excused_timeframes:
          if EventUtils.time_overlap(start_dt, end_dt, tf['start'], tf['end']):
            record['attendance'] = 'E'
    return att_record

  attendance_record = cached_property(get_attendance_record)

  def calculate_summary(self, period):
    """this function examines the Schedule belonging to trainee and search
    through all the Events and Rolls. Returns the number of summary a
    trainee needs to be assigned over the given period."""
    num_A = 0
    num_T = 0
    num_summary = 0
    att_rcd = self.get_attendance_record(period=period)
    for event in att_rcd:
      if event['attendance'] == 'A':
        num_A += 1
      elif event['attendance'] == 'T':
        num_T += 1
    if num_A >= 2:
      num_summary += max(num_A, 0)
    if num_T >= 5:
      num_summary += max(num_T - 3, 0)
    return num_summary

  num_summary = cached_property(calculate_summary)

  # Get events in date range (handles ranges that span multi-weeks)
  # Returns event list sorted in timestamp order
  # If you want to sort by name, use event_list.sort(key=operator.attrgetter('name'))
  def events_in_date_range(self, start, end, listOfSchedules=[]):
    # check for generic group calendar
    if listOfSchedules:
      schedules = listOfSchedules
    else:
      schedules = self.active_schedules

    # figure out which weeks are in the date range.
    c_term = Term.current_term()
    start_week = c_term.term_week_of_date(start)
    end_week = c_term.term_week_of_date(end)
    w_tb = OrderedDict()
    # for every schedule, filter events to get events in the date range.
    for schedule in schedules:
      # create week table for date range that covers more than one week.
      if end_week - start_week > 0:
        # covers first week.
        evs = schedule.events.filter(Q(weekday__gte=start.weekday())).order_by('weekday', 'start', 'end')
        weeks = [start_week]
        w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)
        # covers weeks between first and last week.
        evs = schedule.events.all().order_by('weekday', 'start', 'end')
        weeks = range(start_week + 1, end_week)
        w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)
        # covers last week.
        evs = schedule.events.filter(Q(weekday__lte=end.weekday())).order_by('weekday', 'start', 'end')
        weeks = [end_week]
        w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)
        # create week table for date range that covers only one week.
      else:
        evs = schedule.events.filter(weekday__gte=start.weekday(), weekday__lte=end.weekday()).order_by('weekday', 'start', 'end')
        weeks = range(start_week, end_week + 1)
        w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)

    # create event list.
    return EventUtils.export_event_list_from_table(w_tb, start_datetime=start, end_datetime=end)

  # Get the current event trainee (Attendance Monitor) is in or will be in 15 minutes window before after right now!!
  def immediate_upcoming_event(self, time_delta=15, with_seating_chart=False):

    # Code for debugging
    # Turn this boolean to test locally and receive valid event on page load every time
    test_ev_with_chart = False
    if test_ev_with_chart:
      from schedules.models import Event
      ev = Event.objects.filter(chart__isnull=False)[0]
      date = ev.date_for_week(3)
      # calc date from w
      ev.start_datetime = datetime.combine(date, ev.start)
      ev.end_datetime = datetime.combine(date, ev.end)
      return [ev, ]

    # Actual code starts below

    schedules = self.active_schedules
    c_time = datetime.now()
    delay = timedelta(minutes=time_delta)
    start_time = c_time + delay
    end_time = c_time - delay
    c_term = Term.current_term()
    weeks = set([int(c_term.term_week_of_date(c_time.date()))])
    w_tb = OrderedDict()

    for schedule in schedules:
      evs = schedule.events.filter(Q(weekday=c_time.weekday()) | Q(day=c_time.date())).filter(start__lte=start_time, end__gte=end_time)
      if with_seating_chart:
        evs = evs.filter(chart__isnull=False)
      schedule_weeks = set(map(int, schedule.weeks.split(',')))
      w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks & schedule_weeks, evs, schedule.priority)
    # print w_tb
    return EventUtils.export_event_list_from_table(w_tb)

  @cached_property
  def events(self):
    schedules = self.active_schedules
    w_tb = OrderedDict()
    # create week table
    for schedule in schedules:
      evs = schedule.events.all()
      weeks = [int(x) for x in schedule.weeks.split(',')]
      w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)

    # return all the calculated, composite, priority/conflict resolved list of events
    return EventUtils.export_event_list_from_table(w_tb)

  # events in list of weeks
  def events_in_week_list(self, weeks):
    schedules = self.active_schedules
    w_tb = OrderedDict()
    for schedule in schedules:
      evs = schedule.events.all()
      w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)

    # return all the calculated, composite, priority/conflict resolved list of events
    return EventUtils.export_event_list_from_table(w_tb)

  @cached_property
  def groupevents(self):
    return self.groupevents_in_week_range()

  def groupevents_in_week_list(self, weeks):
    schedules = self.group_schedule
    w_tb = OrderedDict()
    # create week table
    for schedule in schedules:
      evs = schedule.events.all()
      weeks = [int(x) for x in schedule.weeks.split(',')]
      w_tb = EventUtils.compute_prioritized_event_table(w_tb, weeks, evs, schedule.priority)

    # return all the calculated, composite, priority/conflict resolved list of events
    return EventUtils.export_event_list_from_table(w_tb)

  def groupevents_in_week_range(self, start_week=0, end_week=19):
    weeks = [int(x) for x in range(start_week, end_week + 1)]
    return self.groupevents_in_week_list(weeks)


class TAManager(models.Manager):
  def get_queryset(self):
    return super(TAManager, self).get_queryset().filter(type='T', is_active=True)


class InactiveTAManager(models.Manager):
  def get_queryset(self):
    return super(TAManager, self).get_queryset().filter(type='T', is_active=False)


class TrainingAssistant(User):
  class Meta:
    proxy = True
    ordering = ['firstname', 'lastname']

  objects = TAManager()
  inactive = InactiveTAManager()


def default_settings():
  return {"leaveslip": {"selected_ta": -1, "selected_status": "P", "selected_trainee": None}}


# Statistics / records on trainee (e.g. attendance, absences, service/fatigue level, preferences, etc)
class Statistics(models.Model):
  trainee = models.OneToOneField(User, related_name='statistics', null=True, blank=True)

  # String containing book name + last chapter of lifestudy written ([book_id]:[chapter], Genesis:3)
  latest_ls_chpt = models.CharField(max_length=400, null=True, blank=True)

  settings = JSONField(default=default_settings())
