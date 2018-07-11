from datetime import datetime
from terms.models import Term

ROLL_STATUS = (
    ('A', 'Attended'),
    ('S', 'Service'),
    ('I', 'Illness'),
    ('F', 'Fellowship'),
    ('U', 'Unexcused Absence')
)

LOCATIONS = (
    ('TC', 'Training Center'),
    ('MCC', 'Ministry Conference Center'),
    ('Other', 'Other')
)


def count(attendance, status):
  vals = attendance.values()
  return len(filter(lambda v: v == status, vals))


def attendance_stats(semi):
  att = semi.attendance
  d = {}
  for code, status in ROLL_STATUS:
    d[status.split(' ')[0]] = count(att, code)
  d['Absences'] = 5 - d['Attended']
  return d


def location_form_available():
  week = Term.current_term().term_week_of_date(datetime.now())
  return week >= 17 or week <= 19


def attendance_form_available():
  week = Term.current_term().term_week_of_date(datetime.now())
  return week >= 18 or week <= 19
