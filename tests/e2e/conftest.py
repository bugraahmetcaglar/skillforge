from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db


@pytest.fixture
def register_user_payload() -> dict:
    """Fixture to provide a valid registration payload.

    Returns:
        dict: Valid registration data
    """
    return {
        "username": "newuser@example.com",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "StrongP@ssw0rd",
    }


@pytest.fixture
def register_user(api_client: APIClient, register_user_payload: dict) -> dict:
    """Fixture to register a user and return the response.

    Args:
        api_client: API client fixture
        register_user_payload: Registration data

    Returns:
        dict: API response data
    """
    url = reverse("v1_user_register")
    response = api_client.post(url, register_user_payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def login_user(api_client: APIClient, user, user_credentials) -> dict:
    """Fixture to login a user and return the auth tokens.

    Args:
        api_client: API client fixture
        user: User with known credentials
        user_credentials: Username and password

    Returns:
        dict: API response with auth tokens
    """
    url = reverse("v1_user_login")
    response = api_client.post(path=url, data=user_credentials, format="json")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


@pytest.fixture
def auth_client(api_client: APIClient, login_user: dict) -> APIClient:
    """Fixture to provide an authenticated client through the token flow.

    Args:
        api_client: API client fixture
        login_user: Response from login containing tokens

    Returns:
        APIClient: Authenticated API client using token
    """
    access_token = login_user.get("access_token", login_user.get("access"))
    client = api_client
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client
