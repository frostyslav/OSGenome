import base64
import io

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from utils import load_from_file

app = Flask(__name__, template_folder="templates")


@app.route("/", methods=["GET", "POST"])
def main():
    return render_template("snp_resource.html")


@app.route("/excel", methods=["GET", "POST"])
def create_file():
    content = request.form

    filename = content["fileName"]
    filecontents = content["base64"]
    filecontents = base64.b64decode(filecontents)

    bytesIO = io.BytesIO()
    bytesIO.write(filecontents)
    bytesIO.seek(0)

    return send_file(bytesIO, attachment_filename=filename, as_attachment=True)


@app.route("/images/<path:path>")
def send_image(path):
    return send_from_directory("images", path)


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


@app.route("/api/rsids", methods=["GET"])
def get_types():
    return jsonify({"results": results})


@app.route("/api/statistics", methods=["GET"])
def statistics():
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


if __name__ == "__main__":
    results = load_from_file("result_table.json")
    app.run(debug=False)
else:
    results = load_from_file("result_table.json")
