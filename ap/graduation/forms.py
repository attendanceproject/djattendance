from django import forms

from accounts.widgets import TraineeSelect2MultipleInput
from graduation.models import *
from aputils.widgets import DatePicker


class GenericModelForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(GenericModelForm, self).__init__(*args, **kwargs)

  class Meta:
    exclude = ['trainee', 'due_date', 'show_status', 'grad_admin', ]


class TestimonyForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Testimony
    widgets = {
      'top_experience': forms.Textarea(attrs={'rows': 4, 'cols': '100vh', 'class': 'word_count 300'}),
      'encouragement': forms.Textarea(attrs={'rows': 4, 'cols': '100vh', 'class': 'word_count 300'}),
      'overarching_burden': forms.Textarea(attrs={'rows': 4, 'cols': '100vh', 'class': 'word_count 250'}),
      'highlights': forms.Textarea(attrs={'rows': 4, 'cols': '100vh', 'class': 'word_count 150'})
    }


class ConsiderationForm(GenericModelForm):
  def __init__(self, *args, **kwargs):
    super(ConsiderationForm, self).__init__(*args, **kwargs)
    # self.fields['financial'].required = False

  class Meta(GenericModelForm.Meta):
    model = Consideration
    widgets = {
      'attend_XB': forms.RadioSelect,
      'XB_other': forms.TextInput(attrs={'rows': 1, 'cols': '100vh'}),
      'fellowshipped': forms.RadioSelect,
      'fship_date': DatePicker(),
      'consideration_plan': forms.Textarea(attrs={'rows': 4, 'cols': '100vh', 'class': 'char_count'}),
      'comments': forms.Textarea(attrs={'rows': 4, 'cols': '100vh', 'class': 'char_count'}),
    }

  def clean(self):
    attend_XB = self.cleaned_data.get("attend_XB")
    XB_other = self.cleaned_data.get("XB_other")
    fellowshipped = self.cleaned_data.get("fellowshipped")
    fship_date = self.cleaned_data.get("fship_date")

    if attend_XB == "OTHER" and not XB_other:
      raise forms.ValidationError("Please elaborate regarding attending FTTA-XB.")

    if fellowshipped == "OTHER" and not fship_date:
      raise forms.ValidationError("Please set a date to fellowship with the leading brothers in your locality.")



class WebsiteForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Website


class OutlineForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Outline
    widgets = {
      'participate': forms.RadioSelect()
    }


class RemembranceForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Remembrance
    widgets = {
        'remembrance_text': forms.TextInput(attrs={'rows': 1, 'size': '60vh'}),
        'remembrance_reference': forms.TextInput(attrs={'rows': 1, 'size': '30vh'})
    }


class MiscForm(GenericModelForm):

  class Meta(GenericModelForm.Meta):
    model = Misc


class GradAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(GradAdminForm, self).__init__(*args, **kwargs)

  class Meta:
    model = GradAdmin
    exclude = ['term', ]
    widgets = {
        'testimony_due_date': DatePicker(),
        'consideration_due_date': DatePicker(),
        'website_due_date': DatePicker(),
        'outline_due_date': DatePicker(),
        'remembrance_due_date': DatePicker(),
        'misc_due_date': DatePicker(),
        'speaking_trainees': TraineeSelect2MultipleInput(attrs={'id': 'id_trainees'}),
    }
