from __future__ import annotations

import pytest
from model_bakery import baker
from rest_framework.test import APIClient
import ulid

from apps.user.models import User
from core.fields import ULIDField


baker.generators.add(ULIDField, lambda: str(ulid.ULID()))  # type: ignore


@pytest.fixture
def api_client() -> APIClient:
    """Fixture to provide an API client for testing API views.

    Returns:
        APIClient: An instance of Django REST Framework's APIClient
    """
    return APIClient()


@pytest.fixture
def authenticated_client(user: User) -> APIClient:
    """Fixture to provide an authenticated API client for testing API views.

    Args:
        user: A user fixture to authenticate with

    Returns:
        APIClient: An instance of Django REST Framework's APIClient, authenticated
    """
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def authenticated_admin_client(admin_user: User) -> APIClient:
    """Fixture to provide an authenticated admin API client for testing API views.

    Args:
        admin_user: An admin user fixture to authenticate with

    Returns:
        APIClient: An instance of Django REST Framework's APIClient, authenticated as admin
    """
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# ----------------------------------------------------
# Fixtures for User Authentication and API Testing
# ----------------------------------------------------
@pytest.fixture
def user_credentials() -> dict:
    """Fixture to provide valid user credentials.

    Returns:
        dict: Username and password for authentication
    """
    return {
        "username": "user@example.com",
        "password": "Password123!",
    }


@pytest.fixture
def user(db) -> User:
    """Fixture to provide a regular user for testing.

    Returns:
        User: An instance of User model
    """
    user = baker.make(
        User,
        username="user@example.com",
        email="user@example.com",
        first_name="Regular",
        last_name="User",
    )
    user.set_password("Password123!")
    user.save()
    return user


@pytest.fixture
def user_factory(db):
    """Factory fixture to create multiple users with different attributes.

    Returns:
        function: A function that creates User instances
    """

    def _user_factory(**kwargs) -> User:
        """Creates a user with the given attributes.

        Args:
            **kwargs: Attributes to set on the created user

        Returns:
            User: A User instance with the given attributes
        """
        # Default values
        default_values = {
            "username": baker.random_gen.gen_string(10),
            "email": f"{baker.random_gen.gen_string(10)}@example.com",
            "first_name": baker.random_gen.gen_string(8),
            "last_name": baker.random_gen.gen_string(8),
            "is_active": True,
        }

        # Update with provided kwargs
        for key, value in kwargs.items():
            default_values[key] = value

        user = baker.make(User, **default_values)

        # Set password if provided, otherwise use a default
        password = kwargs.get("password", "Password123!")
        user.set_password(password)
        user.save()

        return user

    return _user_factory
