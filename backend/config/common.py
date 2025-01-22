"""
Django settings for server project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their config, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from typing import Tuple

from config.env import BASE_DIR
from config.env import env
from django.utils.translation import gettext_lazy as _

DEBUG = True
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = env("DJANGO_SECRET_KEY")

BASE_FILES_DIR = BASE_DIR / "storage"

STATIC_ROOT = BASE_DIR / "staticfiles"

# Application definition:
INSTALLED_APPS: Tuple[str, ...] = (
    # Default django apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # django-admin:
    "django.contrib.admin",
    "django.contrib.admindocs",
    # other apps: ...
    "apps.application",
)

MIDDLEWARE: Tuple[str, ...] = (
    # Django:
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # django-permissions-policy
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Django HTTP Referrer Policy:
)

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT", cast=int, default=5432),
        "CONN_MAX_AGE": env("CONN_MAX_AGE", cast=int, default=0),
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=15000ms",
        },
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'db_null',
#         'USER': env('POSTGRES_USER'),
#         'PASSWORD': env('POSTGRES_PASSWORD'),
#         'HOST': env('DJANGO_DATABASE_HOST'),
#         'PORT': env('DJANGO_DATABASE_PORT', cast=int),
#         'CONN_MAX_AGE': env('CONN_MAX_AGE', cast=int, default=0),
#         'OPTIONS': {
#             'connect_timeout': 10,
#             'options': '-c statement_timeout=15000ms',
#         },
#     },
# }

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

USE_I18N = True

LANGUAGES = (("en", _("English")),)

LOCALE_PATHS = ("locale/",)

USE_TZ = True
TIME_ZONE = "America/Los_Angeles"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
FILES_STORAGE = BASE_FILES_DIR

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Templates
# https://docs.djangoproject.com/en/4.2/ref/templates/api

TEMPLATES = [
    {
        "APP_DIRS": True,
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # Contains plain text templates, like `robots.txt`:
            BASE_DIR.joinpath("config", "templates"),
        ],
        "OPTIONS": {
            "context_processors": [
                # Default template context processors:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    }
]

# Media files
# Media root dir is commonly changed in production
# (see development.py and production.py).
# https://docs.djangoproject.com/en/4.2/topics/files/

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_FILES_DIR / "media"

# Django authentication system
# https://docs.djangoproject.com/en/4.2/topics/auth/

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

X_FRAME_OPTIONS = "DENY"
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Timeouts
# https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-EMAIL_TIMEOUT

EMAIL_TIMEOUT = 5

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USE_DEPRECATED_PYTZ = False

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000000

FIXTURES_PATH = BASE_DIR / "storage" / "fixtures"

FIXTURE_DIRS = [FIXTURES_PATH]

########### PROJECT VARIABLES ###########
