from django import forms
from fobi.base import FormFieldPlugin, form_element_plugin_registry
from form_manager.form_elements.name_input.forms import NameInputForm


class NameInputPlugin(FormFieldPlugin):
  """Name Field plugin -- autofills with user name if marked as required."""
  uid = "name_input"
  name = "Trainee Name (autofilled)"
  form = NameInputForm
  # Group to which the plugin belongs to
  group = "Custom"

  def get_form_field_instances(self, request=None, form_entry=None, form_element_entries=None, **kwargs):
    kwargs = {
        'required': self.data.required,
        'label': self.data.label,
        'initial': self.data.initial,
        'widget': forms.widgets.TextInput()
    }
    return [(self.data.name, forms.CharField, kwargs), ]

  def submit_plugin_form_data(self, form_entry, request, form, form_element_entries=None, **kwargs):
    props = self.get_form_field_instances()[0][2]
    form.cleaned_data[props['label']] = request.user.full_name
    return form


form_element_plugin_registry.register(NameInputPlugin)
