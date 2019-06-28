from collections import OrderedDict

from aputils.widgets import DatePicker, DatetimePicker
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory

from .constants import SHOW_CHOICES
from .models import (Answer, AnswerChoice, Destination, GospelTrip, LocalImage,
                     NonTrainee, Question, Section)
from .utils import get_airline_codes, get_airport_codes, get_answer_types


class GospelTripForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(GospelTripForm, self).__init__(*args, **kwargs)

  class Meta:
    model = GospelTrip
    fields = "__all__"
    labels = {
      'name': 'Gospel Trip Name',
    }
    widgets = {
      'open_time': DatetimePicker(),
      'close_time': DatetimePicker()
    }

  def clean(self):
    cleaned_data = super(GospelTripForm, self).clean()
    cleaned_open_time = cleaned_data.get('open_time')
    cleaned_close_time = cleaned_data.get('close_time')
    if cleaned_open_time >= cleaned_close_time:
      self._errors["close_time"] = self.error_class(["Close time should be after open time."])
    return cleaned_data


class NonTraineeForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(NonTraineeForm, self).__init__(*args, **kwargs)

  class Meta:
    model = NonTrainee
    exclude = ['gospel_trip', 'application_data', 'assigned_destination']


class LocalImageForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(LocalImageForm, self).__init__(*args, **kwargs)

  class Meta:
    model = LocalImage
    fields = "__all__"


class SectionForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(SectionForm, self).__init__(*args, **kwargs)
    self.fields['show'] = forms.ChoiceField(choices=SHOW_CHOICES)

  class Meta:
    model = Section
    fields = ["name", "show"]


class QuestionForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    super(QuestionForm, self).__init__(*args, **kwargs)
    self.fields['answer_type'] = forms.ChoiceField(choices=get_answer_types())
    self.fields['instruction'].widget.attrs = {'class': 'editor'}

  def clean(self):
    cleaned_data = super(QuestionForm, self).clean()
    cleaned_label = cleaned_data.get('label')
    cleaned_type = cleaned_data.get('answer_type')

    if cleaned_type != "None" or cleaned_type == "":
      if cleaned_label == "":
        self._errors["label"] = self.error_class(["Questions that expect an answer must have a label. If it's just an instruction please select 'None' for answer type "])
      if Question.objects.filter(section__gospel_trip=self.instance.section.gospel_trip,
                                 label=cleaned_label).exclude(id=self.instance.id).exists():
        self._errors["label"] = self.error_class(["This label is already taken. Please input another."])
    if cleaned_type == "destinations":
      if not cleaned_label.startswith("Destination Preference"):
        self._errors["label"] = self.error_class(["Destination questions: must be labeled: 'Destination Preference [number]."])
    return cleaned_data

  class Meta:
    model = Question
    fields = ["label", "instruction", "answer_type", "answer_required"]


class AnswerForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    if 'gospel_trip__pk' in kwargs:
      gospel_trip = kwargs.pop('gospel_trip__pk')
    super(AnswerForm, self).__init__(*args, **kwargs)
    self.fields['response'] = forms.CharField(widget=forms.Textarea)
    if self.instance.question:
      answer_type = self.instance.question.answer_type
      req = self.instance.question.answer_required

      if answer_type in ["text", "None", "", None]:
        pass

      elif answer_type == 'destinations':
        # this is a special case
        choices = [('', '---------')]
        choices.extend([(d['id'], d['name']) for d in Destination.objects.filter(gospel_trip=gospel_trip).values('id', 'name')])
        self.fields['response'] = forms.ChoiceField(choices=choices, required=req)

      elif answer_type == 'date':
        self.fields['response'] = forms.DateField(widget=DatePicker())

      elif answer_type == 'datetime':
        self.fields['response'] = forms.DateTimeField(widget=DatetimePicker())

      elif answer_type == 'airports':
        self.fields['response'].widget.attrs = {'class': 'airport-field'}

      elif answer_type == 'airlines':
        self.fields['response'].widget.attrs = {'class': 'airline-field'}

      else:
        try:
          opts = AnswerChoice.objects.get(name=answer_type).options.split(',')
          choices = [('', '---------')]
          choices.extend([(c, c) for c in opts])
          self.fields['response'] = forms.ChoiceField(choices=choices, required=req)
        except AnswerChoice.DoesNotExist:
          pass

      if self.instance.question.section.show == 'READ ONLY':
        self.fields['response'].widget.attrs['readonly'] = 'true'

      self.fields['response'].required = req

  def clean(self):
    cleaned_data = super(AnswerForm, self).clean()
    cleaned_response = cleaned_data.get('response')
    answer_type = self.instance.question.answer_type

    if answer_type == 'airports':
      if cleaned_response and cleaned_response not in get_airport_codes():
        self._errors["response"] = self.error_class(["Please enter a valid IATA code."])
    elif answer_type == 'airlines':
      if cleaned_response and cleaned_response not in get_airline_codes():
        self._errors["response"] = self.error_class(["Please enter a valid IATA code."])
    return cleaned_data

  class Meta:
    model = Answer
    fields = ['response', ]


QuestionFormSet = inlineformset_factory(Section, Question, form=QuestionForm, extra=1)


class BaseSectionFormset(BaseInlineFormSet):
  def add_fields(self, form, index):
    super(BaseSectionFormset, self).add_fields(form, index)

    # save the formset(s) in the 'nested' property
    # This will allow us to have multiple nested forms for future use
    form.nested = OrderedDict()

    form.nested['Questions'] = QuestionFormSet(
        instance=form.instance,
        data=form.data if form.is_bound else None,
        files=form.files if form.is_bound else None,
        prefix='question-%s-%s' % (
            form.prefix,
            QuestionFormSet.get_default_prefix()),)

  def is_valid(self):
    result = super(BaseSectionFormset, self).is_valid()

    if self.is_bound:
      for form in self.forms:
        if hasattr(form, 'nested'):
          for _, f in form.nested.items():
            result = result and f.is_valid()

    return result

  def save(self, commit=True):
    result = super(BaseSectionFormset, self).save(commit=commit)

    for form in self.forms:
      if hasattr(form, 'nested'):
        if not self._should_delete_form(form):
          for _, f in form.nested.items():
            f.save(commit=commit)

    return result


SectionFormSet = inlineformset_factory(
  GospelTrip, Section, form=SectionForm,
  formset=BaseSectionFormset, extra=1)
