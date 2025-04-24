"""
Test settings for the SkillForge project.

This settings file is used when running tests. It extends the main settings
but overwrites database and other settings that should be different in test environment.
"""

from skillforge.settings.base import *  # noqa

# Set test database to in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

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

# Celery settings for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
