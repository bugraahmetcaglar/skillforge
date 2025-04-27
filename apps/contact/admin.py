from django.contrib import admin
from apps.contact.models import Contact, ContactBackup


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "middle_name", "last_name", "email", "owner", "is_active")
    list_filter = ("is_active",)
    search_fields = ("first_name", "middle_name", "last_name", "email")
    readonly_fields = ("id", "created_at", "last_updated")
    fieldsets = (
        (None, {"fields": ("id", "owner", "is_active")}),
        (
            "Contact Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                    "phone",
                    "address",
                    "notes",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "last_updated")}),
    )


@admin.register(ContactBackup)
class ContactBackupAdmin(admin.ModelAdmin):
    list_display = ("first_name", "middle_name", "last_name", "email", "owner", "deactivated_at")
    list_filter = ("deactivated_at",)
    search_fields = ("first_name", "middle_name", "last_name", "email")
    readonly_fields = (
        "id",
        "created_at",
        "last_updated",
        "deactivated_at",
    )
    fieldsets = (
        (None, {"fields": ("id", "owner", "deactivated_at")}),
        (
            "Contact Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                    "phone",
                    "address",
                    "notes",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "last_updated")}),
    )
