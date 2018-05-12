from datetime import timedelta


class Period(object):
  """ a collection of methods related to calculating attendance periods """

  def period_of_week(self, week):
    """ for a week number, starting from zero, return the period """
    return week / self.duration

  def period_of_date(self, date):
    """ for a calendar date, return the period """
    week, day = self.term.reverse_date(date)  # returns a week and a day
    return self.period_of_week(week)

  def start(self, n):
    """ for a period number, return the start date """
    wk = self.duration * n  # week number for start of this period
    return self.term.start + timedelta(weeks=wk)

  def end(self, n):
    """ for a period number, return end date """
    wk = (n + 1) * self.duration  # week number for start of next period
    return self.term.start + timedelta(weeks=wk, days=-1)  # and subtract one day

  def start_end(self, n):
    return self.start(n), self.end(n)

  @staticmethod
  def last_period():
    return 19

  def __init__(self, term):
    self.term = term   # which term these periods apply to
    self.duration = 2  # number of weeks per period
