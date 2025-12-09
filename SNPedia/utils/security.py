"""Security utilities for OSGenome."""

import base64
from typing import Optional
from werkzeug.utils import secure_filename as werkzeug_secure_filename

# Import from parent package
try:
    from SNPedia.core import ValidationError
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import ValidationError


def secure_filename_wrapper(filename: str) -> str:
    """Secure a filename by removing dangerous characters.
    
    Args:
        filename: Filename to secure
        
    Returns:
        Secured filename
        
    Raises:
        ValidationError: If filename is invalid
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    secured = werkzeug_secure_filename(filename)
    
    if not secured:
        raise ValidationError(f"Invalid filename: {filename}")
    
    return secured


def validate_base64_data(data: str, max_size: Optional[int] = None) -> Optional[bytes]:
    """Validate and decode base64 data.
    
    Args:
        data: Base64 encoded string
        max_size: Maximum size of decoded data in bytes
        
    Returns:
        Decoded bytes or None if invalid
        
    Examples:
        >>> validate_base64_data('SGVsbG8=')
        b'Hello'
        >>> validate_base64_data('invalid!!!')
        None
    """
    try:
        # Check for empty or invalid input
        if not data or not isinstance(data, str):
            return None
        
        # Check if data is valid base64
        decoded = base64.b64decode(data, validate=True)
        
        # Check decoded size
        if max_size and len(decoded) > max_size:
            return None
        
        return decoded
        
    except Exception:
        return None


def sanitize_path(path: str) -> str:
    """Sanitize a file path to prevent directory traversal.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path
        
    Raises:
        ValidationError: If path contains dangerous patterns
    """
    if not path:
        raise ValidationError("Path cannot be empty")
    
    # Check for directory traversal attempts
    if '..' in path or path.startswith('/'):
        raise ValidationError(f"Invalid path: {path}")
    
    return path


def validate_content_type(content_type: str, allowed_types: set) -> bool:
    """Validate content type.
    
    Args:
        content_type: Content type to validate
        allowed_types: Set of allowed content types
        
    Returns:
        True if valid, False otherwise
    """
    if not content_type:
        return False
    
    # Extract main type (ignore parameters)
    main_type = content_type.split(';')[0].strip().lower()
    
    return main_type in allowed_types
