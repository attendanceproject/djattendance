from django.db import models
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from attendance.models import Roll
from accounts.models import Trainee, TrainingAssistant
from services.models import Assignment
from terms.models import Term
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from aputils.utils import RequestMixin


""" leave slips models.py
The leavelslip module takes care of all logic related to... you guessed it, leave slips.


DATA MODELS:
  - LeaveSlip: an abstract class that contains information common to all leave
  leave slips. Extended by Individual and Group slips.

  - IndividualSlip: extends LeaveSlip generic class. A leave slip that only
  applies to one trainee (but can apply to multiple events)

  - GroupSlip: extends LeaveSlip generic class. A leave slip that can apply to
  a group of trainees, and covers a time range (rather than certain events).
"""


class LeaveSlip(models.Model, RequestMixin):

  class Meta:
    verbose_name = 'leave slip'
    ordering = ["-submitted"]
    abstract = True

  LS_TYPES = (
      ('CONF', 'Conference'),
      ('EMERG', 'Family Emergency'),
      ('FWSHP', 'Fellowship'),
      ('FUNRL', 'Funeral'),
      ('GOSP', 'Gospel'),
      ('INTVW', 'Grad School/Job Interview'),
      ('GRAD', 'Graduation'),
      ('MEAL', 'Meal Out'),
      ('NIGHT', 'Night Out'),
      ('OTHER', 'Other'),
      ('SERV', 'Service'),
      ('SICK', 'Sickness'),
      ('SPECL', 'Special'),
      ('WED', 'Wedding'),
      ('NOTIF', 'Notification Only'),
      ('TTRIP', 'Team Trip'),
  )

  LS_STATUS = (
      ('A', 'Approved'),
      ('P', 'Pending'),
      ('F', 'Marked for Fellowship'),
      ('D', 'Denied'),
      ('S', 'TA Sister Approved'),
  )

  type = models.CharField(max_length=5, choices=LS_TYPES)
  status = models.CharField(max_length=1, choices=LS_STATUS, default='P')

  # TA Assigned to this leave slip
  TA = models.ForeignKey(TrainingAssistant, blank=True, null=True, related_name="%(class)sslips", on_delete=models.SET_NULL)

  # TA informed
  TA_informed = models.ForeignKey(TrainingAssistant, blank=True, null=True, related_name="%(class)sslips_informed", on_delete=models.SET_NULL)

  trainee = models.ForeignKey(Trainee, related_name='%(class)ss', on_delete=models.SET_NULL, null=True)  # trainee who submitted the leave slip

  submitted = models.DateTimeField(auto_now_add=True)
  last_modified = models.DateTimeField(auto_now=True)
  finalized = models.DateTimeField(blank=True, null=True)  # when this leave-slip was approved/denied

  description = models.TextField(blank=True, null=True, verbose_name='Trainee description')  # trainee-supplied

  comments = models.TextField(blank=True, null=True, verbose_name='TA comments')  # for TA comments

  private_TA_comments = models.TextField(blank=True, null=True, verbose_name='Private TA comments')  # for inter-TA communication

  texted = models.BooleanField(default=False, verbose_name='texted attendance number')  # for sisters only

  informed = models.BooleanField(blank=True, default=False, verbose_name='informed TA')  # informed TA
  # let's keep this old informed field for now and delete it after we migrate
  # @property
  # def informed(self):
  #   return self.TA_informed is not None

  def get_trainee_requester(self):
    return self.trainee

  @property
  def classname(self):
    # returns whether slip is individual or group
    return str(self.__class__.__name__)[:-4].lower()

  def get_status_for_message(self):
    if self.status == 'S':
      return 'TA sister approved'
    return self.get_status_display().lower()

  def __init__(self, *args, **kwargs):
    super(LeaveSlip, self).__init__(*args, **kwargs)
    self.old_status = self.status

  def save(self, *args, **kwargs):
    if self.status in ['A', 'D'] and self.old_status in ['P', 'F', 'S']:
      self.finalized = datetime.now()
    super(LeaveSlip, self).save(*args, **kwargs)
    self.old_status = self.status

  # deletes dummy roll under leave slip.
  def delete_dummy_rolls(self, roll):
    if Roll.objects.filter(leaveslips__id=self.id, id=roll.id).exist() and roll.status == 'P':
      Roll.objects.filter(id=roll.id).delete()

  def __unicode__(self):
    return "[%s] %s - %s" % (self.submitted.strftime('%m/%d'), self.type, self.trainee)


class IndividualSlipManager(models.Manager):

  def get_queryset(self):
    queryset = super(IndividualSlipManager, self).get_queryset()
    if Term.current_term():
      start_date = Term.current_term().start
      end_date = Term.current_term().end
      return queryset.filter(rolls__date__gte=start_date, rolls__date__lte=end_date).distinct()
    else:
      return queryset


class IndividualSlip(LeaveSlip):

  class Meta:
    verbose_name = 'personal slip'

  objects = IndividualSlipManager()

  rolls = models.ManyToManyField(Roll, related_name='leaveslips')
  # these fields are for meals and nights out
  location = models.TextField(blank=True, null=True)
  host_name = models.TextField(blank=True, null=True)
  host_phone = models.CharField(max_length=25, null=True, blank=True)
  hc_notified = models.TextField(blank=True, null=True)

  @receiver(pre_delete)
  def delete_individualslip(sender, instance, **kwargs):
    if isinstance(instance, IndividualSlip):
      for roll in instance.rolls.all():
        if roll.status == 'P':
          Roll.objects.filter(id=roll.id).delete()

  @property
  def late(self):
    roll = self.rolls.order_by('-date').first()
    if roll:
      date = roll.date
      time = roll.event.end
      return self.submitted > datetime.combine(date, time) + timedelta(hours=48)
    else:
      return False

  @property
  def periods(self):
    rolls = self.rolls.order_by('date')
    if rolls.count() < 1:
      return list()
    first_roll = rolls.first()
    last_roll = rolls.last()
    first_period = Term.current_term().period_from_date(first_roll.date)
    last_period = Term.current_term().period_from_date(last_roll.date)
    return range(first_period, last_period + 1)

  @property
  def events(self):
    evs = []
    for roll in self.rolls.all():
      roll.event.date = roll.date
      roll.event.start_datetime = datetime.combine(roll.date, roll.event.start)
      roll.event.end_datetime = datetime.combine(roll.date, roll.event.end)
      evs.append(roll.event)
    return evs

  def get_date(self):
    return self.rolls.all().order_by('date').first().date

  def get_absolute_url(self):
    return reverse('leaveslips:individual-update', kwargs={'pk': self.id})

  def get_ta_update_url(self):
    return reverse('leaveslips:individual-update', args=(self.id,))

  def get_update_url(self):
    return reverse('leaveslips:individual-update', kwargs={'pk': self.id})


class GroupSlipManager(models.Manager):

  def get_queryset(self):
    queryset = super(GroupSlipManager, self).get_queryset()
    if Term.current_term():
      start_date = Term.current_term().start
      end_date = Term.current_term().end
      return queryset.filter(start__gte=start_date, end__lte=end_date)
    else:
      return queryset


class GroupSlipAllManager(models.Manager):
  def get_queryset(self):
    return super(GroupSlipAllManager, self).get_queryset()


class GroupSlip(LeaveSlip):

  class Meta:
    verbose_name = 'group slip'

  objects = GroupSlipManager()
  objects_all = GroupSlipAllManager()

  start = models.DateTimeField()
  end = models.DateTimeField()
  trainees = models.ManyToManyField(Trainee, related_name='groupslip')  # trainees included in the leave slip
  # Field to relate GroupSlips to Service Assignments
  service_assignment = models.ForeignKey(Assignment, blank=True, null=True, verbose_name="Service", on_delete=models.SET_NULL)

  def get_date(self):
    return self.start.date()

  @property
  def events(self):
    return self.get_trainee_requester().events_in_date_range(self.start, self.end)

  @property
  def periods(self):
    first_period = Term.current_term().period_from_date(self.start.date())
    last_period = Term.current_term().period_from_date(self.end.date())
    return range(first_period, last_period + 1)

  def trainee_list(self):
    return ', '.join([t.full_name for t in self.trainees.all()])

  @property
  def late(self):
    return self.submitted > self.end + timedelta(hours=48)

  def get_update_url(self):
    return reverse('leaveslips:group-update', kwargs={'pk': self.id})

  def get_ta_update_url(self):
    return reverse('leaveslips:group-update', args=(self.id,))

  def get_absolute_url(self):
    return reverse('leaveslips:group-update', kwargs={'pk': self.id})
