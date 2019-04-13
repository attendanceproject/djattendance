from django.core.urlresolvers import reverse
from django.db import models
from accounts.models import Trainee
from terms.models import Term
from datetime import datetime, timedelta

""" graduation models.py

This module allows for administering and taking of graduation surveys, including survey
creation, editing, taking, and stats.

DATA MODELS:
  - Survey: Abstract model for surveys
  - GradAdmin: Allows admin to control all surveys
"""


class GradAdmin(models.Model):

  SHOW_CHOICES = (
      ('NO', 'No'),
      ('YES', 'Yes'),
      ('SHOW', 'Show only')
  )

  term = models.OneToOneField(Term, blank=True)

  # display status
  testimony_show_status = models.CharField(max_length=4, choices=SHOW_CHOICES, default='NO')
  consideration_show_status = models.CharField(max_length=4, choices=SHOW_CHOICES, default='NO')
  website_show_status = models.CharField(max_length=4, choices=SHOW_CHOICES, default='NO')
  outline_show_status = models.CharField(max_length=4, choices=SHOW_CHOICES, default='NO')
  remembrance_show_status = models.CharField(max_length=4, choices=SHOW_CHOICES, default='NO')
  misc_show_status = models.CharField(max_length=4, choices=SHOW_CHOICES, default='NO')

  # survey due date
  testimony_due_date = models.DateField(blank=True, null=True)
  consideration_due_date = models.DateField(blank=True, null=True)
  website_due_date = models.DateField(blank=True, null=True)
  outline_due_date = models.DateField(blank=True, null=True)
  remembrance_due_date = models.DateField(blank=True, null=True)
  misc_due_date = models.DateField(blank=True, null=True)

  # speaking trainees
  speaking_trainees = models.ManyToManyField(Trainee, blank=True)

  # remembrance character limit
  remembrance_char_limit = models.IntegerField(blank=True, null=True)

  def __unicode__(self):
    try:
      return "[Graduation] %s" % (self.term)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  def get_due_date_of(self, survey_name):
    DUE_DATE_OF = {
        'Testimony': self.testimony_due_date,
        'Consideration': self.consideration_due_date,
        'Website': self.website_due_date,
        'Outline': self.outline_due_date,
        'Remembrance': self.remembrance_due_date,
        'Misc': self.misc_due_date,
    }
    return DUE_DATE_OF[survey_name]

  def get_show_status_of(self, survey_name):
    SHOW_STATUS_OF = {
        'Testimony': self.testimony_show_status,
        'Consideration': self.consideration_show_status,
        'Website': self.website_show_status,
        'Outline': self.outline_show_status,
        'Remembrance': self.remembrance_show_status,
        'Misc': self.misc_show_status,
    }
    return SHOW_STATUS_OF[survey_name]

  def get_absolute_url(self):
    return reverse('graduation:grad-admin')


class Survey(models.Model):

  SHOW_CHOICES = (
      ('NO', 'no'),
      ('YES', 'yes'),
      ('SHOW', 'show only')
  )

  # grad admin controls the survey
  grad_admin = models.ForeignKey(GradAdmin, null=True, on_delete=models.SET_NULL)

  # trainee filling out the survey
  trainee = models.ForeignKey(Trainee, null=True, on_delete=models.SET_NULL)

  @property
  def name_of_model(self):
    return self.__class__.__name__

  @property
  def due_date(self):
    d = self.grad_admin.get_due_date_of(self.name_of_model)
    if d:
      return d
    else:
      return datetime.now().date() + timedelta(days=1)

  @property
  def show_status(self):
    return self.grad_admin.get_show_status_of(self.name_of_model)

  def get_absolute_url(self):
    rev_url = 'graduation:' + self.name_of_model.lower() + '-view'
    return reverse(rev_url)

  @classmethod
  def responded_number(cls, term):
    qset = cls.objects.filter(grad_admin__term=term)
    return len(filter(lambda o: o.responded, qset))

  def __unicode__(self):
    try:
      return "[%s] %s - %s" % (self.name_of_model, self.due_date, self.show_status)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  def menu_title(self):
    return self.name_of_model.title()

  class Meta:
    abstract = True


class Testimony(Survey):

  top_experience = models.TextField(null=True)
  encouragement = models.TextField(null=True)
  overarching_burden = models.TextField(null=True)
  highlights = models.TextField(null=True)

  @property
  def responded(self):
    return self.top_experience or self.encouragement or self.overarching_burden or self.highlights


class Consideration(Survey):

  XB_CHOICES = (
      ('YES', 'Yes, I would like to go to FTTA-XB'),
      ('OPEN', 'Open and considering going to FTTA-XB'),
      ('NO', "No, it's not likely I will go to FTTA-XB"),
      ('OTHER', "Other"),
  )

  attend_XB = models.CharField(max_length=5, choices=XB_CHOICES, null=True)

  XB_other = models.TextField(null=True, blank=True, max_length=65) # only filled out if "other" under attend_XB is selected.

  FELLOWSHIP_CHOICES = (
      ('YES', 'Yes'),
      ('NO', 'No'),
      ('OTHER', 'I have not fellowshipped yet, but am scheduled to fellowship on')
  )

  fellowshipped = models.CharField(max_length=5, choices=FELLOWSHIP_CHOICES, null=True)

  fship_date = models.DateField(blank=True, null=True) # only required if "other" under fellowshipped is selected.

  consideration_plan = models.TextField(null=True, max_length=250)

  comments = models.TextField(blank=True, null=True, max_length=150)

  @property
  def responded(self):
    return self.attend_XB or self.fellowshipped or self.consideration_plan


class Website(Survey):

  SCALE = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))

  post_training_website = models.SmallIntegerField(choices=SCALE, null=True)

  reasons = models.TextField(null=True)

  features = models.TextField(null=True)

  FREQ = (
      ("NEVER", "Never"),
      ("MONTHLY", "1-2 times a month"),
      ("WEEKLY", "1-2 times a week"),
      ("OFTEN", "3-5 times a week"),
      ("DAILY", "Everyday")
  )

  frequency = models.CharField(max_length=7, choices=FREQ, null=True)

  doing = models.CharField(max_length=200, null=True)

  residence = models.CharField(max_length=50, null=True)

  email = models.CharField(max_length=50, null=True)

  phone_number = models.CharField(max_length=25, null=True)

  @property
  def responded(self):
    return self.post_training_website or self.reasons or self.features or self.frequency or self.doing or self.residence or self.email or self.phone_number


class Outline(Survey):

  sections = models.CharField(max_length=50, null=True)

  OUTLINE_CHOICES = (
      ("TRUTH", "Speak on a truth point"),
      ("EXP", "Speak my experience")
  )
  participate = models.CharField(max_length=5, choices=OUTLINE_CHOICES, null=True)
  sentence = models.CharField(max_length=500, null=True)

  speaking_section = models.CharField(max_length=50, null=True)
  speaking = models.TextField(blank=True, null=True)

  @property
  def responded(self):
    return self.sections or self.participate


class Remembrance(Survey):

  remembrance_text = models.TextField(blank=True, null=True)
  remembrance_reference = models.TextField(blank=True, null=True)

  @property
  def responded(self):
    return self.remembrance_text or self.remembrance_text


class Misc(Survey):

  grad_invitations = models.SmallIntegerField(blank=True, null=True)
  grad_dvd = models.SmallIntegerField(blank=True, null=True)

  @property
  def responded(self):
    return self.grad_invitations is not None or self.grad_dvd is not None

  def menu_title(self):
    return "Invites & DVDs"
