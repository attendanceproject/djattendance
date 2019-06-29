from django.db.models.functions import Concat
from django.db.models import Value as V
from datetime import date, datetime, timedelta
from decimal import Decimal
from django import forms
from django.contrib import admin
from .models import HouseInspectionFaq, Inspectors, Scores
from houses.models import House
from accounts.models import Trainee
from aputils.widgets import DatePicker, DatetimePicker
from django_select2.forms import ModelSelect2MultipleWidget



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

class ScoresForm(forms.Form):
  
  houses = House.objects.all().order_by('name')
  trainees = Trainee.objects.all()
  #designated_service = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL) 
  #house = forms.IntegerField(label='House ID', 
  #  widget=forms.Select(choices=[(houses[x], houses[x]) for x in range(1, len(houses))])
  #  )
  house = forms.ModelChoiceField(
    label='House ID',
    queryset=House.objects.all(),
    widget=forms.Select(choices=[(houses[x], houses[x]) for x in range(1, len(houses))]),
    required=True
    )
  date = forms.DateField(initial=date.today)   
  ric = forms.ModelChoiceField(
    label='RIC',
    queryset=Trainee.objects.all(),
    widget=forms.Select(choices=[(trainees[i], trainees[i]) for i in range(1, len(trainees))]),
    required=True
    )
  #inspectors_fullname = Inspectors.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name'))

  inspectors = forms.ModelMultipleChoiceField(
    label='Inspectors',
    queryset=Inspectors.objects.all(),
    widget=ModelSelect2MultipleWidget(model=Inspectors, 
      search_fields=['trainee__icontains'],
      attrs={ 'data-placeholder': 'Select one or more inspectors', 'data-width': '50em'},
      ),
    required=True
  )

  score = forms.DecimalField(
    label='Score',    
    min_value=Decimal('0.00'),
    max_value=Decimal('6.00'),
    initial='0.00',
    required=True    
    )
  notes = forms.CharField(
    label='Notes', 
    widget=forms.Textarea,
    required=False
    )
  uninspectable_reason = forms.CharField(
    label = 'Uninspectable (Optional)',
    widget=forms.TextInput(attrs={'placeholder': 'Sick Trainee, Inspector Error, Office says it is uninspectable, Other (type the reason)'}),
    required=False
    )

class DateReportForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(DateReportForm, self).__init__(*args, **kwargs)
    self.fields['date'].required = True
  class Meta:
    model = Scores    
    fields = ['date',]
    widgets =  {
      "date": DatetimePicker(),
    }
  

  

  #def save(self, commit=True):
  #  house_id_cleaned = self.cleaned_data['house_id']
  #def __init__(self, *args, **kwargs):
  #  default_house_id = 0
  #  super(ScoresForm, self).__init__(*args, **kwargs)
  #  self.fields['house'].choices = default_house_id

