# Django setting for testing by cloud resources

################################################################
#                  Database credential changes                 #
#               Test against prod setting closely              #
################################################################

from .testlocal import *

DEBUG = False
TEMPLATE_DEBUG = False

# TODO: Investigate[if DEBUG = False, then Bible Reading Tracker layout = incorrect]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djattendance',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}
