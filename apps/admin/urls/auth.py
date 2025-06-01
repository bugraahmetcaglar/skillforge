from __future__ import annotations

from django.urls import path

from apps.admin.views.auth import AdminLoginView, admin_logout_view

app_name = "auth"

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="login"),
    path("logout/", admin_logout_view, name="logout"),
]
