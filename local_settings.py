__author__ = 'cristian'

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'john',
         'USER': 'cristian',
         'PASSWORD': 'romeoy2k',
         'HOST': 'localhost',
         'PORT': '',
     }
}

SITE_URL = "http://127.0.0.1:8000"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'press@gendabot.com'
EMAIL_HOST_PASSWORD = 'C^7d#G8hy&3z88Dz@df8U5U4!MpmRXf%Y!sj'
DEFAULT_FROM_EMAIL = 'press@gendabot.com'