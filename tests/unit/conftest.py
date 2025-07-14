from __future__ import annotations

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.user.models import User


@pytest.fixture
def api_rf() -> APIRequestFactory:
    """Fixture to provide an API request factory for unit testing.

    Returns:
        APIRequestFactory: An instance of Django REST Framework's APIRequestFactory
    """
    return APIRequestFactory()


@pytest.fixture
def admin_request(api_rf, admin_user) -> Request:
    """Fixture to provide a request from an admin user.

    Args:
        api_rf: API request factory fixture
        admin_user: Admin user fixture

    Returns:
        Request: A request object with an admin user
    """
    request = api_rf.get("/")
    request.user = admin_user
    return request


@pytest.fixture
def mock_user_data() -> dict:
    """Fixture to provide mock user data for testing user creation.

    Returns:
        dict: A dictionary containing valid user data
    """
    return {
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "StrongP@ssw0rd",
    }
