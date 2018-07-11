from plan import Plan, Job
import os
import sys


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
MANAGE_ROOT = os.path.dirname(SITE_ROOT)

LOG_FILE = 'cron.log'
LOG_PATH = os.path.join(SITE_ROOT, LOG_FILE)

ADMIN_EMAIL = 'attendanceproj@gmail.com'

# Get Cronjob user to run cron tasks with
assert 'CRON_USER' in os.environ, 'Set CRON_USER in your .env file!'
CRON_USER = os.environ['CRON_USER']


PROJECT_RELATED_ENV = ['APENV', 
                        ]

if 'PYTHON_EXECUTABLE' in os.environ:
  # This needs to be defined in wsgi to work to fix wsgi replacing sys.executable with wsgi exe
  PYTHON_EXECUTABLE = os.environ['PYTHON_EXECUTABLE']
else:
  PYTHON_EXECUTABLE = sys.executable

ENVIRONMENT = {}

# Add in environment vars relevant to the proj
for var in PROJECT_RELATED_ENV:
  if var in os.environ:
    ENVIRONMENT[var] = os.environ[var]

class DjangoJob(Job):

  def task_template(self):
    return 'cd %s && python {task} >> {output}' % (SITE_ROOT)

# Allows you to regularly run django commands: manage.py task
class DjangoCommandJob(Job):

  def task_template(self):
    # return 'source ~/.bashrc && workon %s && cd %s && python manage.py {task} >> %s' % (VIRTUALENV, MANAGE_ROOT, LOG_PATH)
    return 'cd %s && {environment} %s manage.py {task} >> {output}' % (MANAGE_ROOT, PYTHON_EXECUTABLE)

cron = Plan(environment=ENVIRONMENT, output=LOG_PATH, user=CRON_USER)

# This tells crontab to email admins if any cron job failed.
cron.env('MAILTO', ADMIN_EMAIL)

#################################### Job definitions ###################################

job = DjangoJob(task='task.py', every='1.day', at='02:00')
cron.job(job)

for day in ('sunday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'):
    absentee_report_job = DjangoCommandJob(
        task='send_absentee_roster_emails',
        every=day,
        at='08:00'
    )
    cron.job(absentee_report_job)
# cron.command('env > ~/cronenv', every='1.minute')
# cron.command('ls /tmp', every='1.day', at='12:00')
# cron.command('pwd', every='2.month')
# cron.command('pwd', every='1.minute')
#cron.command('echo $(pwd) + $(date) >> ' + os.path.join(SITE_ROOT, 'cron.log'), every='1.day', at='16:39')
# cron.command('echo "ray" + $(date) >>', every='1.minute')


#################################### Flush #######################################

cron.run('write')
