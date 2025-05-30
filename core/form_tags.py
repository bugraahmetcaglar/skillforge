from __future__ import annotations

from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_class: str) -> str:
    """Add CSS class to form field widget

    Usage: {{ form.field|add_class:"css-class-name" }}
    """
    if hasattr(field, "as_widget"):
        return field.as_widget(attrs={"class": css_class})
    return field


@register.filter(name="add_attrs")
def add_attrs(field, attrs: str) -> str:
    """Add multiple attributes to form field widget

    Usage: {{ form.field|add_attrs:"class:form-control,placeholder:Enter value" }}
    """
    if not hasattr(field, "as_widget"):
        return field

    attr_dict = {}
    for attr in attrs.split(","):
        if ":" in attr:
            key, value = attr.split(":", 1)
            attr_dict[key.strip()] = value.strip()

    return field.as_widget(attrs=attr_dict)


@register.filter(name="has_error")
def has_error(field) -> bool:
    """Check if form field has errors

    Usage: {% if form.field|has_error %}...{% endif %}
    """
    return bool(getattr(field, "errors", None))
