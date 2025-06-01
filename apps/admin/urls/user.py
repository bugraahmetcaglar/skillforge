from __future__ import annotations

from django.urls import path

from apps.admin.views.user import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserUpdateView,
    AdminUserCreateView,
    admin_user_toggle_status,
    admin_user_bulk_action,
)

app_name = "user"

urlpatterns = [
    # List and create
    path("user/list/", AdminUserListView.as_view(), name="list"),
    path("user/create/", AdminUserCreateView.as_view(), name="create"),
    # Individual user actions
    path("user/<str:pk>/", AdminUserDetailView.as_view(), name="detail"),
    path("user/<str:pk>/edit/", AdminUserUpdateView.as_view(), name="edit"),
    path("user/<str:pk>/toggle-status/", admin_user_toggle_status, name="toggle_status"),
]
