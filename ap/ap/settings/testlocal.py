# Django setting to test locally

################################################################
#                   test against dev setting                   #
#                     remove debug toolbar                     #
################################################################

from .dev import *

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('debug_toolbar')
INSTALLED_APPS = tuple(INSTALLED_APPS)

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE = tuple(MIDDLEWARE)

DEBUG_TOOLBAR_CONFIG = {}

################################################################
#                  test against prod setting                   #
################################################################
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
DEFAULT_FROM_EMAIL = 'AP <ap@ftta.com>'
SERVER_EMAIL = 'AP Server <server@ftta.com>'

# Set unlimited persistent connections
CONN_MAX_AGE = 'None'

# Make sure to set this to true when you run server in production (ap.ini file)
FLUSH_CRON_SETTINGS = True if 'FLUSH_CRON_SETTINGS' in os.environ and os.environ['FLUSH_CRON_SETTINGS'] == 'True' else False

# Flush cron_jobs settings (exec only once when server is run)
if FLUSH_CRON_SETTINGS:
  print 'Flushing Cron_job settings!'
  INSTALLED_APPS += ('cron_jobs',)

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
)
