from django.db import models


class NullableCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop("max_length", 254)
        default = kwargs.pop("default", None)
        super().__init__(max_length=max_length, default=default, null=True, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["null"]
        return name, path, args, kwargs