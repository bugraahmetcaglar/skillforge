# Contact App

Contact management system with vCard import, duplicate detection, and advanced filtering capabilities.

## 🚀 Features

- **vCard Import**: Support for .vcf/.vcard files
- **Duplicate Detection**: Phone number-based duplicate finding
- **Advanced Filtering**: Search, organization, date filters
- **Phone Normalization**: Turkish phone number formatting
- **Contact Backup**: Automatic backup on deletion
- **Bulk Operations**: Mass contact operations via admin

## 🏗️ Architecture

### Models
- **Contact**: Main contact storage with comprehensive fields
- **ContactBackup**: Backup storage for deleted contacts
- **ContactManager**: Custom manager for duplicate detection

### Services
- **VCardImportService**: Handles vCard file processing
- **VCardParser**: Parses vCard content and extracts data

## 📋 API Endpoints

```
POST   /api/v1/contact/import/vcard      # Import vCard file
GET    /api/v1/contact/list              # List contacts (paginated)
GET    /api/v1/contact/detail/<id>       # Contact details
GET    /api/v1/contact/duplicate-numbers # Find duplicate phone numbers
```

## 🔧 Usage Examples

### vCard Import
```bash
curl -X POST http://localhost:8000/api/v1/contact/import/vcard \
  -H "Authorization: Bearer <token>" \
  -F "vcard_file=@contacts.vcf"
```

**Response:**
```json
{
  "success": true,
  "message": "Imported 15 of 20 contacts",
  "data": {
    "imported_count": 15,
    "failed_count": 5,
    "total_processed": 20,
    "errors": ["Contact 3: Invalid email format"]
  }
}
```

### List Contacts with Filters
```bash
# Search contacts
curl "http://localhost:8000/api/v1/contact/list?search=john"

# Filter by organization
curl "http://localhost:8000/api/v1/contact/list?organization=google"

# Filter by import source
curl "http://localhost:8000/api/v1/contact/list?import_source=vcard"

# Date range filter
curl "http://localhost:8000/api/v1/contact/list?created_after=2024-01-01"
```

### Find Duplicates
```bash
curl "http://localhost:8000/api/v1/contact/duplicate-numbers" \
  -H "Authorization: Bearer <token>"
```

## 🏭 Models

### Contact (`apps/contact/models.py`)
```python
class Contact(BaseModel):
    ...
```
Main contact storage model with comprehensive fields for personal and business information, supports multiple phone numbers, emails, and organization data.

#### display_name (`apps/contact/models.py`)
```python
@property
def display_name(self):
    ...
```
Property that returns formatted full name or "Unknown Contact" as fallback.

#### delete() (`apps/contact/models.py`)
```python
def delete(self):
    ...
```
Soft-deletes contact by setting is_active=False and creates automatic backup.

#### search() (`apps/contact/models.py`)
```python
@classmethod
def search(cls, user, keyword):
    ...
```
Class method that searches contacts by name, email, or phone across multiple fields.

### ContactBackup (`apps/contact/models.py`)
```python
class ContactBackup(BaseModel):
    ...
```
Backup storage model for deleted contacts with JSON field containing complete contact data.

#### get_field() (`apps/contact/models.py`)
```python
def get_field(self, field_name):
    ...
```
Retrieves specific field value from the stored contact data JSON.

#### restore() (`apps/contact/models.py`)
```python
def restore(self):
    ...
```
Restores contact from backup by reactivating existing contact or creating new one.

### ContactManager (`apps/contact/models.py`)
```python
class ContactManager(models.Manager):
    ...
```
Custom manager providing specialized query methods for contact operations.

#### duplicate_numbers() (`apps/contact/models.py`)
```python
def duplicate_numbers(self, user_id):
    ...
```
Finds contacts with duplicate phone numbers using window functions, returns queryset with ranking and count annotations.

## 📝 Services

### VCardImportService (`apps/contact/services.py`)
```python
class VCardImportService:
    ...
```
Handles vCard file processing and contact import operations for users.

#### import_from_file() (`apps/contact/services.py`)
```python
def import_from_file(self, vcard_file):
    ...
```
Processes uploaded vCard file, parses content, and saves contacts to database with error handling.

### VCardParser (`apps/contact/services.py`)
```python
class VCardParser:
    ...
```
Parses vCard file content and extracts contact data into dictionary format.

#### parse() (`apps/contact/services.py`)
```python
def parse(self, content):
    ...
```
Main parsing method that splits vCard content into blocks and processes each contact entry.

#### extract_full_name() (`apps/contact/services.py`)
```python
def extract_full_name(self, vcard):
    ...
```
Extracts full name from vCard FN field.

#### extract_name() (`apps/contact/services.py`)
```python
def extract_name(self, vcard, data):
    ...
```
Extracts first, middle, and last names from vCard N field.

#### extract_phone_numbers() (`apps/contact/services.py`)
```python
def extract_phone_numbers(self, vcard, data):
    ...
```
Extracts and normalizes phone numbers from vCard TEL fields with type detection.

### ContactFilter (`apps/contact/filter.py`)
```python
class ContactFilter(filters.FilterSet):
    ...
```
Django-filter class providing advanced filtering capabilities for contact queries.

#### filter_search() (`apps/contact/filter.py`)
```python
def filter_search(self, queryset, name, value):
    ...
```
Performs global search across multiple contact fields (name, email, phone, organization).

## 🔍 Filtering System

### ContactFilter
```python
class ContactFilter(filters.FilterSet):
    # Text search
    search = filters.CharFilter(method="filter_search")
    
    # Name filters
    first_name = filters.CharFilter(lookup_expr="icontains")
    last_name = filters.CharFilter(lookup_expr="icontains")
    
    # Contact info
    email = filters.CharFilter(lookup_expr="icontains")
    mobile_phone = filters.CharFilter(lookup_expr="icontains")
    
    # Organization
    organization = filters.CharFilter(lookup_expr="icontains")
    
    # Import source
    import_source = filters.ChoiceFilter(choices=SourceTextChoices.choices)
    
    # Date filters
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    
    def filter_search(self, queryset, name, value):
        """Global search across multiple fields"""
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value) |
            Q(mobile_phone__icontains=value) |
            Q(organization__icontains=value)
        ).distinct()
```

## 📞 Phone Number Utilities

### normalize_phone_number() (`apps/contact/utils.py`)
```python
def normalize_phone_number(phone):
    ...
```
Normalize Turkish phone numbers to +90XXXXXXXXXX format, keeps non-Turkish numbers in original format.

### generate_external_id() (`apps/contact/utils.py`)
```python
def generate_external_id(data, source):
    ...
```
Generate unique external ID for contact using MD5 hash of data and source prefix.

## 🗃️ Import Sources

### Supported Sources
```python
class SourceTextChoices(models.TextChoices):
    GOOGLE = "google", "Google"
    OUTLOOK = "outlook", "Outlook"
    SIM = "sim", "SIM Card"
    ICLOUD = "icloud", "iCloud"
    CSV = "csv", "CSV File"
    MANUAL = "manual", "Manual Entry"
    WHATSAPP = "whatsapp", "WhatsApp"
    TELEGRAM = "telegram", "Telegram"
    LINKEDIN = "linkedin", "LinkedIn"
    VCARD = "vcard", "vCard"
```

## 🛡️ Admin Interface

### Contact Admin Features
- **Analytics Dashboard**: Contact statistics and insights
- **Bulk Backup**: Mass backup creation
- **Advanced Filtering**: Organization, source, date filters
- **Search**: Name, email, phone, organization search
- **Custom Actions**: Backup creation for selected contacts

### Admin URLs
```python
# Custom admin URLs
path("analytics/", self.analytics_view, name="contact_contact_analytics")
path("bulk_backup/", self.bulk_backup_view, name="contact_contact_bulk_backup")
```

## 📊 File Structure

```
apps/contact/
├── __init__.py
├── apps.py                 # App configuration
├── models.py               # Contact and backup models
├── views.py                # API views
├── urls.py                 # URL routing
├── serializers.py          # DRF serializers
├── services.py             # vCard import service
├── utils.py                # Phone normalization utilities
├── filter.py               # Django-filter configurations
├── admin.py                # Django admin customization
├── enums.py                # Choice enums
├── tasks.py                # Background tasks
├── migrations/             # Database migrations
└── README.md               # This file
```

## 🚨 Validation & Security

### vCard File Validation
```python
def validate_vcard_file(self, value):
    """Validate uploaded vCard file"""
    # File extension check
    if not value.name.lower().endswith((".vcf", ".vcard")):
        raise ValidationError("Invalid file format")
    
    # File size check (max 5MB)
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("File too large")
    
    # Content validation
    content = value.read().decode("utf-8")
    if not content.strip().startswith("BEGIN:VCARD"):
        raise ValidationError("Invalid vCard format")
```

### Permission Control
- **IsOwner**: Users can only access their own contacts
- **Authentication Required**: All endpoints require login
- **Object-level Permissions**: Contact ownership validation

## 🔧 Background Tasks

### cleanup_inactive_contacts() (`apps/contact/tasks.py`)
```python
def cleanup_inactive_contacts():
    ...
```
Permanently delete contacts that have been inactive for more than 30 days, contacts are already backed up when deactivated.

### save_contacts_task() (`apps/contact/tasks.py`)
```python
def save_contacts_task(user_id, contacts):
    ...
```
Background task to save contacts to database with error handling and progress tracking.

### enqueue_save_contacts_task() (`apps/contact/tasks.py`)
```python
def enqueue_save_contacts_task(user_id, contacts):
    ...
```
Queue contact saving as background task using Django-Q with timeout and hooks.

## 🚀 Development Tips

### Creating Contacts Programmatically
```python
from apps.contact.models import Contact

# Create contact
contact = Contact.objects.create(
    user=user,
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    mobile_phone="+905321234567",
    import_source="manual"
)
```

### Phone Number Processing
```python
from apps.contact.utils import normalize_phone_number

# Normalize phone numbers
phone = normalize_phone_number("0532 123 45 67")  # +905321234567
phone = normalize_phone_number("+1 804 200 3448")  # +18042003448
```