from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenObtainPairView,
)

from apps.user.v1.views import (
    RegenerateTokenAPIView,
    UserRegisterAPIView,
    UserListAPIView,
    UserDetailAPIView,
)

urlpatterns = [
    # User operations
    path("register/", UserRegisterAPIView.as_view(), name="v1_user_register"),
    path("list/", UserListAPIView.as_view(), name="v1_user_list"),
    path("<uuid:pk>/", UserDetailAPIView.as_view(), name="v1_user_detail"),
    # Token operations
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "token/regenerate/", RegenerateTokenAPIView.as_view(), name="token_regenerate"
    ),
]
