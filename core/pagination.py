# core/pagination.py dosyası
from __future__ import annotations

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from typing import Any


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class that formats paginated responses in a standardized way.

    This paginator provides consistent response formatting while maintaining pagination features:
    - Includes success flag
    - Wraps data in a 'data' key
    - Preserves pagination metadata (count, next, previous, results)
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

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
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )
