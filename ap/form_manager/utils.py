import json  # fobi user json for form_elements not Django models

from fobi.models import FormEntry

ALL_ACCESS = "*"


def get_form_access(form_entry):
  form_elements = form_entry.formelemententry_set.all()
  for el in form_elements:
    data = json.loads(el.plugin_data)
    if data['name'] == 'Access':
      return data['initial']
  return ALL_ACCESS


def user_can_see_form(user, form_entry):
  trainee_ids = get_form_access(form_entry)
  return trainee_ids == ALL_ACCESS or str(user.id) in str(trainee_ids)


def user_forms(user):
  public_FormEntries = FormEntry.objects.filter(is_public=True)
  return filter(lambda pf: user_can_see_form(user, pf), public_FormEntries)
