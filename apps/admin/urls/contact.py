from __future__ import annotations

from django.urls import path

from apps.admin.views.contact import contact_create_placeholder, contact_detail_placeholder, contact_list_placeholder

app_name = "contact"

urlpatterns = [
    # Temporary placeholder URLs
    path("", contact_list_placeholder, name="list"),
    path("create/", contact_create_placeholder, name="create"),
    path("<int:pk>/", contact_detail_placeholder, name="detail"),
]
