"""
Django settings for project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# Load DEBUG from environment variables, default to False if not set
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "food-donation-swe-dev.us-east-1.elasticbeanstalk.com",
    "food-donation-swe-prod.us-east-1.elasticbeanstalk.com",
    "food-donation-swe-test.eba-km8nsjsa.us-east-1.elasticbeanstalk.com",
    "fooddonation-dev.com",
    "fooddonation-prod.com",
    "172.31.30.180",  # PostGres
    "34.202.22.62",  # PostGres
    "127.0.0.1",
    "localhost",
]

# Application definition
load_dotenv()
SITE_ID = int(os.getenv("SITE_ID", "1"))

INSTALLED_APPS = [
    "daphne",
    "database",  # Custom app for database models
    "django.contrib.admin",  # Django's built-in admin interface app # pylint: disable=line-too-long
    "django.contrib.auth",  # Authentication system (handles user authentication and permissions) # pylint: disable=line-too-long
    "django.contrib.contenttypes",  # Content type framework (allows relations between models) # pylint: disable=line-too-long
    "django.contrib.sessions",  # Session framework (manages user sessions, typically cookies-based) # pylint: disable=line-too-long
    "django.contrib.messages",  # Messaging framework (enables message passing between views and templates) # pylint: disable=line-too-long
    "django.contrib.staticfiles",  # Manages static files (CSS, JavaScript, images, etc.)
    # Other apps (custom or third-party apps go here)
    "donor_dashboard",  # Custom app for Donor dashboard
    "recipient_dashboard",  # Custom app for recipient_dashboard
    "recipient_orders",  # View orders placed by a recipient
    "user_profile",  # View user profile
    "messaging",  # Custom app for Messaging functionality
    "accounts.apps.AccountsConfig",  # Custom app for user accounts
    "django.contrib.sites",  # Sites framework (enables associating data with different sites/domains) # noqa
    "compressor",  # Compresses linked and inline JavaScript or CSS into a single cached file # noqa
    "channels",  # A library that extends Django to handle WebSocket connections for real-time features like chat.
    # Allauth - Third-party library for authentication and social account management
    "allauth",  # Core of django-allauth package (handles signups, logins, etc.)
    "allauth.account",  # Allauth's account module (handles user accounts, registration, etc.) # noqa
    "allauth.socialaccount",  # Allauth's social account module (for managing social logins) # noqa
    "allauth.socialaccount.providers.google",  # Specific provider for Google login integration # noqa
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # Middleware provided by django-allauth to handle user accounts (e.g., login state, session) # noqa
]

ROOT_URLCONF = "django_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.user_organizations",  # Enables header to access a user's organizations to avoid querying the database on every page # noqa
            ],
        },
    },
]

WSGI_APPLICATION = "django_management.wsgi.application"
ASGI_APPLICATION = "django_management.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Get .env variables from Qahtan
if "RDS_DB_NAME" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("RDS_DB_NAME"),
            "USER": os.getenv("RDS_USERNAME"),
            "PASSWORD": os.getenv("RDS_PASSWORD"),
            "HOST": os.getenv("RDS_HOSTNAME"),
            "PORT": os.getenv("RDS_PORT"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

COMPRESS_ROOT = BASE_DIR / "static"
COMPRESS_ENABLED = True
STATICFILES_FINDERS = ("compressor.finders.CompressorFinder",)

# Static files (CSS, JavaScript, Images).
# This is where the browser will serve.
STATIC_URL = "/static/"

# Additional locations for static files in our repository
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "accounts.backends.EmailBackend",  # Add your custom email backend
]

SOCIALACCOUNT_ADAPTER = "accounts.adapters.CustomSocialAccountAdapter"

LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"

# ******** HTTPS Setups ********#
# Redirect HTTP to HTTPS
# To allow local development to not redirect to HTTPS. Default to HTTPS
SECURE_SSL_REDIRECT = os.getenv("SSL_REDIRECT", "True") == "True"
# Enforce HTTP Strict Transport Security (HSTS) for 1 year
SECURE_HSTS_SECONDS = 31536000
# Allow site to be included in browsers' HSTS preload lists
SECURE_HSTS_PRELOAD = True
# Apply HSTS to all subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
