"""Error handlers for SNPedia application."""

from typing import TYPE_CHECKING, Tuple

from flask import Flask, Response, current_app, jsonify

from SNPedia.core.logger import logger

if TYPE_CHECKING:
    from werkzeug.exceptions import HTTPException


def register_error_handlers(app: Flask) -> None:
    """Register error handlers with the Flask app.

    Args:
        app (Flask): The Flask application instance to register handlers with.

    Example:
        >>> from flask import Flask
        >>> from SNPedia.api.error_handlers import register_error_handlers
        >>> app = Flask(__name__)
        >>> register_error_handlers(app)
    """

    @app.errorhandler(400)
    def bad_request(error: "HTTPException") -> Tuple[Response, int]:
        """Handle 400 Bad Request errors.

        Args:
            error (HTTPException): The HTTP exception that triggered this handler.

        Returns:
            Tuple[Response, int]: JSON response and HTTP status code.
        """
        logger.warning(f"Bad request: {error.description}")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": error.description or "Invalid request",
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error: "HTTPException") -> Tuple[Response, int]:
        """Handle 404 Not Found errors.

        Args:
            error (HTTPException): The HTTP exception that triggered this handler.

        Returns:
            Tuple[Response, int]: JSON response and HTTP status code.
        """
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                }
            ),
            404,
        )

    @app.errorhandler(413)
    def request_entity_too_large(error: "HTTPException") -> Tuple[Response, int]:
        """Handle 413 Request Entity Too Large errors.

        Args:
            error (HTTPException): The HTTP exception that triggered this handler.

        Returns:
            Tuple[Response, int]: JSON response and HTTP status code.
        """
        logger.warning("File upload too large")
        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
        return (
            jsonify(
                {
                    "error": "File Too Large",
                    "message": f"Maximum file size is {max_size / (1024*1024):.0f}MB",
                }
            ),
            413,
        )

    @app.errorhandler(500)
    def internal_server_error(error: "HTTPException") -> Tuple[Response, int]:
        """Handle 500 Internal Server Error.

        Args:
            error (HTTPException): The HTTP exception that triggered this handler.

        Returns:
            Tuple[Response, int]: JSON response and HTTP status code.
        """
        logger.error(f"Internal server error: {error}")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> Tuple[Response, int]:
        """Handle any unexpected errors.

        Args:
            error (Exception): The exception that triggered this handler.

        Returns:
            Tuple[Response, int]: JSON response and HTTP status code.
        """
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            ),
            500,
        )
