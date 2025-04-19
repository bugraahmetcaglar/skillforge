from django.urls import path

from .views import (
    UserRegisterAPIView,
    UserListAPIView,
    UserDetailAPIView,
)

app_name = "user"

urlpatterns = [
    # User operations
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("list/", UserListAPIView.as_view(), name="list"),
    path("<uuid:pk>/", UserDetailAPIView.as_view(), name="detail"),
]
