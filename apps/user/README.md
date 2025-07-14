# User App

Authentication and user management system with JWT tokens and role-based permissions.

## 🚀 Features

- **JWT Authentication**: Access and refresh token support
- **User Registration**: Email-based registration with validation
- **User Login**: Email/username authentication
- **Profile Management**: User CRUD operations
- **Permission System**: Role-based access control
- **Two API Approaches**: CBV and ViewSet implementations

## 🏗️ Architecture

### Models
- **User**: Extended AbstractUser with ULID primary key
- **Custom Fields**: Email as unique identifier
- **JWT Integration**: Built-in token generation

### API Versions
- **v1**: Class-based views (individual endpoints)
- **v2**: ViewSet approach (consolidated CRUD)

## 📋 API Endpoints

### v1 Endpoints (Class-Based Views)
```
POST   /api/v1/user/register/           # User registration
POST   /api/v1/user/login/              # User login
GET    /api/v1/user/list/               # List users
GET    /api/v1/user/<id>/               # User details
POST   /api/v1/user/token/              # Get JWT tokens
POST   /api/v1/user/token/refresh/      # Refresh token
POST   /api/v1/user/token/verify/       # Verify token
POST   /api/v1/user/token/regenerate/   # Regenerate tokens
```

### v2 Endpoints (ViewSet)
```
GET    /api/v2/user/                    # List users
POST   /api/v2/user/                    # Create user
GET    /api/v2/user/<id>/               # User details
PUT    /api/v2/user/<id>/               # Update user
PATCH  /api/v2/user/<id>/               # Partial update
DELETE /api/v2/user/<id>/               # Delete user
POST   /api/v2/user/register/           # Registration action
POST   /api/v2/user/regenerate_token/   # Token regeneration
```

## 🔧 Usage Examples

### Registration
```bash
curl -X POST http://localhost:8000/api/v1/user/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "User successfully registered",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/user/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }'
```

### Authenticated Request
```bash
curl -X GET http://localhost:8000/api/v1/user/list/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## 🏭 Models

### User (`apps/user/models.py`)
```python
class User(AbstractUser):
    ...
```
Extended AbstractUser with ULID primary key and email as unique identifier.

#### token() (`apps/user/models.py`)
```python
def token(self):
    ...
```
Generates JWT access and refresh tokens for user authentication.

## 📝 Serializers

### UserSerializer (`apps/user/serializers.py`)
```python
class UserSerializer(serializers.ModelSerializer):
    ...
```
Main serializer for user registration and data validation with password validation.

### UserLoginSerializer (`apps/user/serializers.py`)
```python
class UserLoginSerializer(serializers.Serializer):
    ...
```
Handles user login data validation with email and password fields.

### TokenSerializer (`apps/user/serializers.py`)
```python
class TokenSerializer(serializers.Serializer):
    ...
```
Serializes JWT token data containing access and refresh tokens.

## 🔐 Authentication Backend

### Custom Backend
```python
class EmailOrUsernameModelBackend(ModelBackend):
    """Allows login with either username or email"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username), 
                is_active=True
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            User().set_password(password)  # Timing attack protection
        return None
```

**Features:**
- Email or username login
- Timing attack protection
- Single database query optimization

## 🛡️ Permissions

### Custom Permissions
```python
class IsOwner(permissions.BasePermission):
    """Only allow owners of an object to access it"""
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow owners or admin users"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True
        if hasattr(obj, "user"):
            return obj.user == user
        return obj == user
```

## ⚙️ Configuration

### JWT Settings
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### Authentication Backends
```python
AUTHENTICATION_BACKENDS = [
    "core.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]
```

## 🚨 Security Features

### Password Validation
- Minimum 8 characters
- Must include letters and numbers
- Django's built-in validators
- Secure password hashing

### Token Security
- Short-lived access tokens
- Refresh token rotation
- Token blacklisting
- Bearer token authentication

### Timing Attack Protection
- Consistent response times
- Password hash simulation for failed logins

## 📊 File Structure

```
apps/user/
├── __init__.py
├── apps.py                 # App configuration
├── models.py               # User model
├── serializers.py          # DRF serializers
├── migrations/             # Database migrations
├── v1/                     # Version 1 API
│   ├── __init__.py
│   ├── urls.py            # URL routing
│   └── views.py           # Class-based views
├── v2/                     # Version 2 API
│   ├── __init__.py
│   ├── urls.py            # ViewSet URLs
│   └── views.py           # ViewSet implementation
└── README.md              # This file
```

## 🔍 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "success": false,
  "detail": "Error message",
  "code": "ERROR_CODE"  // Only in DEBUG mode
}
```

## 🚀 Development Tips

### Creating Users Programmatically
```python
from apps.user.models import User

# Create regular user
user = User.objects.create_user(
    username="user@example.com",
    email="user@example.com",
    password="password123"
)

# Create superuser
admin = User.objects.create_superuser(
    username="admin@example.com",
    email="admin@example.com",
    password="admin123"
)
```

### Token Usage in Views
```python
from rest_framework.permissions import IsAuthenticated

class MyProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user  # Authenticated user
        return Response({"user_id": user.id})
```