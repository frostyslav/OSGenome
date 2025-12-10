"""Static file serving routes for SNPedia application."""

from flask import Blueprint, abort, send_from_directory
from werkzeug.utils import secure_filename

from SNPedia.core.logger import logger


def create_static_blueprint() -> Blueprint:
    """Create and configure the static file serving blueprint."""
    static = Blueprint("static_files", __name__)

    @static.route("/js/<path:path>")
    def serve_js(path):
        """Serve static JavaScript files with path traversal protection."""
        try:
            safe_path = secure_filename(path)
            return send_from_directory("js", safe_path)
        except Exception as e:
            logger.warning(f"Error serving JS file {path}: {e}")
            abort(404)

    @static.route("/css/<path:path>")
    def serve_css(path):
        """Serve static CSS files with path traversal protection."""
        try:
            safe_path = secure_filename(path)
            return send_from_directory("css", safe_path)
        except Exception as e:
            logger.warning(f"Error serving CSS file {path}: {e}")
            abort(404)

    return static
