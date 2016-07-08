import os

environment = os.environ["ENVIRONMENT"]

if environment in ["prod", "demo", "dev"]:
    hn = 'app' if environment == 'prod' else environment
    ALLOWED_HOSTS = ["{}.betasmartz.com".format(hn)]
    SITE_URL = "http://{}.betasmartz.com".format(hn)
    DEBUG = False
else:
    SITE_URL = "http://{}.betasmartz.com".format(environment)
    DEBUG = True

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
