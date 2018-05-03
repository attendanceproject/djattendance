from .utils import unfinalized_week


def bible_tracker_forced(request):
  forced = True if unfinalized_week(request.user) else False  # forced if bible reading not finalized
  return {'bible_tracker_forced': forced}
