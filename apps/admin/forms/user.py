from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password

from apps.user.models import User


class AdminUserForm(forms.ModelForm):
    """Form for editing existing users in admin panel."""

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email address"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter first name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter last name"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "username": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
            "is_staff": "Designates whether the user can log into this admin site.",
            "is_superuser": "Designates that this user has all permissions without explicitly assigning them.",
        }

    def clean_email(self) -> str | None:
        """Validate email uniqueness."""
        email = self.cleaned_data.get("email")
        if email:
            # Check if email exists for other users
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError("A user with this email already exists.")
            return email

    def clean_username(self) -> str | None:
        """Validate username uniqueness."""
        username = self.cleaned_data.get("username")
        if username:
            # Check if username exists for other users
            existing_user = User.objects.filter(username=username).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError("A user with this username already exists.")
            return username


class AdminUserCreateForm(UserCreationForm):
    """Form for creating new users in admin panel."""

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}),
        help_text="Your password must contain at least 8 characters.",
    )

    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}),
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email address"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter first name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter last name"}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input", "checked": True}  # Default to active
            ),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with default values."""
        super().__init__(*args, **kwargs)

        # Set email as required
        self.fields["email"].required = True

        # Set default values
        if not self.data:
            self.fields["is_active"].initial = True

    def clean_email(self) -> str | None:
        """Validate email uniqueness and format."""
        email = self.cleaned_data.get("email")
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
            return email

    def clean_password1(self) -> str | None:
        """Validate password strength."""
        password1 = self.cleaned_data.get("password1")
        if password1:
            validate_password(password1)
        return password1

    def save(self, commit: bool = True) -> User:
        """Save user with properly hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class AdminUserSearchForm(forms.Form):
    """Form for searching and filtering users in admin panel."""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by username, email, or name...",
                "id": "search-input",
            }
        ),
    )

    status = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Users"),
            ("active", "Active Users"),
            ("inactive", "Inactive Users"),
            ("staff", "Staff Users"),
            ("superuser", "Superusers"),
        ],
        widget=forms.Select(attrs={"class": "form-select", "id": "status-filter"}),
    )

    ordering = forms.ChoiceField(
        required=False,
        choices=[
            ("-date_joined", "Newest First"),
            ("date_joined", "Oldest First"),
            ("username", "Username A-Z"),
            ("-username", "Username Z-A"),
            ("email", "Email A-Z"),
            ("-email", "Email Z-A"),
        ],
        widget=forms.Select(attrs={"class": "form-select", "id": "ordering-select"}),
    )
