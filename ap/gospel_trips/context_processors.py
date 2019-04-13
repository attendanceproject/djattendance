from aputils.trainee_utils import is_trainee

from .models import GospelTrip, Destination


def gospel_trips_available(request):
  user = request.user
  if not hasattr(user, 'type') or not is_trainee(user):
    return {'gospel_trips_available': False}

  # if user is trainee
  try:
    # sorts by latest open_time (most current), finds first gt that is open
    admin = next((gt for gt in GospelTrip.objects.order_by('-open_time') if gt.is_open), None)
    if admin:  # is_open is True
      return {'gospel_trips_available': True}
    else:
      admin = next((gt for gt in GospelTrip.objects.order_by('-open_time') if gt.keep_open), None)
      if admin:  # keep_open is True
        if user.id in admin.get_submitted_trainees():
          return {'gospel_trips_available': True}
    return {'gospel_trips_available': False}
  except GospelTrip.DoesNotExist:
    return {'gospel_trips_available': False}


def teams_available(request):
  user = request.user
  if not hasattr(user, 'type') or not is_trainee(user):
    return {'teams_available': False}
  try:
    admin = next((gt for gt in GospelTrip.objects.order_by('-open_time') if gt.show_teams), None)
    if admin and Destination.objects.filter(gospel_trip=admin, trainees=user).exists():
      return {'teams_available': True}
    else:
      return {'teams_available': False}
  except GospelTrip.DoesNotExist:
    return {'teams_available': False}
