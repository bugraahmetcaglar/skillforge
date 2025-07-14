from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status

from apps.user.models import User

pytestmark = pytest.mark.django_db


@pytest.mark.e2e
@pytest.mark.api
class TestUserRegistrationAPI:
    """E2E tests for the user registration API."""

    def test_user_can_register(self, api_client, register_user_payload):
        """Test that a user can register with valid data."""
        url = reverse("v1_user_register")
        response = api_client.post(url, register_user_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "success" in response.data
        assert response.data["success"] is True
        assert "data" in response.data
        assert "access_token" in response.data["data"]
        assert "refresh_token" in response.data["data"]

        # Verify the user was created in the database
        user_exists = User.objects.filter(username=register_user_payload["username"]).exists()
        assert user_exists is True

    def test_register_with_invalid_data(self, api_client):
        """Test that registration fails with invalid data."""
        url = reverse("v1_user_register")

        # Test with missing fields
        response = api_client.post(url, {"username": "incomplete"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with invalid email
        invalid_data = {
            "username": "newuser",
            "email": "not-an-email",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }
        response = api_client.post(url, invalid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with weak password
        weak_password_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password",  # Too simple
        }
        response = api_client.post(url, weak_password_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_with_existing_username(self, api_client, user):
        """Test that registration fails with an existing username."""
        url = reverse("v1_user_register")
        duplicate_data = {
            "username": user.username,  # Existing username
            "email": "another@example.com",
            "first_name": "Another",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }
        response = api_client.post(url, duplicate_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_with_existing_email(self, api_client, user):
        """Test that registration fails with an existing email."""
        url = reverse("v1_user_register")
        duplicate_data = {
            "username": "different_username",
            "email": user.email,  # Existing email
            "first_name": "Another",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }
        response = api_client.post(url, duplicate_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.e2e
@pytest.mark.api
class TestUserAuthenticationAPI:
    """E2E tests for the user authentication API."""

    def test_user_can_login(self, api_client, user_with_credentials, user_credentials):
        """Test that a user can login with valid credentials."""
        url = reverse("token_obtain_pair")
        response = api_client.post(url, user_credentials, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_with_invalid_credentials(self, api_client, user_with_credentials):
        """Test that login fails with invalid credentials."""
        url = reverse("token_obtain_pair")

        # Test with wrong password
        invalid_credentials = {
            "username": user_with_credentials.username,
            "password": "WrongPassword",
        }
        response = api_client.post(url, invalid_credentials, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test with non-existent user
        non_existent = {
            "username": "nonexistentuser",
            "password": "Password123!",
        }
        response = api_client.post(url, non_existent, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
