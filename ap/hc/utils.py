from aputils.trainee_utils import is_trainee, trainee_from_user
from hc.models import HCRecommendationAdmin, HCSurveyAdmin
from terms.models import Term


def hc_surveys(user):
  ret = False
  if is_trainee(user) and trainee_from_user(user).house.gender not in ['C', None]:
    term = Term.current_term()
    admins = HCSurveyAdmin.objects.filter(open_survey=True).filter(term=term)
    if admins.exists():
      ret = True
  return ret


def hc_recommendations(user):
  ret = False
  if is_trainee(user) and trainee_from_user(user).house.gender not in ['C', None]:
    term = Term.current_term()
    admins = HCRecommendationAdmin.objects.filter(open_survey=True).filter(term=term)
    if admins.exists() > 0:
      ret = True
  return ret
