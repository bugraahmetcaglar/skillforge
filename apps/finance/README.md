# Finance App

Multi-currency subscription tracking and financial management system with 80+ predefined services.

## 🚀 Features

- **Subscription Management**: Track user subscriptions with billing cycles
- **Multi-currency Support**: 8 major currencies (TRY, USD, EUR, GBP, JPY, CNY, RUB, AUD)
- **Payment Methods**: 25+ payment options including Turkish services
- **Service Catalog**: 80+ predefined subscription services
- **Billing Automation**: Automatic billing date refresh
- **Categories**: 36 service categories for organization

## 🏗️ Architecture

### Models
- **SubscriptionServiceCategory**: Service categorization
- **SubscriptionService**: Available subscription services catalog
- **UserSubscription**: Individual user subscription tracking

### API Endpoints
```
POST   /api/v1/finance/subscriptions/create    # Create user subscription
GET    /api/v1/finance/my/subscriptions        # List active subscriptions
```

## 📋 Models Overview

### SubscriptionService (`apps/finance/models.py`)
```python
class SubscriptionService(BaseModel):
    ...
```
Subscription service catalog model storing information about available services with pricing, categories, and trial details.

### SubscriptionServiceCategory (`apps/finance/models.py`)
```python
class SubscriptionServiceCategory(BaseModel):
    ...
```
Categorization model for organizing subscription services into logical groups like "Video Streaming", "Productivity", etc.

### UserSubscription (`apps/finance/models.py`)
```python
class UserSubscription(BaseModel):
    ...
```
Individual user subscription tracking model with billing information, status management, and payment details.

#### refresh_next_billing_date() (`apps/finance/models.py`)
```python
def refresh_next_billing_date(self):
    ...
```
Updates the next billing date when subscription is overdue based on the billing cycle (weekly, monthly, quarterly, etc.).

## 🔧 Usage Examples

### Create Subscription
```bash
curl -X POST http://localhost:8000/api/v1/finance/subscriptions/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "service": 1,
    "plan_name": "Premium",
    "amount": "79.99",
    "currency": "TRY",
    "billing_cycle": "monthly",
    "started_at": "2025-01-01",
    "next_billing_date": "2025-02-01",
    "status": "active",
    "auto_renewal": true,
    "payment_method": "credit_card"
  }'
```

### List My Subscriptions
```bash
curl "http://localhost:8000/api/v1/finance/my/subscriptions" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "service": {
        "name": "Netflix",
        "website_url": "https://netflix.com"
      },
      "plan_name": "Premium",
      "amount": "79.99",
      "currency": "TRY",
      "billing_cycle": "monthly",
      "next_billing_date": "2025-02-01",
      "status": "active"
    }
  ]
}
```

## 💰 Supported Services

### Turkish Services
- **Video Streaming**: Exxen, BluTV, Puhu TV, Tabii, TOD, Gain
- **Music Streaming**: Fizy, Muud
- **E-commerce**: Trendyol Premium, Hepsiburada Premium, N11 Premium
- **Finance**: Tosla Premium
- **Transportation**: BiTaksi Premium

### International Services
- **Video Streaming**: Netflix, Disney+, Amazon Prime Video, YouTube Premium, Apple TV+, HBO Max
- **Music Streaming**: Spotify, Apple Music, YouTube Music, Tidal, Deezer
- **Cloud Storage**: Google Drive, Dropbox, iCloud+, OneDrive, MEGA
- **Productivity**: Microsoft 365, Google Workspace, Notion, Todoist, Evernote, Asana
- **Design**: Adobe Creative Cloud, Canva Pro, Figma, Sketch
- **Development**: GitHub, JetBrains, AWS, Google Cloud, DigitalOcean, Vercel

## 🗂️ Categories (36 Total)

### Primary Categories
- Video Streaming, Music Streaming, Cloud Storage
- Productivity, Design, Development, Communication
- Education, Gaming, VPN & Security, News & Media
- Health & Fitness, E-commerce, Finance, Transportation

### Specialized Categories  
- Dating, AI Services, Travel, Entertainment, Newsletter
- Fitness, Gaming Services, Social Media, Shopping
- News, Books, Software, Hardware, Automation, Marketing

## 💳 Payment Methods (25+ Options)

### Traditional
- Credit/Debit Cards, Bank Transfer, Wire Transfer, EFT

### Digital Wallets
- **International**: PayPal, Apple Pay, Google Pay, Samsung Pay, Amazon Pay
- **Turkish**: Paycell, Turkcell Paycell, Vodafone Cüzdan
- **BNPL**: Klarna, Maxi, Hopi

### Cryptocurrency
- Bitcoin, Ethereum, USDT, Binance Pay

### Payment Platforms
- Stripe, Square

## 📊 Billing Cycles & Status

### BillingCycleChoices
```python
class BillingCycleChoices(models.TextChoices):
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly" 
    QUARTERLY = "quarterly", "Quarterly"
    SEMI_ANNUALLY = "semi_annually", "Semi-Annually"
    ANNUALLY = "annually", "Annually"
```

### SubscriptionStatusChoices
```python
class SubscriptionStatusChoices(models.TextChoices):
    TRIAL = "trial", "Trial Period"
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    PENDING = "pending", "Pending Activation"
```

## 🏭 Data Population

### Setup Script
```python
# Run from Django shell
from scripts.add_subscription_categories_and_services import add_categories, start

# First populate categories (36 categories)
add_categories()

# Then populate services (80+ services)
start()
```

### Categories Examples
```python
categories_data = [
    {"name": "Video Streaming", "description": "Video streaming platforms like Netflix, Disney+"},
    {"name": "Music Streaming", "description": "Music streaming services like Spotify, Apple Music"},
    {"name": "Cloud Storage", "description": "Cloud storage services like Google Drive, Dropbox"},
    {"name": "Productivity", "description": "Productivity tools like Microsoft 365, Notion"},
    # ... 32 more categories
]
```

## 🔧 Admin Interface

### SubscriptionServiceAdmin
- List display: name, category, amount, currency, payment method
- Filters: category, currency, payment method, active status
- Search: name, description, category name

### UserSubscriptionAdmin  
- List display: user, service, plan, amount, billing cycle, status
- Filters: status, billing cycle, currency, auto renewal
- Search: user email, service name, plan name

## 📁 File Structure

```
apps/finance/
├── __init__.py
├── apps.py                 # App configuration
├── models.py               # Financial models
├── views.py                # API views
├── urls.py                 # URL routing
├── serializers.py          # DRF serializers
├── admin.py                # Django admin customization
├── enums.py                # Billing and status choices
├── migrations/             # Database migrations
└── README.md               # This file
```

## 🚀 Development Examples

### Creating User Subscription
```python
from apps.finance.models import UserSubscription, SubscriptionService

# Get service
netflix = SubscriptionService.objects.get(name="Netflix")

# Create subscription
subscription = UserSubscription.objects.create(
    user=user,
    service=netflix,
    plan_name="Premium",
    amount=Decimal("79.99"),
    currency=CurrencyChoices.TRY,
    billing_cycle=BillingCycleChoices.MONTHLY,
    started_at=date.today(),
    next_billing_date=date.today() + relativedelta(months=1),
    status=SubscriptionStatusChoices.ACTIVE,
    payment_method=PaymentMethodChoices.CREDIT_CARD
)
```

### Querying Subscriptions
```python
# Active subscriptions for user
active_subs = UserSubscription.objects.filter(
    user=user,
    status=SubscriptionStatusChoices.ACTIVE
)

# Subscriptions by category
streaming_subs = UserSubscription.objects.filter(
    user=user,
    service__category__name="Video Streaming"
)

# Upcoming renewals (next 7 days)
from datetime import date, timedelta
upcoming = UserSubscription.objects.filter(
    user=user,
    next_billing_date__lte=date.today() + timedelta(days=7),
    status=SubscriptionStatusChoices.ACTIVE
)