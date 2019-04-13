from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    ('Attendance Project', 'attendanceproj@gmail.com'),
)
MANAGERS = ADMINS

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'AP <ap@ftta.org>'
SERVER_EMAIL = 'AP Server <server@ftta.org>'
ABSENT_TRAINEE_ROSTER_EMAIL = 'Absent Trainee Roster <server@ftta.org>'

# Set unlimited persistent connections
CONN_MAX_AGE = 'None'

# Make sure to set this to true when you run server in production (ap.ini file)
FLUSH_CRON_SETTINGS = True if 'FLUSH_CRON_SETTINGS' in os.environ and os.environ['FLUSH_CRON_SETTINGS'] == 'True' else False

# Flush cron_jobs settings (exec only once when server is run)
if FLUSH_CRON_SETTINGS:
  print 'Flushing Cron_job settings!'
  INSTALLED_APPS += ('cron_jobs',)

# Parse database configuration from $DATABASE_URL
import dj_database_url
'''
  For the following to work, you need to:
  export DATABASE_URL='postgres://{{username}}:{{password}}@localhost:5432/{{database}}'
'''
DATABASES = {'default': dj_database_url.config()}

assert 'SECRET_KEY' in os.environ, 'Set SECRET_KEY in your .env file!'
SECRET_KEY = os.environ['SECRET_KEY']
assert 'ABSENTEE_ROSTER_RECIPIENTS' in os.environ, 'Set ABSENTEE_ROSTER_RECIPIENTS in your .env file!'
ABSENTEE_ROSTER_RECIPIENTS += [email.strip(' ') for email in os.environ['ABSENTEE_ROSTER_RECIPIENTS'].split(',')]

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

STATICFILES_DIRS = (
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'select2': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Set the cache backend to select2
SELECT2_CACHE_BACKEND = 'select2'
