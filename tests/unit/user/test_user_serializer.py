from __future__ import annotations

import pytest

from apps.user.serializers import UserSerializer, UserLoginSerializer, TokenSerializer


@pytest.fixture
def mock_user_data(user_credentials):
    """Fixture to provide mock user data for testing."""
    return {
        "username": user_credentials["username"],
        "email": user_credentials["username"],
        "password": user_credentials["password"],
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.mark.unit
@pytest.mark.serializer
class TestUserSerializer:
    """
    Unit tests for the UserSerializer.
    """

    def test_user_serializer_fields(self):
        """Test that UserSerializer has the expected fields."""
        serializer = UserSerializer()
        expected_fields = {"email", "first_name", "last_name", "password"}
        assert set(serializer.fields.keys()) == expected_fields

        # Check that password is write_only
        assert serializer.fields["password"].write_only is True


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
