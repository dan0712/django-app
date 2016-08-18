from main.settings import *

INSTALLED_APPS += ('django_jenkins', )

SECRET_KEY = 'fake-key'
TEST_RUNNER = "tests.fast_test_runner.FastTestRunner"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "betasmartz_dev"
    }
}
PAGE_DEFAULT_TEMPLATE = "support/base.html"
PAGE_LANGUAGES = (('en-us', 'US English'),)
STATIC_URL = '/static/'


# Need to skip migrations for now as migrations created with python2 break with python3
# See https://code.djangoproject.com/ticket/23455
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = DisableMigrations()
