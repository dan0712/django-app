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

'''
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': "betasmartz_{}".format(environment),
         'USER': 'postgres',
         'PASSWORD': os.environ["DB_PASSWORD"],
         'HOST': os.environ["DB_PORT_5432_TCP_ADDR"],
         'PORT': os.environ["DB_PORT_5432_TCP_PORT"],
     }
}
'''

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.zoho.com")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "press@gendabot.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "C^7d#G8hy&3z88Dz@df8U5U4!MpmRXf%Y!sj")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "press@gendabot.com")
STATIC_ROOT = "/collected_static"
