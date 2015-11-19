__author__ = 'cristian'
import os
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': os.environ["DB_NAME"],
         'USER': os.environ["DB_USER"],
         'PASSWORD': os.environ["DB_PASSWORD"],
         'HOST': os.environ["DB_HOST"],
         'PORT': os.environ.get("DB_PORT", ""),
     }
}

SITE_URL = os.environ["SITE_URL"]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]
