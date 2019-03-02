from django.db import models
from houses.models import House
from accounts.models import Trainee
from terms.models import Term
from django.core.urlresolvers import reverse


class HCSurveyAdmin(models.Model):

  # keeps track of term
  term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL)

  # 1st, 2nd, 3rd (etc.) survey of the term
  index = models.SmallIntegerField(default=0)

  open_survey = models.BooleanField(default=False)

  open_time = models.DateTimeField(null=True, blank=True)

  close_time = models.DateTimeField(null=True, blank=True)

  def get_update_url(self):
    return reverse('hc:hc-admin-update', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('hc:hc-admin-delete', kwargs={'pk': self.id})


class HCRecommendationAdmin(models.Model):

  term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL)

  open_survey = models.BooleanField(default=False)

  open_time = models.DateTimeField(null=True, blank=True)

  close_time = models.DateTimeField(null=True, blank=True)


class HCSurvey(models.Model):

  survey_admin = models.ForeignKey(HCSurveyAdmin, null=True, blank=True, on_delete=models.CASCADE)

  # many-to-one: The house (has many surveys) this survey concerns
  house = models.ForeignKey(House, null=True, on_delete=models.SET_NULL)

  # hc submitting the HCSurvey
  hc = models.ForeignKey(Trainee, null=True, on_delete=models.SET_NULL)

  # atmosphere of the house
  atmosphere = models.TextField(blank=True, null=True)

  # situations of the house
  situations = models.TextField(blank=True, null=True)

  # general comments concerning the house
  comment = models.TextField(blank=True, null=True)

  submitted = models.BooleanField(default=False)

  def __unicode__(self):
    try:
      return "House Survey: " + self.house.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class HCTraineeComment(models.Model):

  # the corresponding HC Survey
  hc_survey = models.ForeignKey(HCSurvey, null=True, on_delete=models.SET_NULL)

  # the (resident) trainee this comment concerns
  trainee = models.ForeignKey(Trainee, null=True, on_delete=models.SET_NULL)

  # the comment concerning the trainee
  assessment = models.TextField(blank=True, null=True)

  def __unicode__(self):
    try:
      return "Trainee Comment: " + self.trainee.full_name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class HCRecommendation(models.Model):

  survey_admin = models.ForeignKey(HCRecommendationAdmin, null=True, blank=True, on_delete=models.SET_NULL)

  # The recommendation concerning this house
  house = models.ForeignKey(House, null=True, on_delete=models.SET_NULL)

  # hc writing this recommendation
  hc = models.ForeignKey(Trainee, related_name='hc', null=True, on_delete=models.SET_NULL)

  # trainee recommended by hc for hc role
  recommended_hc = models.ForeignKey(Trainee, related_name='recommended_hc', null=True, on_delete=models.SET_NULL)

  # choice - yes or no
  CHOICE = (('YES', 'yes'), ('NO', 'no'))
  choice = models.CharField(max_length=3, choices=CHOICE, blank=True)

  # detailed recommendation for the chosen trainee
  recommendation = models.TextField(blank=True, null=True)

  def __unicode__(self):
    try:
      return "HC Rec.: " + self.house.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
