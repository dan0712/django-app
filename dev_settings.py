import os

environment = os.environ["ENVIRONMENT"]

# This is my local debug settings, so always have debug on
SITE_URL = "http://{}.betasmartz.com".format(environment)
ALLOWED_HOSTS = ["*"]
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev_database.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

STATIC_ROOT = "/collected_static"
