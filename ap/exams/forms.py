from accounts.models import Trainee
from accounts.widgets import TraineeSelect2MultipleInput
from classes.models import Class
from django.forms import ModelForm
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

from .models import Exam, Session


class ExamCreateForm(ModelForm):
  training_class = ModelChoiceField(
    Class.regularclasses.all(), empty_label=None, label="Training Class"
  )

  class Meta:
    model = Exam
    fields = ('training_class', 'description', 'is_open', 'is_graded_open', 'duration', 'category', 'term')


class ExamReportForm(ModelForm):
  exam = ModelChoiceField(queryset=Exam.objects.all(), required=False, label='Select an exam (Default - all exams)')
  label = 'Trainees whose exams to generate a report for'
  trainee = ModelMultipleChoiceField(
    widget=TraineeSelect2MultipleInput,
    queryset=Trainee.objects.all(),
    required=False,
    label=label
  )

  def __init__(self, *args, **kwargs):
    super(ExamReportForm, self).__init__(*args, **kwargs)
    self.fields['trainee'].widget.attrs = {'id': 'id_trainees'}

  class Meta:
    model = Session
    fields = ('exam', 'trainee',)
