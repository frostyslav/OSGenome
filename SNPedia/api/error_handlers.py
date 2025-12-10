"""Error handlers for SNPedia application."""

from flask import current_app, jsonify

from SNPedia.core.logger import logger


def register_error_handlers(app):
    """Register error handlers with the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
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
    def not_found(error):
        """Handle 404 Not Found errors."""
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
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors."""
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
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
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
    def handle_unexpected_error(error):
        """Handle any unexpected errors."""
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
