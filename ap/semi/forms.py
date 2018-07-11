from semi.models import SemiAnnual
from semi.utils import ROLL_STATUS, LOCATIONS
from django import forms


class AttendanceForm(forms.Form):

  location = forms.ChoiceField(choices=LOCATIONS)
  tuesday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  wednesday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  thursday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  friday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)
  saturday = forms.ChoiceField(choices=ROLL_STATUS, widget=forms.RadioSelect)


class LocationForm(forms.ModelForm):

  location = forms.ChoiceField(choices=LOCATIONS, widget=forms.RadioSelect)
  comments = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'location'}), required=False)

  class Meta:
    model = SemiAnnual
    fields = ['location', 'comments']
