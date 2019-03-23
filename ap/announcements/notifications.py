import datetime
import json
from itertools import chain

from django.contrib import messages
from django.core.urlresolvers import reverse

from models import Announcement
from absent_trainee_roster.models import Roster
from lifestudies.models import Summary
from bible_tracker.models import BibleReading
from leaveslips.models import IndividualSlip, GroupSlip
from web_access.models import WebRequest
from house_requests.models import MaintenanceRequest, LinensRequest, FramingRequest
from audio.models import AudioRequest
from room_reservations.models import RoomReservation
from terms.models import Term
from attendance.models import RollsFinalization
from aputils.trainee_utils import is_trainee, trainee_from_user
from datetime import timedelta


def get_popups(request):
  if not is_trainee(request.user):
    return []
  trainee = trainee_from_user(request.user)
  announcements = Announcement.announcements_for_today(trainee, is_popup=True)
  return announcements


def get_announcements(request):
  notifications = []
  if is_trainee(request.user):
    trainee = trainee_from_user(request.user)
    notifications = chain(discipline_announcements(trainee),
                          server_announcements(trainee),
                          bible_reading_announcements(trainee),
                          request_statuses(trainee),
                          attendance_announcements(trainee),
                          hc_reminder(trainee))
  # sort on severity level of message
  return sorted(notifications, lambda a, b: b[0] - a[0])


def request_statuses(trainee):
  requests = chain(
      IndividualSlip.objects.filter(trainee=trainee, status='F'),
      GroupSlip.objects.filter(trainee=trainee, status='F'),
      WebRequest.objects.filter(trainee=trainee, status='F'),
      Announcement.objects.filter(author=trainee, status='F'),
      MaintenanceRequest.objects.filter(trainee_author=trainee, status='F'),
      LinensRequest.objects.filter(trainee_author=trainee, status='F'),
      FramingRequest.objects.filter(trainee_author=trainee, status='F'),
      AudioRequest.objects.filter(trainee_author=trainee, status='F'),
      Summary.objects.filter(discipline__trainee=trainee, fellowship=True),
      RoomReservation.objects.filter(requester=trainee, status='F')
  )
  message = 'Your <a href="{url}">{request}</a> has been marked for fellowship'
  return [(messages.ERROR, message.format(url=reverse('attendance:attendance-submit'), request=req._meta.verbose_name)) if isinstance(req, IndividualSlip) else (messages.ERROR, message.format(url=req.get_absolute_url(), request=req._meta.verbose_name)) for req in requests]


def bible_reading_announcements(trainee):
  term = Term.current_term()
  week = term.term_week_of_date(datetime.date.today())
  url = reverse('bible_tracker:index')
  fmtString = 'You have not finalized your <a href="{url}">Bible reading</a>'
  try:
    reading = BibleReading.objects.get(trainee=trainee)
  except BibleReading.DoesNotExist:
    return [(messages.WARNING, fmtString.format(url=url))]
  unfinalizedWeeks = []
  fmtString += ' for week {week} yet.'
  for w in range(week):
    key = str(term.id) + "_" + str(w)
    if key in reading.weekly_reading_status:
      json_weekly_reading = json.loads(reading.weekly_reading_status[key])
      if str(json_weekly_reading['finalized']) == 'N':
        unfinalizedWeeks.append("<a href='/bible_tracker?week=" + str(w) + "'>" + str(w) + "</a>")
    else:
      unfinalizedWeeks.append("<a href='/bible_tracker?week=" + str(w) + "'>" + str(w) + "</a>")
  return [(messages.WARNING, fmtString.format(url=url, week=', '.join(unfinalizedWeeks)))] if unfinalizedWeeks else []


def server_announcements(trainee):
  announcements = Announcement.announcements_for_today(trainee)
  return [(messages.INFO, a.announcement) for a in announcements]


def discipline_announcements(trainee):
  url = reverse('lifestudies:discipline_list')
  message = 'Life-study Summary due for {inf}. <a href="{url}">Still need: {due}</a>'
  notifications = map(
      lambda d: (messages.WARNING, message.format(url=url, inf=d.get_infraction_display(), due=d.get_num_summary_due())),
      filter(lambda d: d.get_num_summary_due() > 0, trainee.discipline_set.all())
  )
  return notifications


def attendance_announcements(trainee):
  today = datetime.date.today()
  term = Term.current_term()
  week = term.term_week_of_date(today)
  if trainee.self_attendance:
    try:
      trainee_rf = RollsFinalization.objects.get(trainee=trainee, events_type='EV')
      finalized_weeks = [int(x) for x in trainee_rf.weeks.split(',')]
    except (RollsFinalization.DoesNotExist, ValueError):
      finalized_weeks = []

    weeks = []
    for w in range(week):
      if w not in finalized_weeks:
        weeks.append(str(w))

  else:
    weeks = []
  url = reverse('attendance:attendance-submit')
  message = 'You have not finalized your <a href="{url}">Personal attendance</a> for week {week}. '
  return [(messages.WARNING, message.format(url=url, week=', '.join(weeks)))] if weeks else []

def hc_reminder(trainee):
  if trainee.HC_status() and trainee.house.gender != 'C':
    today = datetime.date.today()
    last_unreported_roster = Roster.objects.filter(unreported_houses=trainee.house).latest('date')
    days_difference = (today - last_unreported_roster.date).days
    last_unreported = last_unreported_roster.date.strftime('%A')
    if last_unreported == "Monday":
      if 0 < days_difference < 4:
        if days_difference == 1:
          day = 'today'
        elif days_difference == 2:
          day = 'yesterday'
        else:
          day = 'on ' + (last_unreported_roster.date + timedelta(days=1)).strftime('%b %d')
        message = "Your house didn't submit a house attendance {day}, please remember to do so. This message will disappear if your house submits house attendance for three consecutive days."
        return [(messages.WARNING, message.format(day=day))]
    else:
      if days_difference < 4:
        if days_difference == 0:
          day = 'today'
        elif days_difference == 1:
          day = 'yesterday'
        else:
          day = 'on ' + last_unreported_roster.date.strftime('%b %d')
        message = "Your house didn't submit a house attendance {day}, please remember to do so. This message will disappear if your house submits house attendance for three consecutive days."
        return [(messages.WARNING, message.format(day=day))]
  return []
