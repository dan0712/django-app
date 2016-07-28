import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&nus@l_#u6@6+ezkldb)xwiiha++9z1omzhamfbd%89@+esi!l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['localhost']

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django_cron',
    'genericadmin',  # Allows nice selection of generic foreign keys in admin interface
    'nested_admin', # for nested inlines
    'django_extensions', # temp. to visualize models only
    'test_without_migrations',
    'tinymce_4',
    'import_export',
    'filebrowser',
    'suit',
    'compat',
    'pages',
    'recurrence',

    'notifications', # move to django-notifications-hq>=1.0 after fixing 
    'pinax.eventlog',  # For our activity tracking

    'rest_framework',
    'rest_framework_swagger',
    'bootstrap3',

    'main',
    'address',
    'user',
    'advisors',
    'portfolios',
)

TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'user.autologout.SessionExpireMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

REST_FRAMEWORK = {
    'PAGE_SIZE': 20,
    # JSON numbers don't suffer from precision loss, they are fixed point. Therefore we want to represent numeric data
    # as numeric data, not as string.
    'COERCE_DECIMAL_TO_STRING': False,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',  # allow client to override, using `?page_size=xxx`.
    'MAX_PAGE_SIZE': 1000,  # maximum limit allowed when using `?page_size=xxx`.
    'DEFAULT_PERMISSION_CLASSES': (
        # RESERVED # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'EXCEPTION_HANDLER': 'api.handlers.api_exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

ROOT_URLCONF = 'main.urls'

WSGI_APPLICATION = 'main.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    "pages.context_processors.media",
    'django.core.context_processors.request',
    'main.context_processors.site_contact'
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_LENGTH = 300

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

AUTH_USER_MODEL = 'main.User'
SHOW_HIJACKUSER_IN_ADMIN = False

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SUPPORT_EMAIL = "support@betasmartz.com"
SUPPORT_PHONE = "1888888888"
IS_DEMO = False
TIME_ZONE = "Australia/Sydney"
PAGE_DEFAULT_TEMPLATE = "support/base.html"
gettext_noop = lambda s: s
PAGE_LANGUAGES = (
    ('en-us', gettext_noop('US English')),
)

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

CMS_UNIHANDECODE_HOST = '/static/unihandecode/'
CMS_UNIHANDECODE_VERSION = '1.0.0'
CMS_UNIHANDECODE_DECODERS = ['ja', 'zh', 'vn', 'kr', 'diacritic']

# Django Suit configuration example
SUIT_CONFIG = {
    # header
    'ADMIN_NAME': 'Betasmartz Admin',
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # forms
    # 'SHOW_REQUIRED_ASTERISK': True,  # Default True
    # 'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    # 'MENU': (
    #     'sites',
    #     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
    #     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
    #     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    # ),

    # misc
    # 'LIST_PER_PAGE': 15
}

BLOOMBERG_HOSTNAME = 'dlsftp.bloomberg.com'
BLOOMBERG_USERNAME = 'dl788259'
BLOOMBERG_PASSWORD = '+gT[zfV9Bu]Ms.4'

CRON_CLASSES = [
    "portfolios.cron.CalculatePortfoliosCron",
    # ...
]

# DOCUMENTATION
SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '2.0',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        #'patch',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'resource_access_handler': None,
    #'base_path':'127.0.0.1:8000/docs/',
    'info': {
        #'contact': 'info@stratifi.com',
        'description': 'Reference',
        'title': 'BetaSmartz API',
    },
    'doc_expansion': 'list',
    #'resource_access_handler': 'api.views.resource_access_handler',
}

# The inflation rate
BETASMARTZ_CPI = 2

# From http://www.aihw.gov.au/deaths/life-expectancy/
MALE_LIFE_EXPECTANCY = 80
FEMALE_LIFE_EXPECTANCY = 84

# Do you want the security questions to be case sensitive?
#SECURITY_QUESTIONS_CASE_SENSITIVE = False

# What is the system currency?
SYSTEM_CURRENCY = 'AUD'

from local_settings import *
