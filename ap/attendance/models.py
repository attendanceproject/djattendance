from datetime import date, datetime

from django.db import models
from schedules.models import Event
from accounts.models import Trainee, User

""" attendance models.py
The attendance module takes care of data and logic directly related
to tracking attendance. It does not handle things such as schedules
or leave slips.

DATA MODELS:
  - Roll: an attendance record per trainee, per event.
      for example, if 10 trainees are supposed to be at an event,
      then there will be 10 roll objects associated to that event,
      as well as each trainee.
"""


class Roll(models.Model):

  ROLL_STATUS = (
      ('P', 'Present'),
      ('A', 'Absent'),
      ('T', 'Tardy'),
      ('U', 'Uniform'),
      ('L', 'Left Class')
  )

  event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)

  trainee = models.ForeignKey(Trainee, null=True, related_name='rolls', on_delete=models.SET_NULL)

  status = models.CharField(max_length=1, choices=ROLL_STATUS)

  # once a roll is finalized, it can no longer be edited
  # except by a TA, attendance monitor, or other admin
  finalized = models.BooleanField(default=False)

  notes = models.CharField(max_length=200, blank=True)

  # the one who submitted this roll
  # for first year should be an attendance monitor, house coordinator, team monitor, or YPC monitor
  # for second year it can either by a second year trainee and/or any of the roles listed above
  # for second year there can be two roll objects per event, one submitted by the second year trainee and one submitted by a monitor, this is for audits

  submitted_by = models.ForeignKey(User, null=True, related_name='submitted_rolls', on_delete=models.SET_NULL)

  # when the roll was last updated
  last_modified = models.DateTimeField(auto_now=True)

  # the date of the event that corresponds with the roll.
  date = models.DateField()

  def __unicode__(self):
    # return status, trainee name, and event
    return "[%s] %s @ [%s] %s" % (self.date, self.event, self.status, self.trainee)

  class Meta:
    ordering = ['-last_modified']

  # only second year trainees have the possibility of duplicate rolls for the purpose of audit
  # if only one roll exists for this event for this trainee on date, then this is the main roll
  # else if there are two rolls for the same trainee, same event and on the same date
  # if the trainee is on self_attenance, return true if the trainee and submitted_by are the same person
  # else if the trainee is not on self attendance, return true if the roll is a present with a leaveslip attached
  # else if the status is not present, return true if the submitted_by and the trainee are not the same
  @property
  def is_main_roll(self):  # this is what shows up on the personal attendance record
    dup_rolls = Roll.objects.filter(trainee=self.trainee, event=self.event, date=self.date)
    if dup_rolls.count() == 1:
      # includes if present roll w/ leave slip by non self-att -- b/c dup_rolls.count = 1
      if self.trainee.self_attendance:
          return True if self.submitted_by == self.trainee else False
      return True

    elif self.trainee.self_attendance:  # main roll if submitted by roll's trainee
      return True if self.submitted_by == self.trainee else False
    # Not on self-attendance
    else:  # main roll if submitted by other trainee
      # includes if present roll w/ leave slip by non self-att -- b/c another trainee submits att
      return False if self.submitted_by == self.trainee else True

  @staticmethod
  def update_or_create(validated_data):
    '''
      Creates roll if not existing, else update
      Reteurn None if event doesn't exist for roll
    '''

    event = validated_data['event']
    roll_date = validated_data['date']
    if type(roll_date) != type(date.today()):
      roll_date = datetime.strptime(roll_date, '%Y-%m-%d').date()
    submitted_by = validated_data['submitted_by']

    # checks if event exists for given event and date
    if not Event.objects.filter(name=event.name, weekday=roll_date.weekday()).exists():
      return None

    newroll, created = Roll.objects.update_or_create(**validated_data)

    return newroll
