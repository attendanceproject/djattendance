from django.core.management.base import BaseCommand
from schedules.models import Event, Schedule
from accounts.models import Trainee
from terms.models import Term
from attendance.models import Roll
from django.db.models import Q
from datetime import *


from datetime import time

class Command(BaseCommand):
  def _create_schedule(self):

    #Generic Schedule
    group_s = Schedule(name='Generic Group Events', season='All', term=Term.current_term(), priority=1, trainee_select='GP')
    group_s.comments = "Use for group leave slips"
    group_s.save()

    group_s.events = Event.objects.filter(Q(type='H')|Q(type='M'))
    events = ["SESS1", "SESS2", "CP Work", "YPCW", "GTF", "Study", "LANG/CHAR"]
    for e in events:
        es = Event.objects.filter(code=e)
        group_s.events.add(*es)

    group_s.trainees = Trainee.objects.all()
    group_s.save()

    #all trainees
    main_s = Schedule(name='Main', season='All', term=Term.current_term(), priority=2)
    main_s.save()

    main_s.events = Event.objects.filter(Q(type='H')|Q(type='M')|Q(class_type='MAIN'))
    main_s.events.add(*Event.objects.filter(code='LANG/CHAR'))
    main_s.trainees = Trainee.objects.all()
    main_s.save()

    #1st year
    oneyear_s = Schedule(name='1st Year', season='All', term=Term.current_term(), priority=3)
    oneyear_s.save()

    oneyear_s.events = Event.objects.filter(class_type='1YR')
    oneyear_s.trainees = Trainee.objects.filter(current_term__lte=2)
    oneyear_s.save()

    #2nd year
    twoyear_s = Schedule(name='2nd Year', season='All', term=Term.current_term(), priority=3)
    twoyear_s.save()

    twoyear_s.events = Event.objects.filter(class_type='2YR')
    twoyear_s.trainees = Trainee.objects.filter(current_term__gte=3)
    twoyear_s.save()

    #campus times
    campus_generic = Schedule(name='Generic Campus', season='All', term=Term.current_term(), priority=4)
    campus_generic.save()

    campus_generic.events = Event.objects.filter(monitor='TM')
    campus_generic.trainees = Trainee.objects.filter(team__type='CAMPUS')
    campus_generic.save()

  def _check_schedules(self):
    ghost_sch = Schedule.objects.filter(trainees__isnull=True).exclude(comments__isnull=True)
    for sch in ghost_sch: 
        print "Schedule ID", sch
        for e in sch.events.all():
            print "Event ID", e
            attached = [r.id for r in Roll.objects.filter(event=e)]
            if attached:
                print "Attached Roll IDs", attached
        print 


  def _check_events(self):
    all_events = list(Event.objects.all())
    for sch in Schedule.objects.all():
        for e in sch.events.all():
            if e in all_events:
                all_events.remove(e)

    print "Events not attached to any schedule and does not have a description"
    for ev in all_events:
        
        if not ev.description:
            print "Event ID", ev.id, ev   

  def handle(self, *args, **options):
    #print("* Populating schedules...")
    #self._create_schedule()
    print ("* Looking through schedules... ")
    self._check_schedules()
    # self._check_events()
    print 'pulled on', datetime.now()
