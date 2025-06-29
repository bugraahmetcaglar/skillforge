from django.urls import path

from apps.finance.views import UserSubscriptionCreateAPIView, ActiveSubscriptionListAPIView


urlpatterns = [
    path("subscriptions/create", UserSubscriptionCreateAPIView.as_view(), name="user-subscription-create-api"),
    path("my/subscriptions", ActiveSubscriptionListAPIView.as_view(), name="active-subscriptions-list-api"),
]
