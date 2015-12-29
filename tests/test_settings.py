SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "tests",
    'main',
    'portfolios',
    'django.contrib.contenttypes',
    'django.contrib.auth',
]
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