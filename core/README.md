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

#### ULIDField
```python
class ULIDField(models.CharField):
    """ULID primary key field for better performance"""
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 26
        kwargs["unique"] = True
        super().__init__(*args, **kwargs)
```

#### NullableCharField
```python
class NullableCharField(models.CharField):
    """CharField that allows NULL instead of empty strings"""
    def __init__(self, *args, **kwargs):
        kwargs.update({"null": True, "blank": True, "default": None})
        super().__init__(*args, **kwargs)
```

### Base Models

#### BaseModel
```python
class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

### Money System

#### Money Class
```python
class Money:
    """Multi-currency money handling with automatic precision"""
    
    def __init__(self, amount, currency="TRY"):
        # Automatic rounding based on currency
        precision = self.CURRENCY_PRECISION.get(currency, 2)
        quantizer = Decimal("0.1") ** precision
        rounded_amount = Decimal(str(amount)).quantize(quantizer)
        self.money = MoneyedMoney(rounded_amount, Currency(currency))
    
    # Arithmetic operations
    def __add__(self, other): # Money + Money
    def __mul__(self, multiplier): # Money * number
    def __truediv__(self, divisor): # Money / number
    
    # Comparisons
    def __eq__(self, other): # Money == Money
    def __lt__(self, other): # Money < Money
```

**Features:**
- Automatic precision handling (JPY=0, BHD=3, others=2)
- Arithmetic operations with type safety
- Currency conversion support
- Serialization to/from dict

### Authentication Backend

#### EmailOrUsernameModelBackend
```python
class EmailOrUsernameModelBackend(ModelBackend):
    """Login with email or username in single query"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username),
                is_active=True
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Timing attack protection
            User().set_password(password)
        return None
```

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

#### BaseAPIView
```python
class BaseAPIView(GenericAPIView):
    """Foundation for standardized API responses"""
    
    def success_response(self, data=None, status_code=200, message=None):
        response_data = {"success": True}
        if message:
            response_data["message"] = message
        if data is not None:
            response_data["data"] = data
        return Response(response_data, status=status_code)
    
    def error_response(self, error_message="", status_code=400):
        return Response({
            "success": False,
            "detail": error_message
        }, status=status_code)
```

#### Specialized Views
- **BaseListAPIView**: Paginated list views
- **BaseCreateAPIView**: Object creation
- **BaseRetrieveAPIView**: Object retrieval
- **BaseUpdateAPIView**: Object updates

### Pagination

#### CustomPageNumberPagination
```python
class CustomPageNumberPagination(PageNumberPagination):
    """Standardized pagination with metadata"""
    
    page_size = 25
    page_size_query_param = "page_size"
    
    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "data": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
        })
```

### Utilities

#### recursive_getattr
```python
def recursive_getattr(obj, attr_path, default=None):
    """Get nested attributes using dot notation"""
    # user.profile.name -> getattr(getattr(user, 'profile'), 'name')
    try:
        attrs = attr_path.split(".")
        current_obj = obj
        for attr in attrs:
            current_obj = getattr(current_obj, attr, None)
            if current_obj is None:
                return default
        return current_obj
    except (AttributeError, TypeError):
        return default
```

#### multi_pop
```python
def multi_pop(dictionary, *keys, default=None):
    """Pop multiple keys from dictionary in one call"""
    return [dictionary.pop(key, default) for key in keys]
```

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

#### ExchangeRateAPI
```python
class ExchangeRateAPI:
    """Exchange rate conversion service"""
    
    def get_exchange_rate(self, base_currency, target_currency, target_date=None):
        """Get conversion rate between currencies"""
        url = f"{self.base_url}/pair/{base_currency}/{target_currency}"
        response = requests.get(url, timeout=30)
        
        if response.ok:
            rate = response.json().get("conversion_rate", 0)
            return Decimal(rate).quantize(Decimal("0.01"))
        return Decimal("0")
```

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

### Custom Exception Handler
```python
def custom_exception_handler(exc, context):
    """Security-aware exception handling"""
    response = drf_exception_handler(exc, context)
    
    if not settings.DEBUG:
        # Mask errors in production
        if response is not None:
            response.data = {"detail": "Invalid request."}
    
    return response
```

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