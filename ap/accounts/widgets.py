from django_select2.forms import Select2MultipleWidget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from ap.forms import TraineeSelectForm


class TraineeSelect2MultipleInput(Select2MultipleWidget):
  def render(self, name, value, attrs=None, renderer=None):
    attrs['class'] = 'trainee-select'
    output = super(TraineeSelect2MultipleInput, self).render(name, value, attrs)
    button = '<button type="button" class="btn btn-default trainee-select" data-toggle="modal" data-target="#trainee_select"><span class="">Add Trainee Group</span></button>'
    select_modal = render_to_string('popups/trainee_select_modal.html', {'trainee_select_form': TraineeSelectForm()})
    return output + mark_safe(button) + mark_safe(select_modal)
