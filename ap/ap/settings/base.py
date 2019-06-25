# Django settings for AP


import os
import django
from django.contrib.messages import constants as message_constants

# Overwritten to False in prod.py
DEBUG = True

# calculated paths for django and the site
# used as starting points for various other paths
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# List of emails to send absentee roster reports to every morning
ABSENTEE_ROSTER_RECIPIENTS = ['attendanceproj@gmail.com', ]

ADMINS = (
    ('Attendance Project', 'attendanceproj@gmail.com'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False  # djattendance (for now) only runs in Anaheim.

# set default datetime format to m/d/y with 12-base. eg: April 14, 2008 3:45pm will be shown as 04/14/2008 03:45 PM
DATETIME_FORMAT = 'm/d/Y h:i A'
DATETIME_INPUT_FORMATS = ['%m/%d/%Y %I:%M %p']

# set default date format to m/d/y. eg: April 14, 2008 will be shown as 04/14/2008
DATE_FORMAT = 'm/d/Y'
DATE_INPUT_FORMATS = ['%m/%d/%Y']

# set default time format to 12-base. eg: 3:45pm will be shown as 03:45 PM
TIME_FORMAT = 'h:i A'
TIME_INPUT_FORMATS = ['%I:%M %p']

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

# Temporary folder for upload, in this example is the subfolder 'upload'
UPLOAD_TO = os.path.join(SITE_ROOT, 'media', 'upload')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h%)g$1=j)_(lozsexfe*=$iwj9l#8mfaszohyg5n0azz691r#b'

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # AP middleware
    'ap.middleware.LoginRequiredMiddleware',
    'bible_tracker.middleware.BibleReadingMiddleware',
    'services.middleware.DesignatedServiceHoursMiddleware'
)

ROOT_URLCONF = 'ap.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ap.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(SITE_ROOT, 'templates')],
    'OPTIONS': {
        'loaders': [
            ('django.template.loaders.cached.Loader',
                [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'
                ]),
        ],
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.debug",
            "django.template.context_processors.media",
            "django.contrib.messages.context_processors.messages",
            "django.template.context_processors.request",
            "exams.context_processors.exams_available",
            "interim.context_processors.interim_intentions_available",
            "gospel_trips.context_processors.gospel_trips_available",
            "gospel_trips.context_processors.teams_available",
            "bible_tracker.context_processors.bible_tracker_forced",
            "announcements.context_processors.class_popup",

            "django.template.context_processors.i18n",
            "django.template.context_processors.static",
            "django.template.context_processors.tz",
            # "sekizai.context_processors.sekizai",
            "fobi.context_processors.theme",
        ],
    },
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

AUTH_USER_MODEL = 'accounts.User'

# Make logins case-insensitive
AUTHENTICATION_BACKENDS = (
    'aputils.backends.CaseInsensitiveModelBackend',
)

APPS = (
    # ap CORE
    'accounts',
    'apimport',
    'aputils',
    'books',
    'classes',
    'houses',
    'localities',
    'rooms',
    'services',
    'teams',
    'terms',

    # ap modules
    'announcements',  # announcements
    'attendance',
    'audio',
    'absent_trainee_roster',
    'badges',  # badge pictures and facebooks
    'bible_tracker',
    'classnotes',
    'dailybread',  # daily nourishment
    'exams',
    'gospel_statistics',
    'gospel_trips',
    'graduation',
    'hc',
    'house_requests',
    'interim',
    'leaveslips',
    'lifestudies',
    'meal_seating',
    'reports',
    'room_reservations',
    'schedules',
    'seating',  # seating charts
    'semi',
    'syllabus',  # class syllabus
    'verse_parse',  # parse outlines for PSRP verses
    'web_access',
    'xb_application',
    'house_inspection',

    # fobi-core
    'fobi',

    # theme
    'fobi.contrib.themes.bootstrap3',

    # form-elements
    'fobi.contrib.plugins.form_elements.fields.boolean',
    'fobi.contrib.plugins.form_elements.fields.date',
    'fobi.contrib.plugins.form_elements.fields.email',
    'fobi.contrib.plugins.form_elements.fields.file',
    'fobi.contrib.plugins.form_elements.fields.float',
    'fobi.contrib.plugins.form_elements.fields.integer',
    'fobi.contrib.plugins.form_elements.fields.radio',
    'fobi.contrib.plugins.form_elements.fields.select_model_object',
    'fobi.contrib.plugins.form_elements.fields.select_multiple_model_objects',
    'fobi.contrib.plugins.form_elements.fields.text',
    'fobi.contrib.plugins.form_elements.fields.time',

    # handlers
    'fobi.contrib.plugins.form_handlers.db_store',

    # custom theme
    'form_manager',

    # custom form-element
    'form_manager.form_elements.name_input',
    'form_manager.form_elements.form_access',
)

# more fobi settings
FOBI_DEFAULT_THEME = 'bootstrap3'
FOBI_RESTRICT_PLUGIN_ACCESS = False
FOBI_THEME_FOOTER_TEXT = ''
# FOBI settings depends on BASE_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__name__))

INSTALLED_APPS = (
    # admin third-party modules
    'adminactions',
    'suit',  # needs to be in front of 'django.contrib.admin'
    'paintstore',
    'solo',
    'django_extensions',
    'webpack_loader',
    'rest_framework_swagger',

    # django contrib
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # third-party django modules
    'bootstrap3',  # easy-to-use bootstrap integration
    'braces',  # Mixins for Django's class-based views.
    # 'explorer',  # SQL explorer
    'django_select2',
    'rest_framework',  # for API
    'django_countries',  # to replace aputils country
    'localflavor',  # to replace aputils states
    'django_filters',
) + APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'import_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'import.log'),
            'when': 'midnight',
            'interval': 1,
            'formatter': 'standard'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'xhtml2pdf': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'apimport': {
            'handlers': ['import_logfile', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

BOOTSTRAP3 = {
    'base_url': None,
    'theme_url': None,
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4',
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(SITE_ROOT, '../webpack/webpack-stats.json'),
    }
}

# URL after login page
LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',  # blue
    message_constants.SUCCESS: 'success',  # green
    message_constants.WARNING: 'warning',  # yellow
    message_constants.ERROR: 'danger',  # red
}

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.ModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ]
}

SUIT_CONFIG = {
    # header
    'ADMIN_NAME': 'FTTA Admin',
    'LIST_PER_PAGE': 20,
    'SEARCH_URL': '',
}

# Settings for graphing SQL Schema
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

# Default for this is 1000 which is a little low for the exam grade entering
# page which might submit 2 values * 500 trainees > 1000
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

# Auto adds in css for admin pages
AUTO_RENDER_SELECT2_STATICS = True

COUNTRIES_FIRST = ['US', 'CN', 'CA', 'BZ', ]

# Communicating with firewall for granting web access requests
HOST = "10.0.8.20"  # hostname or ip address of the firewall (add to /etc/hosts)
PORT = 12345  # server port of application which listens for commands on the firewall

PROJECT_HOME = os.path.dirname(SITE_ROOT)

AUDIO_FILES_ROOT = MEDIA_ROOT + '/audio/Attendance Server'
AUDIO_FILES_URL = MEDIA_URL + 'audio/Attendance Server'

# by default allow rw- r-- r--
FILE_UPLOAD_PERMISSIONS = 0o644

SELECT2_JS = ''
SELECT2_CSS = ''
