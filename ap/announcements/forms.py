from django import forms

from .models import Announcement
from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput
from aputils.trainee_utils import is_TA
from aputils.widgets import DatePicker


class AnnouncementForm(forms.ModelForm):
  announcement_date = forms.DateField(widget=DatePicker())
  announcement_end_date = forms.DateField(widget=DatePicker(), required=False)
  label = 'Trainees to show announcement (if on server).'
  trainees_show = forms.ModelMultipleChoiceField(
      queryset=Trainee.objects.all(),
      label=label,
      required=False,
      widget=TraineeSelect2MultipleInput,
  )

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super(AnnouncementForm, self).__init__(*args, **kwargs)
    # if the user can see/modify the status, not trainee, so make it easy for approved announcements to be created by non-trainees
    self.fields['announcement_end_date'].widget.attrs['class'] += ' hide-if-in-class hide-if-popup show-if-on-tv-page'
    attrs = {'class': 'hide-if-in-class', 'id': 'id_trainees'}
    self.fields['trainees_show'].widget.attrs = attrs
    self.fields['is_popup'].widget.attrs['class'] = 'hide-if-in-class hide-if-on-tv-page'
    self.fields['is_popup'].label = 'Show announcement as a popup.'
    self.fields['all_trainees'].widget.attrs['class'] = 'hide-if-in-class hide-if-on-tv-page'
    self.fields['all_trainees'].label = "Show announcement to all trainees."
    self.fields['trainee_comments'].label = "Trainee's comments/description for why this announcement is necessary."
    self.fields['fellowshipped'].initial = False
    self.fields['fellowshipped'].label = "Has this announcement been fellowshipped and approved by a TA?"

    if not is_TA(user):
      del self.fields['TA_comments']
      del self.fields['status']

    if is_TA(user):
      self.fields['status'].initial = 'A'
      self.fields['status'].widget = forms.HiddenInput()
      del self.fields['trainee_comments']
      del self.fields['fellowshipped']

  def clean(self):
    cleaned_data = super(AnnouncementForm, self).clean()
    type = cleaned_data.get('type')
    end_date = cleaned_data.get('announcement_end_date')
    is_popup = cleaned_data.get('is_popup')
    if (type == 'SERVE' or type == 'TV') and not end_date and not is_popup:
      self._errors["announcement_end_date"] = self.error_class(["This is a required field."])
    return cleaned_data

  class Meta:
    model = Announcement
    fields = [
        'type',
        'is_popup',
        'status',
        'announcement',
        'TA_comments',
        'trainee_comments',
        'fellowshipped',
        'announcement_date',
        'announcement_end_date',
        'all_trainees',
        'trainees_show',
    ]


class AnnouncementDayForm(forms.Form):
  announcement_day = forms.DateField(widget=DatePicker(), label="Choose a date")
