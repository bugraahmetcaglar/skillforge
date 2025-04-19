from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User Model"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    pass


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
