from django.forms import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.admin.widgets import FilteredSelectMultiple

# Widget
class CSIFilteredSelectMultiple(FilteredSelectMultiple):
  def value_from_datadict(self, data, files, name):
    # Return a string of comma separated integers since the database, and
    # field expect a string (not a list).
    return ','.join(data.getlist(name))

  def render(self, name, value, attrs=None, renderer=None):
    # Convert comma separated integer string to a list, since the checkbox
    # rendering code expects a list (not a string)
    if value:
      value = value.split(',')
    return super(CSIFilteredSelectMultiple, self).render(
      name, value, attrs=attrs
    )


# Form field
class CSIMultipleChoiceField(MultipleChoiceField):
  def __init__(self, label, *args, **kwargs):
    kwargs['widget'] = CSIFilteredSelectMultiple(
    verbose_name=label,
    is_stacked=False)
    super(CSIMultipleChoiceField, self).__init__(*args, **kwargs)

  # Value is stored and retrieved as a string of comma separated
  # integers. We don't want to do processing to convert the value to
  # a list like the normal MultipleChoiceField does.
  def to_python(self, value):
    return value

  def validate(self, value):
    # If we have a value, then we know it is a string of comma separated
    # integers. To use the MultipleChoiceField validator, we first have
    # to convert the value to a list.
    if value:
      value = value.split(',')
    super(CSIMultipleChoiceField, self).validate(value)
