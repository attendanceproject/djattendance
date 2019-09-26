from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group

from django_select2.forms import ModelSelect2Widget

from .models import User, Trainee, TrainingAssistant, Locality


class APUserCreationForm(forms.ModelForm):
  """ A form for creating a new user """

  password = forms.CharField(label="Password", widget=forms.PasswordInput)
  password_repeat = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

  class Meta:
    model = User
    fields = ["email", "firstname", "lastname", "gender", ]

  def clean(self):
    cleaned_data = super(APUserCreationForm, self).clean()
    password = cleaned_data.get("password")
    password_repeat = cleaned_data.get("password_repeat")
    if password != password_repeat:
      raise forms.ValidationError("Passwords don't match")
    return cleaned_data

  def save(self, commit=True):
    """ Save the provided password in hashed format """
    user = super(APUserCreationForm, self).save(commit=False)
    user.set_password(self.cleaned_data["password"])
    if commit:
      user.save()
    return user


class APUserChangeForm(forms.ModelForm):
  """ A form for updating users. """

  class Meta:
    model = User
    exclude = ['password']


class GroupForm(forms.ModelForm):
  user_set = forms.ModelMultipleChoiceField(
      label='Trainees',
      queryset=User.objects.prefetch_related('groups'),
      required=False,
      widget=FilteredSelectMultiple('user_set', is_stacked=False)
  )

  class Meta:
    model = Group
    fields = ['name', ]
    widgets = {
        'user_set': FilteredSelectMultiple('user_set', is_stacked=False),
    }


# Adding a custom TraineeAdminForm to use prefetch_related all the locality many-to-many relationship
# to pre-cache the relationships and squash all the n+1 sql calls.
class TraineeAdminForm(forms.ModelForm):
  TRAINEE_TYPES = (
      ('R', 'Regular (full-time)'),  # a regular full-time trainee
      ('S', 'Short-term (long-term)'),  # a 'short-term' long-term trainee
      ('C', 'Commuter'),
  )

  type = forms.ChoiceField(choices=TRAINEE_TYPES)

  class Meta:
    model = Trainee
    exclude = ['password']
    widgets = {
        'locality': ModelSelect2Widget(
            queryset=Locality.objects.all(),
            required=False,
            search_fields=['city__icontains', 'state__icontains']
        )  # could add state and country
    }


# Adding a custom TrainingAssistantAdminForm to for change user form
class TrainingAssistantAdminForm(forms.ModelForm):
  class Meta:
    model = TrainingAssistant
    exclude = ['password', ]


class UserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['firstname', 'lastname', ]


class EmailForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['email', ]


class SwitchUserForm(forms.Form):
  user_id = forms.ModelChoiceField(
      queryset=User.objects.filter(is_active=True),
      required=True,
      widget=ModelSelect2Widget(
          model=User,
          queryset=User.objects.filter(is_active=True),
          search_fields=['firstname__icontains', 'lastname__icontains'],
      ),
  )
