from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status

from apps.user.models import User

pytestmark = [pytest.mark.django_db, pytest.mark.e2e, pytest.mark.api]

REGISTER_URL = reverse("v1_user_register")
LOGIN_URL = reverse("v1_user_login")


class TestUserRegistrationAPI:
    def test_register(self, api_client, register_user_payload):
        """Test that a user can register with valid data."""
        response = api_client.post(path=REGISTER_URL, data=register_user_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        assert response.data["message"] == "User successfully registered"
        assert response.data["success"] is True
        assert "access_token" in response.data["data"]
        assert "refresh_token" in response.data["data"]

        # Verify the user was created in the database
        assert User.objects.filter(email=register_user_payload["email"]).exists()


class TestUserRegistrationBadScenarios:
    def test_register_with_invalid_data(self, api_client):
        """Test that registration fails with invalid data."""
        response = api_client.post(path=REGISTER_URL, data={"email": "incomplete"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with invalid email
        invalid_data = {
            "email": "not-an-email",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }
        response = api_client.post(path=REGISTER_URL, data=invalid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_with_weak_password(self, api_client):
        """Test that registration fails with a weak password."""
        weak_password_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password",  # Too simple
        }
        response = api_client.post(path=REGISTER_URL, data=weak_password_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_with_existing_email(self, api_client, user):
        """Test that registration fails with an existing email."""
        duplicate_data = {
            "email": user.email,
            "first_name": "Another",
            "last_name": "User",
            "password": "StrongP@ssw0rd",
        }
        response = api_client.post(path=REGISTER_URL, data=duplicate_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUserLoginAPI:
    def test_user_can_login(self, api_client, user, user_credentials):
        """Test that a user can login with valid credentials."""
        response = api_client.post(path=LOGIN_URL, data=user_credentials, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]


class TestUserAuthenticationBadScenarios:
    def test_login_with_invalid_credentials(self, api_client, user):
        """Test that login fails with invalid credentials."""
        invalid_credentials = {
            "email": user.email,
            "password": "WrongPassword",
        }
        response = api_client.post(path=LOGIN_URL, data=invalid_credentials, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials." in response.data["detail"]

    def test_login_with_missing_password(self, api_client):
        """Test that login fails with missing fields."""
        response = api_client.post(path=LOGIN_URL, data={"email": "missing-pw"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_empty_fields(self, api_client):
        """Test that login fails with empty fields."""
        response = api_client.post(path=LOGIN_URL, data={}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_invalid_email_format(self, api_client):
        """Test that login fails with an invalid email format."""
        invalid_email = {
            "email": "invalid-email-format",
            "password": "Password123!",
        }

        response = api_client.post(path=LOGIN_URL, data=invalid_email, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_blank_password(self, api_client, user):
        """Test that login fails with a blank password."""
        blank_password = {
            "email": user.email,
            "password": "",
        }

        response = api_client.post(path=LOGIN_URL, data=blank_password, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_blank_email(self, api_client):
        """Test that login fails with a blank email."""
        blank_email = {
            "email": "",
            "password": "Password123!",
        }

        response = api_client.post(path=LOGIN_URL, data=blank_email, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_non_existent_user(self, api_client):
        # Test with non-existent user
        non_existent = {
            "email": "nonexistentuser",
            "password": "Password123!",
        }
        response = api_client.post(path=LOGIN_URL, data=non_existent, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
