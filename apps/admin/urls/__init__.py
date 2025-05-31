from __future__ import annotations

from django.urls import path, include

from apps.admin.urls.dashboard import urlpatterns as dashboard_urls


app_name = "admin"

urlpatterns = [
    # Main dashboard
    path("", include(dashboard_urls)),
    
    # User management
    path("users/", include("apps.admin.urls.user", namespace="user")),
    
    # Contact management
    path("contacts/", include("apps.admin.urls.contact", namespace="contact")),
]