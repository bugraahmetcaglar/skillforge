from __future__ import annotations

import pytest

from apps.user.serializers import UserSerializer, UserLoginSerializer, TokenSerializer


@pytest.mark.unit
@pytest.mark.serializer
class TestUserSerializer:
    """
    Unit tests for the UserSerializer.
    """

    def test_user_serializer_fields(self):
        """Test that UserSerializer has the expected fields."""
        serializer = UserSerializer()
        expected_fields = {"username", "email", "first_name", "last_name", "password"}
        assert set(serializer.fields.keys()) == expected_fields

        # Check that password is write_only
        assert serializer.fields["password"].write_only is True

    def test_password_validation(self, mock_user_data):
        """Test that password validation is working."""
        # Strong password should be valid
        serializer = UserSerializer(data=mock_user_data)
        assert serializer.is_valid() is True

        # Test with common password
        weak_data = mock_user_data.copy()
        weak_data["password"] = "password123"
        serializer = UserSerializer(data=weak_data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors

        # Test with short password
        weak_data["password"] = "short"
        serializer = UserSerializer(data=weak_data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors

    def test_create_method(self, mock_user_data):
        """Test that create method properly creates a user."""
        serializer = UserSerializer(data=mock_user_data)
        assert serializer.is_valid() is True

        user = serializer.save()

        # Verify user attributes
        assert user.username == mock_user_data["username"]
        assert user.email == mock_user_data["email"]
        assert user.first_name == mock_user_data["first_name"]
        assert user.last_name == mock_user_data["last_name"]

        # Verify password was hashed and not stored as plain text
        assert user.password != mock_user_data["password"]
        # Verify the hashed password works for authentication
        assert user.check_password(mock_user_data["password"]) is True


@pytest.mark.unit
@pytest.mark.serializer
class TestUserLoginSerializer:
    """Unit tests for the UserLoginSerializer."""

    def test_login_serializer_fields(self):
        """Test that UserLoginSerializer has the expected fields."""
        serializer = UserLoginSerializer()
        expected_fields = {"username", "password"}
        assert set(serializer.fields.keys()) == expected_fields

        # Check that password is write_only
        assert serializer.fields["password"].write_only is True

    def test_login_serializer_validation(self):
        """Test validation of login data."""
        # Valid data
        valid_data = {"username": "testuser", "password": "Password123!"}
        serializer = UserLoginSerializer(data=valid_data)
        assert serializer.is_valid() is True

        # Missing fields
        incomplete_data = {"username": "testuser"}
        serializer = UserLoginSerializer(data=incomplete_data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors


@pytest.mark.unit
@pytest.mark.serializer
class TestTokenSerializer:
    """Unit tests for the TokenSerializer."""

    def test_token_serializer_fields(self):
        """Test that TokenSerializer has the expected fields."""
        serializer = TokenSerializer()
        expected_fields = {"access_token", "refresh_token"}
        assert set(serializer.fields.keys()) == expected_fields

    def test_token_serialization(self):
        """Test that TokenSerializer properly serializes token data."""
        token_data = {
            "access_token": "sample.access.token",
            "refresh_token": "sample.refresh.token",
        }

        serializer = TokenSerializer(data=token_data)
        assert serializer.is_valid() is True
        assert serializer.data == token_data
