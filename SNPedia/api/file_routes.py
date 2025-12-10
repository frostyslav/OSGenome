"""File handling routes for SNPedia application."""

from flask import Blueprint, abort, request, send_file

from SNPedia.core.logger import logger
from SNPedia.services.file_service import FileService


def create_file_blueprint() -> Blueprint:
    """Create and configure the file handling blueprint."""
    files = Blueprint("files", __name__)

    file_service = FileService()

    @files.route("/excel", methods=["POST"])
    def create_excel_file():
        """Generate Excel file from base64 encoded data."""
        try:
            # Validate required fields
            if "fileName" not in request.form or "base64" not in request.form:
                abort(400, description="Missing required fields")

            filename = request.form["fileName"]
            base64_content = request.form["base64"]

            # Validate and decode content
            file_content = file_service.validate_base64_content(base64_content)
            if file_content is None:
                abort(400, description="Invalid or oversized file content")

            # Create Excel file
            excel_file = file_service.create_excel_file(filename, file_content)
            if excel_file is None:
                abort(400, description="Invalid filename or file type")

            return send_file(
                excel_file,
                download_name=filename,
                as_attachment=True,
                mimetype=file_service.get_excel_mimetype(),
            )

        except Exception as e:
            logger.error(f"Error creating Excel file: {str(e)}")
            abort(500, description="Error generating file")

    return files
