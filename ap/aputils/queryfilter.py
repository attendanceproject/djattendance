from collections import OrderedDict

from django.db.models.query_utils import Q


class QueryFilterService:
  queryfilter_store = OrderedDict()

  def __init__(self):
    pass

  @staticmethod
  def addQ(name, *args, **kwargs):
    # Add trainee__ to beginning of every kwargs
    trainee_kwargs = {}
    for k, v in kwargs.items():
      trainee_kwargs['trainee__%s' % k] = v
    # print 'Adding QueryFilter', name
    QueryFilterService.queryfilter_store[name] = {
      'query': Q(*args, **trainee_kwargs)
    }

  @staticmethod
  def getQ(name):
    return QueryFilterService.queryfilter_store[name]

  @staticmethod
  def get_query(name):
    return QueryFilterService.queryfilter_store[name]['query']

  @staticmethod
  def get_choices():
    CHOICES = ()
    for name, obj in QueryFilterService.queryfilter_store.items():
      CHOICES += ((name, name),)

    return CHOICES


def add(*args, **kwargs):
  QueryFilterService.addQ(*args, **kwargs)


add('Brothers', gender='B')
add('Sisters', gender='S')

add('Couple', meta__is_married=True)
add('Not Couple', meta__is_married=False)
add('Commuter', Q(type='C'))
add('Not Commuter', ~Q(type='C'))

add('First Term', current_term=1)
add('Second Term', current_term=2)
add('Third Term', current_term=3)
add('Fourth Term', current_term=4)
add('First Year', Q(current_term=1) | Q(current_term=2))
add('Second Year', Q(current_term=3) | Q(current_term=4))
add('Not First Term', current_term__gt=1)
add('Not Fourth Term', current_term__lt=4)

add('Car', vehicles__isnull=False)

add('Team Campus', team__type='CAMPUS')
add('Team Community', team__type='COM')
add('Team Children', team__type='CHILD')
add('Team Children or Community', Q(team__type='CHILD') | Q(team__type='COM'))
add('Team YP', team__type='YP')
add('Not Team YP', ~Q(team__type='YP'))
add('Team Internet', team__type='IT')

# qualifications = Qualification.objects.all()

# for q in qualifications:
#   add(q.name, worker__qualifications__name=q.name)


# add('Kitchen Star', worker__qualifications__name='Kitchen Star')
# add('Restroom Star', worker__qualifications__name='Restroom Star')
# add('Sack Lunch Star', worker__qualifications__name='Sack Lunch Star')


# Star filter may be done through qualifications
