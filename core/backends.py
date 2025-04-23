from __future__ import annotations
from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http.request import HttpRequest

from apps.user.models import User


class EmailOrUsernameModelBackend(ModelBackend):
    """Authentication backend that allows login with either
    username or email in a single query.
    """

    def authenticate(
        self,
        request: HttpRequest | None = None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> User | None:
        """Authenticate user with either username or email using a single query with Q objects.

        Args:
            request: The HTTP request
            username: The value entered in the username field (could be email or username)
            password: The password entered

        Returns:
            User object if authentication is successful, None otherwise
        """
        if username is None or password is None:
            return None

        # Use Q objects to check both username and email fields in a single query
        try:
            user = User.objects.get(Q(username=username) | Q(email=username), is_active=True)

            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher to mitigate TIMING ATTACKS
            # This simulates the same time it would take to check a valid user's password
            User().set_password(password)

        return None
