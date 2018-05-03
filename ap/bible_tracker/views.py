from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
# from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from terms.models import Term
from .models import BibleReading
from accounts.models import Trainee
from accounts.serializers import BasicUserSerializer
from rest_framework.renderers import JSONRenderer
from verse_parse.bible_re import *
from aputils.trainee_utils import trainee_from_user, is_TA, is_trainee
from aputils.decorators import group_required
import json
import datetime

# Default for First-year and Second-year bible reading
bible_books = testaments['ot'] + testaments['nt']
bible_books_list = [book[0] for book in bible_books]


def calcFirstYearProgress(user_checked_list):
  first_year_checked_list = [int(book_code.split("_")[1]) for book_code in user_checked_list.keys() if book_code.startswith('1_')]

  first_year_progress = 0
  for checked_book in first_year_checked_list:
    first_year_progress = first_year_progress + sum([int(chapter_verse_count) for chapter_verse_count in bible_books[checked_book][3]])
  return (first_year_checked_list, int(float(first_year_progress) / 31102.0 * 100))


def calcSecondYearProgress(user_checked_list):
  second_year_checked_list = [int(book_code.split("_")[1]) for book_code in user_checked_list.keys() if book_code.startswith('2_')]

  second_year_progress = 0
  for checked_book in second_year_checked_list:
    second_year_progress = second_year_progress + sum([int(chapter_verse_count) for chapter_verse_count in bible_books[checked_book][3]])
  return (second_year_checked_list, int(float(second_year_progress) / 7957.0 * 100))


@group_required(['training_assistant'])
def report(request):

  current_term = Term.current_term()
  term_id = current_term.id

  p = request.POST
  start_date = current_term.start.strftime('%Y%m%d')
  start_week = ""
  end_week = ""
  cutoff_range = "100"
  stat_options = []
  trainee_stats = []

  if request.method == 'POST':
    start_date = current_term.start.strftime('%Y%m%d')
    start_week = int(p.get('start_range', ''))
    end_week = int(p.get('end_range', ''))
    stat_options = [int(x) for x in p.getlist('stats[]')]
    cutoff_range = int(p.get('cutoff_range', ''))

    trainee_bible_readings = BibleReading.objects.filter(Q(trainee__type='R') | Q(trainee__type='C')).select_related('trainee').all()

    trainee_stats = []

    for trainee_bible_reading in trainee_bible_readings:
      stats = trainee_bible_reading.weekly_statistics(start_week, end_week, term_id)
      user_checked_list = trainee_bible_reading.books_read

      first_year_checked_list, first_year_progress = calcFirstYearProgress(user_checked_list)
      second_year_checked_list, second_year_progress = calcSecondYearProgress(user_checked_list)

      stats['percent_firstyear'] = first_year_progress
      stats['percent_secondyear'] = second_year_progress

      if stats['percent_complete_madeup'] < cutoff_range or cutoff_range == 100:
        trainee_stats.append(stats)

  context = {
      'start_date': start_date,
      'trainee_stats': trainee_stats,
      'stat_options': stat_options,
      'start_week': start_week,
      'end_week': end_week,
      'cutoff_range': cutoff_range,
  }
  return render(request, 'bible_tracker/report.html', context=context)


def index(request):
  my_user = request.user
  if is_TA(my_user):
      first = Trainee.objects.first().pk
      my_user = Trainee.objects.get(pk=request.GET.get('userId', first))

  # Default for Daily Bible Reading
  listJSONRenderer = JSONRenderer()
  l_render = listJSONRenderer.render
  trainees = Trainee.objects.all()
  trainees_bb = l_render(BasicUserSerializer(trainees, many=True).data)
  current_term = Term.current_term()
  term_id = current_term.id
  start_date = current_term.start.strftime('%Y%m%d')

  current_date = datetime.date.today()
  try:
    current_week = Term.reverse_date(current_term, current_date)[0]
  except ValueError:
    current_week = 19
  term_week_code = str(term_id) + "_" + str(current_week)

  try:
    trainee_bible_reading = BibleReading.objects.get(trainee=my_user)
    user_checked_list = trainee_bible_reading.books_read
  except ObjectDoesNotExist:
    user_checked_list = {}
    trainee_bible_reading = BibleReading(trainee=trainee_from_user(my_user), weekly_reading_status={term_week_code: "{\"status\": \"_______\", \"finalized\": \"N\"}"}, books_read={})
    trainee_bible_reading.save()
  except MultipleObjectsReturned:
    return HttpResponse('Multiple bible reading records found for trainee!')

  first_year_checked_list, first_year_progress = calcFirstYearProgress(user_checked_list)
  second_year_checked_list, second_year_progress = calcSecondYearProgress(user_checked_list)

  if term_week_code in trainee_bible_reading.weekly_reading_status:
    weekly_reading = trainee_bible_reading.weekly_reading_status[term_week_code]
    json_weekly_reading = json.loads(weekly_reading)
    weekly_status = str(json_weekly_reading['status'])
    finalized = str(json_weekly_reading['finalized'])
  else:
    weekly_status = "_______"
    finalized = "N"
  print weekly_status

  # Send data to the template!!!
  context = {
      'bible_books_list': bible_books_list,
      'first_year_checked_list': first_year_checked_list,
      'second_year_checked_list': second_year_checked_list,
      'first_year_progress': first_year_progress,
      'second_year_progress': second_year_progress,
      'weekly_status': weekly_status,
      'current_week': current_week,
      'start_date': start_date,
      'finalized': finalized,
      'trainees_bb': trainees_bb,
      'trainee': my_user,
  }
  return render(request, 'bible_tracker/index.html', context=context)


# AJAX for first-year and second-year bible reading
def updateBooks(request):
  my_user = request.user
  if request.method == 'GET':
    return HttpResponse('Error: This is a private endpoint, only accept post')
  elif request.method == 'POST':
    try:
      if is_TA(my_user):
        my_user = Trainee.objects.get(pk=request.POST['userId'])
      # Setup
      isChecked = request.POST['checked']
      myYear = request.POST['year']

      trainee_bible_reading = BibleReading.objects.get(trainee=my_user)
      book_code = request.POST['year'] + "_" + request.POST['book']

      # If checked, adds book to the database
      if isChecked == "true":
        trainee_bible_reading.books_read[book_code] = 'Y'
        trainee_bible_reading.save()
      # If not checked, deletes book from the database
      else:
        del trainee_bible_reading.books_read[book_code]
        trainee_bible_reading.save()

      # Calculates how much the progress bar changes for both first-year and second-year bible reading
      user_checked_list = trainee_bible_reading.books_read

      if(myYear == "1"):
        first_year_checked_list, first_year_progress = calcFirstYearProgress(user_checked_list)
        return HttpResponse(str(first_year_progress))
      else:
        second_year_checked_list, second_year_progress = calcSecondYearProgress(user_checked_list)
        return HttpResponse(str(second_year_progress))
    except ObjectDoesNotExist:
      return HttpResponse('Error from ajax call')
      # return HttpResponse(str(0))


def changeWeek(request):
  my_user = request.user
  if request.is_ajax():
    if is_TA(my_user):
      my_user = Trainee.objects.get(pk=request.GET['userId'])
    week_id = request.GET['week']
    current_term = Term.current_term()
    term_id = current_term.id
    term_week_code = str(term_id) + "_" + str(week_id)
    try:
      trainee_weekly_reading = BibleReading.objects.get(trainee=my_user).weekly_reading_status[term_week_code]
      json_weekly_reading = json.dumps(trainee_weekly_reading)
      print json_weekly_reading
    except (BibleReading.DoesNotExist, KeyError):
      trainee_weekly_reading = "{\"status\": \"_______\", \"finalized\": \"N\"}"
      json_weekly_reading = json.dumps(trainee_weekly_reading)
    return HttpResponse(json_weekly_reading, content_type='application/json')


def updateStatus(request):
  my_user = request.user
  if request.is_ajax():
    if is_TA(my_user):
      my_user = Trainee.objects.get(pk=request.POST['userId'])
    week_id = request.POST['week_id']
    print week_id
    weekly_status = request.POST['weekly_status']

    current_term = Term.current_term()
    term_id = current_term.id
    term_week_code = str(term_id) + "_" + str(week_id)

    try:
      trainee_bible_reading = BibleReading.objects.get(trainee=my_user)
      print trainee_bible_reading

    except BibleReading.DoesNotExist:
      trainee_bible_reading = BibleReading(trainee=my_user, weekly_reading_status={term_week_code: "{\"status\": \"_______\", \"finalized\": \"N\"}"}, books_read={})

    if term_week_code not in trainee_bible_reading.weekly_reading_status:
      trainee_bible_reading.weekly_reading_status[term_week_code] = "{\"status\": \"_______\", \"finalized\": \"N\"}"

    trainee_weekly_reading = trainee_bible_reading.weekly_reading_status[term_week_code]
    json_weekly_reading = json.loads(trainee_weekly_reading)
    print trainee_weekly_reading
    if str(json_weekly_reading['finalized']) == 'Y':
      return HttpResponse("Already finalized, so cannot save.", status=400)
    json_weekly_reading['status'] = weekly_status
    hstore_weekly_reading = json.dumps(json_weekly_reading)
    trainee_bible_reading.weekly_reading_status[term_week_code] = hstore_weekly_reading
    trainee_bible_reading.save()

    return HttpResponse(weekly_status)


def finalizeStatus(request):
  my_user = request.user
  if request.is_ajax():
    action = request.POST['action']
    week_id = request.POST['week_id']
    forced = request.POST.get('forced', False)

    current_term = Term.current_term()
    term_id = current_term.id
    term_week_code = str(term_id) + "_" + str(week_id)
    now = datetime.date.today()

    lastDayofWeek = Term.enddate_of_week(current_term, int(week_id))
    WedofNextWeek = lastDayofWeek + datetime.timedelta(days=3)
    # if not TA, cannot finalize till right time.
    if is_trainee(my_user):
      if forced:
        pass
      elif now >= WedofNextWeek or now < lastDayofWeek:
        return HttpResponse('Cannot finalize now', status=400)
    if is_TA(my_user):
      my_user = Trainee.objects.get(pk=request.POST['userId'])

    try:
      trainee_bible_reading = BibleReading.objects.get(trainee=my_user)

    except BibleReading.DoesNotExist:
      trainee_bible_reading = BibleReading(
          trainee=my_user,
          weekly_reading_status={
              term_week_code: "{\"status\": \"_______\", \"finalized\": \"N\"}"
          },
          books_read={}
      )

    if term_week_code not in trainee_bible_reading.weekly_reading_status:
      trainee_bible_reading.weekly_reading_status[term_week_code] = "{\"status\": \"_______\", \"finalized\": \"N\"}"

    trainee_weekly_reading = trainee_bible_reading.weekly_reading_status[term_week_code]
    json_weekly_reading = json.loads(trainee_weekly_reading)
    if action == "finalize" and str(json_weekly_reading['finalized']) == 'Y':
      return HttpResponse("Already finalized, so cannot finalize.", status=400)
    if action == "finalize":
      json_weekly_reading['finalized'] = "Y"
    if action == "unfinalize":
      json_weekly_reading['finalized'] = "N"
    hstore_weekly_reading = json.dumps(json_weekly_reading)
    trainee_bible_reading.weekly_reading_status[term_week_code] = hstore_weekly_reading
    trainee_bible_reading.save()

    return HttpResponse("Successfully finalized")
