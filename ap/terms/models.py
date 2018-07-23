import datetime
from datetime import timedelta, date
from exceptions import ValueError

from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from aputils.utils import ensure_date

""" TERM models.py

This schedules module is for representing weekly trainee schedules.

Data Models
- Term:
  a term of the full-time training, consisting of twenty weeks

"""

FIRST_PERIOD = 0
FIRST_WEEK = 0
LAST_PERIOD = 9
LAST_WEEK = 19

SPRING = 'Spring'
FALL = 'Fall'


class Term(models.Model):
  class Meta:
    ordering = ['year', '-season']

  # cache variable stores current term
  # TODO: cache needs to be refreshed each term (on import)
  _current_term = None

  # whether this is the current term
  current = models.BooleanField(default=False)

  # a term's season; i.e. Spring/Fall
  season = models.CharField(max_length=6,
                            choices=(
                              (SPRING, SPRING),
                              (FALL, FALL),
                            ),
                            default=None)

  # which year this term is in; e.g. 2014
  year = models.PositiveSmallIntegerField()

  # first day of the term, the monday of pre-training
  start = models.DateField(verbose_name='start date')

  # the last day of the term, the sat of semiannual
  end = models.DateField(verbose_name='end date')

  # return term's full name; e.g. Fall 2014
  def _name(self):
    return self.season + " " + str(self.year)

  name = property(_name)

  # return term's short code; e.g. Fa14
  def _code(self):
    return self.season[:2] + str(self.year)[2:]

  code = property(_code)

  def _length(self):
    """ number of weeks in the term """
    return 20  # hardcoded until it ever changes

  length = property(_length)

  @staticmethod
  def current_term():
    """ Return the current term """

    # TODO: This cache needs to be blown away at the beginning of each term
    if Term._current_term:
      return Term._current_term

    today = datetime.date.today()
    try:
      Term._current_term = Term.objects.get(current=True)
      return Term._current_term
    except ObjectDoesNotExist:
      # logging.critical('Could not find any terms marked as the current term!')
      # try to return term by date (will not work for interim)
      try:
        return Term.objects.get(Q(start__lte=today), Q(end__gte=today))
      except ObjectDoesNotExist, ProgrammingError:
        # logging.critical('Could not find any terms that match current date!')
        return None
    except MultipleObjectsReturned:
      # logging.critical('More than one term marked as current term! Check your Term models')
      # try to return term by date (will not work for interim)
      return Term.objects.get(Q(start__lte=today), Q(end__gte=today))
    except:
      return None

  @staticmethod
  def next_term():
    """Return the next term"""
    current = Term.current_term()

    if current.season == SPRING:
      return Term(season=FALL, year=current.year)
    else:
      return Term(season=SPRING, year=current.year+1)

  @staticmethod
  def current_season():
    return Term.current_term().season

  @staticmethod
  def set_current_term(term):
    """ Set term to current, set all other terms to not current """
    Term.objects.filter(current=True).update(current=False)
    term.current = True
    term.save()

  @staticmethod
  def decode(code):
    """ Decode term shorthand (e.g. Sp15) """
    return Term.objects.filter(year__endswith=code[2:]).get(season__startswith=code[:2])

  @staticmethod
  def all_weeks_choices():
    ct = Term.current_term()
    if not ct:
      return [(i, 'Week %d' % (i)) for i in range(20)]
    WEEKS_CHOICES = ()
    # create 20 weeks
    for i in range(20):
      s = ct.startdate_of_week(i).strftime("%m/%d")
      e = ct.enddate_of_week(i).strftime("%m/%d")
      WEEKS_CHOICES += ((i, 'Week %d (%s - %s)' % (i, s, e)),)

    return WEEKS_CHOICES

  @property
  def monday_start(self):
    '''
      Returns the real start ot the term (Monday of week start is on)
    '''
    return self.start - timedelta(days=self.start.weekday())

  def is_date_within_term(self, d):
    d = ensure_date(d)
    return d >= self.start and d <= self.end

  def currently_in_term(self):
    today = date.today()
    return self.is_date_within_term(today)

  def startdate_of_week(self, week):
    '''
      Accepts Weeks in range: 0-19 (Returns Monday)
      Guarantee we'll always return a Monday, regardless of start date of term
    '''
    return self.monday_start + timedelta(weeks=week)

  def enddate_of_week(self, week):
    '''
      Accepts Weeks in range: 0-19 (Returns Lord's day)
      Guarantee we'll always return a Lord's Day, regardless of start date of term
    '''
    return self.monday_start + timedelta(weeks=week + 1) - timedelta(days=1)

  def startdate_of_period(self, period):
    '''
      Accepts Periods in range: 0-9
    '''
    return self.startdate_of_week(period*2)

  def enddate_of_period(self, period):
    '''
      Accepts Periods in range: 0-9
    '''
    return self.enddate_of_week(period*2+1)

  def period_from_date(self, date):
    if not self.is_date_within_term(date):
      print 'Outside term range, defaulting to last period'
      return LAST_PERIOD
    return (self.term_week_of_date(date)) // 2

  def term_week_of_date(self, date):
    if not self.is_date_within_term(date):
      print str(date) + ' outside term range, defaulting to last week'
      return LAST_WEEK
    return (date.isocalendar()[1] - self.start.isocalendar()[1])

  def get_date(self, week, day):
    """
      return an absolute date for a term week/day pair
      Week (0-19), Day (0-6) where 0 is Monday
    """
    return self.monday_start + timedelta(days=(week * 7 + day))

  def reverse_date(self, date):
    """ returns a term week/day pair for an absolute date, starting from 0/0 """
    if self.start <= date <= self.end:
      # days since the term started
      delta = date - self.monday_start
      return (delta.days / 7, delta.days % 7)
    # if not within the dates the term, raise an error
    else:
      # by default return last date in term
      return (19, 6)

  def is_attendance_finalized(self, week, trainee):
    today = datetime.date.today()
    term = self.current_term()
    week_start = term.startdate_of_week(week)
    week_end = term.enddate_of_week(week)
    if trainee.rolls.filter(date__lte=week_end, date__gte=week_start, finalized=True, submitted_by=trainee).count() > 0:
      return True
    else:
      return False

  def __unicode__(self):
    try:
      return self.name
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
