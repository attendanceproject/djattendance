from datetime import datetime

from audio.models import AudioFile
from audio.utils import parse_audio_name, AUDIO_DATE_FORMAT

TEST_NAMES = [
    'YP-08 2018-04-21 PBradley and EYeow.mp3',
    'MF-05 2018-03-28 JPrim&PDeng.mp3',
    'PT-05 2018-02-24 The Vision and the Ministry of the Age MChen.mp3',
    'GE-15 2018-06-07 DWise.mp3',
    'LS-06 2018-04-05 ALim.mp3',
    'PT-00 2018-02-19 An Opening Word & First-term Testimonies RScatterday & DHigashi.mp3',
    'MR-06 2018-04-02 DCP presentation & Gospel Trip DSady & BBuntain.mp3',
    'MF-11 2018-05-09 Y1 PDeng.mp3',
    'FW-14 2018-06-02 4T DWise & RGood.mp3',
    'FW-10 2018-05-03 4T MNiu & DYoon.mp3',
    'FW-10 2018-05-05 Medical School Fellowship DChiang & DCuthbertson.mp3',
    'CH-02 2018-03-08 WHale.mp3',
    'B1-10 2018-05-03 DHo.mp3',
    'MR-01 2018-02-26 First Term Testimonies, Gospel Trip Reports, Team Selection.mp3',
    'MR-05 2018-03-26 Morning Revival Fellowship ALi & PDeng.mp3',
]


def create_audio_file(name):
  a = AudioFile()
  a.audio_file.name = name
  return a


def test_audio_code():
  codes = [
      'YP',
      'MF',
      'PT',
      'GE',
      'LS',
      'PT',
      'MR',
      'MF',
      'FW',
      'FW',
      'FW',
      'CH',
      'B1',
      'MR',
      'MR',
  ]
  for i, name in enumerate(TEST_NAMES):
    assert parse_audio_name(name).code == codes[i]
    assert create_audio_file(name).code == codes[i]


def test_audio_week():
  weeks = [
      8,
      5,
      5,
      15,
      6,
      0,
      6,
      11,
      14,
      10,
      10,
      2,
      10,
      1,
      5
  ]
  for i, name in enumerate(TEST_NAMES):
    assert parse_audio_name(name).week == weeks[i]
    aFile = create_audio_file(name)
    assert aFile.week == (weeks[i] if aFile.code != 'PT' else 0)


def test_audio_date():
  dates = [
      '2018-04-21',
      '2018-03-28',
      '2018-02-24',
      '2018-06-07',
      '2018-04-05',
      '2018-02-19',
      '2018-04-02',
      '2018-05-09',
      '2018-06-02',
      '2018-05-03',
      '2018-05-05',
      '2018-03-08',
      '2018-05-03',
      '2018-02-26',
      '2018-03-26',
  ]
  for i, name in enumerate(TEST_NAMES):
    d = datetime.strptime(dates[i], AUDIO_DATE_FORMAT).date()
    assert parse_audio_name(name).date == d
    assert create_audio_file(name).date == d


def test_audio_title():
  titles = [
      '',
      '',
      'The Vision and the Ministry of the Age',
      '',
      '',
      'An Opening Word & First-term Testimonies',
      'DCP presentation & Gospel Trip',
      'Y1',
      '4T',
      '4T',
      'Medical School Fellowship',
      '',
      '',
      'First Term Testimonies, Gospel Trip Reports, Team Selection',
      'Morning Revival Fellowship',
  ]
  for i, name in enumerate(TEST_NAMES):
    assert parse_audio_name(name).title == titles[i]
    assert create_audio_file(name).title == titles[i]


def test_audio_speakers():
  speakers = [
      ['PBradley', 'EYeow'],
      ['JPrim', 'PDeng'],
      ['MChen'],
      ['DWise'],
      ['ALim'],
      ['RScatterday', 'DHigashi'],
      ['DSady', 'BBuntain'],
      ['PDeng'],
      ['DWise', 'RGood'],
      ['MNiu', 'DYoon'],
      ['DChiang', 'DCuthbertson'],
      ['WHale'],
      ['DHo'],
      [],
      ['ALi', 'PDeng'],
  ]
  for i, name in enumerate(TEST_NAMES):
    assert parse_audio_name(name).speakers == speakers[i]
    assert create_audio_file(name).speakers == speakers[i]
