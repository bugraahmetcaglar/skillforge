import uuid
import datetime

from django.db import models


class SkillForgeBaseQuerySet(models.QuerySet):
    def update(self, *args, **kwargs):
        if "last_updated" not in kwargs:
            kwargs["last_updated"] = datetime.datetime.now()
        return super().update(**kwargs)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(db_index=True, default=datetime.datetime.now())
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True