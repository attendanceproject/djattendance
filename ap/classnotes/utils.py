from datetime import date, datetime
from itertools import chain

from accounts.models import Trainee
from attendance.models import Roll
from leaveslips.models import IndividualSlip, GroupSlip
from terms.models import Term

from .models import Classnotes


def assign_classnotes(week=None):
  term = Term.current_term()
  start = term.start
  end = term.end
  if week is not None:
    end = term.enddate_of_week(week)
  for trainee in Trainee.objects.all().iterator():
    update_classnotes_list(trainee)
    assign_individual_classnotes(trainee, start, end)


def assign_individual_classnotes(trainee, start, end):
  '''
    Assign Classnotes based on class absences
    - Any special leave of absence (eg. interviews, wedding):
      1 class notes / absence
    - Sickness & Unexcused absences & Others:
      1 class notes the number of absence >= 3
  '''
  # look at trainee's absences (for class event).
  # Increment absence_counts based on classname (HStore)
  regular_absence_counts = {}
  rolls = trainee.rolls.all().filter(date__gte=start, date__lte=end, status='A', event__type='C').order_by('date').select_related('event')

  # Afternoon classes
  rolls = rolls.exclude(event__class_type='AFTN')
  # Monday Revival Meeting
  rolls = rolls.exclude(event__name='Monday Revival Meeting')
  rolls = rolls.exclude(event__name='Morning Revival Fellowship')

  for roll in rolls.iterator():
    classname = roll.event.name
    leavesliplist = list(get_leaveslip(trainee, roll))
    if len(leavesliplist) > 0:
      for leaveslip in leavesliplist:
        # Special: Wedding, Graduation, Funeral, Interview.
        if leaveslip.type in ['INTVW', 'GRAD', 'WED', 'FUNRL']:
          generate_classnotes(trainee, roll, 'S')

        # Regular: Sickness, Unexcused, Others, Fellowship, Notif only
        if leaveslip.type in ['OTHER', 'SICK', 'FWSHP', 'SPECL', 'NOTIF']:
          if classname in regular_absence_counts:
            regular_absence_counts[classname] += 1
            if (regular_absence_counts[classname]) > 2:
              generate_classnotes(trainee, roll, 'R')
          else:
            regular_absence_counts[classname] = 1
        # Missed classes with conference or service leave slips results in no class notes
    else:
      # no leave slip == unexcused absence
      if classname in regular_absence_counts:
        regular_absence_counts[classname] += 1
        if (regular_absence_counts[classname]) > 2:
          generate_classnotes(trainee, roll, 'R')
      else:
        regular_absence_counts[classname] = 1


# Delete classnotes that are no longer needed based on changes
# made to the trainee's rolls (ie. the trainee was not absent in class)
def update_classnotes_list(trainee):
  classnotes_list = Classnotes.objects.filter(trainee=trainee, status='U').prefetch_related('event')
  for classnotes in classnotes_list.iterator():
    roll = Roll.objects.filter(trainee=trainee, event=classnotes.event, date=classnotes.date).prefetch_related('event').first()
    if roll and not roll.status == 'A':
      classnotes.delete()
    if roll and roll.status == 'A':
      # check if there is an updated leave slip for it
      # delete classnotes if the leave slip is a conference or service
      leavesliplist = get_leaveslip(trainee, roll)
      for leaveslip in leavesliplist:
        if leaveslip.type == 'CONF' or leaveslip.type == 'SERV':
          classnotes.delete()
          break


def calculate_number_classnotes(trainee, roll):
  return Classnotes.objects.filter(trainee=trainee, event=roll.event, type='R').count()


def get_leaveslip(trainee, roll):
  individualslips = IndividualSlip.objects.filter(trainee=trainee, status='A', rolls__in=[roll])
  roll_start_datetime = datetime.combine(roll.date, roll.event.start)
  roll_end_datetime = datetime.combine(roll.date, roll.event.end)
  groupslips = GroupSlip.objects.filter(trainees=trainee, status='A', start__lte=roll_end_datetime, end__gte=roll_start_datetime)
  return chain(individualslips, groupslips)


def generate_classnotes(trainee, roll, type):
  classnotes = Classnotes.objects.filter(trainee=trainee, event=roll.event, date=roll.date).first()
  if not classnotes:
    classnotes = Classnotes(trainee=trainee, event=roll.event, date=roll.date, date_assigned=date.today(), type=type, content='')
  else:
    # In the case of multiple leave slips for one absence,
    # special case has a higher priority.
    if classnotes.type == 'R' and type == 'S':
      classnotes.type = type
  classnotes.save()


# TODO
def generate_reports():
  return None


# TODO
def generate_individual_reports(trainee):
  return None


def classnotes_owed(trainee):
  classnotes = Classnotes.objects.filter(trainee=trainee, status='U')
  return len(classnotes)
