from django import forms
from absent_trainee_roster.models import Entry, Roster
from datetime import date
# from django_select2.fields import ModelSelect2Field
# from django_select2.widgets import Select2Widget
from absent_trainee_roster.models import Roster, Entry, Absentee

class RosterForm(forms.ModelForm):
	class Meta:
		model = Roster


class AbsentTraineeForm(forms.ModelForm):

	comments = forms.CharField(required=False, max_length=40, widget=forms.TextInput(attrs={'class':'comments'}))

	class Meta:
		model = Entry
		fields = ('absentee', 'reason', 'comments')
		# widgets = {
		# 	'absentee': Select2Widget(select2_options={
		# 		'width':'element',
		# 		}),
		# }

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(AbsentTraineeForm, self).__init__(*args, **kwargs)
		#Every trainee should have an absentee profile
		self.fields['absentee'].queryset = Absentee.objects.filter(account__trainee__house=self.user.trainee.house)
		self.fields['absentee'].label = 'Name'
		self.fields['absentee'].empty_label = ''
		self.fields['absentee'].widget.attrs={'class': 'select2'}
	

class NewEntryFormSet(forms.formsets.BaseFormSet):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(NewEntryFormSet, self).__init__(*args, **kwargs)
		for form in self.forms:
			form.empty_permitted =False

	def _construct_forms(self):
		self.forms = []
		for i in xrange(self.total_form_count()):
			self.forms.append(self._construct_form(i, user=self.user))
	
	def clean(self):
		#Checks that no two forms registers the same absentee.
		if any(self.errors):
			#Don't bother validating the formset unless each form is valid on its own
			return
		roster = Roster.objects.filter(date=date.today())[0]
		entries = Entry.objects.filter(roster=roster)
		absentees = []
		list = []
		for i in range(0, self.total_form_count()):
			form = self.forms[i]
			absentee = form.cleaned_data['absentee']
			#checks that absentee is not duplicated in formset
			if absentee in absentees:
				raise forms.ValidationError("You're submitting entries for the same trainee.")
			absentees.append(absentee)
			
			# checks that absentee is not already in roster
			for entry in entries:
				if absentee == entry.absentee:
					list.append(absentee)
		if list:
			raise forms.ValidationError("Entry/Entries for %s has already been submitted." %', '.join(map(str,list)))
			
		
