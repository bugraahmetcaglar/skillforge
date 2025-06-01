from __future__ import annotations

from django.urls import path

from apps.admin.views.dashboard import AdminDashboardView, AdminStatsAPIView

app_name = "dashboard"

urlpatterns = [
    path("", AdminDashboardView.as_view(), name="index"),
    path("stats/", AdminStatsAPIView.as_view(), name="stats_api"),
]
