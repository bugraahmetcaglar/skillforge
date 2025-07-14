"""
Test settings for the SkillForge project.
"""

import os
from skillforge.settings.base import *  # noqa

# Override SECRET_KEY for tests
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-test-key-for-testing-only")

DEBUG = False

# Use PostgreSQL in CI, SQLite locally
if os.environ.get("CI"):
    # GitHub Actions environment
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "test_skillforge"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    # Local development - use SQLite for speed
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

# Remove django-q from installed apps for tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django_q"]

# Disable Q_CLUSTER for tests
Q_CLUSTER = {}

# Speed up password hashing in tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Use in-memory cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# Use console email backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Turn off non-essential middleware
MIDDLEWARE = [m for m in MIDDLEWARE if "debug" not in m.lower()]

# Disable logging during tests to reduce noise
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["null"],
            "propagate": False,
        },
    },
}
