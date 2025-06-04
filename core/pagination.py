from __future__ import annotations

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from typing import Any

from core.utils import recursive_getattr


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class that formats paginated responses in a standardized way.

    This paginator provides consistent response formatting while maintaining pagination features:
    - Includes success flag
    - Wraps data in a 'data' key
    - Preserves pagination metadata (count, next, previous, results)
    """

    page_size = 25
    page_size_query_param = "page_size"

    def get_paginated_response(self, data: list[Any]) -> Response:
        """Override to return a response in our standard format.

        Args:
            data: The serialized page data

        Returns:
            Response: A response with success flag, data, and pagination info
        """
        return Response(
            {
                "success": True,
                "data": {
                    "count": recursive_getattr(self, "page.paginator.count", ""),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )
