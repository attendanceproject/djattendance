import datetime

from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse

from accounts.models import User, Trainee
from aputils.utils import RequestMixin


class Announcement(models.Model, RequestMixin):

  class Meta:
    verbose_name = "announcement"
    ordering = ['-announcement_date']

  ANNOUNCE_STATUS = (
      ('A', 'Approved'),
      ('P', 'Pending'),
      ('F', 'Marked for Fellowship'),
      ('D', 'Denied'),
  )

  ANNOUNCE_TYPE = (
      ('CLASS', 'In-class'),
      ('SERVE', 'On the server')
  )

  status = models.CharField(max_length=1, choices=ANNOUNCE_STATUS, default='P')
  type = models.CharField(max_length=5, choices=ANNOUNCE_TYPE, default='CLASS')

  date_requested = models.DateTimeField(auto_now_add=True)
  author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
  TA_comments = models.TextField(null=True, blank=True)
  trainee_comments = models.TextField(null=True, blank=True)
  is_popup = models.BooleanField(default=False, blank=True)
  announcement = models.TextField()
  announcement_date = models.DateField()
  announcement_end_date = models.DateField(null=True, blank=True)
  trainees_show = models.ManyToManyField(Trainee, related_name="announcement_show", blank=True)
  trainees_read = models.ManyToManyField(Trainee, related_name="announcement_read", blank=True)
  all_trainees = models.BooleanField(default=True)

  def __unicode__(self):
    try:
      return '<Announcement %s> by %s' % (self.announcement, self.author)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  @staticmethod
  def announcements_for_today(trainee, is_popup=False):
    today = datetime.date.today()
    if is_popup:
      announcements = Announcement.objects.all()
    else:
      announcements = Announcement.objects.filter(announcement_end_date__gte=today)

    announcements = announcements\
        .filter(Q(type='SERVE', status='A',
                announcement_date__lte=today,
                is_popup=is_popup) &
                (Q(all_trainees=True) | Q(trainees_show=trainee)))\
        .exclude(trainees_read=trainee)
    return announcements

  @staticmethod
  def get_create_url():
    return reverse('announcements:announcement-request')

  def get_absolute_url(self):
    return reverse('announcements:announcement-detail', kwargs={'pk': self.id})

  def get_update_url(self):
    return reverse('announcements:announcement-update', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('announcements:announcement-delete', kwargs={'pk': self.id})

  def get_trainee_requester(self):
    return self.author

  def get_category(self):
    return self.get_type_display()

  def get_status(self):
    return self.get_status_display()

  def get_date_created(self):
    return self.date_requested

  @staticmethod
  def get_detail_template():
    return 'announcement_list/description.html'

  @staticmethod
  def get_table_template():
    return 'announcement_detail/table.html'

  @staticmethod
  def get_ta_button_template():
    return 'announcement_list/ta_buttons.html'

  @staticmethod
  def get_button_template():
    return 'announcement_list/buttons.html'
