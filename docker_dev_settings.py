# This is an example local_settings.py file for using the dev_database.sqlite3
# with the docker-compose deployment
import os
environment = os.environ.get('ENVIRONMENT', 'dev')

# This is my local debug settings, so always have debug on
SITE_URL = "http://{}.betasmartz.com".format(environment)
ALLOWED_HOSTS = ["*"]
DEBUG = True
TEMPLATE_DEBUG = True

if os.environ.get('USE_SQLITE', 'True') != 'False':
    # use sqlite3 outside of docker deployment
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'dev_database.sqlite3',
            'TEST': {'NAME': 'test_database.sqlite3'}
        }
    }
else:
    # docker deployment uses postgres
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': "betasmartz_{}".format(environment),
            'USER': 'betasmartz_{}'.format(environment),
            'PASSWORD': os.environ["DB_PASSWORD"],
            'HOST': os.environ.get('DB_HOST', 'postgres'),
            'PORT': os.environ.get('DB_PORT', 5432)
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

