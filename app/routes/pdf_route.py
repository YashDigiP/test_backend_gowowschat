from flask import request, jsonify
from services.pdf_service import process_pdf_upload, process_ask_pdf
from services.pg13_guard import pg13_guard

def register_pdf_routes(app):
    @app.route("/upload-pdf", methods=["POST"])
    def upload_pdf():
        return process_pdf_upload(request)

    @app.route("/ask-pdf", methods=["POST"])
    @pg13_guard
    def ask_pdf():
        return process_ask_pdf(request)
