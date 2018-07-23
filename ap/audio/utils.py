import sys
import re
from collections import namedtuple
from datetime import datetime

AudioFileName = namedtuple('AudioFileName', [
    'code',
    'week',
    'date',
    'title',
    'speakers',
])

SEPARATOR = ' '
DASH = '-'
AUDIO_DATE_FORMAT = '%Y-%m-%d'

# Updated 6/16/2018
SPEAKERS = [
    'ALim',
    'ALi',
    'BAdamo',
    'BDanker',
    'CBirchler',
    'CKennard',
    'DBernier',
    'DDong',
    'DHigashi',
    'DHo',
    'DKoo',
    'DSady',
    'DWise',
    'DYoon',
    'EMarks',
    'ERomero',
    'EYeow',
    'JLee',
    'JOladele',
    'JPrim',
    'KLii',
    'MChen',
    'MNiu',
    'OTuktarov',
    'PBradley',
    'PDeng',
    'PHarvey',
    'RGood',
    'RKangas',
    'RScatterday',
    'SYowell',
    'TEspinosa',
    'VMolina',
    'WHale',
    'AYu',
    'BBuntain',
    'BPhilips',
    'CWilde',
    'DTaylor',
    'JRosario',
    'KWalker',
    'MMiller',
    'MStewart',
    'RGraver',
    'POnica',
    'TGoetz',
    'DChiang',
    'DCuthbertson'
]

SPEAKER_REGEXES = [
   (speaker, r'\b({0})\b'.format(speaker)) for speaker in SPEAKERS
]


def parse_audio_name(name):
  name = name[:-4]  # remove .mp3 from end of file name
  code = name.split(SEPARATOR)[0].split(DASH)[0]
  week = int(name.split(SEPARATOR)[0].split(DASH)[1])
  file_date = datetime.strptime(name.split(SEPARATOR)[1], AUDIO_DATE_FORMAT).date()
  speaker_index, speakers = _parse_speakers(name)
  title = _parse_title(name, speaker_index)
  return AudioFileName(code, week, file_date, title, speakers)


def _parse_speakers(name):
  first_index = sys.maxint
  speakers = []
  for speaker, regex in SPEAKER_REGEXES:
    match = re.search(regex, name)
    if match:
      index = match.start()
      speakers.append((index, speaker))
      first_index = min(first_index, index)
  speakers.sort()
  speakers = [s[1] for s in speakers]
  return first_index, speakers


def _parse_title(name, speaker_index):
  without_speakers = name[:speaker_index - 1]
  return SEPARATOR.join(without_speakers.split(SEPARATOR)[2:])
