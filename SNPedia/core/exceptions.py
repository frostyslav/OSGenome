"""Custom exceptions for OSGenome."""


class OSGenomeException(Exception):
    """Base exception for OSGenome."""
    pass


class ConfigurationError(OSGenomeException):
    """Configuration related errors."""
    pass


class ValidationError(OSGenomeException):
    """Data validation errors."""
    pass


class CrawlerError(OSGenomeException):
    """SNPedia crawler errors."""
    pass


class ImportError(OSGenomeException):
    """Genome import errors."""
    pass


class FileOperationError(OSGenomeException):
    """File operation errors."""
    pass


class RateLimitError(CrawlerError):
    """Rate limiting errors."""
    pass


class NetworkError(CrawlerError):
    """Network related errors."""
    pass


class DataNotFoundError(OSGenomeException):
    """Data not found errors."""
    pass
