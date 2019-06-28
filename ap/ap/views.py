import json
from datetime import date

from announcements.notifications import get_announcements, get_popups
from aputils.trainee_utils import is_TA, is_trainee, trainee_from_user
from aputils.utils import WEEKDAY_CODES
from bible_tracker.models import (EMPTY_WEEKLY_STATUS, UNFINALIZED_STR,
                                  BibleReading)
from bible_tracker.views import EMPTY_WEEK_CODE_QUERY
from dailybread.models import Portion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from house_requests.models import MaintenanceRequest
from services.models import WeekSchedule, Worker
from terms.models import FIRST_WEEK, LAST_WEEK, Term


@login_required
def home(request):
  user = request.user
  trainee = trainee_from_user(user)
  worker = None

  # Set default values
  current_week = 19
  weekly_status = EMPTY_WEEKLY_STATUS
  finalized_str = UNFINALIZED_STR
  designated_list = []
  assigned_list = []
  service_day = []

  # Default for Daily Bible Reading
  current_term = Term.current_term()
  term_id = current_term.id

  if is_trainee(user):
    worker = Worker.objects.get(trainee=user)

    if request.GET.get('week_schedule'):
      current_week = request.GET.get('week_schedule')
      current_week = int(current_week)
      current_week = current_week if current_week < LAST_WEEK else LAST_WEEK
      current_week = current_week if current_week > FIRST_WEEK else FIRST_WEEK
      cws = WeekSchedule.get_or_create_week_schedule(trainee, current_week)
    else:
      # Do not set as user input.
      current_week = Term.current_term().term_week_of_date(date.today())
      cws = WeekSchedule.get_or_create_week_schedule(trainee, current_week)

    # try:
    #   # Do not set as user input.
    #   current_week = Term.current_term().term_week_of_date(date.today())
    #   cws = WeekSchedule.get_or_create_week_schedule(trainee, current_week)

    # except ValueError:
    #   cws = WeekSchedule.get_or_create_current_week_schedule(trainee)

    term_week_code = str(term_id) + "_" + str(current_week)

    try:
      trainee_bible_reading = BibleReading.objects.get(trainee=user)
    except ObjectDoesNotExist:
      trainee_bible_reading = BibleReading(
        trainee=trainee_from_user(user),
        weekly_reading_status={term_week_code: EMPTY_WEEK_CODE_QUERY},
        books_read={})
      trainee_bible_reading.save()
    except MultipleObjectsReturned:
      return HttpResponse('Multiple bible reading records found for trainee!')

    if term_week_code in trainee_bible_reading.weekly_reading_status:
      weekly_reading = trainee_bible_reading.weekly_reading_status[term_week_code]
      json_weekly_reading = json.loads(weekly_reading)
      weekly_status = str(json_weekly_reading['status'])
      finalized_str = str(json_weekly_reading['finalized'])

    worker_assignments = worker.assignments.filter(week_schedule=cws)
    designated_list = list(service.encode("utf-8") for service in worker_assignments.filter(service__category__name="Designated Services").values_list('service__name', flat=True))
    assigned_list = list(service.encode("utf-8") for service in worker_assignments.exclude(service__category__name="Designated Services").values_list('service__name', flat=True))
    service_day = list(worker_assignments.exclude(service__category__name="Designated Services").values_list('service__weekday', flat=True))

  data = {
      'daily_nourishment': Portion.today(),
      'user': user,
      'worker': worker,
      'isTrainee': is_trainee(user),
      'trainee_info': BibleReading.weekly_statistics,
      'current_week': current_week,
      'weekly_status': weekly_status,
      'weeks': Term.all_weeks_choices(),
      'finalized': finalized_str,
      'weekday_codes': json.dumps(WEEKDAY_CODES),
      'service_day': json.dumps(service_day),
      'assigned_list': json.dumps(assigned_list),
      'designated_list': json.dumps(designated_list),
  }

  notifications = get_announcements(request)
  for notification in notifications:
    tag, content = notification
    messages.add_message(request, tag, content)
  data['popups'] = get_popups(request)

  if is_trainee(user):
    trainee = trainee_from_user(user)
    # Bible Reading progress bar
    trainee_bible_reading = BibleReading.objects.filter(trainee=trainee).first()
    if trainee_bible_reading is None:
      data['bible_reading_progress'] = 0
    else:
      _, year_progress = BibleReading.calcBibleReadingProgress(trainee_bible_reading, user)
      data['bible_reading_progress'] = year_progress

  # condition for maintenance brothers
  elif is_TA(user) and user.has_group(['facility_maintenance']) and user.groups.all().count() == 1:
    data['house_requests'] = MaintenanceRequest.objects.all()
    data['request_status'] = MaintenanceRequest.STATUS

  return render(request, 'index.html', context=data)


def custom404errorview(request):
  ctx = {
    'image_path': 'img/404error.png',
    'page_title': 'Page Not Found'
  }
  return render(request, 'error.html', context=ctx)


def custom500errorview(request):
  ctx = {
    'image_path': 'img/500error.png',
    'page_title': 'Internal Server Error'
  }
  return render(request, 'error.html', context=ctx)


def custom502errorview(request):
  ctx = {
    'image_path': 'img/502error.png',
    'page_title': 'Bad Gateway Error'
  }
  return render(request, 'error.html', context=ctx)


def custom503errorview(request):
  ctx = {
    'image_path': 'img/503error.png',
    'page_title': 'Service Unavailable'
  }
  return render(request, 'error.html', context=ctx)


def custom504errorview(request):
  ctx = {
    'image_path': 'img/504error.png',
    'page_title': 'Gateway Timeout'
  }
  return render(request, 'error.html', context=ctx)


def printerinstructions(request):
  ctx = {
    'image_path': 'img/printer.jpg',
    'page_title': 'Printer Instructions',
  }
  return render(request, 'printer.html', context=ctx)
