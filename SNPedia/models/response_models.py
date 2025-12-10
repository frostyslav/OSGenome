"""Response models for API endpoints.

This module defines standardized response models for all API endpoints,
ensuring consistent data structures and type safety across the application.

The models use dataclasses for automatic generation of common methods
and provide type hints for better IDE support and runtime validation.

Example:
    Creating a basic API response:
        >>> response = APIResponse(success=True, message="Operation completed")
        >>> response_dict = response.to_dict()
        >>> print(response_dict['success'])  # True

    Creating a paginated response:
        >>> data = [{"id": 1}, {"id": 2}]
        >>> paginated = PaginatedResponse(
        ...     data=data, page=1, page_size=10, total=2,
        ...     total_pages=1, has_next=False, has_prev=False
        ... )
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class APIResponse:
    """Base API response model for standardized responses.

    Provides a consistent structure for all API responses with success status,
    optional message, data payload, and timestamp information.

    Attributes:
        success (bool): Whether the operation was successful.
        message (Optional[str]): Optional human-readable message.
        data (Optional[Any]): Optional response data payload.
        timestamp (Optional[datetime]): Response timestamp, auto-generated if None.

    Example:
        >>> response = APIResponse(success=True, data={"count": 42})
        >>> response.to_dict()
        {'success': True, 'timestamp': '2024-01-01T12:00:00', 'data': {'count': 42}}
    """

    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Set timestamp if not provided.

        Automatically sets the timestamp to the current time if not
        explicitly provided during initialization.
        """
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Converts the response object to a dictionary suitable for JSON
        serialization, including only non-None fields.

        Returns:
            Dict[str, Any]: Dictionary representation of the response.

        Example:
            >>> response = APIResponse(success=True, message="Done")
            >>> response.to_dict()
            {'success': True, 'message': 'Done', 'timestamp': '2024-01-01T12:00:00'}
        """
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

        if self.message is not None:
            result["message"] = self.message

        if self.data is not None:
            result["data"] = self.data

        return result


@dataclass
class PaginatedResponse:
    """Response model for paginated data.

    Provides a standardized structure for paginated API responses,
    including the data items and comprehensive pagination metadata.

    Attributes:
        data (List[Any]): The actual data items for the current page.
        page (int): Current page number (1-indexed).
        page_size (int): Number of items per page.
        total (int): Total number of items across all pages.
        total_pages (int): Total number of pages.
        has_next (bool): Whether there is a next page available.
        has_prev (bool): Whether there is a previous page available.

    Example:
        >>> response = PaginatedResponse(
        ...     data=[{"id": 1}, {"id": 2}],
        ...     page=1, page_size=10, total=25,
        ...     total_pages=3, has_next=True, has_prev=False
        ... )
        >>> print(f"Showing page {response.page} of {response.total_pages}")
    """

    data: List[Any]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Converts the paginated response to a dictionary with separate
        'results' and 'pagination' sections for clear API structure.

        Returns:
            Dict[str, Any]: Dictionary with 'results' and 'pagination' keys.

        Example:
            >>> response = PaginatedResponse(data=[1, 2], page=1, page_size=10,
            ...                            total=2, total_pages=1,
            ...                            has_next=False, has_prev=False)
            >>> response.to_dict()
            {'results': [1, 2], 'pagination': {'page': 1, 'page_size': 10, ...}}
        """
        return {
            "results": self.data,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total": self.total,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
            },
        }


@dataclass
class StatisticsResponse:
    """Response model for statistics data."""

    total: int
    interesting: int
    uncommon: int
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "total": self.total,
            "interesting": self.interesting,
            "uncommon": self.uncommon,
        }

        if self.message:
            result["message"] = self.message

        return result


@dataclass
class HealthCheckResponse:
    """Response model for health check endpoint."""

    status: str
    data_loaded: bool
    data_count: int
    config_valid: bool
    config_warnings: List[str]
    version: str
    cache_stats: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "data_loaded": self.data_loaded,
            "data_count": self.data_count,
            "config_valid": self.config_valid,
            "config_warnings": self.config_warnings,
            "version": self.version,
            "cache": self.cache_stats,
        }


@dataclass
class ConfigResponse:
    """Response model for configuration endpoint."""

    config: Dict[str, Any]
    environment: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"config": self.config, "environment": self.environment}
