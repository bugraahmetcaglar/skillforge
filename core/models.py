from __future__ import annotations

from typing import Dict, Any
from django.db import models
from django.conf import settings
from django.utils import timezone
from mongoengine import Document, DateTimeField

import logging
import ulid

logger = logging.getLogger(__name__)


class MongoBaseModel(Document):
    """Base model for all MongoDB documents"""

    created_at = DateTimeField(default=timezone.now, db_index=True)
    updated_at = DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    meta = {"abstract": True, "ordering": ["-created_at"]}

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        if not self.id:
            self.id = str(ulid.ULID())
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return self.to_mongo().to_dict()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"


class SkillForgeBaseQuerySet(models.QuerySet):
    def update(self, *args, **kwargs):
        if "last_updated" not in kwargs:
            kwargs["last_updated"] = timezone.now()
        return super().update(**kwargs)


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
