from __future__ import absolute_import

from datetime import datetime

from attendance.utils import Period
from terms.models import Term
from accounts.models import Trainee
from lifestudies.models import Discipline
from datetime import date, datetime

logger = get_task_logger(__name__)

def assignDiscipline():
  try:
    logger.info("Start task")
    term = Term.current_term()
    period = Period(term).period_of_date(date.today())
    for trainee in Trainee.objects.filter(is_active=True).all():
      amount = 0
      amount += trainee.calculate_summary(period)
      logger.info('%s : %d life studies' % (trainee.full_name, amount))
      Discipline.assign_attendance_summaries(trainee, period, amount)
  except Exception, msg:
    logger.error(msg)

# currently takes between 0.04 and 0.05 sec to run for one trainee
# @periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*"))) #Run every minute (For debugging)
# @periodic_task(run_every=(crontab(hour="10", minute="0", day_of_week="6"))) #Run every Lord's Day at 10pm
def assignDiscipline_periodic():
  assignDiscipline()
