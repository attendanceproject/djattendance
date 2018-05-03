from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from attendance.models import *
from schedules.models import *
from accounts.models import *
from terms.models import Term
from leaveslips.models import *
from datetime import *
import random
import pickle

def new_roll(trainees=[], am=[]):
    events = Event.objects.filter(type="C")
    status = ['P', 'A', 'T', 'U', 'L']
    for trainee in trainees:
        if trainee.gender == "B":
            cur_am = random.choice(am.filter(gender="B"))
        elif trainee.gender == "S":
            cur_am = random.choice(am.filter(gender="S"))
        for e in events:
            random.seed()
            week = Term.current_term().term_week_of_date(date.today())
            trainee_stat = random.choice(status)
            if trainee_stat == "P":
                Roll(event=e, trainee=trainee, status=random.choice(status), submitted_by=cur_am, date=Term.get_date(Term.current_term(), week, e.weekday)).save()
            elif trainee_stat == "A":
                Roll(event=e, trainee=trainee, status="A", submitted_by=cur_am, date=Term.get_date(Term.current_term(), week, e.weekday)).save()
            else:
                Roll(event=e, trainee=trainee, status=random.choice(['A', trainee_stat]), submitted_by=cur_am, date=Term.get_date(Term.current_term(), week, e.weekday)).save()

class Command(BaseCommand):
    # to use: python ap/manage.py populate_rolls --settings=ap.settings.dev
    def _create_rolls(self):
        # change the array below to get different trainees
        trainees = Trainee.objects.filter(current_term__gt=2)
        am = Trainee.objects.filter(groups__name="attendance_monitors")
        if not len(am):
          am_group = Group.objects.get(name='attendance_monitors')
          bro = Trainee.objects.filter(gender='B').order_by('?').first()
          sis = Trainee.objects.filter(gender='S').order_by('?').first()
          print('no attendance monitors found, selecting random brother {0} and sister {1}'.format(bro, sis))
          bro.groups.add(am_group)
          sis.groups.add(am_group)
        new_roll(trainees, am)


    def handle(self, *args, **options):
        print('* Populating rolls...')
        self._create_rolls()
