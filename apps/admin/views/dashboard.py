from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from apps.contact.models import Contact
from apps.user.models import User


@method_decorator([login_required, staff_member_required], name="dispatch")
class AdminDashboardView(TemplateView):
    """Main admin dashboard with statistics and overview."""

    template_name = "admin/dashboard/index.html"

    def get_context_data(self, **kwargs) -> dict:
        """Get dashboard statistics and context data."""
        context = super().get_context_data(**kwargs)

        # Get current date for filtering
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
        new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()

        # Contact statistics
        total_contacts = Contact.objects.count()
        active_contacts = Contact.objects.filter(is_active=True).count()
        new_contacts_week = Contact.objects.filter(created_at__date__gte=week_ago).count()
        new_contacts_month = Contact.objects.filter(created_at__date__gte=month_ago).count()

        # Import source breakdown
        import_sources = Contact.objects.values("import_source").annotate(count=Count("id")).order_by("-count")

        # Recent users
        recent_users = User.objects.select_related().order_by("-date_joined")[:5]

        # Recent contacts
        recent_contacts = Contact.objects.select_related("owner").filter(is_active=True).order_by("-created_at")[:5]

        context.update(
            {
                # User stats
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "new_users_week": new_users_week,
                "new_users_month": new_users_month,
                # Contact stats
                "total_contacts": total_contacts,
                "active_contacts": active_contacts,
                "inactive_contacts": total_contacts - active_contacts,
                "new_contacts_week": new_contacts_week,
                "new_contacts_month": new_contacts_month,
                # Breakdown data
                "import_sources": import_sources,
                # Recent data
                "recent_users": recent_users,
                "recent_contacts": recent_contacts,
                # Page info
                "page_title": "Dashboard",
                "current_section": "dashboard",
            }
        )

        return context


@method_decorator([login_required, staff_member_required], name="dispatch")
class AdminStatsAPIView(TemplateView):
    """API endpoint for dashboard statistics (AJAX)."""

    def get(self, request, *args, **kwargs):
        """Return JSON stats for dashboard widgets."""
        from django.http import JsonResponse

        # This could be used for real-time dashboard updates
        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "total_contacts": Contact.objects.count(),
            "active_contacts": Contact.objects.filter(is_active=True).count(),
        }

        return JsonResponse(stats)
