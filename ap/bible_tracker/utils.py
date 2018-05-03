from datetime import timedelta, date
from .models import BibleReading
from terms.models import Term
from aputils.trainee_utils import is_trainee, trainee_from_user
import json


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
  for week in range(Term.current_term().term_week_of_date(date.today()) - 1, 0, -1):
    if not is_week_finalized(user, week):
      return week
