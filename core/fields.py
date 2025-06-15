import ulid

from django.db import models


class NullableCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop("max_length", 254)
        default = kwargs.pop("default", None)
        super().__init__(max_length=max_length, default=default, null=True, blank=True, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["null"]
        del kwargs["blank"]
        return name, path, args, kwargs


class ULIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 26
        kwargs["unique"] = kwargs.get("unique", True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value is None or value == "":
            value = ulid.ULID()
            setattr(model_instance, self.attname, value)
        return value

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)
