from apps.finance.models import UserSubscription
from apps.finance.serializers import UserSubscriptionSerializer
from core.permissions import IsOwner
from core.views import BaseCreateAPIView, BaseListAPIView


class UserSubscriptionCreateAPIView(BaseCreateAPIView):
    permission_classes = [IsOwner]
    serializer_class = UserSubscriptionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success_response(
            status_code=201,
            message="User subscription created successfully",
        )


class ActiveSubscriptionListAPIView(BaseListAPIView):
    permission_classes = [IsOwner]
    serializer_class = UserSubscriptionSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            return self.error_response(
                status_code=403,
                error_message="You must be logged in to view your subscriptions.",
            )

        return self.success_response(
            data=self.get_serializer(
                UserSubscription.objects.filter(user=user, status="active"), many=True
            ).data
        )
