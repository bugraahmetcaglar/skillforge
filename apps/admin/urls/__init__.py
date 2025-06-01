from __future__ import annotations

from django.urls import path, include

app_name = "admin"

urlpatterns = [
    # Main dashboard
    path("", include("apps.admin.urls.dashboard", namespace="dashboard")),
    # Authentication
    path("auth/", include("apps.admin.urls.auth", namespace="auth")),
    # User management
    path("users/", include("apps.admin.urls.user", namespace="user")),
    # Contact management
    path("contacts/", include("apps.admin.urls.contact", namespace="contact")),
]
