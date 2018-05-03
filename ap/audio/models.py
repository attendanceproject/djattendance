from datetime import datetime
import re

from django.db import models
from django import forms
from django.utils.functional import cached_property
from django.core.urlresolvers import reverse
from django.conf import settings

from terms.models import Term
from classnotes.models import Classnotes
from schedules.models import Event
from accounts.models import Trainee
from aputils.decorators import for_all_methods
from aputils.utils import OverwriteStorage, RequestMixin

# run from live server to mount A/V files for read-only access
# sudo mount -t cifs -o username=guest //10.0.8.254/Audio/ audio


def valid_audiofile_name(name):
  if not re.match(AUDIO_FILE_FORMAT, name) or re.match(PRETRAINING_FORMAT, name):
    return False
  return True


def validate_audiofile_name(name):
  if not valid_audiofile_name(name):
    raise forms.ValidationError('Invalid audio file name format')


fs = OverwriteStorage(
    location=settings.AUDIO_FILES_ROOT,
    base_url=settings.AUDIO_FILES_URL,
    file_permissions_mode=0o755
)


def order_audio_files(files):
  lambdas = [
      lambda f: f.audio_file.name.split(' ')[2],
      lambda f: f.code,
      lambda f: f.event.name if f.event else '',
      lambda f: f.week,
  ]
  for l in lambdas:
      files = sorted(files, key=l)
  return files


def order_decorator(filter_function):
  def ordered_filter(*args, **kwargs):
    filtered = filter_function(*args, **kwargs)
    return order_audio_files(filtered)
  return ordered_filter


@for_all_methods(order_decorator)
class AudioFileManager(models.Manager):
  def filter_list(self, week, trainee):
    term = Term.current_term()
    # return pre-training recordings
    if week == 0:
      return filter(lambda f: f.code == 'PT' and f.term == term, self.all())
    # also filters year: if not a class with a Y1/Y2 designation or if the class year matches trainee's year, add file to files list
    return filter(lambda f: f.week == week and f.term == term and f.can_trainee_view(trainee), self.all())

  def filter_term(self, term):
    return filter(lambda f: f.term == term, self.all())

  def get_file(self, event, date):
    return filter(lambda f: f.event == event and f.date == date, self.all())


# class codes: MR, FM, WG, TG, CH, GK, GW, GE, B1/B2, LS, SP, E1/E2, NJ, YP, FW
# B1-01 2017-03-02 DSady.mp3
AUDIO_FILE_FORMAT = re.compile(r"^\w{2}-\d{2} \d{4}-\d{2}-\d{2} .+\.mp3$")
# PT-00 2017-02-18 An Opening Word DHigashi.mp3
PRETRAINING_FORMAT = re.compile(r"^\w{2}-\d{2} \d{4}-\d{2}-\d{2} \w+( \w+)* \w+\.mp3$")
SEPARATOR = ' '


class AudioFile(models.Model):

  objects = AudioFileManager()

  audio_file = models.FileField(storage=fs, validators=[validate_audiofile_name])

  @property
  def fellowship_code(self):
    if not self.code == 'FW':
      return ''
    return self.audio_file.name.split(SEPARATOR)[2]

  def can_trainee_view(self, trainee):
    class_visible = not self.year or self.year == (trainee.current_term + 1) / 2
    code = self.fellowship_code
    if code == 'YP':
      fellowship_code = 'YP' in trainee.team.code
    elif code == 'HC':
      fellowship_code = trainee.groups.filter(name='HC').exists()
    elif code == '4T':
      fellowship_code = trainee.current_term = 4
    elif code == 'PS':
      fellowship_code = trainee.groups.filter(name='PSRP_facilitator').exists()
    else:
      fellowship_code = True
    return class_visible and fellowship_code

  def __unicode__(self):
    return '<Audio File {0}>'.format(self.audio_file.name)

  @property
  def code(self):
    return self.audio_file.name.split(SEPARATOR)[0].split('-')[0]

  @property
  def date(self):
    return datetime.strptime(self.audio_file.name.split(SEPARATOR)[1], '%Y-%m-%d').date()

  @property
  def display_name(self):
    return (self.event.name + self.pretraining_class() if self.event else self.audio_file.name.split('.')[0])

  @cached_property
  def term(self):
    t = filter(lambda term: term.is_date_within_term(self.date), Term.objects.all())
    return t[0] if t else None

  @cached_property
  def event(self):
    return Event.objects.filter(av_code=self.code).first()

  def pretraining_class(self):
    if self.code in ('PT', 'FW'):
      return ': ' + ' '.join(self.audio_file.name.split(SEPARATOR)[2:-1])
    return ''

  @property
  def week(self):
    if self.code == 'PT':
      return 0
    return int(self.audio_file.name.split(SEPARATOR)[0].split('-')[1])

  @property
  def speaker(self):
    return self.audio_file.name.split(SEPARATOR)[-1].split('.')[0]

  @property
  def year(self):
    if self.code in ('WG', 'TG', 'E1', 'B1', 'YP'):
      return 1
    elif self.code in ('B2', 'LS', 'E2', 'NJ'):
      return 2
    else:  # main classes: 'MR', 'FM', 'CH', 'GK', 'GW', 'GE', 'B2', 'SP', FW')
      return 0

  def get_full_name(self):
    return 'Week {0} {1} by {2}'.format(self.week, self.display_name, self.speaker)

  def request(self, trainee):
    return self.audio_requests.filter(trainee_author=trainee).first()

  def classnotes(self, trainee):
    return Classnotes.objects.filter(trainee=trainee, event=self.event, date=self.date).first()

  def has_leaveslip(self, trainee):
    has_leaveslip = False
    attendance_record = trainee.attendance_record
    excused_events = filter(lambda r: r['attendance'] == 'E', attendance_record)
    for record in excused_events:
      d = datetime.strptime(record['start'].split('T')[0], '%Y-%m-%d').date()
      if record['event'] == self.event and d == self.date:
        has_leaveslip = True
    return has_leaveslip

  def can_download(self, trainee):
    request = self.request(trainee)
    return self.has_leaveslip(trainee) or (request and request.status == 'A')

  def get_absolute_url(self):
    return reverse('audio:audio-update', kwargs={'pk': self.id})


class AudioRequestManager(models.Manager):
  def filter_term(self, term):
    ids = map(lambda f: f.id, AudioFile.objects.filter_term(term))
    return self.filter(audio_requested__in=ids).distinct()


class AudioRequest(models.Model, RequestMixin):

  objects = AudioRequestManager()

  AUDIO_STATUS = (
      ('A', 'Approved'),
      ('P', 'Pending'),
      ('F', 'Marked for Fellowship'),
      ('D', 'Denied'),
  )
  status = models.CharField(max_length=1, choices=AUDIO_STATUS, default='P')
  date_requested = models.DateTimeField(auto_now_add=True)
  trainee_author = models.ForeignKey(Trainee, on_delete=models.SET_NULL, null=True)
  TA_comments = models.TextField(null=True, blank=True)
  trainee_comments = models.TextField()
  audio_requested = models.ManyToManyField(AudioFile, related_name='audio_requests')

  @staticmethod
  def get_button_template():
    return 'audio/ta_buttons.html'

  @staticmethod
  def get_ta_button_template():
    return 'audio/ta_buttons.html'

  @staticmethod
  def get_detail_template():
    return 'audio/ta_detail.html'

  def get_absolute_url(self):
    return reverse('audio:audio-update', kwargs={'pk': self.id})

  def get_trainee_requester(self):
    return self.trainee_author

  def get_status(self):
    return self.get_status_display()

  def get_date_created(self):
    return self.date_requested

  def get_category(self):
    return ', '.join(map(lambda a: a.code + ' week ' + str(a.week), self.audio_requested.all()))
