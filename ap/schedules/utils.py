from datetime import timedelta


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
  from schedules.models import Schedule
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
