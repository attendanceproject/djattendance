from aputils.trainee_utils import is_trainee, trainee_from_user
from hc.models import HCRecommendationAdmin, HCSurveyAdmin
from terms.models import Term


def hc_surveys(user):
  ret = False
  if is_trainee(user):
    tr = trainee_from_user(user)
    if tr.has_group(['HC']) and tr.type != 'C':
      term = Term.current_term()
      admins = HCSurveyAdmin.objects.filter(open_survey=True).filter(term=term)
      if admins.exists():
        ret = True
  return ret


def hc_recommendations(user):
  ret = False
  if is_trainee(user):
    tr = trainee_from_user(user)
    if tr.has_group(['HC']) and tr.type != 'C':
      term = Term.current_term()
      admins = HCRecommendationAdmin.objects.filter(open_survey=True).filter(term=term)
      if admins.exists() > 0:
        ret = True
  return ret
