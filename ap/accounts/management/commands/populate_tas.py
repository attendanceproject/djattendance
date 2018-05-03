from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import User

class Command(BaseCommand):
  # to use: python ap/manage.py populate_tas --settings=ap.settings.dev

  def _create_ta(self, ta):
    email = '.'.join(ta.lower().split(' ')) + "@lsm.org"
    firstname = ta.split(' ')[0]
    lastname = ta.split(' ')[1]
    date_of_birth = '1974-12-12'
    u = User(is_active=True, email=email, firstname=firstname, lastname=lastname, type='T', date_of_birth=date_of_birth, is_staff=True, is_admin=True)
    u.set_password('ap')
    u.save()
    return u

  def _create_tas(self):
    # change the array below to get different tas
    tas = ['Andrew Li', 'Jerome Keh', 'Joseph Bang', 'Paul Deng', 'Walt Hale', 'Joe Prim', 'Oscar Tuktarov', 'Doug Gedeon', 'Dennis Higashi']
    sister_tas = ['Nikki Miao', 'Hannah Chumreonlert', 'Raizel Macaranas', 'Ann Buntain', 'Annie Uy']
    perm = Group.objects.get(name='training_assistant')
    rperm = Group.objects.get(name='regular_training_assistant')

    for ta in tas:
      u = self._create_ta(ta)
      u.gender = 'B'
      rperm.user_set.add(u)
      perm.user_set.add(u)
      u.save()

    for ta in sister_tas:
      u = self._create_ta(ta)
      u.gender = 'S'
      rperm.user_set.add(u)
      perm.user_set.add(u)
      u.save()

    user = User(is_active=True, email='ap@gmail.com', firstname='AP', lastname='DEV', is_staff=True, is_admin=True, is_superuser=True)
    user.set_password('ap')
    user.save()

  def handle(self, *args, **options):
    User.objects.all().delete()
    print('* Populating tas...')
    self._create_tas()
