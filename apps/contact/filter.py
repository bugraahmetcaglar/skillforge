from __future__ import annotations

from django.db.models import Q
from django_filters import rest_framework as filters

from apps.contact.models import Contact
from core.enums import SourceTextChoices


class ContactFilter(filters.FilterSet):
    # Text search across multiple fields
    search = filters.CharFilter(method="filter_search", help_text="Search in name, email, phone, organization")

    # Name filters
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    full_name = filters.CharFilter(field_name="full_name", lookup_expr="icontains")

    # Contact info filters
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    phone = filters.CharFilter(method="filter_phone", help_text="Search in any phone field")

    # Organization filters
    organization = filters.CharFilter(field_name="organization", lookup_expr="icontains")
    job_title = filters.CharFilter(field_name="job_title", lookup_expr="icontains")
    department = filters.CharFilter(field_name="department", lookup_expr="icontains")

    # Import source filter
    import_source = filters.ChoiceFilter(choices=SourceTextChoices.choices)

    # Date filters
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    imported_after = filters.DateTimeFilter(field_name="imported_at", lookup_expr="gte")
    imported_before = filters.DateTimeFilter(field_name="imported_at", lookup_expr="lte")

    # Birthday filters
    has_birthday = filters.BooleanFilter(method="filter_has_birthday")
    birthday_month = filters.NumberFilter(field_name="birthday__month")
    birthday_day = filters.NumberFilter(field_name="birthday__day")

    # Tags filter (JSON field)
    tags = filters.CharFilter(method="filter_tags", help_text="Search by tag name")

    class Meta:
        model = Contact
        fields = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(full_name__icontains=value)
            | Q(nickname__icontains=value)
            | Q(email__icontains=value)
            | Q(mobile_phone__icontains=value)
            | Q(home_phone__icontains=value)
            | Q(work_phone__icontains=value)
            | Q(organization__icontains=value)
            | Q(job_title__icontains=value)
            | Q(department__icontains=value)
            | Q(notes__icontains=value)
        ).distinct()

    def filter_phone(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(mobile_phone__icontains=value)
            | Q(home_phone__icontains=value)
            | Q(work_phone__icontains=value)
            | Q(second_phone__icontains=value)
            | Q(third_phone__icontains=value)
        ).distinct()

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__icontains=value) if value else queryset
