from django import forms
from django.forms import ModelForm, CharField, ModelChoiceField
from django.forms.formsets import formset_factory
from aputils.models import City
from houses.models import House
from teams.models import Team
from aputils.widgets import DatePicker


class DateForm(forms.Form):
  start_date = forms.DateField(required=True, widget=DatePicker())
  end_date = forms.DateField(required=True, widget=DatePicker())


class CityForm(ModelForm):
  class Meta:
    model = City
    fields = ['name', 'state', 'country']

  def __init__(self, *args, **kwargs):
    super(CityForm, self).__init__(*args, **kwargs)
    for field in iter(self.fields):
      self.fields[field].widget.attrs.update({
          'class': 'form-control'
      })


CityFormSet = formset_factory(CityForm, extra=0)


class TeamForm(ModelForm):
  class Meta:
    model = Team
    fields = ['name', 'code', 'type', 'locality']

  def __init__(self, *args, **kwargs):
    super(TeamForm, self).__init__(*args, **kwargs)
    for field in iter(self.fields):
      self.fields[field].widget.attrs.update({
          'class': 'form-control'
      })


TeamFormSet = formset_factory(TeamForm, extra=0)


class HouseForm(ModelForm):
  address = CharField(max_length=150)
  city = ModelChoiceField(queryset=City.objects.all())
  zip = CharField(max_length=10)

  class Meta:
    model = House
    fields = ['name', 'gender']

  def __init__(self, *args, **kwargs):
    super(HouseForm, self).__init__(*args, **kwargs)
    for field in iter(self.fields):
      self.fields[field].widget.attrs.update({
          'class': 'form-control'
      })


HouseFormSet = formset_factory(HouseForm, extra=0)
