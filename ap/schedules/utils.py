from datetime import datetime, timedelta

from django.db.models import Count
from accounts.models import Trainee
from attendance.models import Roll
from schedules.models import Event, Schedule
from terms.models import Term

from aputils.eventutils import EventUtils

def afternoon_class_transfer(trainee_ids, event_id, start_week):
  # assume that existing schedules for each of the afternoon class for the full term already exists
  # this util methods takes a list of trainee ids and the event id for the intended transfer along with the start week
  # identifies the potential rolls that may needs to be transferred
  # then moves the trainees onto their new schedule along with their rolls
  # this is a specifica case of schedule update with strict known paramter settings that allows rolls update with relative certainty

  # rolls that needs to be transferred onto their new schedule
  ct = Term.current_term()
  trainees = Trainee.objects.filter(id__in=trainee_ids)
  rolls = Roll.objects.filter(trainee__in=trainees, event__class_type='AFTN', event__weekday__in=[1, 3], event__monitor='AM', date__gte=ct.startdate_of_week(start_week))

  ev = Event.objects.get(id=event_id)
  potential_sch = ev.schedules.order_by('priority')
  new_sch = potential_sch.first()


  # check to make sure there's only two events on the new schedule and they match the afternoon class criteria
  check1 = new_sch.events.all().count() == 2
  check2 = new_sch.events.filter(class_type='AFTN', monitor='AM').count() == 2
  if not(check1 and check2):
    return "Transfer unsuccessful. Problem with new schedule."

  # look for possibly already created schedule for transfer
  # identifies by starting week
  found = False
  for sch in potential_sch.exclude(id=new_sch.id):
    startWeek = int(sch.weeks.split(',')[0])
    if start_week == startWeek and sch.events.count() == 2:
      events = sch.events.all()
      if events[0].class_type == 'AFTN' and events[1].class_type == 'AFTN':
        new_sch = sch
        found = True

  # if not found, then create, else just use the one that's found
  all_names = ''
  if not found:

    old_sch = potential_sch.first()
    new_sch.pk = None
    new_sch.save()

    new_sch.priority = old_sch.priority
    new_sch.import_to_next_term = False
    new_sch.name = new_sch.name + ' - transfer'
    new_sch.comments = old_sch.comments + ' // used for transfers'
    weeks = ''

    # includes service week (week 18)
    for i in range(start_week, 19):
      weeks = weeks + str(i) + ','
    new_sch.weeks = weeks[:-1]
    new_sch.save()

    for event in old_sch.events.all():
      new_sch.events.add(event)
    new_sch.save()

  # # priority calculation and recalibration
  afternoon_schs = Schedule.objects.annotate(ev_count=Count('events')).filter(ev_count=2, events__weekday=1, events__monitor='AM')
  afternoon_schs_ids = set(afternoon_schs.values_list('id', flat=True))
  check_sch_ids = set()
  for trainee in trainees:
    intersect = afternoon_schs_ids.intersection(set(trainee.active_schedules.values_list('id', flat=True)))
    check_sch_ids = check_sch_ids.union(intersect)

  new_sch.priority = afternoon_schs.filter(id__in=check_sch_ids).order_by('-priority').first().priority + 1
  new_sch.save()

  # regardless of found or not, add the trainees to their new schedule and make string of names to render
  for trainee in trainees:
    new_sch.trainees.add(trainee)
    all_names = all_names + trainee.full_name + ', '
  new_sch.save()
  all_names = all_names[0:-2]

  # move rolls that are attached to the old schedule
  rolls.filter(event__weekday=1).update(event=new_sch.events.get(weekday=1))
  rolls.filter(event__weekday=3).update(event=new_sch.events.get(weekday=3))

  return "Successfully moved " + all_names + " to " + str(ev.name) + " starting from week " + str(start_week) + "."

# takes the given list of schedules along with trainee_set and weeks and uses the EventUtils method to create an OrderedDict that represents trainee's chedule
# the same method is used for the backend feed for the personal attendance, that way we keep everything consistent
# the rolls are then checked against that huge OrderedDict to see if everything aligns, anything that stands out is a ghost roll and needs to be reconciled
def validate_rolls_to_schedules(schedules, trainee_set, weeks, rolls):
  roll_ids = []

  current_term = Term.current_term()
  w_tb = EventUtils.collapse_priority_event_trainee_table(weeks, schedules, trainee_set)
  potential_rolls = rolls.order_by('date', 'event__start')
  for roll in potential_rolls:
    key = current_term.reverse_date(roll.date)
    evs = w_tb[key]
    if roll.event not in evs or (roll.event in evs and roll.trainee not in evs[roll.event] ):
      roll_ids.append(roll.id)

  invalid_rolls = Roll.objects.filter(id__in=roll_ids)
  return invalid_rolls


def next_dow(d, day):
  while d.weekday() != day:
    d += timedelta(1)
  return d


def should_split_schedule(schedule, week):
  """ Returns true if the schedule should be split if the schedule change takes place
    starting the inputted week. """
  if not schedule.term or not schedule.term.current:
    return False

  # Parent schedules should not be split.  Instead, split one of the split schedules off of
  # the parent schedule
  if schedule.is_parent_schedule:
    return False

  # If active before and after the given week, then we'll need to split
  weeks = [int(x) for x in schedule.weeks.split(',')]

  active_before = False
  active_after = False

  for w in range(1, week):
    if w in weeks:
      active_before = True

  if max(weeks) >= week:
    active_after = True

  if active_before and active_after:
    return True

  return False


def split_schedule(schedule, week):
  """ If the schedule needs to split, returns a tuple of schedules--the parent schedule
    (which may or may not be the schedule that was passed in), the earlier split of the
    schedule, and the later split of the schedule.  Both of the splits will contain
    identical data to the original--only the weeks and pertinent settings on the schedules
    will have changed.  Make sure that any non-trainee changes you make are propagated to
    both the parent schedule and the newer split if you want the changes to be imported
    to the schedule on the following term.

    If the schedule does not need to be split, you will get a tuple of parent schedule,
    None, passed in schedule.  The parent schedule and passed in schedule may be the same.
  """

  if not should_split_schedule(schedule, week):
    if schedule.parent_schedule:
      return schedule.parent_schedule, None, schedule
    else:
      return schedule, None, schedule

  # clone
  schedule_copy = Schedule.objects.get(id=schedule.id)
  s1 = schedule_copy
  s1.pk = None
  s1.save()

  schedule_copy = Schedule.objects.get(id=schedule.id)
  s2 = schedule_copy
  s2.pk = None
  s2.save()

  s1.trainees = schedule.trainees.all()
  s2.trainees = schedule.trainees.all()

  s1.events = schedule.events.all()
  s2.events = schedule.events.all()

  weeks = [int(x) for x in schedule.weeks.split(',')]
  s1_weeks = [i for i in weeks if i < week]
  s2_weeks = [i for i in weeks if i >= week]
  s1.weeks = ','.join(map(str, s1_weeks))
  s2.weeks = ','.join(map(str, s2_weeks))

  # splits should not be ported to the following term.  Only parent schedules get moved, so
  # make sure changes are made both to s2 and parent schedule (after return)
  s1.import_to_next_term = s2.import_to_next_term = False

  # splits are parented to the original parent, if it exists
  if not schedule.parent_schedule:
    s1.parent_schedule = s2.parent_schedule = schedule
    schedule.is_parent_schedule = True

  s1.is_parent_schedule = s2.is_parent_schedule = False
  s1.trainee_set_locked = True

  s1.save()
  s2.save()

  schedule.trainees = []
  schedule.trainee_set_locked = True

  # If this schedule has a parent schedule, this schedule is no longer needed.
  # Todo(import2): After writing unit tests, consider if it's worthwhile to make it so
  # we don't create an extra schedule in this case (i.e. instead of creating s1, just
  # use schedule directly)
  if schedule.parent_schedule:
    schedule.is_deleted = True
  else:
    schedule.is_parent_schedule = True

  schedule.save()

  if schedule.parent_schedule:
    return schedule.parent_schedule, s1, s2
  else:
    return schedule, s1, s2


def assign_trainees_to_schedule(schedule):
    """
    This function is used in apimport.utils.import_csv.
    This function handles new term (no split necessary) and mid term imports (splitting)
    For new term:
      - A new term must be created before the term begins. (see. apimport.utils.create_term)
      - New schedules must be generated or imported from previous terms (see apimport.utils.migrate_schedules)
        - The new schedules MUST have a queryfilter, even if a schedules should include all trainees.
    For mid term:
      - Current schedules do not need to be touched.
      - The import_csv will change trainee filelds (i.e teams, year, etc.) based on the import file.
      - The current schedules will assign trainees based on its query filter.
      - Splitting will based on week this function is called (i.e now)

    """
    if schedule.is_locked:
      return

    new_set = schedule._get_qf_trainees()
    current_set = schedule.trainees.all()

    # If the schedules are identical, bail early
    to_add = new_set.exclude(pk__in=current_set)
    to_delete = current_set.exclude(pk__in=new_set)

    if not to_add and not to_delete:
      return

    # Does the schedule need to be split?
    term = Term.current_term()
    if term is None or datetime.now().date() > term.end:
      return

    if datetime.now().date() < term.start:
      week = -1
    else:
      week = term.term_week_of_date(datetime.today().date())

    weeks_set = set(eval(schedule.weeks))

    if len(set(range(0, week + 1)).intersection(weeks_set)) > 0:
      # Splitting
      s1 = Schedule(
          name=schedule.name,
          comments=schedule.comments,
          priority=schedule.priority,
          season=schedule.season,
          term=term
      )
      s2 = Schedule(
          name=schedule.name,
          comments=schedule.comments,
          priority=schedule.priority,
          season=schedule.season,
          term=term
      )

      if schedule.parent_schedule:
        s1.parent_schedule = schedule.parent_schedule
        s2.parent_schedule = schedule.parent_schedule
      else:
        s1.parent_schedule = schedule
        s2.parent_schedule = schedule

      sched_weeks = [int(x) for x in schedule.weeks.split(',')]
      s1_weeks = []
      s2_weeks = []
      for x in sched_weeks:
        if x <= week:
          s1_weeks.append(x)
        else:
          s2_weeks.append(x)

      s1.weeks = ','.join(map(str, s1_weeks))
      s2.weeks = ','.join(map(str, s1_weeks))

      s1.is_locked = True

      # only the most recent needs a query_filter.  Older ones don't need it.
      s2.query_filter = schedule.query_filter
      s1.save()
      s2.save()

      s1.trainees = current_set
      s2.trainees = new_set

      s1.save()
      s2.save()

      schedule.trainees = []
      schedule.is_locked = True
      schedule.save()
    else:
      # No split necessary
      schedule.trainees = new_set
      schedule.save()
