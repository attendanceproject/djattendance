import datetime

from aputils.widgets import DatePicker
from django import forms


class ReportGenerateForm(forms.Form):
  # training_class = ModelChoiceField(Class.objects.all(), empty_label=None)
  date_from = forms.DateField(widget=DatePicker(), label="From: ")
  date_to = forms.DateField(widget=DatePicker(), label="to: ")
  attendancePeriodStart = forms.DateTimeField(initial=datetime.date.today)
  attendancePeriodEnd = forms.DateTimeField(initial=datetime.date.today)
  Gender = forms.CharField(initial='M')
  Term = forms.IntegerField(initial='1')
  GeneralItems = forms.CharField(max_length=500)
  GeneralReport = forms.CharField(max_length=500)
