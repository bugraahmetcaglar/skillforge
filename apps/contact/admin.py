from django import forms
from django.contrib import admin

from apps.contact.models import Contact, ContactBackup


class ContactAdminForm(forms.ModelForm):
    """Custom form for Contact admin."""

    class Meta:
        model = Contact
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    form = ContactAdminForm

    list_display = ["display_name", "email", "mobile_phone", "created_at"]
    list_filter = ["import_source", "is_active", "created_at", "organization"]
    search_fields = ["first_name", "last_name", "email", "mobile_phone", "organization"]
    readonly_fields = ["external_id", "imported_at", "created_at", "last_updated"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("first_name", "middle_name", "last_name", "full_name", "nickname", "email")},
        ),
        ("Phone Numbers", {"fields": ("mobile_phone", "home_phone", "work_phone", "second_phone", "third_phone")}),
        ("Organization", {"fields": ("organization", "job_title", "department"), "classes": ("collapse",)}),
        ("Personal", {"fields": ("birthday", "anniversary", "notes"), "classes": ("collapse",)}),
        ("Import Info", {"fields": ("import_source", "external_id", "imported_at"), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("created_at", "last_updated", "is_active"), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        """Auto-set owner to current user if not set"""
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        """Add custom analytics URL"""
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path("analytics/", self.analytics_view, name="contact_analytics"),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        """Contact analytics view"""
        from django.db import models
        from django.shortcuts import render

        stats = Contact.objects.filter(is_active=True).aggregate(
            total_contacts=models.Count("id"),
            total_with_email=models.Count("id", filter=models.Q(email__isnull=False) & ~models.Q(email="")),
            total_with_phone=models.Count(
                "id", filter=models.Q(mobile_phone__isnull=False) & ~models.Q(mobile_phone="")
            ),
            total_with_work_phone=models.Count(
                "id", filter=models.Q(work_phone__isnull=False) & ~models.Q(work_phone="")
            ),
        )

        # Separate query for import source stats
        source_stats = (
            Contact.objects.filter(is_active=True)
            .values("import_source")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )

        # Separate query for organization stats
        org_stats = (
            Contact.objects.filter(is_active=True, organization__isnull=False)
            .exclude(organization="")
            .values("organization")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )

        context = {
            "title": "Contact Analytics",
            "duplicate_count": Contact.objects.duplicate_numbers(request.user).count(),
            "source_stats": source_stats,
            "org_stats": org_stats,
            "total_contacts": stats["total_contacts"],
            "total_with_email": stats["total_with_email"],
            "total_with_phone": stats["total_with_phone"],
            "total_with_work_phone": stats["total_with_work_phone"],
        }

        return render(request, "admin/contact/analytics.html", context)


@admin.register(ContactBackup)
class ContactBackupAdmin(admin.ModelAdmin):
    list_display = ["contact_info", "owner", "created_at", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["owner__username", "owner__email"]
    readonly_fields = ["contact", "contact_data", "created_at", "last_updated"]

    def contact_info(self, obj):
        """Show contact info from backup data"""
        if obj.contact_data:
            first_name = obj.contact_data.get("first_name", "")
            middle_name = obj.contact_data.get("middle_name", "")
            last_name = obj.contact_data.get("last_name", "")
            return f"{first_name} {middle_name} {last_name}".strip() or "Unknown Contact"
        return "No data"

    contact_info.short_description = "Contact"

    def has_add_permission(self, request):
        """Disable adding new backups via admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable changing existing backups via admin"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting backups via admin"""
        return False
