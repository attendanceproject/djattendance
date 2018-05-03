from django import forms

from accounts.widgets import TraineeSelect2MultipleInput
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from .models import IndividualSlip, GroupSlip
from accounts.models import Trainee
from services.models import Assignment


class LeaveslipForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(LeaveslipForm, self).__init__(*args, **kwargs)
    self.fields['type'].label = 'Reason'
    self.fields['TA'].label = 'TA assigned to this leave slip: %s' % self.instance.TA.full_name + '. Transfer to:'
    self.fields['TA_informed'].label = 'Training office informed? ' + ('Yes' if self.instance.informed else 'No')
    if not self.instance.informed:
      self.fields['TA_informed'].widget.attrs['class'] = 'hidden-input'
    self.fields['description'].widget.attrs['rows'] = 2
    self.fields['private_TA_comments'].widget.attrs['rows'] = 2
    self.fields['comments'].widget.attrs['rows'] = 2


class IndividualSlipForm(LeaveslipForm):
  def __init__(self, *args, **kwargs):
    super(IndividualSlipForm, self).__init__(*args, **kwargs)
    self.fields['location'].widget.attrs['rows'] = 2
    self.fields['location'].widget.attrs['class'] = 'night-out meal-out'
    self.fields['host_name'].widget.attrs['rows'] = 2
    self.fields['host_name'].widget.attrs['class'] = 'night-out meal-out'
    self.fields['host_phone'].widget.attrs['class'] = 'night-out'
    self.fields['hc_notified'].label = 'HC notified'
    self.fields['hc_notified'].widget.attrs['rows'] = 2
    self.fields['hc_notified'].widget.attrs['class'] = 'night-out'

  class Meta:
    model = IndividualSlip
    fields = ['trainee', 'type', 'description', 'location', 'host_name', 'host_phone', 'hc_notified',
              'private_TA_comments', 'comments', 'TA_informed', 'texted', 'TA']


class GroupSlipForm(LeaveslipForm):
  trainees = forms.ModelMultipleChoiceField(
      queryset=Trainee.objects.all(),
      required=True,
      widget=ModelSelect2MultipleWidget(model=Trainee),
  )

  def __init__(self, *args, **kwargs):
    super(GroupSlipForm, self).__init__(*args, **kwargs)

  class Meta:
    model = GroupSlip
    fields = ['trainees', 'type', 'description', 'private_TA_comments', 'comments', 'start', 'end', 'TA_informed', 'texted', 'TA']


class GroupSlipAdminForm(forms.ModelForm):
  trainees = forms.ModelMultipleChoiceField(
      queryset=Trainee.objects.all(),
      label='Trainees',
      required=False,
      widget=TraineeSelect2MultipleInput,
  )

  service_assignment = forms.ModelChoiceField(
      label='Service Assignment',
      queryset=Assignment.objects.all(),
      required=False,
      widget=ModelSelect2Widget(
          model=Assignment,
          search_fields=['service__name__icontains'],
      ),
  )

  def __init__(self, *args, **kwargs):
    super(GroupSlipAdminForm, self).__init__(*args, **kwargs)
