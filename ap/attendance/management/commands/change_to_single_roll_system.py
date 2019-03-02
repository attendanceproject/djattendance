from accounts.models import TrainingAssistant, User
from attendance.models import Roll
from terms.models import Term

from django.core.management.base import BaseCommand

TAS = list(TrainingAssistant.objects.all())
AMS = list(User.objects.filter(groups__name="attendance_monitors").exclude(groups__name="training_assistant").exclude(groups__name="dev"))

class Command(BaseCommand):
  # to use: python ap/manage.py change_to_single_roll_system
  def _change_to_single_roll_system(self):
    rolls = Roll.objects.all()
    if Term.current_term():
      start_date = Term.current_term().start
      end_date = Term.current_term().end
      rolls = rolls.filter(date__gte=start_date, date__lte=end_date)
    rolls = list(rolls)
    i = 0
    while rolls:
      roll = rolls[i]
      trainee = roll.trainee
      event = roll.event
      date = roll.date

      duplicates = Roll.objects.filter(trainee=trainee, event=event.id, date=date)
      if duplicates.count() == 1:
        dup = duplicates.first()
        if dup.submitted_by != trainee:
          dup.submitted_by = trainee
          dup.save()
      else:
        trainee_roll = duplicates.filter(submitted_by=trainee)
        TA_roll = duplicates.filter(submitted_by__in=TAS)
        AM_roll = duplicates.filter(submitted_by__in=AMS)

        if trainee_roll.count() == 1 and TA_roll.count() == 1 and AM_roll.count() == 0:
          if TA_roll[0].last_modified >= trainee_roll[0].last_modified:
            print "Deleting:", trainee_roll[0].id, trainee_roll[0].submitted_by, trainee_roll[0].trainee
            trainee_roll.delete()
          else:
            print "Deleting:", TA_roll[0].id, TA_roll[0].submitted_by, TA_roll[0].trainee
            TA_roll.delete()
        elif (trainee_roll.count() == 1 and TA_roll.count() == 0 and AM_roll.count() == 1) or \
              (trainee_roll.count() == 0 and TA_roll.count() == 1 and AM_roll.count() == 1):
          print "Deleting:", AM_roll[0].id, AM_roll[0].submitted_by, AM_roll[0].trainee
          AM_roll.delete()
        elif trainee_roll.count() == 1 and TA_roll.count() == 1 and AM_roll.count() == 1:
          print "Check the rolls related to:", trainee_roll[0].event
        else:
          #there should only be one of each max
          print "Check the rolls related to:", trainee_roll[0].event

      rolls.pop()

  def handle(self, *args, **options):
    print '* Let it begin *'
    self._change_to_single_roll_system()
