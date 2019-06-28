from datetime import datetime

from terms.models import Term

ROLL_STATUS = (
    ('P', 'Present'),
    ('S', 'Service'),
    ('A', 'Absent')
)

LOCATIONS = (
    ('TC', 'Training Center'),
    ('MCC', 'Ministry Conference Center'),
    ('Other', 'Other')
)

REQUEST_STATUS = (
    ('P', 'Pending'),
    ('A', 'Accepted'),
    ('D', 'Denied'),
    ('F', 'Fellowship'),
)


def count(attendance, status):
  vals = attendance.values()
  return len(filter(lambda v: v == status, vals))


def attendance_stats(semi):
  att = semi.attendance
  d = {}
  for code, status in ROLL_STATUS:
    d[status.split(' ')[0]] = count(att, code)
  d['Absences'] = 5 - d['Present']
  return d


def semi_form_available():
  week = Term.current_term().term_week_of_date(datetime.now())
  return week >= 17 and week <= 19


def semi_annual_training():
  ct = Term.current_term()
  if ct.season == 'Spring':
    return 'July ' + str(ct.year)
  else:
    return 'December ' + str(ct.year)
