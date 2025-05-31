from __future__ import annotations

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, QuerySet
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.urls import reverse_lazy

from apps.user.models import User
from apps.admin.forms.user import AdminUserForm, AdminUserCreateForm


@method_decorator([login_required, staff_member_required], name="dispatch")
class AdminUserListView(ListView):
    """List view for managing users in admin panel."""

    model = User
    template_name = "admin/user/list.html"
    context_object_name = "users"
    paginate_by = 25

    def get_queryset(self) -> QuerySet[User]:
        """Filter and search users based on query parameters."""
        queryset = User.objects.annotate(contact_count=Count("contacts", filter=Q(contacts__is_active=True)))

        # Search functionality
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        # Status filter
        status = self.request.GET.get("status", "")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        elif status == "staff":
            queryset = queryset.filter(is_staff=True)
        elif status == "superuser":
            queryset = queryset.filter(is_superuser=True)

        # Ordering
        ordering = self.request.GET.get("ordering", "-date_joined")
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, **kwargs) -> dict:
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "User Management",
                "current_section": "users",
                "search_query": self.request.GET.get("search", ""),
                "current_status": self.request.GET.get("status", ""),
                "current_ordering": self.request.GET.get("ordering", "-date_joined"),
                "total_users": self.get_queryset().count(),
            }
        )
        return context


@method_decorator([login_required, staff_member_required], name="dispatch")
class AdminUserDetailView(DetailView):
    """Detail view for individual user in admin panel."""

    model = User
    template_name = "admin/user/detail.html"
    context_object_name = "user_obj"  # Avoid conflict with request.user

    def get_object(self) -> User | Http404:
        """Get user object with related data."""
        return get_object_or_404(User.objects.select_related().prefetch_related("contacts"), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        """Add user statistics and related data."""
        context = super().get_context_data(**kwargs)
        user_obj = self.object

        # User statistics
        total_contacts = user_obj.contacts.count()
        active_contacts = user_obj.contacts.filter(is_active=True).count()

        # Recent contacts
        recent_contacts = user_obj.contacts.filter(is_active=True).order_by("-created_at")[:5]

        # Contact import sources
        import_sources = user_obj.contacts.values("import_source").annotate(count=Count("id")).order_by("-count")

        context.update(
            {
                "page_title": f"User: {user_obj.username}",
                "current_section": "users",
                "total_contacts": total_contacts,
                "active_contacts": active_contacts,
                "inactive_contacts": total_contacts - active_contacts,
                "recent_contacts": recent_contacts,
                "import_sources": import_sources,
            }
        )
        return context


@method_decorator([login_required, staff_member_required], name="dispatch")
class AdminUserUpdateView(UpdateView):
    """Update view for editing users in admin panel."""

    model = User
    form_class = AdminUserForm
    template_name = "admin/user/form.html"

    def get_success_url(self):
        """Redirect to user detail after successful update."""
        return reverse_lazy("admin:user:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(self.request, f"User {self.object.username} updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add context for the template."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": f"Edit User: {self.object.username}",
                "current_section": "users",
                "form_action": "Update",
            }
        )
        return context


@method_decorator([login_required, staff_member_required], name="dispatch")
class AdminUserCreateView(CreateView):
    """Create view for adding new users in admin panel."""

    model = User
    form_class = AdminUserCreateForm
    template_name = "admin/user/form.html"
    success_url = reverse_lazy("admin:user:list")

    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(self.request, f"User {form.cleaned_data['username']} created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add context for the template."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Create New User",
                "current_section": "users",
                "form_action": "Create",
            }
        )
        return context


@login_required
@staff_member_required
def admin_user_toggle_status(request, pk: str):
    """Toggle user active status (AJAX endpoint)."""
    if request.method != "POST":
        return redirect("admin:user:list")

    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} {status} successfully.")

    # Return JSON response for AJAX or redirect for regular request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse

        return JsonResponse({"success": True, "is_active": user.is_active, "message": f"User {status} successfully."})

    return redirect("admin:user:detail", pk=pk)


@login_required
@staff_member_required
def admin_user_bulk_action(request):
    """Handle bulk actions on users."""
    if request.method != "POST":
        return redirect("admin:user:list")

    action = request.POST.get("action")
    user_ids = request.POST.getlist("user_ids")

    if not user_ids:
        messages.error(request, "No users selected.")
        return redirect("admin:user:list")

    users = User.objects.filter(id__in=user_ids)

    if action == "activate":
        users.update(is_active=True)
        messages.success(request, f"{users.count()} users activated.")
    elif action == "deactivate":
        users.update(is_active=False)
        messages.success(request, f"{users.count()} users deactivated.")
    else:
        messages.error(request, "Invalid action.")

    return redirect("admin:user:list")
