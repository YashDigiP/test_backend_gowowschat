from flask import request, jsonify, send_file
from services.db_service import handle_db_query, export_to_excel, export_to_pdf, get_all_column_names
from services.pg13_guard import pg13_guard


def register_db_routes(app):
    @app.route("/ask-db", methods=["POST"])
    @pg13_guard
    def ask_db():
        return handle_db_query(request)

    @app.route("/export-excel", methods=["POST"])
    def export_excel():
        return export_to_excel(request)

    @app.route("/export-pdf", methods=["POST"])
    def export_pdf():
        return export_to_pdf(request)

    @app.route("/download/<filename>")
    def download_file(filename):
        try:
            return send_file(f"exports/{filename}", as_attachment=True)
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404

    @app.route("/get-columns", methods=["GET"])
    def get_columns():
        return jsonify(get_all_column_names())
