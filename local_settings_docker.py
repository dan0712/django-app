import os

environment = os.environ["ENVIRONMENT"]

if environment == "prod":
    DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql_psycopg2',
             'NAME': "betasmartz_prod",
             'USER': "postgres",
             'PASSWORD': os.environ["DB_PASSWORD"],
             'HOST': os.environ["DB_HOST"],
             'PORT': 5432,
         }
    }
    SITE_URL = "app.betasmartz.com"
    DEBUG = False
    # ALLOWED_HOSTS = ["app.betasmartz.com"]

elif environment == "dev":
    DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql_psycopg2',
             'NAME': "betasmartz_dev",
             'USER': "postgres",
             'PASSWORD': os.environ["DB_PASSWORD"],
             'HOST': os.environ["DB_HOST"],
             'PORT': 5432,
         }
    }
    SITE_URL = "demo.betasmartz.com"
    DEBUG = True
    
    
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.zoho.com")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "press@gendabot.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "C^7d#G8hy&3z88Dz@df8U5U4!MpmRXf%Y!sj")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "press@gendabot.com")
STATIC_ROOT = "/collected_static"