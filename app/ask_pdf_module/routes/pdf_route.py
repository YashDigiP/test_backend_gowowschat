from flask import request
from services.ask_pdf_service import handle_pdf_query

def register_pdf_routes(app):
    @app.route("/ask-pdf", methods=["POST"])
    def ask_pdf():
        return handle_pdf_query(request)