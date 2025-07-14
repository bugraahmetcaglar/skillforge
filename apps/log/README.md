# Log App

Advanced logging system with structured log management, analytics, and performance optimizations.

## 🚀 Features

- **Structured Logging**: JSON formatted logs with context
- **Database Storage**: PostgreSQL-based log persistence
- **Advanced Search**: Multi-level cached search system
- **Analytics Dashboard**: Log statistics and insights
- **Performance Optimization**: Aggressive caching and query optimization
- **Automated Cleanup**: Retention policy-based log cleanup
- **Request Context**: User, IP, request path tracking

## 🏗️ Architecture

### Models
- **LogEntry**: Main log storage with comprehensive fields
- **Custom Indexes**: Optimized for common query patterns

### Services
- **LogSearchService**: Ultra-optimized search with caching
- **DatabaseLogHandler**: Custom logging handler for Django

## 📋 API Endpoints

```
GET    /api/v1/logs/search/         # Search logs with filters
GET    /api/v1/logs/errors/         # Recent error logs (cached)
GET    /api/v1/logs/stats/          # Log statistics and analytics
POST   /api/v1/logs/cache/          # Cache management (warm/clear)
```

## 🔧 Usage Examples

### Search Logs
```bash
# Basic search
curl "http://localhost:8000/api/v1/logs/search/?q=error&level=ERROR"

# Time-based search
curl "http://localhost:8000/api/v1/logs/search/?hours=24&limit=100"

# User-specific logs
curl "http://localhost:8000/api/v1/logs/search/?user_id=123&hours=12"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1234,
        "timestamp": "2024-01-15T10:30:00Z",
        "level": "ERROR",
        "message": "Database connection failed",
        "logger_name": "django.db.backends",
        "request_path": "/api/v1/users/",
        "status_code": 500,
        "user_username": "john_doe"
      }
    ],
    "metadata": {
      "total_count": 1,
      "search_time_ms": 25,
      "cached": true,
      "cache_level": "L1_FULL"
    }
  }
}
```

### Get Recent Errors
```bash
curl "http://localhost:8000/api/v1/logs/errors/?hours=24&limit=50"
```

### Log Statistics
```bash
curl "http://localhost:8000/api/v1/logs/stats/"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_logs": 15420,
    "logs_24h": 342,
    "error_count_24h": 12,
    "error_rate_24h": 3.51,
    "level_distribution": {
      "ERROR": 12,
      "WARNING": 45,
      "INFO": 280,
      "DEBUG": 5
    },
    "health_status": "healthy"
  }
}
```

## 🏭 Models

### LogEntry (`apps/log/models.py`)
```python
class LogEntry(BaseModel):
    ...
```
Main log storage model with comprehensive fields for timestamp, level, message, request context, performance metrics, and exception information.

#### cleanup_old_logs() (`apps/log/models.py`)
```python
@classmethod
def cleanup_old_logs(cls):
    ...
```
Clean up old logs based on retention policy while preserving critical logs with security keywords.

#### create_from_log_record() (`apps/log/models.py`)
```python
@classmethod
def create_from_log_record(cls, record, extra_context=None):
    ...
```
Create LogEntry from Python logging.LogRecord with additional request context.

## 🔍 Advanced Search System

### LogSearchService
```python
class LogSearchService:
    """Ultra-optimized log search with multi-level caching"""
    
    def search_logs(self, query="", level="", hours=24, user_id=None, limit=100):
        """Search logs with aggressive caching"""
        
        # Multi-level cache key
        cache_key = self._generate_cache_key(query, level, hours, user_id, limit)
        
        # L1 Cache - Full result cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # L2 Cache - Query result cache
        query_cache_key = f"query:{cache_key}"
        cached_queryset = cache.get(query_cache_key)
        
        if cached_queryset:
            results = cached_queryset[:limit]
        else:
            # Database query with optimization
            queryset = self._build_ultra_optimized_queryset(query, level, hours, user_id)
            results = list(queryset[:limit])
            cache.set(query_cache_key, results, self.cache_timeout // 2)
        
        # Serialize and cache full result
        search_result = {
            "results": [self._serialize_log_entry(log) for log in results],
            "metadata": self._get_metadata(results, cached_queryset)
        }
        
        cache.set(cache_key, search_result, self.cache_timeout)
        return search_result
```

### Cache Strategy
- **L1 Cache**: Full search results (30 minutes)
- **L2 Cache**: Query results (15 minutes)  
- **Hourly Cache**: Pre-aggregated data (1 hour)
- **Stats Cache**: Statistics (2 hours)

## 🗃️ Log Levels & Enums

### LogLevel Choices
```python
class LogLevel(BaseEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    EXCEPTION = "EXCEPTION"
    CRITICAL = "CRITICAL"
```

### Environment Choices
```python
class Environment(BaseEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
```

## 🛠️ Custom Log Handler

### DatabaseLogHandler (`apps/log/handlers.py`)
```python
class DatabaseLogHandler(logging.Handler):
    ...
```
PostgreSQL log handler using Django ORM with thread-local request context storage.

#### emit() (`apps/log/handlers.py`)
```python
def emit(self, record):
    ...
```
Emit log record to PostgreSQL database with request context, includes error handling to prevent application breakage.

#### set_request_context() (`apps/log/handlers.py`)
```python
def set_request_context(self, **context):
    ...
```
Set request context in thread-local storage for middleware integration.

## 🧹 Automated Cleanup

### cleanup_old_logs() (`apps/log/tasks.py`)
```python
def cleanup_old_logs():
    ...
```
Scheduled task to cleanup old logs based on retention policy (DEBUG: 7 days, INFO: 30 days, WARNING: 90 days, ERROR: 365 days).

### warm_log_cache() (`apps/log/tasks.py`)
```python
def warm_log_cache():
    ...
```
Scheduled task to warm up log search caches with frequently accessed data.

### setup_log_scheduled_tasks() (`apps/log/tasks.py`)
```python
def setup_log_scheduled_tasks():
    ...
```
Setup all log-related scheduled tasks including daily cleanup, cache warming, and weekly deep cleanup.

## ⚙️ Configuration

### Django Settings
```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
        },
        "database": {
            "level": "WARNING",
            "class": "apps.log.handlers.DatabaseLogHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "database"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "database"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
```

### Cache Configuration
```python
# Redis cache settings for log system
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
```

## 🛡️ Admin Interface

### LogEntry Admin Features
- **Read-only Interface**: Prevent log modification
- **Advanced Filtering**: Level, timestamp, logger filters
- **Search**: Message and logger name search
- **Analytics Link**: Direct access to analytics dashboard
- **Bulk Actions**: Disabled for data integrity

### Admin URLs
```python
# Custom admin analytics URL
path("analytics/", self.analytics_view, name="log_analytics")
```

### Analytics Dashboard
- Log level distribution with percentages
- Top active loggers
- Error rate calculations
- Quick action buttons
- Performance metrics

## 📊 Performance Features

### Query Optimization
- **Select Only**: Limited field selection for performance
- **Compound Indexes**: Multi-field indexes for common queries
- **Pagination**: Efficient pagination with cursor-based approach
- **Connection Pooling**: Database connection optimization

### Caching Strategy
```python
# Cache timeouts by data type
self.cache_timeout = 1800          # 30 minutes - general cache
self.error_cache_timeout = 3600    # 1 hour - error logs
self.stats_cache_timeout = 7200    # 2 hours - statistics
```

### Memory Management
- **Limited Results**: Maximum 500 results per query
- **Field Selection**: Only necessary fields loaded
- **Lazy Loading**: Deferred field loading where possible
- **Query Batching**: Bulk operations for efficiency

## 📈 Analytics & Monitoring

### Health Status Calculation
```python
def calculate_health_status(error_rate_24h):
    """Calculate system health based on error rate"""
    if error_rate_24h < 1:
        return "excellent"
    elif error_rate_24h < 3:
        return "healthy"  
    elif error_rate_24h < 8:
        return "warning"
    else:
        return "critical"
```

### Performance Metrics
- Average logs per hour
- Error density calculation
- Search response times
- Cache hit ratios
- Database query counts

## 📁 File Structure

```
apps/log/
├── __init__.py
├── apps.py                 # App configuration
├── models.py               # LogEntry model
├── views.py                # API views
├── urls.py                 # URL routing
├── serializers.py          # DRF serializers
├── services.py             # Search service with caching
├── handlers.py             # Custom log handler
├── admin.py                # Django admin with analytics
├── enums.py                # Log level and environment enums
├── tasks.py                # Background cleanup tasks
├── migrations/             # Database migrations
└── README.md               # This file
```

## 🚨 Security & Best Practices

### Data Protection
- **User Privacy**: Sensitive data filtering
- **SQL Injection**: Parameterized queries
- **Access Control**: Admin-only endpoints
- **Rate Limiting**: API request limiting

### Error Handling
- **Graceful Degradation**: Fallback when logging fails
- **Circuit Breaker**: Prevent log system overload
- **Exception Isolation**: Logging errors don't break app

### Performance Guidelines
- **Async Logging**: Non-blocking log writes
- **Batch Operations**: Bulk log processing
- **Index Maintenance**: Regular index optimization
- **Cache Warming**: Proactive cache population

## 🔧 Usage in Code

### Manual Logging
```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Debug information")
logger.info("User login successful")
logger.warning("High memory usage detected")
logger.error("Database connection failed")
logger.critical("System shutdown initiated")
```

### Request Context Logging
```python
# Automatic context from middleware
logger.error("Payment processing failed", extra={
    "user_id": request.user.id,
    "request_path": request.path,
    "ip_address": get_client_ip(request)
})
```

### Structured Logging
```python
# JSON structured logs
logger.info("User action", extra={
    "extra_data": {
        "action": "profile_update",
        "fields_changed": ["first_name", "email"],
        "success": True
    }
})
```