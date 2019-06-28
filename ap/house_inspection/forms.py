from django import forms
from .models import HouseInspectionFaq
from aputils.widgets import DatePicker

'''
class FaqForm(forms.Form):
    question = forms.Textarea()
    answer = forms.Textarea()
    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
'''

class FaqForm(forms.ModelForm):
	class Meta:
		model = HouseInspectionFaq
		fields = ['question', 'answer', 'status', 'trainee']

class QuestionRequestCreateForm(forms.ModelForm):

  #date_expire = forms.DateField(widget=DatePicker(), label="Request expires after: ")
  #comments = forms.CharField(
  #    widget=forms.Textarea(
  #        attrs={
  #            'placeholder': 'Please be as detailed and specific as possible to prevent unnecessary delays'
  #        }
  #    )
  #) maybe include the comments later

  def clean_date_expire(self):
    """ Invalid form if date expire is earlier than today """
    data = self.cleaned_data['date_expire']
    if datetime.now().date() > data:
      raise forms.ValidationError("Date expire has already passed.")
    return data

  class Meta:
    model = HouseInspectionFaq
    fields = ['question',]

class HouseInspectionFaqAnswerForm(forms.ModelForm):

  class Meta:
    model = HouseInspectionFaq
    fields = ['answer',]

class HouseInspectionFaqCommentForm(forms.ModelForm):
  class Meta:
    model = HouseInspectionFaq
    fields = ['comment',]