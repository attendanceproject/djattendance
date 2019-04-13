from datetime import date, datetime, time, timedelta

from accounts.models import User
from books.models import Book
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from terms.models import Term
from attendance.utils import Period

""" lifestudies models.py
This discipline module handles the assigning and managing of
the life-study summaries from the TA side and the submitting
from the trainees' side.

DISCIPLINE
  - A discipline is assigned by TA to a single trainees, along with the
    number of summaries needed to complete it.
  - The model methods are mostly invovled with the summaries that are
    related to it.
  - A discipline is completed when ALL summaries associated are approved
  - approving a discipline is done by approving all related summaries

SUMMARY
  - A summary is related to a single book and has the content inputted by
    a trainee.

"""

class DisciplineManager(models.Manager):
  def get_queryset(self):
    queryset = super(DisciplineManager, self).get_queryset()
    if Term.current_term():
      start_date = Term.current_term().start
      end_date = Term.current_term().end
      return queryset.filter(date_assigned__gte=start_date, date_assigned__lte=end_date).distinct()
    else:
      return queryset


class DisciplineAllManager(models.Manager):
  def get_queryset(self):
    return super(DisciplineAllManager, self).get_queryset()


class Discipline(models.Model):

  objects = DisciplineManager()
  objects_all = DisciplineAllManager()

  TYPE_OFFENSE_CHOICES = (
    ('MO', 'Monday Offense'),
    ('RO', 'Regular Offense'),
  )

  TYPE_INFRACTION_CHOICES = (
    ('AT', 'Attendance'),
    ('CI', 'Cell Phone & Internet'),
    ('MS', 'Missed Service'),
    ('S', 'Speeding'),
    ('AN', 'Alarm Noise'),
    ('G', 'Guard'),
    ('C', 'Curfew'),
    ('M', 'Misplaced Item'),
    ('HI', 'House Inspection'),
    ('L', 'Library'),
    ('MISC', 'Misc'),
  )

  # an infraction is the reason for the trainee to be assigned discipline
  infraction = models.CharField(choices=TYPE_INFRACTION_CHOICES, max_length=4)

  # a quantity refers to how many summaries are assigned
  quantity = models.PositiveSmallIntegerField()

  # the date of the assignment of the discipline.
  date_assigned = models.DateTimeField(auto_now_add=True)

  # the due date and time for the discipline to be submitted by
  due = models.DateTimeField()

  # the type of offense being assigned
  offense = models.CharField(choices=TYPE_OFFENSE_CHOICES, default='RO', max_length=2)

  trainee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

  missed_service = models.TextField(blank=True, null=True)

  note = models.TextField(blank=True)

  # sort disciplines by name
  class Meta:
    ordering = ["trainee__lastname"]

  def approve_all_summary(self):
    for summary in self.summary_set.all():
      summary.approve()
    self.save()
    return self.summary_set.all()

  def get_num_summary_due(self):
    """get the number of summary that still needs to be submitted"""
    return self.quantity - len(self.summary_set.filter(approved=True).all())

  def get_num_summary_approved(self):
    """get the number of summary that still needs to be approved"""
    num = 0
    for summary in self.summary_set.all():
      if summary.approved is True:
        num = num + 1
    return num

  def show_create_button(self):
    """checks whether create life-study button will show or not"""
    return self.quantity - len(self.summary_set.all()) > 0 and not (self.offense == 'MO' and date.today().weekday() != 0)

  # if this is True it means all the lifestudies has been approved and all
  # have been submitted. This assume num of summary submitted not larger
  # than num of summary assigned
  def is_completed(self):
    return self.get_num_summary_due() <= 0

  # decrease the quantity of the discipline by the number specified. Subtract 1
  # summary if num is not specified
  def decrease_penalty(self, num=1):
    if self.quantity - num < 1:
      # Delete the discipline
      self.delete()
    else:
      self.quantity -= num
      self.save()
    return self.quantity

  # increase the quantity of the discipline by the number specified. Add 1
  # more summary if num is not specified
  def increase_penalty(self, num=1):
    self.quantity += num
    self.save()
    return self.quantity

  @staticmethod
  def calculate_summary(trainee, period):
    """this function examines the Schedule belonging to trainee and search
    through all the Events and Rolls. Returns the number of summary a
    trainee needs to be assigned over the given period."""
    num_A = 0
    num_T = 0
    num_summary = 0
    current_term = Term.current_term()
    for roll in trainee.rolls.all():
      if roll.date >= Period(current_term).start(period) and roll.date <= Period(current_term).end(period):
        if roll.status == 'A':
          num_A += 1
        elif roll.status == 'L' or roll.status == 'T' or roll.status == 'U':
          num_T += 1
    if num_A >= 2:
      num_summary += num_A
    if num_T >= 5:
      num_summary += num_T - 3
    return num_summary

  @staticmethod
  def assign_attendance_summaries(trainee, period, amount):
    """this function is meant to be used with calculate_summary supplying the
    amount parameter. It takes the trainee given and assigns to him or her the
    amount of life-study summaries specified for the period given"""
    now = datetime.now()
    due = datetime.combine(now.date() + timedelta(weeks=1, days=1), time(18, 45))
    d = Discipline(infraction='AT', quantity=amount, date_assigned=now,
                   due=due, offense='MO', trainee=trainee)
    d.save()

  # Grab last date_submitted summary, grab book and check if chapter reached, auto-increment
  def next_summary_book_chapter(self):
    last_book = self.summary_set.latest('date_submitted')
    print 'last', last_book
    return last_book

  def __unicode__(self):
    try:
      return "[{offense}] {name}. Infraction: {infraction}. Quantity: \
        {quantity}. Still need {num_summary_due} summaries. Completed: \
        {is_completed}".format(
        name=self.trainee.full_name,
        infraction=self.infraction, offense=self.offense,
        quantity=self.quantity, num_summary_due=self.get_num_summary_due(),
        is_completed=self.is_completed())
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class SummaryManager(models.Manager):
  def get_queryset(self):
    queryset = super(SummaryManager, self).get_queryset()
    if Term.current_term():
      start_date = Term.current_term().start
      end_date = Term.current_term().end
      return queryset.filter(date_submitted__gte=start_date, date_submitted__lte=end_date).distinct()
    else:
      return queryset


class SummaryAllManager(models.Manager):
  def get_queryset(self):
    return super(SummaryAllManager, self).get_queryset()


class Summary(models.Model):

  objects = SummaryManager()
  objects_all = SummaryAllManager()

  # the content of the summary (> 250 words)
  content = models.TextField(blank=True)

  # the book assigned to summary
  # relationship: many summaries to one book
  book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.SET_NULL)

  # the chapter assigned to summary
  chapter = models.PositiveSmallIntegerField()

  # if the summary has been approved
  approved = models.BooleanField(default=False)

  # if the summary is marked for fellowship
  fellowship = models.BooleanField(default=False)

  """ Decided to remove this field. We now auto hide approved submissions"""
  # if the summary is marked for delete then we hide
  # deleted = models.BooleanField(default=False)

  # which discipline this summary is associated with
  discipline = models.ForeignKey(Discipline, on_delete=models.SET_NULL, null=True)

  # automatically generated date when summary is submitted
  date_submitted = models.DateTimeField(auto_now_add=True)

  # minWord Count
  minimum_words = models.PositiveSmallIntegerField(default=250)

  # hardCopy
  submitting_paper_copy = models.BooleanField(default=False)

  # sort summaries by name
  class Meta:
    ordering = ["approved"]

  def __unicode__(self):
    try:
      return "[{book} ch. {chapter}] {name}. Approved: {approved}".format(
        name=self.discipline.trainee.full_name,
        book=self.book.name, chapter=self.chapter, approved=self.approved)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  # remove fellowship mark if approved
  def approve(self):
    self.approved = True
    self.fellowship = False
    self.save()
    return self

  def unapprove(self):
    self.approved = False
    self.save()
    return self

  def set_fellowship(self):
    self.fellowship = True
    self.save()
    return self

  def remove_fellowship(self):
    self.fellowship = False
    self.save()
    return self

  def clean(self, *args, **kwargs):
    """Custom validator for word count"""
    wc_list = self.content.split()
    if len(wc_list) < self.minimum_words and self.submitting_paper_copy is False:
      raise ValidationError("Your word count is less than {count}".format(count=self.minimum_words))
    super(Summary, self).clean(*args, **kwargs)

  def save(self, *args, **kwargs):
    self.full_clean()
    super(Summary, self).save(*args, **kwargs)

  def next(self):
    return Summary.objects.filter(date_submitted__gt=self.date_submitted, discipline=self.discipline).order_by('date_submitted').first()

  def prev(self):
    return Summary.objects.filter(date_submitted__lt=self.date_submitted, discipline=self.discipline).order_by('-date_submitted').first()

  def get_absolute_url(self):
    return reverse('lifestudies:summary_detail', kwargs={'pk': self.id})
