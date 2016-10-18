import os

environment = os.environ["ENVIRONMENT"]

if environment in ["production", "demo"]:
    hn = 'app' if environment == 'production' else environment
    ALLOWED_HOSTS = ["{}.betasmartz.com".format(hn)]
    SITE_URL = "https://{}.betasmartz.com".format(hn)
    DEBUG = False
else:
    SITE_URL = "https://{}.betasmartz.com".format(environment)
    DEBUG = True
    TEMPLATE_DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', "betasmartz_{}".format(environment)),
        'USER': os.environ.get('DB_USER', 'betasmartz_{}'.format(environment)),
        'PASSWORD': os.environ["DB_PASSWORD"],
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': os.environ.get('DB_PORT', 5432)
    }
}

# Docker redis target
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ['REDIS_URI'],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

STATIC_ROOT = "/collected_static"

# Mailgun on deployments
# Mailgun Email settings if MAILGUN_API_KEY is in environ
if os.environ.get('MAILGUN_API_KEY'):
    EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"


# Cloud Swift Storage Settings
SOFTLAYER_REGION = 'tor01'  # Toronto
PUBLIC_SOFTLAYER_URL = 'https://%s.objectstorage.softlayer.net/auth/v1.0/' % SOFTLAYER_REGION  # public
PRIVATE_SOFTLAYER_URL = 'https://%s.objectstorage.service.networklayer.com/auth/v1.0/' % SOFTLAYER_REGION  # only accessible from softlayer instances, use for production

# media
DEFAULT_FILE_STORAGE = 'swift.storage.SwiftStorage'
# static
STATICFILES_STORAGE = 'swift.storage.StaticSwiftStorage'

SWIFT_AUTH_URL = os.environ.get('ST_AUTH', PUBLIC_SOFTLAYER_URL)
SWIFT_USERNAME = os.environ.get('ST_USER', '')
SWIFT_KEY = os.environ.get('ST_KEY', '')
SWIFT_CONTAINER_NAME = os.environ.get('SWIFT_CONTAINER_NAME', 'betasmartz_%s' % environment)  # media container
SWIFT_STATIC_CONTAINER_NAME = SWIFT_CONTAINER_NAME + '_static'  # static container
SWIFT_AUTO_CREATE_CONTAINER = True
SWIFT_USE_TEMP_URLS = True
SWIFT_USE_TEMP_URLS_STATIC = False
SWIFT_TEMP_URL_KEY = os.environ.get('SWIFT_TEMP_URL_KEY', 'testing9990')
SWIFT_AUTO_CREATE_CONTAINER_ALLOW_ORIGIN = True
