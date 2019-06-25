from django import forms
from accounts.models import Trainee
from houses.models import House
from .models import HCSurveyAdmin, HCRecommendationAdmin, HCSurvey, HCRecommendation, HCTraineeComment
from aputils.widgets import DatetimePicker


class HCRecommendationAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(HCRecommendationAdminForm, self).__init__(*args, **kwargs)

  class Meta:
    model = HCRecommendationAdmin
    fields = ["open_time", "close_time", "open_survey", ]
    widgets = {
      "open_time": DatetimePicker(),
      "close_time": DatetimePicker(),
    }


class HCSurveyAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(HCSurveyAdminForm, self).__init__(*args, **kwargs)

  class Meta:
    model = HCSurveyAdmin
    fields = ["open_time", "close_time", "open_survey", ]
    widgets = {
      "open_time": DatetimePicker(),
      "close_time": DatetimePicker(),
    }


class HCSurveyForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(HCSurveyForm, self).__init__(*args, **kwargs)

  class Meta:
    model = HCSurvey
    fields = ['atmosphere', 'situations', 'comment', ]
    widgets = {
      'atmosphere': forms.Textarea(attrs={'rows': 4}),
      'situations': forms.Textarea(attrs={'rows': 4}),
      'comment': forms.Textarea(attrs={'rows': 4}),
    }


class HCTraineeCommentForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(HCTraineeCommentForm, self).__init__(*args, **kwargs)

  class Meta:
    model = HCTraineeComment
    exclude = ['hc_survey', 'trainee', ]
    widgets = {
      'assessment': forms.Textarea(attrs={'rows': 4}),
    }


class HCRecommendationForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    house = kwargs.pop('house')
    super(HCRecommendationForm, self).__init__(*args, **kwargs)
<<<<<<< HEAD
    self.fields['recommended_hc'].queryset = user.house.residents.exclude(groups__name='HC').filter(current_term__in=[2, 3])
=======
    residents = Trainee.objects.filter(house=house)
    hc_ids = [r.id for r in residents if r.has_group(['HC'])]
    self.fields['recommended_hc'].queryset = residents.exclude(id__in=hc_ids).filter(current_term__in=[2, 3])
>>>>>>> dev

  class Meta:
    model = HCRecommendation
    fields = ['recommended_hc', 'choice', 'recommendation', ]
    widgets = {
      'recommendation': forms.Textarea(attrs={'rows': 3}),
    }
