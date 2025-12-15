"""Logging configuration for OSGenome.

This module provides centralized logging configuration for the OSGenome application.
It offers both simple logger creation and comprehensive logging setup with
customizable formatting and output options.

The module supports environment-based configuration and provides sensible defaults
for different deployment scenarios.

Example:
    Basic logger usage:
        >>> from SNPedia.core.logger import get_logger
        >>> logger = get_logger("my_module")
        >>> logger.info("Application started")

    Custom logging configuration:
        >>> configure_logging(level="DEBUG", format_string="%(name)s: %(message)s")
        >>> logger = get_logger("debug_module", level="DEBUG")
"""

import logging
import os
import sys
from typing import Optional


def get_logger(name: str = "osgenome", level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses LOG_LEVEL environment variable

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Determine log level
        if level is None:
            level = os.environ.get("LOG_LEVEL", "INFO").upper()

        log_level = getattr(logging, level, logging.INFO)
        logger.setLevel(log_level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger


def configure_logging(
    level: Optional[str] = None, format_string: Optional[str] = None
) -> None:
    """Configure root logging for the application.

    Sets up the root logger with the specified level and format string.
    This affects all loggers in the application unless they have their
    own specific configuration.

    Args:
        level (Optional[str]): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                              If None, uses LOG_LEVEL environment variable or INFO.
        format_string (Optional[str]): Custom format string for log messages.
                                     If None, uses a default format with timestamp.

    Example:
        >>> configure_logging(level="DEBUG")
        >>> configure_logging(level="INFO", format_string="%(levelname)s: %(message)s")
    """
    if level is None:
        level = os.environ.get("LOG_LEVEL", "INFO").upper()

    log_level = getattr(logging, level, logging.INFO)

    if format_string is None:
        format_string = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"

    logging.basicConfig(
        level=log_level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


# Default logger instance for backward compatibility
logger = get_logger("app")
