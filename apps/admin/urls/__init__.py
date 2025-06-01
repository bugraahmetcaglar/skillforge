from django.urls import include, path

app_name = "admin"

urlpatterns = [
    # Include user URLs
    path("user/", include("apps.admin.urls.user", namespace="user")),
    # Include contact URLs
    path("contact/", include("apps.admin.urls.contact", namespace="contact")),
    # Include dashboard URLs
    path("dashboard/", include("apps.admin.urls.dashboard", namespace="dashboard")),
    # Include authentication URLs
    path("auth/", include("apps.admin.urls.auth", namespace="auth")),
]
