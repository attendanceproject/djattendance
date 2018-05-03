from django import forms
from .models import XBApplication, XBAdmin
from aputils.widgets import DatePicker


class XBApplicationForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(XBApplicationForm, self).__init__(*args, **kwargs)
    self.fields['name'].label = "Name (First and Last)"
    self.fields['address'].label = "Home address"
    self.fields['automobile'].label = "Do you plan to bring an automobile?"
    self.fields['seats'].label = "If yes, how many seats including driver"
    self.fields['grad_date'].label = "Month/Year graduated"
    self.fields['loans'].label = "Do you have any significant student loans or other debt?"
    self.fields['first_church'].label = "Locality where you first contacted the church"
    self.fields['first_church_date'].label = "Date when you first contacted the church"
    self.fields['ftta_service'].label = "Areas of church service you have been involved in/designated services while attending FTTA:"
    self.fields['marital'].label = "Marital status"
    self.fields['date_marriage'].label = "Date of marriage"
    self.fields['spouse_attitude'].label = "Spouse's attitude towards the training"
    self.fields['pertinent_info'].label = "Other Pertinent information"
    self.fields['ftt_location'].label = "Previous training in Taipei, Anaheim or other FTT"
    self.fields['support_yourself'].label = "Yourself"
    self.fields['support_church'].label = "Church"
    self.fields['support_family'].label = "Family/Friends"
    self.fields['support_other'].label = "Other"

  class Meta:
    model = XBApplication
    exclude = ['trainee', 'submitted', 'date_submitted', 'last_updated']
    widgets = {
      "birthdate": DatePicker(),
      "date_saved": DatePicker(),
      "date_baptized": DatePicker(),
      "first_church_date": DatePicker(),
      "grad_date": DatePicker(),
      "date_marriage": DatePicker(),
      "gender": forms.RadioSelect,
      "loans": forms.RadioSelect,
      "automobile": forms.RadioSelect,
      "citizenship": forms.RadioSelect,
      "marital": forms.RadioSelect,
      "spouse_attitude": forms.RadioSelect,
      "support_yourself": forms.CheckboxInput,
      "support_church": forms.CheckboxInput,
      "support_family": forms.CheckboxInput,
      "support_other": forms.CheckboxInput,
      'ftta_service': forms.TextInput(attrs={'rows': 1, 'size': '60vh'}),
      'pertinent_info': forms.Textarea(attrs={'rows': 4, 'cols': '100'}),
    }


class XBAdminForm(forms.ModelForm):  # used in grad.views
  def __init__(self, *args, **kwargs):
    super(XBAdminForm, self).__init__(*args, **kwargs)

  class Meta:
    model = XBAdmin
    exclude = ['term', ]
    widgets = {
        'due_date': DatePicker(),
    }
