from rest_framework import serializers

from apps.finance.models import UserSubscription


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = (
            "service",
            "description",
            "plan_name",
            "amount",
            "currency",
            "billing_cycle",
            "started_at",
            "next_billing_date",
            "trial_end_date",
            "cancelled_at",
            "status",
            "auto_renewal",
            "payment_method",
            "payment_account",
            "notes",
        )
    
    def create(self, validated_data):
        # Automatically set the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Create the UserSubscription instance
        return super().create(validated_data)
