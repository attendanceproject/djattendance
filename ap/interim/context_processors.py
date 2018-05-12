from .models import InterimIntentionsAdmin
from aputils.trainee_utils import is_trainee
from terms.models import Term

from datetime import datetime


def interim_intentions_available(request):
  user = request.user
  if not hasattr(user, 'type') or not is_trainee(user):
    return {'interim_intentions_available': False}

  try:
    admin = InterimIntentionsAdmin.objects.get(term=Term.current_term())
    if admin.open_time:
        if datetime.now() < admin.open_time:
          return {'interim_intentions_available': False}
    elif admin.close_time:
      if datetime.now() > admin.close_time:
        return {'interim_intentions_available': False}
    return {'interim_intentions_available': True}
  except InterimIntentionsAdmin.DoesNotExist:
    return {'interim_intentions_available': False}
