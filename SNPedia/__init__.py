"""OSGenome - Open Source Genome Analysis Application.

This package provides tools for analyzing genetic data from services like 23andMe
by cross-referencing with SNPedia.
"""

__version__ = '2.0.0'
__author__ = 'OSGenome Contributors'

# Import core functionality
from .core import (
    get_config,
    load_config,
    get_logger,
    OSGenomeException,
    ConfigurationError,
    ValidationError,
)

# Import utilities
from .utils import (
    export_to_file,
    load_from_file,
    validate_rsid,
    validate_allele,
)

__all__ = [
    '__version__',
    '__author__',
    # Core
    'get_config',
    'load_config',
    'get_logger',
    # Exceptions
    'OSGenomeException',
    'ConfigurationError',
    'ValidationError',
    # Utils
    'export_to_file',
    'load_from_file',
    'validate_rsid',
    'validate_allele',
]
