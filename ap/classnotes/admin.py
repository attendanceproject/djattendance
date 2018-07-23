from django.contrib import admin
from .models import Classnotes


class ClassnotesAdmin(admin.ModelAdmin):
  list_display = ['pk', 'trainee', 'event', 'date']


# Register your models here.
admin.site.register(Classnotes, ClassnotesAdmin)
