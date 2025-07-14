from __future__ import annotations

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User


@pytest.mark.unit
@pytest.mark.model
class TestUserModel:
    """Test cases for the User model."""

    def test_token(self, user):
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
