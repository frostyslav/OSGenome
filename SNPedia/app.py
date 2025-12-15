"""Main Flask application.

This module contains the Flask application factory and main application setup.
It configures the application with blueprints, error handlers, and security headers.

Example:
    Basic usage:
        >>> from SNPedia.app import create_app
        >>> app = create_app()
        >>> app.run()

    Production usage:
        >>> app = create_app()
        >>> # Use with gunicorn or other WSGI server

Attributes:
    app (Flask): The main Flask application instance.
"""

import os

from flask import Flask, Response, render_template

from SNPedia.api.error_handlers import register_error_handlers
from SNPedia.api.file_routes import create_file_blueprint
from SNPedia.api.routes import create_api_blueprint
from SNPedia.api.static_routes import create_static_blueprint
from SNPedia.core.config import load_config
from SNPedia.core.logger import logger
from SNPedia.core.metrics import init_metrics


def create_app() -> Flask:
    """Create and configure the Flask application.

    This function implements the application factory pattern, creating a new
    Flask application instance with all necessary configuration, blueprints,
    and middleware.

    Returns:
        Flask: Configured Flask application instance.

    Raises:
        ValueError: If configuration loading fails.

    Example:
        >>> app = create_app()
        >>> app.config['TESTING'] = True
        >>> with app.test_client() as client:
        ...     response = client.get('/')
        ...     assert response.status_code == 200
    """
    app = Flask(__name__, template_folder="templates")

    # Load configuration
    try:
        config_class = load_config(app)
        logger.info(f"Application started with {config_class.__name__}")
    except ValueError as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    # Register blueprints
    app.register_blueprint(create_api_blueprint())
    app.register_blueprint(create_file_blueprint())
    app.register_blueprint(create_static_blueprint())

    # Register error handlers
    register_error_handlers(app)

    # Initialize Prometheus metrics
    init_metrics(app)

    # Main route
    @app.route("/", methods=["GET", "POST"])
    def main() -> str:
        """Render the main application page.

        Returns:
            str: Rendered HTML template for the main SNP resource page.
        """
        return render_template("snp_resource.html")

    # Security headers
    @app.after_request
    def set_security_headers(response: Response) -> Response:
        """Add security headers to all responses.

        This function adds comprehensive security headers to protect against
        common web vulnerabilities including XSS, clickjacking, and content
        type sniffing attacks.

        Args:
            response (Response): The Flask response object to modify.

        Returns:
            Response: The modified response object with security headers.

        Note:
            Security headers include:
            - X-Content-Type-Options: Prevents MIME type sniffing
            - X-Frame-Options: Prevents clickjacking attacks
            - X-XSS-Protection: Enables XSS filtering
            - Strict-Transport-Security: Enforces HTTPS
            - Content-Security-Policy: Controls resource loading
        """
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://unpkg.com https://cdn.sheetjs.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.sheetjs.com; "
            "font-src 'self' https://cdnjs.cloudflare.com;"
        )
        return response

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    # Never run with debug=True in production
    debug_mode: bool = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    # Bind to all interfaces for Docker compatibility - use FLASK_HOST env var to override
    host = os.environ.get("FLASK_HOST", "0.0.0.0")  # nosec B104
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(debug=debug_mode, host=host, port=port)
