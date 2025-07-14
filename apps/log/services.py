from __future__ import annotations

import hashlib
import logging

from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import QuerySet
from typing import Dict, List, Optional, Any

from apps.log.models import LogEntry

logger = logging.getLogger(__name__)


class LogSearchService:
    """Service for advanced log searching with optimized caching and performance"""

    def __init__(self):
        # AGGRESSIVE CACHE TIMES
        self.cache_timeout = 1800  # 30 minutes
        self.error_cache_timeout = 3600  # 1 hour
        self.stats_cache_timeout = 7200  # 2 hours
        self.max_results = 500  # Reduced for performance

        # Pre-define field sets for different use cases
        self.list_fields = [
            "id",
            "timestamp",
            "level",
            "message",
            "logger_name",
            "request_path",
            "status_code",
            "app_name",
        ]
        self.search_fields = self.list_fields + ["module", "function_name"]
        self.user_fields = ["user__id", "user__username"]

    def search_logs(
        self,
        query: str = "",
        level: str = "",
        hours: int = 24,
        user_id: Optional[int] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:

        limit = min(limit, self.max_results)

        # Multi-level cache key
        cache_key = self._generate_cache_key(query, level, hours, user_id, limit)

        # L1 Cache
        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result["metadata"]["cached"] = True
            cached_result["metadata"]["cache_level"] = "L1_FULL"
            return cached_result

        # L2 Cache
        query_cache_key = f"query:{cache_key}"
        cached_queryset = cache.get(query_cache_key)

        start_time = datetime.now()

        if cached_queryset:
            results = cached_queryset[:limit]
            logger.debug(f"L2 cache hit: {query_cache_key}")
        else:
            queryset = self._build_ultra_optimized_queryset(query, level, hours, user_id)
            if not queryset:
                return {"results": [], "metadata": {"total_count": 0, "returned_count": 0, "search_time_ms": 0}}

            results = list(queryset[:limit])

            # Save queryset to cache L2
            # Shorter cache time for query results
            cache.set(query_cache_key, results, self.cache_timeout // 2)
            logger.info(f"DB query executed: {len(results)} results")

        # Serialize
        serialized_results = [self._serialize_log_entry(log) for log in results]

        # Stats - get from cache or minimal stats
        stats = self._get_cached_stats(query, level, hours, user_id)

        search_result = {
            "results": serialized_results,
            "metadata": {
                "total_count": len(results),
                "returned_count": len(results),
                "search_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                "cached": False,
                "cache_level": "L2_QUERY" if cached_queryset else "DB_HIT",
                "filters": {"query": bool(query), "level": bool(level), "hours": hours, "user_id": bool(user_id)},
            },
            "stats": stats,
        }

        # save full result to L1 cache
        cache.set(cache_key, search_result, self.cache_timeout)

        return search_result

    def get_recent_errors(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent error logs with minimal DB load and caching"""

        # Tiered cache keys
        cache_key = f"errors:v3:{hours}:{limit}"
        hourly_cache_key = f"errors:hourly:{hours}"

        # L1: Exact match cache
        cached = cache.get(cache_key)
        if cached:
            return cached

        # L2: Hourly pre-aggregated cache
        hourly_errors = cache.get(hourly_cache_key)
        if hourly_errors:
            # Slice from hourly cache
            results = hourly_errors[:limit]
            cache.set(cache_key, results, 600)  # Cache specific limit
            return results

        # L3: Database with minimal fields
        time_threshold = datetime.now() - timedelta(hours=hours)

        error_logs = (
            LogEntry.objects.only(*self.list_fields)
            .filter(level__in=["ERROR", "CRITICAL"], timestamp__gte=time_threshold)
            .order_by("-timestamp")[:100]
        )  # Get more for hourly cache

        # Serialize all for hourly cache
        all_errors = [self._serialize_log_entry(log) for log in error_logs]

        # Cache both hourly and specific
        cache.set(hourly_cache_key, all_errors, self.error_cache_timeout)
        specific_results = all_errors[:limit]
        cache.set(cache_key, specific_results, 600)

        logger.info(f"Errors DB hit: {len(all_errors)} errors cached")
        return specific_results

    def _build_ultra_optimized_queryset(
        self, query: str, level: str, hours: int, user_id: Optional[int]
    ) -> QuerySet[LogEntry] | None:
        # Start with minimal fields
        fields_needed = self.search_fields.copy()
        if user_id or query:  # Only add user fields if needed
            fields_needed.extend(self.user_fields)

        queryset = LogEntry.objects.only(*fields_needed)

        # Add select_related only if user fields needed
        if user_id or any("user" in field for field in fields_needed):
            queryset = queryset.select_related("user")

        # Most selective filter first (time)
        if hours > 0:
            time_threshold = datetime.now() - timedelta(hours=hours)
            queryset = queryset.filter(timestamp__gte=time_threshold)

        # Level filter (highly selective)
        if level:
            queryset = queryset.filter(level=level.upper())

        # User filter
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Text search (least selective, last)
        if query and len(query) > 2:
            queryset = self._apply_minimal_text_search(queryset, query)
            if not queryset:
                return None  # No results for this query

        return queryset.order_by("-timestamp")

    def _apply_minimal_text_search(self, queryset, query: str) -> QuerySet[LogEntry] | None:
        """Apply minimal text search to avoid heavy DB load"""

        # Skip very short queries
        if len(query) <= 2:
            return queryset

        # For performance, use simple containment
        # PostgreSQL will use GIN index if available
        return queryset.filter(message__icontains=query)

    def _get_cached_stats(self, query: str, level: str, hours: int, user_id: Optional[int]) -> Dict:
        """Get stats from cache or return minimal stats for performance"""

        stats_key = f"stats:{level}:{hours}:{bool(user_id)}"
        cached_stats = cache.get(stats_key)

        if cached_stats:
            return cached_stats

        # Simplified stats for performance
        minimal_stats = {
            "total_in_range": "cached",  # Don't hit DB for this
            "by_level": {},
            "time_range": {
                "newest": datetime.now().isoformat(),
                "oldest": (datetime.now() - timedelta(hours=hours)).isoformat(),
            },
        }

        # Cache minimal stats
        cache.set(stats_key, minimal_stats, 3600)  # 1 hour
        return minimal_stats

    def _serialize_log_entry(self, log_entry: LogEntry) -> Dict[str, Any]:
        return {
            "id": log_entry.pk,
            "timestamp": log_entry.timestamp.isoformat(),
            "level": log_entry.level,
            "message": log_entry.message[:200],
            "logger_name": log_entry.logger_name,
            "request_path": getattr(log_entry, "request_path", ""),
            "status_code": getattr(log_entry, "status_code", None),
            "app_name": log_entry.app_name,
            "user_username": getattr(log_entry.user, "username", None) if hasattr(log_entry, "user") else None,
        }

    def _generate_cache_key(self, query: str, level: str, hours: int, user_id: Optional[int], limit: int) -> str:
        """Generate optimized cache key"""
        # Normalize query for better cache hits
        normalized_query = query.lower().strip() if query else ""
        key_data = f"v4:{normalized_query}:{level}:{hours}:{user_id}:{limit}"
        return f"log:{hashlib.md5(key_data.encode()).hexdigest()}"

    def warm_cache(self) -> Dict[str, int]:
        """Pre-warm frequently used caches"""
        warming_stats = {}

        # Warm recent errors
        warming_stats["errors_24h"] = len(self.get_recent_errors(24, 50))
        warming_stats["errors_1h"] = len(self.get_recent_errors(1, 20))

        # Warm common searches
        warming_stats["search_errors_24h"] = len(self.search_logs(level="ERROR", hours=24)["results"])
        warming_stats["search_all_1h"] = len(self.search_logs(hours=1, limit=100)["results"])

        logger.info(f"Cache warmed: {warming_stats}")
        return warming_stats
