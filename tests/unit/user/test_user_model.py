from __future__ import annotations

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User


@pytest.mark.unit
@pytest.mark.model
class TestUserModel:
    """Test cases for the User model."""

    def test_create_user(self, user_factory):
        """Test that a user can be created with valid data."""
        # Create a user with the factory
        user = user_factory()

        # Verify the user was created
        assert user.id is not None
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_custom_id_field(self, user):
        """Test that the custom ULID id field is being used."""
        # Verify the ID is a string and has the ULID format (26 characters)
        assert isinstance(user.id, str)
        assert len(user.id) == 26

    def test_email_must_be_unique(self, user, user_factory):
        """Test that users cannot be created with duplicate emails."""
        # Attempt to create another user with the same email
        with pytest.raises(Exception):  # Could be IntegrityError or ValidationError
            user_factory(email=user.email)

    def test_token_method(self, user):
        """Test that the token method returns valid JWT tokens."""
        # Get tokens from the model method
        tokens = user.token()

        # Verify the tokens exist
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        # Verify they're strings and not empty
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0

        # Verify the access token can be decoded and contains the user ID
        # This is just a simple validation that the token is related to our user
        refresh = RefreshToken(tokens["refresh_token"])
        user_id = refresh["user_id"]
        assert str(user.id) == user_id

    def test_create_superuser(self):
        """Test creating a superuser."""
        # Create a superuser
        superuser = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="StrongP@ssw0rd",
        )

        # Verify superuser flags
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    def test_username_and_email_are_required(self):
        """Test that username and email are required fields."""
        # Attempt to create a user without username
        with pytest.raises(ValueError):
            User.objects.create_user(
                username="",
                email="test@example.com",
                password="StrongP@ssw0rd",
            )

        # Attempt to create a user without email
        with pytest.raises(ValueError):
            User.objects.create_user(
                username="testuser",
                email="",
                password="StrongP@ssw0rd",
            )
