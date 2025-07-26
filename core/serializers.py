from rest_framework import serializers


class NullableCharSerializer(serializers.CharField):
    """CharField that allows None/null values like NullableCharField"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('allow_null', True)
        kwargs.setdefault('allow_blank', True)
        kwargs.setdefault('required', False)
        kwargs.setdefault('default', None)
        super().__init__(**kwargs)
