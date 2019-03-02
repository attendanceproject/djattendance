from django import forms
from semi.models import SemiAnnual
from semi.utils import LOCATIONS, REQUEST_STATUS, ROLL_STATUS


class AttendanceForm(forms.Form):

  tuesday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  wednesday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  thursday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  friday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  saturday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)


class LocationForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    is_TA = kwargs.pop('is_TA', None)
    super(LocationForm, self).__init__(*args, **kwargs)

    self.fields['other_location'].required = False

    self.fields['request_comments'].label = "Comments"
    self.fields['request_comments'].placeholder = "Insert the reason for wihy you would like to study here"
    self.fields['request_comments'].required = False

    self.fields['ta_comments'].label = "TA Response"
    self.fields['ta_comments'].required = False

    self.fields['status'].label = "Request Status"
    self.fields['status'].required = False

    if not is_TA:
      self.fields['status'].disabled = True
      self.fields['ta_comments'].disabled = True

  location = forms.ChoiceField(choices=LOCATIONS, widget=forms.RadioSelect)
  other_location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'location'}))
  request_comments = forms.Textarea(attrs={'rows': 4, 'cols': '100vh'})
  ta_comments = forms.Textarea(attrs={'rows': 4, 'cols': '100vh'})
  status = forms.ChoiceField(choices=REQUEST_STATUS)

  class Meta:
    model = SemiAnnual
    exclude = ['trainee', 'term', 'attendance', ]
