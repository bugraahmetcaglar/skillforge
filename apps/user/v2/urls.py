from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenVerifyView,
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.user.v2.views import UserViewSet


# Router definition for ViewSet approach
router = DefaultRouter()
router.register("user", UserViewSet, basename="user")


"""Note that URLs are automatically created as follows:
- /user/ -> list (GET) and create new user (POST)
- /user/{id}/ -> specific user detail (GET), update (PUT/PATCH), delete (DELETE)
- /user/register/ -> custom registration endpoint (POST)
- /user/regenerate_token/ -> endpoint to regenerate tokens (POST)
"""


urlpatterns = [
    # Automatically generated URLs for ViewSet
    path("", include(router.urls)),
    # Individual views for token operations (for more specialized behaviors)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
