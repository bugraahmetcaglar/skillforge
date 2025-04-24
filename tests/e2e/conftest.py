from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.user.models import User


@pytest.fixture
def register_user_payload() -> dict:
    """
    Fixture to provide a valid registration payload.
    
    Returns:
        dict: Valid registration data
    """
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "StrongP@ssw0rd",
    }


@pytest.fixture
def register_user(api_client: APIClient, register_user_payload: dict) -> dict:
    """
    Fixture to register a user and return the response.
    
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
def login_user(api_client: APIClient, user_with_credentials, user_credentials) -> dict:
    """
    Fixture to login a user and return the auth tokens.
    
    Args:
        api_client: API client fixture
        user_with_credentials: User with known credentials
        user_credentials: Username and password
        
    Returns:
        dict: API response with auth tokens
    """
    url = reverse("token_obtain_pair")
    response = api_client.post(url, user_credentials, format="json")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


@pytest.fixture
def auth_client(api_client: APIClient, login_user: dict) -> APIClient:
    """
    Fixture to provide an authenticated client through the token flow.
    
    Args:
        api_client: API client fixture
        login_user: Response from login containing tokens
        
    Returns:
        APIClient: Authenticated API client using token
    """
    access_token = login_user.get("access_token", login_user.get("access"))
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


@pytest.fixture
def user_flow():
    """
    Fixture to provide a complete user flow helper: register, login, update, etc.
    
    Returns:
        dict: Dictionary of helper functions for user flow testing
    """
    def _register_and_login(client: APIClient, user_data: dict) -> tuple[dict, dict]:
        """
        Register a user and then login.
        
        Args:
            client: API client
            user_data: Registration data
            
        Returns:
            tuple: (Registration response, Login response)
        """
        register_url = reverse("v1_user_register")
        register_response = client.post(register_url, user_data, format="json")
        
        login_url = reverse("token_obtain_pair")
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        login_response = client.post(login_url, login_data, format="json")
        
        return register_response.json(), login_response.json()
    
    def _get_authenticated_client(client: APIClient, tokens: dict) -> APIClient:
        """
        Create an authenticated client from tokens.
        
        Args:
            client: API client
            tokens: Dict containing access_token
            
        Returns:
            APIClient: Authenticated client
        """
        access_token = tokens.get("access_token", tokens.get("access"))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        return client
    
    return {
        "register_and_login": _register_and_login,
        "get_authenticated_client": _get_authenticated_client,
    }