# Finance App Documentation

## Overview

The Finance app manages user subscriptions and financial services within the SkillForge platform. It provides a comprehensive system for tracking subscription services, managing user subscriptions, and monitoring financial commitments.

## Features

- **Subscription Service Management**: Catalog of available subscription services with categories
- **User Subscription Tracking**: Personal subscription management for users
- **Multi-currency Support**: Support for 8 major currencies (TRY, USD, EUR, GBP, JPY, CNY, RUB, AUD)
- **Payment Method Integration**: 25+ payment methods including Turkish local services
- **Billing Cycle Management**: Weekly, monthly, quarterly, semi-annual, and annual billing
- **Subscription Status Tracking**: Trial, active, paused, cancelled, expired, and pending states
- **RESTful API**: Full CRUD operations via Django REST Framework

## Models

### SubscriptionServiceCategory

Organizes subscription services into logical categories.

```python
class SubscriptionServiceCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
```

**Example Categories:**
- Video Streaming (Netflix, Disney+, Exxen)
- Music Streaming (Spotify, Apple Music, Fizy)
- Cloud Storage (Google Drive, iCloud+, Dropbox)
- Productivity (Microsoft 365, Notion, Asana)
- Design (Adobe Creative Cloud, Figma, Canva Pro)

### SubscriptionService

Represents available subscription services that users can subscribe to.

```python
class SubscriptionService(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(SubscriptionServiceCategory, ...)
    logo_url = models.URLField(null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, ...)
    currency = models.CharField(choices=CurrencyChoices.choices, ...)
    payment_method = models.CharField(choices=PaymentMethodChoices.choices, ...)
    free_trial_days = models.PositiveIntegerField(null=True, blank=True)
    free_trial_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
```

### UserSubscription

Tracks individual user subscriptions with detailed billing and status information.

```python
class UserSubscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    service = models.ForeignKey(SubscriptionService, on_delete=models.PROTECT)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(choices=CurrencyChoices.choices)
    billing_cycle = models.CharField(choices=BillingCycleChoices.choices)
    started_at = models.DateField()
    next_billing_date = models.DateField()
    trial_end_date = models.DateField(null=True, blank=True)
    cancelled_at = models.DateField(null=True, blank=True)
    status = models.CharField(choices=SubscriptionStatusChoices.choices)
    auto_renewal = models.BooleanField(default=False)
    payment_method = models.CharField(choices=PaymentMethodChoices.choices)
    payment_account = models.CharField(max_length=100, blank=True)
    notes = models.TextField(null=True, blank=True)
```

## API Endpoints

### User Subscription Management

- `POST /api/v1/finance/subscriptions/create` - Create a new user subscription
- `GET /api/v1/finance/my/subscriptions` - List user's active subscriptions

### Request/Response Examples

**Create Subscription:**
```json
POST /api/v1/finance/subscriptions/create
{
    "service": 1,
    "plan_name": "Premium",
    "amount": "79.99",
    "currency": "TRY",
    "billing_cycle": "monthly",
    "started_at": "2025-01-01",
    "next_billing_date": "2025-02-01",
    "status": "active",
    "auto_renewal": true,
    "payment_method": "credit_card",
    "payment_account": "Garanti *1234"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User subscription created successfully"
}
```

## Enums and Choices

### Currency Support
- **TRY** - Turkish Lira
- **USD** - US Dollar
- **EUR** - Euro
- **GBP** - British Pound
- **JPY** - Japanese Yen
- **CNY** - Chinese Yuan
- **RUB** - Russian Ruble
- **AUD** - Australian Dollar

### Payment Methods
**Traditional:**
- Credit/Debit Cards
- Bank Transfer, Wire Transfer, EFT

**Digital Wallets:**
- PayPal, Apple Pay, Google Pay, Samsung Pay
- Turkish: Paycell, Turkcell Paycell, Vodafone Cüzdan
- BNPL: Klarna, Maxi, Hopi

**Cryptocurrency:**
- Bitcoin, Ethereum, USDT, Binance Pay

### Billing Cycles
- **weekly** - Weekly billing
- **monthly** - Monthly billing
- **quarterly** - Quarterly billing
- **semi_annually** - Semi-annual billing
- **annually** - Annual billing

### Subscription Status
- **trial** - Trial Period
- **active** - Active subscription
- **paused** - Temporarily paused
- **cancelled** - User cancelled
- **expired** - Subscription expired
- **pending** - Pending activation

## Admin Interface

### SubscriptionServiceAdmin
- List view with category, amount, currency, payment method filters
- Search by name, description, category
- Read-only timestamps

### SubscriptionServiceCategoryAdmin
- Basic CRUD operations
- Search and filter capabilities

### UserSubscriptionAdmin
- Comprehensive list view showing user, service, billing details
- Advanced filtering by status, billing cycle, currency
- User and service search functionality

## Data Population

The app includes a comprehensive script to populate initial data:

### Categories (36 total)
- Video Streaming, Music Streaming, Cloud Storage
- Productivity, Design, Development, Communication
- Education, Gaming, VPN & Security, News & Media
- Health & Fitness, E-commerce, Finance, Transportation
- And 21 more specialized categories

### Services (80+ popular services)
**Turkish Services:**
- Exxen, BluTV, Puhu TV, Tabii, TOD, Gain
- Fizy, Muud
- Trendyol Premium, Hepsiburada Premium, N11 Premium
- Tosla Premium, BiTaksi Premium

**International Services:**
- Netflix, Disney+, Amazon Prime Video, YouTube Premium
- Spotify, Apple Music, YouTube Music, Tidal
- Google Drive, Dropbox, iCloud+, OneDrive
- Microsoft 365, Notion, Asana, Trello
- Adobe Creative Cloud, Figma, Canva Pro

**Usage:**
```python
# Run from Django shell
from scripts.add_subscription_categories_and_services import add_categories, start

# First populate categories
add_categories()

# Then populate services
start()
```

## Architecture

### Design Patterns
- **Repository Pattern**: Clean separation of data access logic
- **Service Layer**: Business logic isolation in services
- **Factory Pattern**: Model creation with sensible defaults
- **Observer Pattern**: Django signals for subscription events

### Security Features
- **Permission-based Access**: Owner-based permissions using `IsOwner`
- **Input Validation**: Comprehensive serializer validation
- **Data Integrity**: Foreign key constraints with PROTECT on delete
- **User Context**: Automatic user assignment in subscription creation

### Database Design
- **Normalization**: Proper table relationships with foreign keys
- **Indexing**: Database indexes on frequently queried fields
- **Constraints**: Unique constraints and data validation
- **Soft Deletes**: BaseModel provides soft delete functionality

## Future Enhancements

### Planned Features
1. **Bill Management**: Recurring bills (electricity, water, internet)
2. **Expense Tracking**: Monthly expense analytics
3. **Budget Management**: Budget limits and alerts
4. **Reporting**: Financial reports and insights
5. **Notifications**: Subscription renewal reminders
6. **Integration**: Payment gateway integrations

### Technical Improvements
1. **Caching**: Redis caching for frequently accessed data
2. **Background Tasks**: django-q tasks for subscription processing
3. **API Versioning**: Versioned API endpoints
4. **Rate Limiting**: API rate limiting implementation
5. **Monitoring**: Subscription status monitoring
6. **Analytics**: Usage analytics and metrics

## Usage Examples

### Creating a User Subscription
```python
from apps.finance.models import UserSubscription, SubscriptionService
from apps.user.models import User

# Get user and service
user = User.objects.get(username="john_doe")
netflix = SubscriptionService.objects.get(name="Netflix")

# Create subscription
subscription = UserSubscription.objects.create(
    user=user,
    service=netflix,
    plan_name="Premium",
    amount=79.99,
    currency="TRY",
    billing_cycle="monthly",
    started_at="2025-01-01",
    next_billing_date="2025-02-01",
    status="active",
    payment_method="credit_card"
)
```

### Querying User Subscriptions
```python
# Get all active subscriptions for a user
active_subs = UserSubscription.objects.filter(
    user=user, 
    status="active"
)

# Get subscriptions by category
streaming_subs = UserSubscription.objects.filter(
    user=user,
    service__category__name="Video Streaming"
)

# Get upcoming renewals
from datetime import date, timedelta
upcoming = UserSubscription.objects.filter(
    user=user,
    next_billing_date__lte=date.today() + timedelta(days=7)
)
```

This Finance app provides a solid foundation for comprehensive subscription and financial management within the SkillForge platform, with room for extensive future enhancements.
