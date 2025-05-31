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
    path("", AdminUserListView.as_view(), name="list"),
    path("create/", AdminUserCreateView.as_view(), name="create"),
    
    # Individual user actions
    path("<str:pk>/", AdminUserDetailView.as_view(), name="detail"),
    path("<str:pk>/edit/", AdminUserUpdateView.as_view(), name="edit"),
    path("<str:pk>/toggle-status/", admin_user_toggle_status, name="toggle_status"),
    
    # Bulk actions
    path("bulk-action/", admin_user_bulk_action, name="bulk_action"),
]