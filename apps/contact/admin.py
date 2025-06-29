from __future__ import annotations

import datetime
import logging

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.forms import model_to_dict
from django.shortcuts import render

from apps.contact.models import Contact, ContactBackup

logger = logging.getLogger(__name__)


class ContactAdminForm(forms.ModelForm):
    """Custom form for Contact admin."""

    class Meta:
        model = Contact
        exclude = ("owner", "external_id", "imported_at", "created_at", "last_updated")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    form = ContactAdminForm
    actions = ["create_backup_action"]

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

    def create_backup_action(self, request, queryset):
        backup_count = 0
        for contact in queryset:
            ContactBackup.objects.create(
                contact=contact,
                owner=contact.owner,
                contact_data=model_to_dict(contact),
            )
            backup_count += 1
        self.message_user(request, f"Created {backup_count} backup(s) for selected contacts.", messages.SUCCESS)

    def get_urls(self):
        """Add custom analytics URL"""
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path("analytics", self.analytics_view, name="contact_contact_analytics"),
            path("bulk_backup", self.bulk_backup_view, name="contact_contact_bulk_backup"),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        """Contact analytics view"""
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

    def bulk_backup_view(self, request):
        """Custom admin action to create backups for selected contacts"""
        if request.method == "POST":
            contacts = Contact.objects.filter(is_active=True, owner=request.user).select_related("owner").order_by("id")
            success_ids, fail_ids = [], []

            for contact in contacts:
                try:
                    dict_contact = model_to_dict(contact)
                    contact_id = dict_contact.pop("id")
                    owner_id = dict_contact.pop("owner")

                    for key, value in dict_contact.items():
                        if isinstance(value, (datetime.datetime, datetime.date)):
                            dict_contact[key] = value.isoformat()

                    ContactBackup.objects.create(contact=contact, owner_id=owner_id, contact_data=dict_contact)
                    success_ids.append(contact_id)
                except Exception as err:
                    logger.exception(f"Error creating backups: {err}, Contact ID: {getattr(contact, "id", "Unknown")} data: {contact}")
                    fail_ids.append(getattr(contact, "id", "Unknown"))
                    continue

            if success_ids:
                messages.success(request, f"Successfully created backup for Contact IDs: {success_ids}")
            if fail_ids:
                messages.error(request, f"Failed to create backups, Contact IDs: {fail_ids}")

            return render(request, "admin/contact/bulk_backup_success.html", {"backup_count": len(success_ids)})

        # Show confirmation page
        total_contacts = Contact.objects.filter(is_active=True).count()
        return render(
            request,
            "admin/contact/bulk_backup_confirm.html",
            {"title": "Bulk Backup Contacts", "total_contacts": total_contacts},
        )


@admin.register(ContactBackup)
class ContactBackupAdmin(admin.ModelAdmin):
    list_display = ["owner", "created_at", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["owner__username", "owner__email"]
    readonly_fields = ["contact", "contact_data", "created_at", "last_updated"]

    def has_add_permission(self, request):
        """Disable adding new backups via admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable changing existing backups via admin"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting backups via admin"""
        return False
