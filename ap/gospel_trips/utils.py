import json
import os
from datetime import datetime

import requests
from django.conf import settings  # for access to MEDIA_ROOT
from requests.exceptions import ConnectionError

from .constants import ANSWER_TYPES, IATA_API_KEY
from .models import AnswerChoice, GospelTrip, Question, Section

JSON_FILE_DIR = os.path.join('gospel_trips', 'exports')
APP_ROOT = os.path.join(settings.SITE_ROOT, 'gospel_trips')


def export_to_json(gt):
  '''gt is a GospelTrip object'''

  file_path = os.path.join(settings.MEDIA_ROOT, JSON_FILE_DIR)
  full_path = os.path.join(file_path, gt.name.replace(' ', '_') + '.json')
  fdir = os.path.dirname(full_path)
  if not os.path.isdir(fdir):
    os.makedirs(fdir)

  form = {'name': gt.name}
  form['sections'] = []
  for section in gt.section_set.all():
    form['sections'].append({
        'name': section.name,
        'show': section.show,
        '_order': section._order})

    form['sections'][-1]['questions'] = []
    for question in section.question_set.all():
      form['sections'][-1]['questions'].append({
          'instruction': question.instruction,
          'answer_type': question.answer_type,
          'label': question.label,
          'answer_required': question.answer_required,
          '_order': question._order})
  j = json.dumps(form, indent=2)
  f = open(full_path, 'w')
  print >> f, j  # TODO: Python3
  f.close()
  return full_path


def import_from_json(path):
  '''this function does not validate. Please use export_to_json. '''
  f = open(path)
  data = json.load(f)
  try:
    gt = GospelTrip(name=data['name'] + ' (Copy)', open_time=datetime(2018, 1, 1), close_time=datetime(2018, 1, 2))
    gt.save()
    for section in data['sections']:
      sec = Section(_order=section['_order'], name=section['name'], show=section['show'], gospel_trip=gt)
      sec.save()

      for question in section['questions']:
        quest = Question(
            _order=question['_order'], instruction=question['instruction'], label=question.get('label', ''),
            answer_type=question['answer_type'], answer_required=question['answer_required'], section=sec)
        quest.save()
    return 1
  except AttributeError:
    return 0


def get_answer_types():
  choices = [('', '---------')]
  types = ANSWER_TYPES[:]
  types.extend(AnswerChoice.objects.values_list('name', flat=True))
  choices.extend([(a, a) for a in types])
  return choices


def update_airport_codes():
  url = "https://iatacodes.org/api/v6/airports?api_key=" + IATA_API_KEY
  try:
    r = requests.get(url).json()
    return [res['code'] for res in r['response']]
  except (ConnectionError, KeyError) as e:
    print e
    return []


def get_airport_codes():
  try:
    full_path = os.path.join(APP_ROOT, 'airports.json')
    f = open(full_path)
    data = json.load(f)
    return [res['code'] for res in data['response']]
  except Exception:
    return []


def udpate_airline_codes():
  url = "https://iatacodes.org/api/v7/airlines?api_key=" + IATA_API_KEY
  try:
    r = requests.get(url).json()
    return [res['iata_code'] for res in r['response']]
  except (ConnectionError, KeyError) as e:
    print e
    return []


def get_airline_codes():
  try:
    full_path = os.path.join(APP_ROOT, 'airlines.json')
    f = open(full_path)
    data = json.load(f)
    return [res['iata_code'] for res in data['response']]
  except Exception:
    return []


def section_order_validator(data, newest_key):
  post_data = data.get("section-order", "")
  if post_data:
    if "None" in post_data:
      post_data = post_data.replace("None", "0").split(',')
    order_list = [int(d) for d in post_data]
    if newest_key in order_list:
      order_list.remove(0)
    else:
      order_list = [newest_key if x == 0 else x for x in order_list]
    return order_list
  return None
