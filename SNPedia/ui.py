import base64
import io
import logging
import os

from data_crawler import SNPCrawl
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)

logger = logging.getLogger("ui")
logging.basicConfig()
logger.setLevel("DEBUG")

app = Flask(__name__, template_folder="templates")


@app.route("/", methods=["GET", "POST"])
def main():
    print(vars(request.form))
    # if os.path.exists("SNPedia"):
    #     joiner = os.path.join(os.path.curdir, "SNPedia")
    # else:
    #     joiner = os.path.curdir
    # filepath = os.path.join(joiner, "templates", "snp_resource.html")
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
    return jsonify({"results": dfCrawl.rsid_list})


if __name__ == "__main__":
    if os.path.exists("SNPedia"):
        joiner = os.path.join(os.path.curdir, "SNPedia")
    else:
        joiner = os.path.curdir
    filepath = os.path.join(joiner, "data", "results.json")
    snppath = os.path.join(joiner, "data", "personal_snps.json")
    if os.path.isfile(filepath):
        if os.path.isfile(snppath):
            dfCrawl = SNPCrawl(file_path=filepath, snp_path=snppath)
        else:
            dfCrawl = SNPCrawl(file_path=filepath)
    app.run(debug=True)
