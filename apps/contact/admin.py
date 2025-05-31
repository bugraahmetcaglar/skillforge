from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.contact.models import Contact, ContactBackup


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Enhanced Contact admin with search, filtering, and modern interface
    """
    
    # List view configuration
    list_display = [
        "get_full_name", 
        "email", 
        "mobile_phone", 
        "organization", 
        "import_source",
        "owner",
        "is_active",
        "created_at"
    ]
    
    list_filter = [
        "is_active",
        "import_source", 
        "created_at",
        ("owner", admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        "first_name", 
        "last_name", 
        "full_name",
        "email", 
        "mobile_phone",
        "organization",
        "job_title"
    ]
    
    # Pagination
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ["first_name", "last_name"]
    
    # Readonly fields
    readonly_fields = [
        "id", 
        "created_at", 
        "last_updated", 
        "imported_at",
        "external_id",
        "deactivated_at"
    ]
    
    # Form layout
    fieldsets = (
        ("Contact Information", {
            "fields": (
                ("first_name", "middle_name", "last_name"),
                "full_name",
                "nickname",
                "email",
                ("mobile_phone", "home_phone", "work_phone"),
            )
        }),
        ("Organization", {
            "fields": (
                "organization",
                "job_title", 
                "department"
            ),
            "classes": ("collapse",)
        }),
        ("Personal Information", {
            "fields": (
                "birthday",
                "anniversary",
                "notes"
            ),
            "classes": ("collapse",)
        }),
        ("Import Information", {
            "fields": (
                "import_source",
                "external_id",
                "imported_at"
            ),
            "classes": ("collapse",)
        }),
        ("System Information", {
            "fields": (
                "id",
                "owner",
                "is_active",
                "created_at",
                "last_updated",
                "deactivated_at"
            ),
            "classes": ("collapse",)
        })
    )
    
    # Actions
    actions = ["deactivate_contacts", "export_as_csv"]
    
    def get_full_name(self, obj: Contact) -> str:
        """Display full name with fallback"""
        if obj.full_name:
            return obj.full_name
        elif obj.first_name or obj.last_name:
            return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        else:
            return obj.email or obj.mobile_phone or "Unnamed Contact"
    get_full_name.short_description = "Name"
    get_full_name.admin_order_field = "first_name"
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimize queryset and filter by user permissions"""
        qs = super().get_queryset(request)
        
        # Optimize with select_related
        qs = qs.select_related("owner")
        
        # Filter by user permissions
        if not request.user.is_superuser:
            qs = qs.filter(owner=request.user)
            
        return qs
    
    def has_change_permission(self, request: HttpRequest, obj: Contact | None = None) -> bool:
        """Check change permissions"""
        if not super().has_change_permission(request, obj):
            return False
            
        # Superusers can change everything
        if request.user.is_superuser:
            return True
            
        # Users can only change their own contacts
        if obj and obj.owner != request.user:
            return False
            
        return True
    
    def has_delete_permission(self, request: HttpRequest, obj: Contact | None = None) -> bool:
        """Disable delete - use deactivate instead"""
        return False
    
    def deactivate_contacts(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Deactivate selected contacts"""
        count = 0
        for contact in queryset:
            if contact.is_active:
                contact.deactivate()
                count += 1
        
        self.message_user(
            request,
            f"Successfully deactivated {count} contact(s)."
        )
    deactivate_contacts.short_description = "Deactivate selected contacts"
    
    def export_as_csv(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Export selected contacts as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'First Name', 'Last Name', 'Email', 'Mobile Phone', 
            'Organization', 'Job Title', 'Import Source', 'Created At'
        ])
        
        for contact in queryset:
            writer.writerow([
                contact.first_name or '',
                contact.last_name or '',
                contact.email or '',
                contact.mobile_phone or '',
                contact.organization or '',
                contact.job_title or '',
                contact.get_import_source_display(),
                contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_as_csv.short_description = "Export selected contacts as CSV"


@admin.register(ContactBackup)
class ContactBackupAdmin(admin.ModelAdmin):
    """
    Contact Backup admin interface
    """
    
    list_display = ["id", "owner", "created_at"]
    list_filter = ["created_at", ("owner", admin.RelatedOnlyFieldListFilter)]
    search_fields = ["owner__username", "owner__email"]
    readonly_fields = ["id", "owner", "contact_data", "created_at", "last_updated"]
    list_per_page = 25
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        """Disable manual creation of backups"""
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: ContactBackup | None = None) -> bool:
        """Disable editing of backups"""
        return False
    
    def has_delete_permission(self, request: HttpRequest, obj: ContactBackup | None = None) -> bool:
        """Only superusers can delete backups"""
        return request.user.is_superuser