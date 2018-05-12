from django.core.urlresolvers import reverse
from django.db import models
from accounts.models import Trainee
from terms.models import Term

""" interim models.py


"""


class InterimIntentionsAdmin(models.Model):

  term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL)

  open_time = models.DateTimeField(null=True, blank=True)

  close_time = models.DateTimeField(null=True, blank=True)

  date_1yr_return = models.DateTimeField(null=True, blank=True)

  date_2yr_return = models.DateTimeField(null=True, blank=True)

  earliest_arrival_date = models.DateField(null=True, blank=True)

  term_begin_date = models.DateField(null=True, blank=True)

  def get_absolute_url(self):
    return reverse('interim:interim_intentions_admin')


class InterimIntentions(models.Model):
  INTENT_CHOICES = (
      ('R', 'Returning'),
      ('N', 'Graduating or not returning'),
      ('U', 'Unsure if I will return next term'),
  )

  POST_INTENT_CHOICES = (
      ('USC', 'Serve Full-Time: College campus in the U.S.'),
      ('OCC', 'Serve Full-Time: College campus in other countries'),
      ('LSM', 'Serve Full-Time: Living Stream Ministry'),
      ('BFA', 'Serve Full-Time: Bibles for America'),
      ('OTH', 'Serve Full-Time: Other (explain'),
      ('XB', 'Attend the FTTA Extension in Boston'),
      ('JOB', 'Take a Job'),
      ('SCH', 'Return to school'),
      ('UND', 'Other/Undecided (explain)'),
      ('NON', 'None'),
  )

  trainee = models.ForeignKey(Trainee, null=True, on_delete=models.SET_NULL)

  admin = models.ForeignKey(InterimIntentionsAdmin, null=True, blank=True, on_delete=models.SET_NULL)

  cell_phone = models.CharField(max_length=50, blank=True, default='555-555-5555')

  email = models.CharField(max_length=50, blank=True)

  home_phone = models.CharField(max_length=50, blank=True, default='555-555-5555')

  home_locality = models.CharField(max_length=50, blank=True)

  home_address = models.CharField(max_length=50, blank=True, null=True)

  home_city = models.CharField(max_length=50, blank=True, null=True)

  home_state = models.CharField(max_length=50, blank=True, null=True)

  home_zip = models.CharField(max_length=50, blank=True, null=True)

  intent = models.CharField(max_length=1, choices=INTENT_CHOICES, default="R")

  post_training_intentions = models.CharField(max_length=3, choices=POST_INTENT_CHOICES, default='NON')

  post_intent_comments = models.CharField(max_length=250, blank=True)

  submitted = models.BooleanField(default=False)

  date_submitted = models.DateField(null=True, blank=True)

  last_updated = models.DateTimeField(null=True, blank=True)

  def __unicode__(self):
    return "[InterimIntentions] %s - %s" % (self.trainee.full_name, self.submitted)

  def get_absolute_url(self):
    return reverse('interim:interim_intentions')


class InterimItinerary(models.Model):
  interim_intentions = models.ForeignKey(InterimIntentions, null=True, on_delete=models.SET_NULL)

  start = models.DateField(null=True, blank=True)

  end = models.DateField(null=True, blank=True)

  comments = models.CharField(max_length=250, blank=True)

  def __unicode__(self):
    return "[InterimItinerary] - %s" % (self.interim_intentions.trainee.full_name)
