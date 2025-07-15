# Core Utilities

Shared utilities, custom fields, base classes, and helper functions used across the SkillForge platform.

## 🚀 Features

- **Custom Fields**: ULID and NullableChar fields
- **Base Models**: Common functionality for all models
- **Money System**: Multi-currency money handling
- **Permissions**: Custom permission classes
- **Views**: Base API view classes
- **Pagination**: Standardized pagination
- **Utilities**: Helper functions and tools

## 📁 Structure

```
core/
├── __init__.py
├── backends.py             # Authentication backends
├── enums.py               # Shared enums and choices
├── fields.py              # Custom model fields
├── models.py              # Base model classes
├── money.py               # Money handling system
├── pagination.py          # Custom pagination
├── permissions.py         # Permission classes
├── views.py               # Base API views
├── utils.py               # Helper utilities
└── services/              # Shared services
    ├── __init__.py
    └── exchange_rate_api.py
```

## 🏗️ Components

### Custom Fields

### ULIDField (`core/fields.py`)
```python
class ULIDField(models.CharField):
    ...
```
ULID primary key field for better performance and uniqueness than traditional auto-increment IDs.

### NullableCharField (`core/fields.py`)
```python
class NullableCharField(models.CharField):
    ...
```
CharField that allows NULL instead of empty strings, with automatic null=True, blank=True, default=None setup.

### Base Models

### BaseModel (`core/models.py`)
```python
class BaseModel(models.Model):
    ...
```
Abstract base model providing common fields (is_active, created_at, last_updated) for all models across the platform.

### Money System

### Money (`core/money.py`)
```python
class Money:
    ...
```
Multi-currency money handling class with automatic precision based on currency type and support for arithmetic operations.

#### __add__() (`core/money.py`)
```python
def __add__(self, other):
    ...
```
Add two money objects of the same currency.

#### __mul__() (`core/money.py`)
```python
def __mul__(self, multiplier):
    ...
```
Multiply money by a number (int, float, or Decimal).

#### __truediv__() (`core/money.py`)
```python
def __truediv__(self, divisor):
    ...
```
Divide money by a number with zero division protection.

#### to_dict() (`core/money.py`)
```python
def to_dict(self):
    ...
```
Convert Money object to dictionary representation for serialization.

#### from_dict() (`core/money.py`)
```python
@classmethod
def from_dict(cls, data):
    ...
```
Create Money object from dictionary data.

### Authentication Backend

### EmailOrUsernameModelBackend (`core/backends.py`)
```python
class EmailOrUsernameModelBackend(ModelBackend):
    ...
```
Authentication backend allowing login with email or username in single database query with timing attack protection.

#### authenticate() (`core/backends.py`)
```python
def authenticate(self, request, username=None, password=None, **kwargs):
    ...
```
Authenticates user with email or username, includes timing attack protection by simulating password verification for non-existent users.

### Permissions

#### IsOwner
```python
class IsOwner(permissions.BasePermission):
    """Only object owners can access"""
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user
```

#### IsOwnerOrAdmin
```python
class IsOwnerOrAdmin(permissions.BasePermission):
    """Owners or admin staff can access"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True
        if hasattr(obj, "user"):
            return obj.user == user
        return obj == user
```

### Base Views

### BaseAPIView (`core/views.py`)
```python
class BaseAPIView(GenericAPIView):
    ...
```
Foundation class for standardized API responses with success/error helpers and integrated logging.

#### success_response() (`core/views.py`)
```python
def success_response(self, data=None, status_code=200, message=None):
    ...
```
Returns standardized success response with optional data and message.

#### error_response() (`core/views.py`)
```python
def error_response(self, error_message="", status_code=400):
    ...
```
Returns standardized error response with error message and status code.

### BaseListAPIView (`core/views.py`)
```python
class BaseListAPIView(mixins.ListModelMixin, BaseAPIView):
    ...
```
Base view for paginated list operations with standardized response format.

### BaseCreateAPIView (`core/views.py`)
```python
class BaseCreateAPIView(mixins.CreateModelMixin, BaseAPIView):
    ...
```
Base view for object creation with success response formatting.

### BaseRetrieveAPIView (`core/views.py`)
```python
class BaseRetrieveAPIView(mixins.RetrieveModelMixin, BaseAPIView):
    ...
```
Base view for single object retrieval with standardized response.

### BaseUpdateAPIView (`core/views.py`)
```python
class BaseUpdateAPIView(mixins.UpdateModelMixin, BaseAPIView):
    ...
```
Base view for object updates supporting both PUT and PATCH operations.

### Pagination

### CustomPageNumberPagination (`core/pagination.py`)
```python
class CustomPageNumberPagination(PageNumberPagination):
    ...
```
Standardized pagination class with metadata and success flag formatting.

#### get_paginated_response() (`core/pagination.py`)
```python
def get_paginated_response(self, data):
    ...
```
Returns paginated response with success flag, count, next/previous links, and results.

### Utilities

### recursive_getattr() (`core/utils.py`)
```python
def recursive_getattr(obj, attr_path, default=None):
    ...
```
Get nested attributes using dot notation (e.g., "user.profile.name") with default value fallback.

### multi_pop() (`core/utils.py`)
```python
def multi_pop(dictionary, *keys, default=None):
    ...
```
Pop multiple keys from dictionary in one call, returns list of popped values.

### Enums

#### CurrencyChoices
```python
class CurrencyChoices(models.TextChoices):
    TRY = "TRY", "Turkish Lira"
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    GBP = "GBP", "British Pound"
    # ... 8 total currencies
```

#### PaymentMethodChoices
```python
class PaymentMethodChoices(models.TextChoices):
    # Credit/Debit Cards
    CREDIT_CARD = "credit_card", "Credit Card"
    DEBIT_CARD = "debit_card", "Debit Card"
    
    # Digital Wallets
    PAYPAL = "paypal", "PayPal"
    APPLE_PAY = "apple_pay", "Apple Pay"
    
    # Turkish Services
    PAYCELL = "paycell", "Paycell"
    TURKCELL_PAYCELL = "turkcell_paycell", "Turkcell Paycell"
    
    # Cryptocurrency
    BITCOIN = "bitcoin", "Bitcoin"
    ETHEREUM = "ethereum", "Ethereum"
    # ... 25+ total methods
```

### Services

### ExchangeRateAPI (`core/services/exchange_rate_api.py`)
```python
class ExchangeRateAPI:
    ...
```
Exchange rate conversion service using external API for real-time currency conversion.

#### get_exchange_rate() (`core/services/exchange_rate_api.py`)
```python
def get_exchange_rate(self, base_currency, target_currency, target_date=None):
    ...
```
Get conversion rate between currencies with optional historical date support, returns quantized Decimal.

## 🔧 Usage Examples

### Using Custom Fields
```python
class MyModel(BaseModel):
    id = ULIDField(primary_key=True)
    name = NullableCharField(max_length=100)
    # NULL instead of empty string
```

### Money Operations
```python
from core.money import Money

# Create money objects
price = Money("99.99", "USD")
tax = Money("8.50", "USD")

# Arithmetic operations
total = price + tax  # Money object
discount = total * 0.1  # 10% discount
final_price = total - discount

# Currency conversion
usd_amount = Money("100.00", "USD")
# Convert using exchange rate service
```

### Using Base Views
```python
class MyAPIView(BaseCreateAPIView):
    serializer_class = MySerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Created successfully"
            )
        return self.error_response("Validation failed")
```

### Permissions
```python
class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
```

## 🚨 Error Handling

### custom_exception_handler() (`core/views.py`)
```python
def custom_exception_handler(exc, context):
    ...
```
Security-aware exception handling that masks detailed errors in production while preserving debug information in development.

## 🏗️ Design Patterns

### Factory Pattern
- Model creation with sensible defaults
- Service instantiation with configuration

### Repository Pattern  
- Data access abstraction in services
- Clean separation of concerns

### Strategy Pattern
- Multiple authentication backends
- Configurable payment methods

## 🔐 Security Features

### Timing Attack Protection
- Consistent response times in auth backend
- Password hash simulation for failed logins

### Input Validation
- Custom field validation
- Serializer-level validation
- Model-level constraints

### Permission System
- Object-level permissions
- Role-based access control
- Admin privilege separation

## ⚡ Performance Optimizations

### Database
- Optimized indexes on base models
- Efficient query patterns in utilities
- Connection pooling support

### Caching
- Service-level caching utilities
- Response caching helpers
- Cache key generation

### Memory Management
- Lazy loading patterns
- Minimal object creation
- Efficient data structures