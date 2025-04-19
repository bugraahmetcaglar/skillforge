import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)

    def token(self) -> dict:
        refresh = RefreshToken.for_user(self)
        return {"refresh_token": f"{refresh}", "access_token": f"{refresh.access_token}"}
