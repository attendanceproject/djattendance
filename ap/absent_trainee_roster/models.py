from django.db import models

from accounts.models import Trainee
from houses.models import House

""" absent_trainee_roster models.py
The absent trainee roster module takes care of generating daily absent trainee rosters
from HC imported forms.

ABSENTEE
-represents each trainee as an absentee

ROSTERMANAGER
-initializes each newly created roster with the list of houses that need to submit their absent trainee form

ROSTER
-compiles all the absent trainee forms submitted on a given date

ENTRY
-form submitted by the house coordinators to be compiled and generated as the roster

"""


class Absentee(Trainee):
  class Meta:
    proxy = True

  @property
  def name(self):
    return self.full_name

  @property
  def term(self):
    return self.current_term

  def __unicode__(self):
    try:
      return self.full_name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class RosterManager(models.Manager):
  # Only works for one-to-one relationships. Currently does not work for other types
  use_for_related_fields = True

  # when roster is created in admin, admin calls RosterAdmin.save_related()
  # to add the unreported houses.
  def create_roster(self, date):
    roster = self.create(date=date)
    roster.save()  # have to save before adding many-to-many relationship
    # initialize with all houses unreported (remove houses from list when hc submits form).
    for house in House.objects.all():
      roster.unreported_houses.add(house)
    roster.save()
    return roster

  def get_queryset(self):
    return super(RosterManager, self).get_queryset().order_by('date')


class Roster(models.Model):
  objects = RosterManager()

  date = models.DateField(primary_key=True)

  objects = RosterManager()
  unreported_houses = models.ManyToManyField(House, related_name='rosters', blank=True)
  notes = models.CharField(max_length=250, blank=True)

  def __unicode__(self):
    try:
      return self.date.strftime("%m/%d/%Y") + " roster"
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class Entry(models.Model):

  ABSENT_REASONS = (
      ('C', 'Conference'),
      ('SI', 'Sick'),
      ('SE', 'Service'),
      ('O', 'Other'),
      ('T', 'Out of Town'),
      ('F', 'Fatigue'),
  )

  roster = models.ForeignKey(Roster, on_delete=models.SET_NULL, null=True)
  absentee = models.ForeignKey(Absentee, on_delete=models.SET_NULL, null=True)
  reason = models.CharField(max_length=2, choices=ABSENT_REASONS)
  # to be removed, not yet done to minimize model changes mid-term
  coming_to_class = models.BooleanField(default=False)
  comments = models.CharField(max_length=250, blank=True)

  class Meta:
    verbose_name_plural = 'entries'
    unique_together = ('roster', 'absentee',)

  def __unicode__(self):
    try:
      return '%s - %s' % (self.absentee.full_name, self.roster)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

