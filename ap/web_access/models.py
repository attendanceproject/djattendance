from datetime import date, datetime, timedelta

from django.db import models
from django.core.urlresolvers import reverse

from accounts.models import Trainee
from aputils.utils import RequestMixin


""" web-access models.py
This module handles requests for Internet access either made by trainees or for
a guest by their MAC address.

REQUEST
  - This model represents a web-access request submitted by a trainee or
  guest.

"""


class WebRequest(models.Model, RequestMixin):

  TYPE_APPROVAL_STATUS_CHOICES = (
      ('P', 'Pending'),
      ('A', 'Approved'),
      ('F', 'Marked for Fellowship'),
      ('D', 'Denied'),
  )

  TYPE_REASON_CHOICES = (
      ('Go', 'Gospel'),
      ('Sr', 'Service'),
      ('GA', 'Graduate Application'),
      ('Fs', 'Fellowship'),
      ('Ot', 'Other'),
  )

  MINUTES_CHIOCES = (
      (15, '15 minutes'),
      (30, '30 minutes'),
      (45, '45 minutes'),
      (60, '1 hour'),
      (90, '1 hour 30 minutes'),
      (120, '2 hours'),
      (180, '3 hours'),
      (240, '4 hours'),
      (300, '5 hours'),
  )

  status = models.CharField(choices=TYPE_APPROVAL_STATUS_CHOICES, max_length=2, default='P')
  reason = models.CharField(choices=TYPE_REASON_CHOICES, max_length=2)
  minutes = models.PositiveSmallIntegerField(choices=MINUTES_CHIOCES)
  date_assigned = models.DateTimeField(auto_now_add=True)
  time_started = models.DateTimeField(auto_now_add=False, blank=True, null=True)
  date_expire = models.DateField()
  mac_address = models.CharField(blank=True, null=True, max_length=60)
  trainee = models.ForeignKey(Trainee, blank=True, null=True, on_delete=models.SET_NULL)
  comments = models.TextField()
  TA_comments = models.TextField(blank=True, null=True)
  urgent = models.BooleanField(default=False)
  guest_name = models.CharField(max_length=60, blank=True, null=True)

  def get_category(self):
    return self.get_reason_display()

  def get_date_created(self):
    return self.date_assigned

  def get_status(self):
    return self.get_status_display()

  @property
  def requester_name(self):
    if self.guest_name:
      return self.guest_name
    if self.trainee:
      return self.trainee.full_name
    return "Guest"

  def get_trainee_requester(self):
    return self.trainee

  @staticmethod
  def get_create_url():
    return reverse('web_access:web_access-create')

  def get_update_url(self):
    return reverse('web_access:web_access-update', kwargs={'pk': self.id})

  def get_absolute_url(self):
    return reverse('web_access:web_access-detail', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('web_access:web_access-delete', kwargs={'pk': self.id})

  @staticmethod
  def get_detail_template():
    return 'web_access/web_access_description.html'

  @staticmethod
  def get_table_template():
    return 'web_access/web_access_detail_table.html'

  @staticmethod
  def get_ta_button_template():
    return 'web_access/ta_buttons.html'

  @staticmethod
  def get_button_template():
    return 'web_access/buttons.html'

  # Sort by trainee name
  class Meta:
    ordering = ['date_assigned', 'date_expire', 'trainee__firstname']

  @property
  def is_expired(self):
    past_expiration_date = date.today() > self.date_expire
    used_up = False
    if self.time_started:
      used_up = self.time_started + timedelta(minutes=self.minutes) < datetime.now()
    return past_expiration_date or used_up

  def __unicode__(self):
    try:
      if self.trainee is None:
        fullname = self.guest_name
      else:
        fullname = self.trainee.full_name
      return '[{reason}] {name}. Duration: {duration}'.format(
          name=fullname,
          reason=self.reason,
          duration=self.minutes
      )
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
