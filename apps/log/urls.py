from django.urls import path
from apps.log.views import LogSearchAPIView, RecentErrorsAPIView, LogStatsAPIView


urlpatterns = [
    # Log APIs
    path("search/", LogSearchAPIView.as_view(), name="log_search"),
    path("errors/", RecentErrorsAPIView.as_view(), name="recent_errors"),
    path("stats/", LogStatsAPIView.as_view(), name="log_stats"),
]
