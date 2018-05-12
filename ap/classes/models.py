from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from schedules.models import Event
import os


"""" CLASSES models.py

This is a utility module that will be used by other apps, such as class notes or
class syllabi, A/V requests, etc.

It reprents FTTA classes such as God's Economy, Wed night ministry meeting, or
Greek II and Character.

Each instance of a Class object represents a class *for a given term*

Data Models:
    - Class: a class in the FTTA
    - ClassFile: a file (i.e pdf, doc, etc.) for a class (i.e Greek, Character, etc.)

"""

from django.utils.deconstruct import deconstructible

CLASS_CHOICES = (
    ('Greek', 'Greek'),
    ('German', 'German'),
    ('Character', 'Character'),
    ('PSRP', 'PSRP'),
    ('4th Term', 'T4'),
)

# everyone has permissions for these
CLASS_CHOICES_ALL = (
    ('Presentations', 'Presentations'),
)
CLASS_CHOICES_ALL_ITEMS = [c[0] for c in CLASS_CHOICES_ALL]

CLASS_CHOICES += CLASS_CHOICES_ALL

ELECTIVES = r''
for x, y, in CLASS_CHOICES:
  ELECTIVES += x + '|'


@deconstructible
class CustomPath(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        sub_path = '{0}/{1}'.format(instance.for_class, filename)
        print os.path.join(self.path, sub_path)
        return os.path.join(self.path, sub_path)


custom_path = CustomPath("class_files")


class ClassManager(models.Manager):

  def get_queryset(self):
    return super(ClassManager, self).get_queryset().filter(type='C')


class Class(Event):
  class Meta:
    proxy = True
    verbose_name_plural = 'classes'

  def save(self, *args, **kwargs):
    self.type = 'C'
    print 'custom save', self
    super(Class, self).save(*args, **kwargs)

  objects = ClassManager()


class ClassFile(models.Model):

  label = models.CharField(max_length=50, null=True)

  for_class = models.CharField(max_length=30, choices=CLASS_CHOICES, null=True)

  def upload_path(fileObject, filename):
    # i.e 'class_files/Greek/vocab.pdf'
    return 'class_files/{0}/{1}'.format(fileObject.for_class, filename)

  file = models.FileField(upload_to=custom_path, max_length=250)

  def get_delete_url(self):
    return reverse('classes:delete-file', kwargs={'pk': self.id})

  def delete(self, *args, **kwargs):
    if os.path.isfile(self.file.path):
      os.remove(self.file.path)

    super(ClassFile, self).delete(*args, **kwargs)
