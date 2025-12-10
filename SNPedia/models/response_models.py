"""Response models for API endpoints."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class APIResponse:
    """Base API response model."""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
        
        if self.message is not None:
            result["message"] = self.message
        
        if self.data is not None:
            result["data"] = self.data
            
        return result


@dataclass
class PaginatedResponse:
    """Response model for paginated data."""
    data: List[Any]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "results": self.data,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total": self.total,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev
            }
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
        result = {
            "total": self.total,
            "interesting": self.interesting,
            "uncommon": self.uncommon
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
            "cache": self.cache_stats
        }


@dataclass
class ConfigResponse:
    """Response model for configuration endpoint."""
    config: Dict[str, Any]
    environment: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "config": self.config,
            "environment": self.environment
        }