from __future__ import annotations

import pytest
from django.test import override_settings
from model_bakery import baker
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User


@pytest.fixture
def user_credentials() -> dict:
    """Fixture to provide valid user credentials.
    
    Returns:
        dict: Username and password for authentication
    """
    return {
        "username": "testuser",
        "password": "StrongP@ssw0rd",
    }


@pytest.fixture
def user_with_credentials(user_credentials: dict) -> User:
    """Fixture to provide a user with known credentials.
    
    Args:
        user_credentials: Dictionary containing username and password
        
    Returns:
        User: User with the provided credentials
    """
    user = baker.make(
        User,
        username=user_credentials["username"],
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )
    user.set_password(user_credentials["password"])
    user.save()
    return user


@pytest.fixture
def auth_tokens(user_with_credentials: User) -> dict:
    """Fixture to provide authentication tokens for a user.
    
    Args:
        user_with_credentials: User with known credentials
        
    Returns:
        dict: Access and refresh tokens
    """
    refresh = RefreshToken.for_user(user_with_credentials)
    return {
        "refresh_token": str(refresh),
        "access_token": str(refresh.access_token),
    }


@pytest.fixture
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def mailoutbox(settings):
    """Fixture to capture emails sent during tests.
    
    Returns:
        list: List of sent emails
    """
    from django.core import mail
    return mail.outbox


@pytest.fixture
def multiple_users(user_factory) -> list[User]:
    """Fixture to provide multiple users for testing list endpoints.
    
    Args:
        user_factory: Factory to create users
        
    Returns:
        list: List of User instances
    """
    users = [
        user_factory(
            username=f"testuser{i}",
            email=f"user{i}@example.com",
            first_name=f"First{i}",
            last_name=f"Last{i}",
        )
        for i in range(5)
    ]
    return users