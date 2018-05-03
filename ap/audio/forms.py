from django import forms

from aputils.trainee_utils import is_TA
from terms.models import Term
from .models import AudioRequest, AudioFile, order_audio_files


class AudioRequestForm(forms.ModelForm):
  class Meta:
    model = AudioRequest

    fields = (
        'trainee_comments',
        'audio_requested',
        'TA_comments'
    )

    labels = {
        'trainee_comments': 'Please describe the reason for your request in detail.',
    }

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user')
    super(AudioRequestForm, self).__init__(*args, **kwargs)
    sorted_files = order_audio_files(AudioFile.objects.filter_term(Term.current_term()))
    choices = [(a.id, a.get_full_name()) for a in sorted_files]
    self.fields['audio_requested'].choices = choices
    if not is_TA(self.user):
      self.fields['TA_comments'].disabled = True


class AudioRequestTACommentForm(forms.ModelForm):
  class Meta:
    model = AudioRequest
    fields = ['TA_comments']
