from archfinch.settings_local import *

import djcelery
djcelery.setup_loader()

ADMINS = (
    ('drx', 'luke@archfinch.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/django/archfinch/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

WEB_ROOT = '/var/www/archfinch/cache/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/adminmedia/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'archfinch.main.middleware.NofollowMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'archfinch.main.middleware.SearchEngineReferrerMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'archfinch.main.middleware.ShortenerMiddleware',
)

ROOT_URLCONF = 'archfinch.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/django/archfinch/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.markup',
    'archfinch.main',
    'archfinch.account',
    'archfinch.links',
    'archfinch.lists',
    'archfinch.wiki',
    'archfinch.users',
    'archfinch.search',
    'archfinch.comments',
    'archfinch.sync',
    'djcelery',
    'lazysignup',
    'reversetag',
    'django_js_utils',
)
if DEBUG:
    INSTALLED_APPS += (
        'devserver',
        'django_extensions',
    )
    DEVSERVER_MODULES = (
        'devserver.modules.sql.SQLRealTimeModule',
        'devserver.modules.sql.SQLSummaryModule',
        'devserver.modules.profile.ProfileSummaryModule',

        # Modules not enabled by default
        'devserver.modules.ajax.AjaxDumpModule',
        #'devserver.modules.profile.MemoryUseModule',
        'devserver.modules.cache.CacheSummaryModule',
    )
    DEVSERVER_TRUNCATE_SQL = False

    STATIC_URL = 'media'
else:
    INSTALLED_APPS += (
        'sentry',
        'sentry.client',
    )

AUTHENTICATION_BACKENDS = (
    'archfinch.users.auth_backends.ModelBackend',
    'lazysignup.backends.LazySignupBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login'

USER_MODEL = 'users.User'
LAZYSIGNUP_USER_MODEL = USER_MODEL

LAZYSIGNUP_USER_AGENT_BLACKLIST = (
    'slurp',
    'googlebot',
    'yandex',
    'msnbot',
    'baiduspider',
    'pingdom',
    'cloudkick',
    'facebook',
)

DOMAIN = 'archfinch.com'
SHORT_DOMAIN = 'arfn.ch'

