from datetime import datetime
from collections import OrderedDict
from copy import copy


class EventUtils:
  # Handles ev.day correclty and returns all ev in terms of week, weekday
  @staticmethod
  def compute_prioritized_event_table(w_tb, weeks, evs, priority):
    '''
    Handles priority collision detection and normalizes ev.day events
    '''
    for w in weeks:
      for ev in evs:
        # skip if current week is not for one off event
        if ev.day and ev.week_from_date(ev.day) != w:
          continue
        # absolute date is already calculated
        weekday = ev.weekday
        ev.priority = priority
        # hacking ordered dict to behave like a set
        day_evnts = w_tb.setdefault((w, weekday), set())

        # check for conflicts.
        # append ev to list, check for any conflicts (intersectinng time), replace any intersecting evs
        for day_evnt in day_evnts.copy():
          if day_evnt.check_time_conflict(ev):
            # replace ev if conflict
            # delete any conflicted evs
            day_evnts.remove(day_evnt)
        # append after remove all conflicting events
        day_evnts.add(ev)
    return w_tb

  # Create list from table and add absolute date to event
  @staticmethod
  def export_event_list_from_table(w_tb, start_datetime=None, end_datetime=None):
    event_list = []
    for (w, d), evs in w_tb.items():
      # Sort the events in each week
      evs = sorted(evs, key=lambda x: (x.start, x.end))
      for ev in evs:
        date = ev.date_for_week(w)
        # calc date from w
        ev.start_datetime = datetime.combine(date, ev.start)
        ev.end_datetime = datetime.combine(date, ev.end)
        if (start_datetime is None or start_datetime <= ev.start_datetime) and (end_datetime is None or end_datetime >= ev.end_datetime):
          # append a copy of ev to answer list you will return. B/c same event can have multiple instance across different weeks
          event_list.append(copy(ev))
    return event_list

  @staticmethod
  def collapse_priority_event_trainee_table(weeks, schedules, t_set):
    '''
      Go through all schedules and override conflicting events trainee roster list
      with trainee list that has higher priority

      Returns table {ev: set([trainee1, trainee2])} in order of increasing start/end time of ev
    '''

    # Prioritized weekly event table
    # {(w, weekday): OrderedDict(ev: set([trainee1, trainee2,]))}
    w_tb = OrderedDict()

    wk_set = set([int(w) for w in weeks])

    for schedule in schedules:
      # order events so collision detection behavior is very predictable
      evs = schedule.events.order_by('weekday', 'start', 'end')
      valid_weeks = set([int(x) for x in schedule.weeks.split(',')]).intersection(wk_set)
      t_intersect = set(schedule.trainees.all()).intersection(t_set)
      for w in valid_weeks:
        for ev in evs:
          # skip if current week is not for one off event
          if ev.day and ev.week_from_date(ev.day) != w:
            continue
          # absolute date is already calculated
          weekday = ev.weekday
          ev.priority = schedule.priority
          day_evnts = w_tb.setdefault((w, weekday), OrderedDict())

          # check for conflicts.
          # append ev to list, check for any conflicts (intersectinng time), replace any intersecting evs
          # Cop day_evnts b/c later on will modified same events over multi-weeks to add start_time
          for day_evnt in day_evnts.copy():
            if day_evnt.check_time_conflict(ev):
              # replace ev if conflict
              # delete any conflicted evs
              # remove trainees in t_intersect from conflicting event and add new event with trainees in it
              day_evnts[day_evnt] -= t_intersect

          # Add new ev to day with t_intersect trainees inside
          # if ev already exist, add trainess onto that event
          if ev not in day_evnts:
            day_evnts[ev] = t_intersect.copy()
          else:
            day_evnts[ev] |= t_intersect.copy()

    return w_tb

  @staticmethod
  def export_typed_ordered_roll_list(w_tb, type):
    # OrderedDict so events are in order of start/end time when iterated out unto the template
    event_trainee_tb = []
    for (w, d), evs in w_tb.items():
      for ev, ts in evs.items():
        # only calculate ev for type wanted
        if (type == ev.type) or (type == 'RF' and ev.monitor == 'RF'):
          date = ev.date_for_week(w)
          # calc date from w
          ev.start_datetime = datetime.combine(date, ev.start)
          ev.end_datetime = datetime.combine(date, ev.end)
          # append a copy of ev to answer list you will return. B/c same event can have multiple instance across different weeks
          event_trainee_tb.append((copy(ev), ts))

    event_trainee_tb.sort(key=lambda ev_ts: ev_ts[0].start_datetime)
    return event_trainee_tb

  # Gets all trainees attending event in week from w_tb table
  @staticmethod
  def get_trainees_attending_event_in_week(w_tb, event, week):
    week = int(week)
    weekday = event.get_uniform_weekday()
    evs = w_tb.setdefault((week, weekday), set())

    if event in evs:
      return evs[event]
    else:
      return set()

  @staticmethod
  def flip_roll_list(roll_table):
    '''
      Takes {event: Set([trainee1, trainee2,])} to flips to pivot on trainees =>
      {trainee1: [event1, event2]}

      We had to use list for events because they're not hashed properly into a dictionary as keys
    '''
    t_ev_tb = {}
    ordered_ev_list = []

    for ev, ts in roll_table:
      # Only add event if it has none-zero # of trainees
      if len(ts) > 0:
        ordered_ev_list.append(ev)
      for t in ts:
        t_ev_tb.setdefault(t, []).append(ev)

    return (ordered_ev_list, t_ev_tb)
