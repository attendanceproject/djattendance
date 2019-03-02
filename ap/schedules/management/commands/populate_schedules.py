from django.core.management.base import BaseCommand
from schedules.models import Event, Schedule
from accounts.models import Trainee
from terms.models import Term
from teams.models import Team
from django.db.models import Q
from datetime import *


class Command(BaseCommand):
  def _create_schedule(self):

    # Generic Schedule
    group_s = Schedule(name='Generic Group Events', season='All', term=Term.current_term(), priority=1, trainee_select='GP', import_to_next_term=True)
    group_s.comments = "Use for group leaveslips"
    group_s.save()

    group_s.events = Event.objects.filter(Q(type='H') | Q(type='M'))
    events = ["SESS1", "SESS2", "CP Work", "YPCW", "GTF", "Study", "LANG/CHAR"]
    for e in events:
        es = Event.objects.filter(code=e)
        group_s.events.add(*es)

    group_s.trainees = Trainee.objects.all()
    group_s.save()

    # all trainees
    main_s = Schedule(name='Main', season='All', term=Term.current_term(), priority=2, import_to_next_term=True)
    main_s.save()

    main_s.events = Event.objects.filter(Q(type='H') | Q(type='M') | Q(class_type='MAIN'))
    main_s.events.add(*Event.objects.filter(code='LANG/CHAR'))
    main_s.trainees = Trainee.objects.all()
    main_s.save()

    # 1st year
    oneyear_s = Schedule(name='1st Year', season='All', trainee_select='FY', term=Term.current_term(), priority=2, import_to_next_term=True)
    oneyear_s.save()

    oneyear_s.events = Event.objects.filter(class_type='1YR')
    oneyear_s.trainees = Trainee.objects.filter(current_term__lte=2)
    oneyear_s.save()

    # 2nd year
    twoyear_s = Schedule(name='2nd Year', season='All', trainee_select='SY', term=Term.current_term(), priority=2, import_to_next_term=True)
    twoyear_s.save()

    twoyear_s.events = Event.objects.filter(class_type='2YR')
    twoyear_s.trainees = Trainee.objects.filter(current_term__gte=3)
    twoyear_s.save()

    for team in Team.objects.all():
      schedule = Schedule(
          name=team.name, season='All', term=Term.current_term(),
          priority=3, import_to_next_term=True, trainee_select='TE',
          team_roll=team
      )
      schedule.save()
      schedule.events = Event.objects.filter(monitor='TM')
      schedule.trainees = Trainee.objects.filter(team=team)
      schedule.save()

    campus_generic = Schedule(name='Generic Campus', season='All', term=Term.current_term(), priority=4)
    campus_generic.save()

    campus_generic.events = Event.objects.filter(monitor='TM')
    campus_generic.trainees = Trainee.objects.filter(team__type='CAMPUS')
    campus_generic.save()

  def handle(self, *args, **options):
    print("* Populating schedules...")
    self._create_schedule()
    print 'pulled on', datetime.now()
