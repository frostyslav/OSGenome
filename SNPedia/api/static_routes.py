"""Static file serving routes for SNPedia application."""

import os

from flask import Blueprint, Response, abort, send_from_directory
from werkzeug.utils import secure_filename

from SNPedia.core.logger import logger


def create_static_blueprint() -> Blueprint:
    """Create and configure the static file serving blueprint."""
    static = Blueprint("static_files", __name__)

    @static.route("/js/<path:path>")
    def serve_js(path: str) -> Response:
        """Serve static JavaScript files with path traversal protection."""
        try:
            # Validate path components individually to preserve directory structure
            path_parts = path.split("/")
            safe_parts = [secure_filename(part) for part in path_parts if part]
            safe_path = "/".join(safe_parts)

            # Additional security check - ensure no path traversal
            if ".." in safe_path or safe_path.startswith("/"):
                abort(404)

            js_dir = os.path.join(os.path.dirname(__file__), "..", "js")
            response = send_from_directory(js_dir, safe_path)
            response.headers["Content-Type"] = "text/javascript"
            return response
        except Exception as e:
            logger.warning(f"Error serving JS file {path}: {e}")
            abort(404)

    @static.route("/css/<path:path>")
    def serve_css(path: str) -> Response:
        """Serve static CSS files with path traversal protection."""
        try:
            # Validate path components individually to preserve directory structure
            path_parts = path.split("/")
            safe_parts = [secure_filename(part) for part in path_parts if part]
            safe_path = "/".join(safe_parts)

            # Additional security check - ensure no path traversal
            if ".." in safe_path or safe_path.startswith("/"):
                abort(404)

            css_dir = os.path.join(os.path.dirname(__file__), "..", "css")
            response = send_from_directory(css_dir, safe_path)
            response.headers["Content-Type"] = "text/css"
            return response
        except Exception as e:
            logger.warning(f"Error serving CSS file {path}: {e}")
            abort(404)

    return static
