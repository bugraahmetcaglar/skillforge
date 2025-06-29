from django.db import models


class SubscriptionServiceCategoryChoices(models.TextChoices):
    STREAMING_VIDEO = "streaming_video", "Video Streaming"
    STREAMING_MUSIC = "streaming_music", "Music Streaming"
    CLOUD_STORAGE = "cloud_storage", "Cloud Storage"
    PRODUCTIVITY = "productivity", "Productivity & Office"
    DESIGN = "design", "Design & Creative"
    DEVELOPMENT = "development", "Development & Tech"
    COMMUNICATION = "communication", "Communication"
    EDUCATION = "education", "Learning & Education"
    GAMING = "gaming", "Gaming"
    VPN_SECURITY = "vpn_security", "VPN & Security"
    NEWS_MEDIA = "news_media", "News & Media"
    HEALTH_FITNESS = "health_fitness", "Health & Fitness"
    ECOMMERCE = "ecommerce", "E-commerce & Shopping"
    FINANCE = "finance", "Finance & Banking"
    TRANSPORTATION = "transportation", "Transportation"
    DATING = "dating", "Dating & Social"
    AI_SERVICES = "ai_services", "AI & Machine Learning"
    TRAVEL = "travel", "Travel & Booking"
    ENTERTAINMENT = "entertainment", "Entertainment & Leisure"
    NEWSLETTER = "newsletter", "Newsletter & Content"
    FITNESS = "fitness", "Fitness & Wellness"
    GAMING_SERVICES = "gaming_services", "Gaming Services"
    SOCIAL_MEDIA = "social_media", "Social Media"
    SHOPPING = "shopping", "Shopping & Retail"
    NEWS = "news", "News & Information"
    MUSIC = "music", "Music & Audio"
    VIDEO = "video", "Video & Streaming"
    BOOKS = "books", "Books & Literature"
    SOFTWARE = "software", "Software & Tools"
    HARDWARE = "hardware", "Hardware & Devices"
    AUTOMATION = "automation", "Automation & Integration"
    MARKETING = "marketing", "Marketing & Advertising"
    GAMING_SUBSCRIPTIONS = "gaming_subscriptions", "Gaming Subscriptions"
    CLOUD_SERVICES = "cloud_services", "Cloud Services"
    COMPUTER_PROGRAM = "computer_program", "Computer Programs"
    MOBILE_APP = "mobile_app", "Mobile Apps"
    WEB_SERVICE = "web_service", "Web Services"
    OTHER = "other", "Other"


class BillingCycleChoices(models.TextChoices):
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    SEMI_ANNUALLY = "semi_annually", "Semi-Annually"
    ANNUALLY = "annually", "Annually"


class SubscriptionStatusChoices(models.TextChoices):
    TRIAL = "trial", "Trial Period"
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    PENDING = "pending", "Pending Activation"


class BillTypeChoices(models.TextChoices):
    ELECTRICITY = "electricity", "Electricity"
    NATURAL_GAS = "natural_gas", "Natural Gas"
    WATER = "water", "Water"
    MOBILE_PHONE = "mobile_phone", "Mobile Phone"
    INTERNET = "internet", "Internet"
    LANDLINE = "landline", "Landline"
    CABLE_TV = "cable_tv", "Cable TV"
    RENT = "rent", "Rent"
    INSURANCE = "insurance", "Insurance"
    LOAN = "loan", "Loan Payment"
    CREDIT_CARD = "credit_card", "Credit Card"
    OTHER = "other", "Other"


class UsageFrequencyChoices(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    RARELY = "rarely", "Rarely"
    NEVER = "never", "Never Used"
    UNKNOWN = "unknown", "Unknown"


class BillStatusChoices(models.TextChoices):
    UNSETTLED = "unsettled", "Unsettled"
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    TERMINATED = "terminated", "Terminated"
    SUSPENDED = "suspended", "Suspended"
