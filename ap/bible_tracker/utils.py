import json
from datetime import date, timedelta

from aputils.trainee_utils import is_trainee, trainee_from_user
from terms.models import Term

from .models import BibleReading


def is_week_finalized(user, week):
    finalized = True
    term = Term.current_term()
    try:
      if is_trainee(user):
        trainee = trainee_from_user(user)
        today = date.today()
        term_week_code = str(term.id) + "_" + str(week)
        try:
          trainee_weekly_reading = BibleReading.objects.get(trainee=trainee).weekly_reading_status[term_week_code]
          json_weekly_reading = json.loads(trainee_weekly_reading)
        except (BibleReading.DoesNotExist, KeyError):
          trainee_weekly_reading = "{\"status\": \"_______\", \"finalized\": \"N\"}"
          json_weekly_reading = json.loads(trainee_weekly_reading)
        try:
          if today > term.startdate_of_week(week) + timedelta(8):
            if str(json_weekly_reading['finalized']) == 'N':
              finalized = False
        except TypeError:
          pass
    except AttributeError:
      pass
    return finalized


def unfinalized_week(user):
  current_term = Term.current_term()
  if date.today() < current_term.start:
      return None
    # current week = up to week we want to access + 1
  current_week = Term.reverse_date(current_term, date.today())[0]
  if date.today() <= current_term.startdate_of_week(current_week) + timedelta(1):
      # Cannot access past week's because today is less than Wednesday
      current_week = current_week - 1
  for week in range(0, current_week):
    if not is_week_finalized(user, week):
      return week
