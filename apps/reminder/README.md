# Reminder App

Task automation and reminder system with financial reminders, birthday alerts, and subscription notifications.

## 🚀 Features

- **Finance Reminders**: Subscription payments, bill due dates
- **Birthday Alerts**: Contact birthday notifications
- **Task Automation**: Scheduled reminder tasks
- **Multi-currency**: Financial reminders with currency support
- **Telegram Integration**: Automated notifications via Telegram
- **Recurring Reminders**: Repeat patterns for ongoing tasks

## 🏗️ Architecture

### Models
- **BaseReminder**: Abstract base for all reminder types
- **FinanceReminder**: Financial and subscription reminders

### Tasks
- **Background Processing**: Django-Q scheduled tasks
- **Telegram Notifications**: Automated message sending

## 📋 Models Overview

### BaseReminder (`apps/reminder/models.py`)
```python
class BaseReminder(BaseModel):
    ...
```
Abstract base model for all reminder types providing common fields like title, status, reminder date, and snooze functionality.

#### mark_as_completed() (`apps/reminder/models.py`)
```python
def mark_as_completed(self):
    ...
```
Sets reminder status to completed and updates last_updated timestamp.

#### mark_as_snoozed() (`apps/reminder/models.py`)
```python
def mark_as_snoozed(self, snooze_until):
    ...
```
Snoozes reminder until specific datetime, increments snooze count, and sets status to snoozed.

#### mark_as_failed() (`apps/reminder/models.py`)
```python
def mark_as_failed(self):
    ...
```
Marks reminder as failed and updates timestamp.

### FinanceReminder (`apps/reminder/models.py`)
```python
class FinanceReminder(BaseReminder):
    ...
```
Financial reminder model extending BaseReminder with amount, currency, payment details, and subscription linking.

## 🔄 Status Management

### Reminder Statuses
```python
class ReminderStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"
    SNOOZED = "snoozed", "Snoozed"
```

### Status Methods
```python
# Mark as completed
reminder.mark_as_completed()

# Snooze until specific datetime
reminder.mark_as_snoozed(snooze_until=datetime.now() + timedelta(hours=2))

# Mark as failed
reminder.mark_as_failed()
```

## 📧 Background Tasks

### Birthday Reminders
```python
def generate_birthday_reminders_in_30_days():
    """Generate birthday reminders for next 30 days"""
    today = date.today()
    end_date = today + timedelta(days=30)
    
    contacts = Contact.objects.filter(
        is_active=True,
        birthday__isnull=False,
        # Date range logic for birthdays
    ).order_by("birthday")
    
    message = "🎂 <b>Upcoming Birthdays:</b>\n\n"
    for contact in contacts:
        message += f"• {contact.display_name} - {contact.birthday.strftime('%d %B')}\n"
    
    TelegramReminderAPI().send_message(message)
    return True
```

### Subscription Renewals
```python
def generate_auto_renewal_subscription_reminders():
    """Alert for subscriptions renewing in 7 days"""
    today = date.today()
    end_date = today + timedelta(days=7)
    
    subscriptions = UserSubscription.objects.filter(
        is_active=True,
        auto_renewal=True,
        next_billing_date__range=[today, end_date],
        status=SubscriptionStatusChoices.ACTIVE
    ).select_related("user", "service")
    
    message = "🔔 <b>Subscription Auto Renewal Reminder:</b>\n\n"
    for sub in subscriptions:
        message += f"• <b>Service:</b> {sub.service.name}\n"
        message += f"• <b>Amount:</b> {sub.amount} {sub.currency}\n"
        message += f"• <b>Date:</b> {sub.next_billing_date.strftime('%d %B %Y')}\n\n"
    
    TelegramReminderAPI().send_message(message)
    return True
```

### Monthly Expense Reports
```python
def monthly_subscription_expense_report():
    """Generate monthly subscription expense report"""
    today = date.today()
    start_date = today.replace(day=1)
    end_date = (start_date + relativedelta(months=1)).replace(day=1)
    
    subscriptions = UserSubscription.objects.filter(
        next_billing_date__gte=start_date,
        next_billing_date__lt=end_date,
        status=SubscriptionStatusChoices.ACTIVE
    )
    
    total_amount = Decimal("0.00")
    for subscription in subscriptions:
        # Convert to TRY if needed
        if subscription.currency != CurrencyChoices.TRY:
            rate = ExchangeRateAPI().get_exchange_rate(
                subscription.currency, CurrencyChoices.TRY
            )
            converted = subscription.amount * rate
        else:
            converted = subscription.amount
        
        total_amount += converted
    
    message = f"💰 <b>This Month's Subscription Total:</b>\n\n"
    message += f"• <b>Amount:</b> {total_amount} TRY\n"
    
    TelegramReminderAPI().send_message(message)
    return True
```

### Billing Date Refresh
```python
def refresh_next_billing_dates():
    """Update past billing dates based on cycle"""
    today = date.today()
    overdue_subs = UserSubscription.objects.filter(
        next_billing_date__lt=today,
        status=SubscriptionStatusChoices.ACTIVE
    )
    
    for subscription in overdue_subs:
        subscription.refresh_next_billing_date()
    
    return True
```

## 📊 Finance Categories

### Expense Categories
```python
class ExpenseCategoryChoices(models.TextChoices):
    PERSONAL = "personal", "Personal"
    BUSINESS = "business", "Business"
    INVESTMENT = "investment", "Investment"
    SUBSCRIPTION = "subscription", "Subscription"
    UTILITIES = "utilities", "Utilities"
    TRANSPORTATION = "transportation", "Transportation"
    FOOD = "food", "Food & Dining"
    ENTERTAINMENT = "entertainment", "Entertainment"
    HEALTH = "health", "Health & Medical"
    EDUCATION = "education", "Education"
    # ... more categories
```

## 📱 Telegram Integration

### Reminder Notifications
- Birthday alerts with contact names and dates
- Subscription renewal warnings
- Monthly expense summaries
- Payment due date alerts
- Auto-renewal confirmations

### Message Formatting
```python
# Birthday reminder format
message = """🎂 <b>Upcoming Birthdays:</b>

• John Doe - 15 January
• Jane Smith - 18 January
• Mike Johnson - 22 January"""

# Subscription reminder format  
message = """🔔 <b>Subscription Renewal:</b>

• <b>Service:</b> Netflix Premium
• <b>Amount:</b> 79.99 TRY
• <b>Date:</b> 15 January 2025
• <b>Website:</b> netflix.com"""
```

## ⏰ Scheduling System

### Task Scheduling
```python
# Daily birthday check at 9 AM
schedule(
    "apps.reminder.tasks.generate_birthday_reminders_in_30_days",
    schedule_type=Schedule.DAILY,
    next_run=datetime.now().replace(hour=9, minute=0)
)

# Weekly subscription renewal check
schedule(
    "apps.reminder.tasks.generate_auto_renewal_subscription_reminders", 
    schedule_type=Schedule.WEEKLY
)

# Monthly expense reports
schedule(
    "apps.reminder.tasks.monthly_subscription_expense_report",
    schedule_type=Schedule.MONTHLY
)
```

### Billing Date Management
```python
# Auto-refresh overdue billing dates
schedule(
    "apps.reminder.tasks.refresh_next_billing_dates",
    schedule_type=Schedule.DAILY,
    next_run=datetime.now().replace(hour=6, minute=0)
)
```

## 💱 Currency Handling

### Multi-currency Support
- Automatic conversion to TRY for Turkish users
- Exchange rate API integration
- Real-time rate fetching
- Currency-specific formatting

### Conversion Example
```python
# Convert subscription amount to TRY
if subscription.currency != CurrencyChoices.TRY:
    exchange_rate = ExchangeRateAPI().get_exchange_rate(
        base_currency=subscription.currency,
        target_currency=CurrencyChoices.TRY
    )
    try_amount = subscription.amount * exchange_rate
else:
    try_amount = subscription.amount
```

## 📁 File Structure

```
apps/reminder/
├── __init__.py
├── apps.py                 # App configuration
├── models.py               # Reminder models
├── enums.py                # Status and category choices
├── tasks.py                # Background task definitions
├── admin.py                # Django admin (if needed)
├── migrations/             # Database migrations
└── README.md               # This file
```

## 🔧 Usage Examples

### Creating Finance Reminder
```python
from apps.reminder.models import FinanceReminder

reminder = FinanceReminder.objects.create(
    user=user,
    title="Netflix Subscription Payment",
    amount=Decimal("79.99"),
    currency=CurrencyChoices.TRY,
    finance_category=ExpenseCategoryChoices.SUBSCRIPTION,
    due_date=date(2025, 1, 15),
    reminder_date=datetime(2025, 1, 12, 9, 0),
    alert_days_before=3
)
```

### Snoozing Reminder
```python
# Snooze for 2 hours
snooze_until = datetime.now() + timedelta(hours=2)
reminder.mark_as_snoozed(snooze_until)
```

### Completing Reminder
```python
# Mark as completed
reminder.mark_as_completed()
```

## 🚨 Error Handling

### Task Error Management
- Failed task logging
- Retry mechanisms
- Fallback notifications
- Error alerting

### Telegram API Failures
- Connection timeout handling
- Rate limit management
- Message delivery confirmation
- Offline queuing

## ⚡ Performance Features

### Optimizations
- Efficient date range queries
- Bulk database operations
- Cached exchange rates
- Minimal API calls

### Database Efficiency
- Indexed date fields
- Optimized foreign key queries
- Selective field loading
- Connection pooling