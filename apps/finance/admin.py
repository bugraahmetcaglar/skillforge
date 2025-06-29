from django.contrib import admin

from apps.finance.models import SubscriptionService, SubscriptionServiceCategory


@admin.register(SubscriptionService)
class SubscriptionServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "amount",
        "currency",
        "payment_method",
        "free_trial_available",
        "free_trial_days",
        "is_active",
    )
    search_fields = ("name", "description", "category__name")
    list_filter = ("category", "currency", "payment_method", "is_active")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_updated")


@admin.register(SubscriptionServiceCategory)
class SubscriptionServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active", "created_at", "last_updated")
    search_fields = ("name", "description")
    list_filter = ("is_active", "created_at", "last_updated")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_updated")
