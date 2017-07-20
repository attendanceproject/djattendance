from datetime import datetime

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property

from terms.models import Term
from schedules.models import Event
from .utils import audio_dir

fs = FileSystemStorage(location=audio_dir())

class AudioFileManager(models.Manager):
  def filter_week(self, week):
    term = Term.current_term()
    return sorted(filter(lambda f: f.week == week and f.term == term, AudioFile.objects.all()), key=lambda f: f.date)

class AudioFile(models.Model):

  objects = AudioFileManager()

  # File name format is something like this: B1-01 2017-03-02 DSady.mp3
  audio_file = models.FileField(storage=fs)

  def __unicode__(self):
    return '<Audio File {0}>'.format(self.audio_file.name)

  @property
  def code(self):
    try:
      return self.audio_file.name.split('_')[0].split('-')[0]
    except:
      return ''

  @property
  def date(self):
    try:
      return datetime.strptime(self.audio_file.name.split('_')[1], '%Y-%m-%d').date()
    except Exception as e:
      return

  @cached_property
  def term(self):
    try:
      t = filter(lambda term: term.is_date_within_term(self.date), Term.objects.all())
      return t[0] if t else None
    except:
      return

  @property
  def event(self):
    try:
      return Event.objects.get(av_code=self.code)
    except:
      return

  @property
  def week(self):
    try:
      return int(self.audio_file.name.split('_')[0].split('-')[1])
    except:
      return

  @property
  def speaker(self):
    try:
      return self.audio_file.name.split('_')[-1].split('.')[0]
    except:
      return
