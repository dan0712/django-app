# This is an example local_settings.py file for using the dev_database.sqlite3
# with the docker-compose deployment
environment = 'dev'

# This is my local debug settings, so always have debug on
SITE_URL = "http://{}.betasmartz.com".format(environment)
ALLOWED_HOSTS = ["*"]
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'betasmartz/dev_database.sqlite3',
        'TEST': {'NAME': 'test_database.sqlite3'}
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

STATIC_ROOT = "/collected_static"

# Just email to console for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

