import os
from main.settings import *

INSTALLED_APPS += ('django_jenkins', )

SECRET_KEY = 'fake-key'
TEST_RUNNER = "tests.fast_test_runner.FastTestRunner"
PAGE_DEFAULT_TEMPLATE = "support/base.html"
PAGE_LANGUAGES = (('en-us', 'US English'),)
STATIC_URL = '/static/'

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework.authentication.SessionAuthentication',
)

# Need to skip migrations for now as migrations created with python2 break with python3
# See https://code.djangoproject.com/ticket/23455
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()

USE_TZ = True

# Mailgun Email settings if MAILGUN_API_KEY is in environ
if os.environ.get('MAILGUN_API_KEY'):
    EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"
