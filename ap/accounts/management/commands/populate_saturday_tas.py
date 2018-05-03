from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from accounts.models import User

class Command(BaseCommand):
  # to use: python ap/manage.py populate_saturday_tas --settings=ap.settings.dev

  def _populate_saturday_tas(self):
    # change the array below to get different tas
    tas = ['Alberto Pagan', 'Andrew Chung', 'Ben Kwan', 'Benjamin Chen', 'Chris Roca', 'Guy Cao', 'Joshua Chang', 'Justin Jang', 'Paul Chiang', 'Sam Lee', 'Simon Chon', 'Tim Gachago']
    ta_perm = Group.objects.get(name='training_assistant')
    sta_perm = Group.objects.get(name='saturday_training_assistant')

    for ta in tas:
      firstname = ta.split(' ')[0]
      lastname = ta.split(' ')[1]
      try:
        ta_obj = User.objects.get(firstname=firstname, lastname=lastname)
        print 'added ', ta_obj
        sta_perm.user_set.add(ta_obj)
        ta_perm.user_set.add(ta_obj)
      except ObjectDoesNotExist:
        print ta, 'does not exist'

  def handle(self, *args, **options):
    print('* Populating saturday tas...')
    self._populate_saturday_tas()
