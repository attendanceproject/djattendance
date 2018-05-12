from django.db import models

from terms.models import Term

from .util import _image_upload_path, resize_image
from django.conf import settings

from solo.models import SingletonModel
from paintstore.fields import ColorPickerField

class Badge(models.Model):
  """
  A training badge. There are different badges for trainees,
  staff and so forth. Otherwise known as a profile picture.
  """

  BADGE_TYPES = (
    ('T', 'Trainee'),
    ('S', 'Staff'),
    ('XS', 'XB-Staff'),
    ('X', 'XB-Trainee'),
  )

  GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
  )

  type = models.CharField(max_length=2, choices=BADGE_TYPES, default='T')
  original = models.ImageField(upload_to=_image_upload_path, null=True, blank=True)
  term_created = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True)
  # thumbnail
  # badge_size

  # badge information
  # can be automatically populated from user account
  firstname = models.CharField(max_length=50, null=True, blank=True)
  middlename = models.CharField(max_length=1, null=True, blank=True)
  lastname = models.CharField(max_length=50, null=True, blank=True)
  gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
  title = models.CharField(max_length=30, null=True, blank=True)
  locality = models.CharField(max_length=100, null=True, blank=True)
  avatar = models.CharField(max_length=255, null=True, blank=True)
  deactivated = models.BooleanField(default=False)

  # for defining images' paths after dropping it through dropzonejs
  def get_upload_path(self, filename):
    path = "badges/"
    if self.type == 'T':
      path += "trainees/" + self.term_created.code + '/'
    elif self.type == 'S':
      path += "staff/"
    elif self.type == 'X':
      path += "xb/"
    elif self.type == 'XS':
      path += "bostonstaff/"
    return path + filename

  def save(self, *args, **kwargs):
    super(Badge, self).save(*args, **kwargs)
    resize_image(self.original)
    name = self.original.path.split('media')
    self.avatar = "media" + name[1] + ".avatar"
    print self.avatar
    super(Badge, self).save(*args, **kwargs)

  def __unicode__(self):
    try:
      return u"[%s] %s" % (self.type, self.original.name)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


# singleton object to hold badge color settings
class BadgePrintSettings(SingletonModel):
  banner_color = ColorPickerField(blank=True, null=True)

  def __unicode__(self):
    try:
      return u"Badge Printing Configuration"
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    verbose_name = "Badge Printing Configuration"
