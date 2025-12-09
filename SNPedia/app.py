import base64
import io
import os
import logging

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
    abort,
)
from werkzeug.utils import secure_filename
from SNPedia.core.config import load_config
from SNPedia.utils.cache_manager import (
    load_json_lazy,
    load_json_paginated,
    get_cache_stats,
    clear_all_cache,
    invalidate_cache
)

# Create Flask app
app = Flask(__name__, template_folder="templates")

# Load configuration
try:
    config_class = load_config(app)
    app.logger.info(f"Application started with {config_class.__name__}")
except ValueError as e:
    logging.error(f"Failed to load configuration: {e}")
    raise

# Rate limiting storage (simple in-memory for now)
request_counts = {}


@app.route("/", methods=["GET", "POST"])
def main():
    return render_template("snp_resource.html")


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def validate_base64(data):
    """Validate base64 data before decoding."""
    try:
        # Check for empty or invalid input
        if not data or not isinstance(data, str):
            return None
        
        # Check if data is valid base64
        decoded = base64.b64decode(data, validate=True)
        
        # Check decoded size
        if len(decoded) > app.config['MAX_CONTENT_LENGTH']:
            return None
        
        return decoded
    except Exception:
        return None


@app.route("/excel", methods=["POST"])
def create_file():
    """Generate Excel file from base64 encoded data."""
    # Validate required fields
    if 'fileName' not in request.form or 'base64' not in request.form:
        abort(400, description="Missing required fields")
    
    filename = request.form["fileName"]
    
    # Sanitize filename
    filename = secure_filename(filename)
    if not filename or not allowed_file(filename):
        abort(400, description="Invalid filename or file type")
    
    # Validate and decode base64 content
    filecontents = validate_base64(request.form["base64"])
    if filecontents is None:
        abort(400, description="Invalid or oversized file content")
    
    try:
        bytesIO = io.BytesIO()
        bytesIO.write(filecontents)
        bytesIO.seek(0)
        
        return send_file(
            bytesIO,
            download_name=filename,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        app.logger.error(f"Error creating Excel file: {str(e)}")
        abort(500, description="Error generating file")


@app.route("/images/<path:path>")
def send_image(path):
    """Serve static image files with path traversal protection."""
    try:
        # secure_filename prevents directory traversal
        safe_path = secure_filename(path)
        return send_from_directory("images", safe_path)
    except Exception:
        abort(404)


@app.route("/js/<path:path>")
def send_js(path):
    """Serve static JavaScript files with path traversal protection."""
    try:
        safe_path = secure_filename(path)
        return send_from_directory("js", safe_path)
    except Exception:
        abort(404)


@app.route("/css/<path:path>")
def send_css(path):
    """Serve static CSS files with path traversal protection."""
    try:
        safe_path = secure_filename(path)
        return send_from_directory("css", safe_path)
    except Exception:
        abort(404)


@app.route("/api/rsids", methods=["GET"])
def get_types():
    """Get RSIDs data with pagination support."""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', app.config.get('DEFAULT_PAGE_SIZE', 100), type=int)
        
        # Limit page size
        max_page_size = app.config.get('MAX_PAGE_SIZE', 1000)
        if page_size > max_page_size:
            page_size = max_page_size
        
        # Check if pagination is requested
        use_pagination = 'page' in request.args or 'page_size' in request.args
        
        if use_pagination:
            # Load with pagination
            result = load_json_paginated("result_table.json", page=page, page_size=page_size)
            return jsonify({
                "results": result['data'],
                "pagination": {
                    "page": result['page'],
                    "page_size": result['page_size'],
                    "total": result['total'],
                    "total_pages": result['total_pages'],
                    "has_next": result['has_next'],
                    "has_prev": result['has_prev']
                }
            })
        else:
            # Load all data (cached)
            results = load_json_lazy("result_table.json")
            if not results:
                return jsonify({"results": [], "message": "No data available"}), 200
            return jsonify({"results": results})
            
    except Exception as e:
        app.logger.error(f"Error fetching RSIDs: {str(e)}")
        abort(500, description="Error fetching data")


@app.route("/api/statistics", methods=["GET"])
def statistics():
    """Get statistics about the genetic data."""
    try:
        # Load data from cache
        results = load_json_lazy("result_table.json")
        
        if not results:
            return jsonify({
                "total": 0,
                "interesting": 0,
                "uncommon": 0,
                "message": "No data available"
            }), 200
        
        total_entries = len(results)
        interesting_entries = 0
        uncommon_entries = 0
        
        for entry in results:
            if "IsInteresting" in entry and entry["IsInteresting"].lower() == "yes":
                interesting_entries += 1
            if "IsUncommon" in entry and entry["IsUncommon"].lower() == "yes":
                uncommon_entries += 1

        return jsonify(
            {
                "total": total_entries,
                "interesting": interesting_entries,
                "uncommon": uncommon_entries,
            }
        )
    except Exception as e:
        app.logger.error(f"Error calculating statistics: {str(e)}")
        abort(500, description="Error calculating statistics")


@app.route("/api/config", methods=["GET"])
def get_config_info():
    """Get non-sensitive configuration information."""
    try:
        config_dict = config_class.to_dict()
        return jsonify({
            "config": config_dict,
            "environment": os.environ.get('FLASK_ENV', 'development')
        })
    except Exception as e:
        app.logger.error(f"Error fetching config: {str(e)}")
        abort(500, description="Error fetching configuration")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check if data file exists and can be loaded
        results = load_json_lazy("result_table.json")
        data_loaded = results is not None and len(results) > 0
        data_count = len(results) if results else 0
        
        # Check configuration
        validation = config_class.validate()
        
        # Get cache stats
        cache_stats = get_cache_stats()
        
        return jsonify({
            "status": "healthy" if validation['valid'] else "degraded",
            "data_loaded": data_loaded,
            "data_count": data_count,
            "config_valid": validation['valid'],
            "config_warnings": validation['warnings'],
            "version": app.config.get('APP_VERSION', 'unknown'),
            "cache": cache_stats
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route("/api/cache/stats", methods=["GET"])
def cache_stats():
    """Get cache statistics."""
    try:
        stats = get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Error fetching cache stats: {str(e)}")
        abort(500, description="Error fetching cache statistics")


@app.route("/api/cache/clear", methods=["POST"])
def clear_cache():
    """Clear all cache entries."""
    try:
        clear_all_cache()
        app.logger.info("Cache cleared via API")
        return jsonify({"message": "Cache cleared successfully"})
    except Exception as e:
        app.logger.error(f"Error clearing cache: {str(e)}")
        abort(500, description="Error clearing cache")


@app.route("/api/cache/invalidate/<filename>", methods=["POST"])
def invalidate_file_cache(filename):
    """Invalidate cache for a specific file."""
    try:
        # Sanitize filename
        safe_filename = secure_filename(filename)
        if not safe_filename:
            abort(400, description="Invalid filename")
        
        invalidate_cache(safe_filename)
        app.logger.info(f"Cache invalidated for {safe_filename}")
        return jsonify({"message": f"Cache invalidated for {safe_filename}"})
    except Exception as e:
        app.logger.error(f"Error invalidating cache: {str(e)}")
        abort(500, description="Error invalidating cache")


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    app.logger.warning(f"Bad request: {error.description}")
    return jsonify({
        "error": "Bad Request",
        "message": error.description or "Invalid request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found"
    }), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors."""
    app.logger.warning("File upload too large")
    return jsonify({
        "error": "File Too Large",
        "message": f"Maximum file size is {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB"
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    app.logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handle any unexpected errors."""
    app.logger.error(f"Unexpected error: {error}", exc_info=True)
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.sheetjs.com; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://unpkg.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.sheetjs.com;"
    return response


if __name__ == "__main__":
    # Never run with debug=True in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1')
