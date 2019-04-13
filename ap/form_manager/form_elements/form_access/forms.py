from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput
from django import forms
from fobi.base import BasePluginForm, get_theme

theme = get_theme(request=None, as_instance=True)


class FormAccessForm(forms.Form, BasePluginForm):
  """ Form Access form. """

  plugin_data_fields = [
      ("name", "Access"),
      ("label", "Access"),
      ("initial", ""),
  ]

  # This important for trainee_select.js
  attrs = {
      'id': 'id_trainees',
  }

  name = forms.CharField(label="Name", required=False)

  label = forms.CharField(label="Label", required=False)

  initial = forms.ModelMultipleChoiceField(
      queryset=Trainee.objects.all(),
      label="Trainees",
      required=False,
      widget=TraineeSelect2MultipleInput(attrs=attrs),
  )

  def get_plugin_data(self, request=None, json_format=True):
    """Get plugin data.

    overwrites get_plugin_data() to convert queryset to list of ints
    see fobi.base for more.

    """

    qs = self.cleaned_data.get('initial')  # QuerySet of Trainees
    ids = []
    if len(qs) > 0:
      for q in qs:
        ids.append(q.id)

    self.cleaned_data['initial'] = ids
    self.cleaned_data['name'] = 'Access'
    self.cleaned_data['label'] = 'Access'

    return self._get_plugin_data(
        self.plugin_data_fields,
        request=request,
        json_format=json_format
    )
