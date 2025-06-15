from __future__ import annotations

from django.db import models
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


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
