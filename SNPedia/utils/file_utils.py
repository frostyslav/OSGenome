"""File utility functions for OSGenome."""

import json
import os

# Import from parent package
try:
    from SNPedia.core import get_config, get_logger
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import get_config, get_logger

# Get logger
logger = get_logger(__name__)

# Load configuration
config = get_config()

# Configuration values
MAX_FILE_SIZE_LOAD = config.MAX_FILE_SIZE_LOAD


def export_to_file(data: dict, filename: str) -> bool:
    """Export data to JSON file with error handling.

    Args:
        data: Dictionary to export
        filename: Name of the file to create

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not filename:
            logger.error("No filename provided for export")
            return False

        if not isinstance(data, (dict, list)):
            logger.error(f"Invalid data type for export: {type(data)}")
            return False

        parent_path = _get_parent_path()
        data_dir = os.path.join(parent_path, "data")

        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
                logger.info(f"Created data directory: {data_dir}")
            except OSError as e:
                logger.error(f"Failed to create data directory: {e}")
                return False

        filepath = os.path.join(data_dir, filename)

        # Write to temporary file first, then rename (atomic operation)
        temp_filepath = filepath + ".tmp"
        try:
            with open(temp_filepath, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)

            # Atomic rename
            os.replace(temp_filepath, filepath)
            logger.debug(f"Successfully exported data to {filepath}")
            return True

        except OSError as e:
            logger.error(f"Failed to write file {filepath}: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass
            return False

    except Exception as e:
        logger.error(f"Unexpected error in export_to_file: {e}")
        return False


def load_from_file(filename: str, use_cache: bool = False) -> dict:
    """Load data from JSON file with error handling.

    Args:
        filename: Name of the file to load
        use_cache: Whether to use caching (default: False for backward compatibility)

    Returns:
        dict: Loaded data or empty dict if error
    """
    # Use cache manager if caching is enabled
    if use_cache:
        try:
            from SNPedia.utils.cache_manager import load_json_lazy

            data = load_json_lazy(filename, use_cache=True)
            return data if data is not None else {}
        except ImportError:
            logger.warning("Cache manager not available, falling back to direct load")

    # Direct load without caching
    try:
        if not filename:
            logger.error("No filename provided for load")
            return {}

        filepath = os.path.join(_get_parent_path(), "data", filename)

        if not os.path.isfile(filepath):
            logger.warning(f"File not found: {filepath}")
            return {}

        # Check file is readable
        if not os.access(filepath, os.R_OK):
            logger.error(f"File not readable: {filepath}")
            return {}

        # Check file size (prevent loading huge files)
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE_LOAD:
            logger.error(
                f"File too large: {filepath} ({file_size} bytes, max {MAX_FILE_SIZE_LOAD})"
            )
            return {}

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, (dict, list)):
                logger.error(f"Invalid data type in file {filepath}: {type(data)}")
                return {}

            logger.debug(f"Successfully loaded data from {filepath}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {filepath}: {e}")
            return {}
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error in file {filepath}: {e}")
            return {}
        except OSError as e:
            logger.error(f"IO error reading file {filepath}: {e}")
            return {}

    except Exception as e:
        logger.error(f"Unexpected error in load_from_file: {e}")
        return {}


def _get_parent_path() -> str:
    """Get the parent path for data files.

    Returns:
        str: Path to the root directory (where data folder should be)
    """
    try:
        # Always use the root directory, not SNPedia subdirectory
        return os.path.curdir
    except Exception as e:
        logger.error(f"Error getting parent path: {e}")
        return os.path.curdir
