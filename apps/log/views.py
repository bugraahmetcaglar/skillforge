from __future__ import annotations

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.log.services import LogSearchService
from core.views import BaseAPIView
from apps.log.serializers import LogSearchSerializer

logger = logging.getLogger(__name__)


class LogSearchAPIView(BaseAPIView):
    """Ultra-optimized log search API with multi-level caching"""

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = LogSearchSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_service = LogSearchService()

    def get(self, request):
        """Search logs with advanced filters and performance optimization"""
        # Validate request parameters
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            # Perform ultra-optimized search
            results = self.search_service.search_logs(
                query=validated_data.get("q", ""),
                level=validated_data.get("level", ""),
                hours=validated_data.get("hours", 24),
                user_id=validated_data.get("user_id"),
                limit=validated_data.get("limit", 100),
            )


            return self.success_response(data=results)

        except Exception as err:
            logger.error(f"Log search error: {err}", exc_info=True)
            return self.error_response("Search failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecentErrorsAPIView(BaseAPIView):
    """Ultra-fast recent errors API with tiered caching"""

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = LogSearchSerializer

    @method_decorator(cache_page(60 * 10))  # View-level cache as backup
    def get(self, request):
        """Get recent error logs with aggressive caching"""
        # Validate parameters (reuse search serializer)
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        search_service = LogSearchService()

        try:
            # Get from tiered cache system
            errors = search_service.get_recent_errors(
                hours=validated_data.get("hours", 24), limit=validated_data.get("limit", 50)
            )

            # Response with cache optimization info
            response_data = {
                "errors": errors,
                "metadata": {
                    "hours": validated_data.get("hours", 24),
                    "limit": validated_data.get("limit", 50),
                    "count": len(errors),
                    "cache_optimized": True,
                    "performance_mode": "ultra_fast",
                },
            }

            return self.success_response(data=response_data, message=f"Retrieved {len(errors)} recent errors (cached)")

        except Exception as err:
            logger.error(f"Recent errors API error: {err}", exc_info=True)
            return self.error_response("Failed to retrieve recent errors")


class LogStatsAPIView(BaseAPIView):
    """Ultra-cached log statistics API"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    @method_decorator(cache_page(60 * 120))  # 2 hours view cache
    def get(self, request, *args, **kwargs):
        """Get log statistics with aggressive caching"""
        from django.db.models import Count
        from datetime import datetime, timedelta
        from apps.log.models import LogEntry

        try:
            # Use cached computation when possible
            cache_key = "log_stats_ultra_optimized"
            from django.core.cache import cache
            from django.db.models import Q

            cached_stats = cache.get(cache_key)
            if cached_stats:
                cached_stats["metadata"] = {
                    "cached": True,
                    "cache_level": "STATS_FULL",
                    "performance_mode": "ultra_cached",
                }
                return self.success_response(data=cached_stats, message="Statistics retrieved from cache")

            # Calculate stats with optimized queries
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)

            # Use efficient single queries
            stats_24h = LogEntry.objects.filter(timestamp__gte=last_24h).aggregate(
                total=Count("id"),
                errors=Count("id", filter=Q(level__in=["ERROR", "CRITICAL"])),
                warnings=Count("id", filter=Q(level="WARNING")),
                info=Count("id", filter=Q(level="INFO")),
            )

            total_logs = LogEntry.objects.count()
            logs_7d = LogEntry.objects.filter(timestamp__gte=last_7d).count()

            # Calculate derived metrics
            logs_24h = stats_24h["total"]
            error_count_24h = stats_24h["errors"]
            error_rate_24h = (error_count_24h / logs_24h * 100) if logs_24h > 0 else 0

            # Level distribution (optimized)
            level_distribution = {
                "ERROR": stats_24h["errors"],
                "WARNING": stats_24h["warnings"],
                "INFO": stats_24h["info"],
                "DEBUG": logs_24h - stats_24h["errors"] - stats_24h["warnings"] - stats_24h["info"],
            }

            # Top error sources (limited for performance)
            top_error_sources = list(
                LogEntry.objects.filter(timestamp__gte=last_24h, level__in=["ERROR", "CRITICAL"])
                .values("logger_name")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
                .values_list("logger_name", flat=True)
            )

            # Health status calculation
            if error_rate_24h < 1:
                health_status = "excellent"
            elif error_rate_24h < 3:
                health_status = "healthy"
            elif error_rate_24h < 8:
                health_status = "warning"
            else:
                health_status = "critical"

            # Compile final stats
            stats = {
                "total_logs": total_logs,
                "logs_24h": logs_24h,
                "logs_7d": logs_7d,
                "error_count_24h": error_count_24h,
                "error_rate_24h": round(error_rate_24h, 2),
                "level_distribution": level_distribution,
                "top_error_sources": top_error_sources,
                "health_status": health_status,
                "performance_metrics": {
                    "avg_logs_per_hour": round(logs_24h / 24, 1),
                    "error_density": round(error_count_24h / max(logs_24h, 1), 4),
                },
            }

            # Cache for 2 hours
            cache.set(cache_key, stats, 7200)

            # Add metadata
            stats["metadata"] = {
                "cached": False,
                "cache_level": "COMPUTED_FRESH",
                "performance_mode": "optimized_queries",
                "computation_time": "minimized",
            }
            logger.info("Log statistics computed and cached successfully")
            return self.success_response(data=stats, message="Statistics computed and cached")

        except Exception as err:
            logger.exception(f"Log stats error: {err}", exc_info=True)
            return self.error_response("Failed to retrieve log statistics")


class LogCacheManagementAPIView(BaseAPIView):
    """API for cache management and warming"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        """Manual cache warming or clearing"""

        action = request.data.get("action", "warm")
        search_service = LogSearchService()

        try:
            if action == "warm":
                # Warm caches
                warming_stats = search_service.warm_cache()
                logger.info(f"Cache warming completed: {warming_stats}")
                return self.success_response(data={"warming_stats": warming_stats}, message="Cache warming completed")

            elif action == "clear":
                # Clear caches
                from django.core.cache import cache

                cache.clear()
                logger.info("All log caches cleared")
                return self.success_response(data={"cleared": True}, message="All caches cleared")

            else:
                logger.error(f"Invalid cache action: {action}")
                return self.error_response(
                    "Invalid action. Use 'warm' or 'clear'", status_code=status.HTTP_400_BAD_REQUEST
                )

        except Exception as err:
            logger.exception(f"Cache management error: {err}", exc_info=True)
            return self.error_response("Cache management failed")
