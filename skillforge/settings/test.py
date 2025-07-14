# Test settings for the SkillForge project.
import os
from skillforge.settings.base import *  # noqa

# Override SECRET_KEY for tests if not provided
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-test-key-for-testing-only')

# Set test database to in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable Django-Q for tests to avoid Redis dependency
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_q']

# Remove Django-Q configuration
Q_CLUSTER = {}

# Rest of the existing test settings...