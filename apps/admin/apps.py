from __future__ import annotations

from django.apps import AppConfig


class AdminConfig(AppConfig):
    """Configuration for the admin application.
    
    This app handles custom admin interface functionality,
    organized by different modules (user, contact, etc.)
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admin"
    verbose_name = "SkillForge Admin"

    def ready(self) -> None:
        """Import admin modules when app is ready."""
        # Import all admin modules to register them
        from apps import admin