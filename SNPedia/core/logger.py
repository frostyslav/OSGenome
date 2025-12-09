"""Logging configuration for OSGenome."""

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
            fmt="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger


def configure_logging(level: Optional[str] = None, format_string: Optional[str] = None):
    """Configure root logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
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
        stream=sys.stdout
    )


# Default logger instance for backward compatibility
logger = get_logger("app")
