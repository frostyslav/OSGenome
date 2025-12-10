"""Main Flask application."""

import os
from flask import Flask, render_template

from SNPedia.core.config import load_config
from SNPedia.core.logger import logger
from SNPedia.api.routes import create_api_blueprint
from SNPedia.api.file_routes import create_file_blueprint
from SNPedia.api.static_routes import create_static_blueprint
from SNPedia.api.error_handlers import register_error_handlers


def create_app():
    """Application factory pattern."""
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
    
    # Main route
    @app.route("/", methods=["GET", "POST"])
    def main():
        return render_template("snp_resource.html")
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = (
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
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1')
