from __future__ import annotations

import pytest

from apps.user.models import User
from apps.user.serializers import UserSerializer


@pytest.mark.integration
class TestUserServiceIntegration:
    """Integration tests for user-related services and components.
    Tests the interaction between serializers, models and the database.
    """

    def test_user_serializer_create(self, mock_user_data):
        """Test that the UserSerializer can create a user."""
        # Create a user through the serializer
        serializer = UserSerializer(data=mock_user_data)
        assert serializer.is_valid()
        user = serializer.save()

        # Verify the user was created correctly
        assert user.username == mock_user_data["username"]
        assert user.email == mock_user_data["email"]
        assert user.first_name == mock_user_data["first_name"]
        assert user.last_name == mock_user_data["last_name"]
        assert user.check_password(mock_user_data["password"]) is True

        # Verify it's in the database
        db_user = User.objects.get(username=mock_user_data["username"])
        assert db_user.id == user.id

    def test_user_serializer_validation(self):
        """Test that UserSerializer properly validates data."""
        # Test with invalid email
        invalid_data = {
            "username": "testuser",
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }
        serializer = UserSerializer(data=invalid_data)
        assert serializer.is_valid() is False
        assert "email" in serializer.errors

        # Test with weak password
        weak_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password",  # Too simple
        }
        serializer = UserSerializer(data=weak_password_data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors

    def test_user_uniqueness_constraints(self, user):
        """Test that the database enforces uniqueness constraints."""
        # Try to create a user with the same username
        duplicate_username_data = {
            "username": user.username,  # Duplicate
            "email": "different@example.com",
            "first_name": "Another",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }

        serializer = UserSerializer(data=duplicate_username_data)
        assert serializer.is_valid() is False
        assert "username" in serializer.errors

        # Try to create a user with the same email
        duplicate_email_data = {
            "username": "differentuser",
            "email": user.email,  # Duplicate
            "first_name": "Different",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }

        serializer = UserSerializer(data=duplicate_email_data)
        assert serializer.is_valid() is False
        assert "email" in serializer.errors

    def test_authentication_backend(self, user_with_credentials, user_credentials):
        """Test that the custom authentication backend works correctly."""
        # Authenticate with username
        user_by_username = User.objects.get(username=user_credentials["username"])
        assert user_by_username is not None
        assert user_by_username.id == user_with_credentials.id

        # Authenticate with email (using EmailOrUsernameModelBackend)
        from django.contrib.auth import authenticate

        # Should work with username
        user_auth = authenticate(
            username=user_credentials["username"], password=user_credentials["password"]
        )
        assert user_auth is not None
        assert user_auth.id == user_with_credentials.id

        # Should also work with email
        email_auth = authenticate(
            username=user_with_credentials.email,  # Use email instead of username
            password=user_credentials["password"],
        )
        assert email_auth is not None
        assert email_auth.id == user_with_credentials.id

        # Should fail with wrong password
        wrong_auth = authenticate(
            username=user_credentials["username"], password="WrongPassword"
        )
        assert wrong_auth is None

    def test_user_token_integration(self, user):
        """Test the integration between User model and JWT tokens."""
        # Get tokens from the model method
        tokens = user.token()

        # Verify we can use them with the JWT system
        from rest_framework_simplejwt.tokens import AccessToken

        # Parse the access token to get the user ID
        access_token = tokens["access_token"]
        token_data = AccessToken(access_token)

        # Verify the token contains the correct user ID
        assert str(user.id) == token_data["user_id"]
