from accounts.models import Trainee


def is_trainee(user):
  """
  >>> from accounts.models import User
  >>> user = User.objects.create(firstname="Firstname", lastname="Lastname", type="R", email="username@gmail.com")
  >>> is_trainee(user)
  True
  >>> user.type = "C"
  >>> user.save()
  >>> is_trainee(user)
  True
  >>> user.type = "S"
  >>> user.save()
  >>> is_trainee(user)
  True
  >>> user.type = "T"
  >>> user.save()
  >>> is_trainee(user)
  False
  """

  try:
    t = user.type
    return t in ('R', 'C', 'S')
  except AttributeError:
    return False


def is_TA(user):

  """
  >>> from accounts.models import User
  >>> user = User.objects.create(firstname="Firstname1", lastname="Lastname1", type="T", email="username1@gmail.com")
  >>> is_TA(user)
  True
  >>> user.type = "R"
  >>> user.save()
  >>> is_TA(user)
  False
  >>> user.type = "C"
  >>> user.save()
  >>> is_TA(user)
  False
  >>> user.type = "S"
  >>> user.save()
  >>> is_TA(user)
  False
  """
  t = user.type
  return t == 'T'


def trainee_from_user(user):
  """
  >>> from accounts.models import User
  >>> user = User.objects.create(firstname="Firstname2", lastname="Lastname2", type="S", email="username2@gmail.com")
  >>> trainee_from_user(user)
  <Trainee: Firstname2 Lastname2>
  >>> user.type = "R"
  >>> user.save()
  >>> trainee_from_user(user)
  <Trainee: Firstname2 Lastname2>
  >>> user.type = "C"
  >>> user.save()
  >>> trainee_from_user(user)
  <Trainee: Firstname2 Lastname2>
  >>> user.type = "2"
  >>> user.save()
  >>> trainee_from_user(user)
  """

  try:
    return Trainee.objects.get(id=user.id)
  except Trainee.DoesNotExist:
    return None
