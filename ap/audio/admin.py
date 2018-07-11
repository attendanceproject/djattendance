from django.contrib import admin

from terms.models import Term
from .models import AudioFile, AudioRequest

class AudioAdmin(admin.ModelAdmin):
  search_fields = ('audio_file',)

admin.site.register(AudioFile, AudioAdmin)
admin.site.register(AudioRequest)
