from django.contrib import admin
from apps.contact.models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "middle_name", "last_name", "email", "owner")
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
                    "mobile_phone",
                    "addresses",
                    "notes",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "last_updated")}),
    )
    
    def has_delete_permission(self, request, obj=None) -> bool:
        # return super().has_delete_permission(obj) and obj.is_active
        return False
