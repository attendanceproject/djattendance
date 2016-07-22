from datetime import date

from django import forms
from django.utils.functional import cached_property

from absent_trainee_roster.models import Roster, Entry, Absentee
from accounts.models import Trainee


class RosterForm(forms.ModelForm):
  class Meta:
    model = Roster
    fields = '__all__'


class AbsentTraineeForm(forms.ModelForm):
  comments = forms.CharField(required=False, max_length=40, widget=forms.TextInput(attrs={'class':'comments form-control', 'placeholder':'Comments'}))


  class Meta:
    model = Entry
    fields = ('absentee', 'reason', 'coming_to_class', 'comments')

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(AbsentTraineeForm, self).__init__(*args, **kwargs)

    if self.user:
      absentees = Absentee.objects.filter(is_active=True, house__isnull=False)
      #filter the queryset according to user(house) if the form is used by HCs
      if self.user.groups.filter(name='absent_trainee_roster').exists():
        # get all trainees if on absent_trainee_roster service
        self.fields['absentee'].queryset = absentees
      else:
        self.fields['absentee'].queryset = absentees.filter(house=self.user.house)

    self.fields['absentee'].label = 'Name'
    self.fields['absentee'].empty_label = '--Name--'
    self.fields['absentee'].widget.attrs={'class': 'form-control'}
    self.fields['reason'].widget.attrs={'class': 'form-control'}


class NewEntryFormSet(forms.models.BaseModelFormSet):
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(NewEntryFormSet, self).__init__(*args, **kwargs)
    # for form in self.forms:
      # This logic below allows form.cleaned_data to show for unchanged initial data (to help calculate delete)
      # if not form.initial:
      #   # catch case for extra empty at bottom and new empty elements
      #   form.empty_permitted = True
      # else:
      #   # existing data
      #   form.empty_permitted = False

  @cached_property
  def forms(self):
    forms = [self._construct_form(i, user=self.user) for i in xrange(self.total_form_count())]
    return forms

  def clean(self):
    #Checks that no two forms registers the same absentee.
    if any(self.errors):
      #Don't bother validating the formset unless each form is valid on its own
      return
    absentees = set() # list of absentee id's
    for i in xrange(self.total_form_count()):
      if self.data['form-' + str(i) + '-absentee']:
        absentee = int(self.data['form-' + str(i) + '-absentee'])
        if absentee in absentees:
          raise forms.ValidationError("You're submitting multiple entries for the same trainee.")
        absentees.add(absentee)
    return super(NewEntryFormSet, self).clean()
