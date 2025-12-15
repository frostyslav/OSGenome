"""Service for file operations and Excel generation."""

import base64
import io
from typing import Optional

from flask import current_app
from werkzeug.utils import secure_filename

from SNPedia.core.logger import logger


class FileService:
    """Service for handling file operations."""

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate if filename is allowed."""
        if not filename or not isinstance(filename, str):
            return False

        allowed_extensions = current_app.config.get(
            "ALLOWED_EXTENSIONS", {"xlsx", "xls"}
        )
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
        )

    @staticmethod
    def validate_base64_content(data: str) -> Optional[bytes]:
        """Validate and decode base64 content."""
        try:
            # Check for empty or invalid input
            if not data or not isinstance(data, str):
                logger.warning("Empty or invalid base64 data")
                return None

            # Check if data is valid base64
            decoded = base64.b64decode(data, validate=True)

            # Check decoded size
            max_size = current_app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
            if len(decoded) > max_size:
                logger.warning(f"File content too large: {len(decoded)} bytes")
                return None

            return decoded

        except Exception as e:
            logger.error(f"Error validating base64 content: {e}")
            return None

    @staticmethod
    def create_excel_file(filename: str, content: bytes) -> Optional[io.BytesIO]:
        """Create Excel file from content."""
        try:
            # Sanitize filename
            safe_filename = secure_filename(filename)
            if not safe_filename or not FileService.validate_filename(safe_filename):
                logger.error(f"Invalid filename: {filename}")
                return None

            # Create BytesIO object
            bytes_io = io.BytesIO()
            bytes_io.write(content)
            bytes_io.seek(0)

            return bytes_io

        except Exception as e:
            logger.error(f"Error creating Excel file: {e}")
            return None

    @staticmethod
    def get_excel_mimetype() -> str:
        """Get MIME type for Excel files."""
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
