from __future__ import annotations

from typing import Any
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render
from django.urls import path

from apps.log.models import LogEntry
from core.utils import recursive_getattr


class LogAnalyticsAdmin(admin.ModelAdmin):
    """Dummy admin for creating menu item"""

    def has_module_permission(self, request):
        return recursive_getattr(request, "user.is_superuser", False)

    def has_view_permission(self, request, obj=None):
        return recursive_getattr(request, "user.is_superuser", False)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "level", "logger_name", "message_short", "user", "request_path"]
    list_filter = ["level", "timestamp", "logger_name"]
    search_fields = ["message", "logger_name", "request_path"]
    readonly_fields = ["timestamp", "level", "message", "logger_name", "user", "request_path", "status_code"]

    def message_short(self, obj):
        """Show first 50 characters of message"""
        return f"{obj.message[:50]}..."

    message_short.short_description = "Message"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False

    def get_urls(self):
        """Add custom analytics URL"""
        urls = super().get_urls()
        custom_urls = [
            path("analytics/", self.analytics_view, name="log_analytics"),
        ]
        return custom_urls + urls

    def analytics_view(self, request) -> HttpResponse:
        """Simple log analytics view"""
        # Count by level
        level_stats = LogEntry.objects.values("level").annotate(count=Count("id")).order_by("-count")

        # Count by logger
        logger_stats = LogEntry.objects.values("logger_name").annotate(count=Count("id")).order_by("-count")[:10]

        context = {
            "title": "Log Analytics",
            "level_stats": level_stats,
            "logger_stats": logger_stats,
        }

        return render(request, "admin/log/analytics.html", context)
