from django import forms
from .models import Classnotes


class NewClassnotesForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(NewClassnotesForm, self).__init__(*args, **kwargs)

  class Meta:
    model = Classnotes
    exclude = ('status', 'date_submitted', )
    # widgets = {'minimum_words': forms.HiddenInput()}


class EditClassnotesForm(forms.ModelForm):

  class Meta:
    model = Classnotes
    exclude = ('status', 'comments', 'date', 'date_submitted', 'event', 'type', 'trainee')
    widgets = {'minimum_words': forms.HiddenInput()}

  def save(self, commit=True):
    classnotes = super(EditClassnotesForm, self).save(commit=False)
    if commit:
      classnotes.save()
    return classnotes


class ApproveClassnotesForm(forms.ModelForm):

  class Meta:
    model = Classnotes
    # exclude = ('status', 'content', 'date', 'date_submitted', 'event', 'type', 'trainee')
    fields = ['comments', 'submitting_paper_copy']
