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

    list_display = ["display_name", "email", "mobile_phone", "organization", "import_source", "created_at"]
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
