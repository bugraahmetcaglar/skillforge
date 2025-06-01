from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from apps.user.models import User


@method_decorator([csrf_protect, never_cache], name="dispatch")
class AdminLoginView(TemplateView):
    """Simple template-based admin login view."""

    template_name = "admin/auth/login.html"

    def post(self, request, *args, **kwargs):
        """Handle login form submission."""
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not (username and password):
            messages.error(request, "Invalid request.")
            return self.get(request, *args, **kwargs)

        user = User.objects.filter(Q(Q(email=username) | Q(username=username)), is_superuser=True).first()
        if user is None or not getattr(user, "is_superuser", False):
            messages.error(request, "Invalid request.")
            return self.get(request, *args, **kwargs)

        user = authenticate(request, username=user.username, password=password)

        login(request, user)
        messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")

        # Redirect to next URL or dashboard
        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("admin:dashboard:index")

    def get_context_data(self, **kwargs):
        """Add context for login template."""
        context = super().get_context_data(**kwargs)
        context.update({"page_title": "Admin Login", "show_navbar": False})
        return context


@login_required
def admin_logout_view(request):
    """Custom admin logout view."""
    user_name = request.user.get_full_name() or request.user.email
    logout(request)

    messages.success(request, f"Goodbye {user_name}! You've been logged out successfully.")
    return redirect("admin_login")
