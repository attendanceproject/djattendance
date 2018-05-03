from django.core.management.base import BaseCommand
from accounts.models import Trainee, User
from leaveslips.models import GroupSlip, IndividualSlip
from attendance.models import Roll
from datetime import datetime
import random


class Command(BaseCommand):
  # to use: python ap/manage.py populate_lifestudies --settings=ap.settings.dev
  def _create_leaveslips(self):

    tas = User.objects.filter(type='T')
    ils_types = ['CONF', 'EMERG', 'FWSHP', 'FUNRL', 'GOSP', 'INTVW', 'GRAD', 'MEAL', 'NIGHT', 'OTHER', 'SERV', 'SICK', 'SPECL', 'WED', 'NOTIF']
    gls_types = ['CONF', 'MEAL', 'NIGHT', 'OTHER']
    for ta in tas:
      trainees = Trainee.objects.filter(TA=ta)
      if trainees.count() > 0:
        val = random.sample(range(0, trainees.count() - 1), 6)
        for v in val[0:2]:
          t = trainees[v]
          r = Roll.objects.filter(trainee=t)
          if r.count() > 0:
            ils = IndividualSlip(type=random.choice(ils_types), status='P', trainee=t, comments='populated data for sample', description='insert trainee excuse eg: sick with love', TA=ta)
            ils.save()
            roll = r[random.choice(range(0, r.count() - 1))]
            ils.rolls.add(roll)
            ils.save()

        for v in val[3:6]:
          t = trainees[v]
          t_house = Trainee.objects.filter(house=t.house)
          r = Roll.objects.filter(trainee=t)
          if r.count() > 0:
            roll = r[random.choice(range(0, r.count() - 1))]
            # print roll.event.start, roll.date
            st = datetime.combine(roll.date, roll.event.start)
            en = datetime.combine(roll.date, roll.event.end)
            gls = GroupSlip(type=random.choice(gls_types), status='P', trainee=t, comments='populated data for sample', TA=ta, start=st, end=en)
            gls.save()
            for th in t_house:
              gls.trainees.add(th)
            gls.save()

  # def _update_leaveslips(self):
  #   all_IS = IndividualSlip.objects.all()
  #   for IS in all_IS:
  #     for r in IS.rolls.all():

  def handle(self, *args, **options):
    print("* Populating leave slips...")
    self._create_leaveslips()
    # print ('* Updating Leavslips ')
    # self._update_leaveslips()
