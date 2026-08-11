"""
Core Pagination
================
Standardised pagination classes for all API list endpoints.

Responses follow the envelope:
    {
        "success": true,
        "count": 245,
        "next": "https://mynaroda.in/api/v1/trees/?page=3",
        "previous": "https://mynaroda.in/api/v1/trees/?page=1",
        "results": [ ... ]
    }
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Default paginator for all list endpoints.
    Returns 20 items per page; clients can request up to 100.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data: list) -> Response:
        return Response(
            {
                "success": True,
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "results": data,
            }
        )


class GalleryPagination(PageNumberPagination):
    """
    Larger page size for gallery endpoints to support masonry infinite scroll.
    Returns 30 items per page (optimised for masonry grid rendering).
    """

    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 60

    def get_paginated_response(self, data: list) -> Response:
        return Response(
            {
                "success": True,
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "has_more": self.get_next_link() is not None,
                "results": data,
            }
        )


class LargeResultsSetPagination(PageNumberPagination):
    """
    Used for admin list endpoints where larger datasets are needed.
    Returns 50 items per page; admin can request up to 200.
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data: list) -> Response:
        return Response(
            {
                "success": True,
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
