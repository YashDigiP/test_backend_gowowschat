# routes/kb_routes.py

import os
from flask import Blueprint, request, jsonify
from services.kb_service import (
    list_kb_folders,
    list_kb_folder,
    save_uploaded_pdf,
    ask_kb_path,
    KB_ROOT,
    read_kb_pdf
)
from services.pg13_guard import pg13_guard

def register_kb_routes(app):
    kb_bp = Blueprint("kb", __name__)

    @kb_bp.route("/list-kb-folders", methods=["GET"])
    def api_list_kb_folders():
        return jsonify(list_kb_folders())

    @kb_bp.route("/list-kb-folder", methods=["GET"])
    def api_list_kb_folder():
        folder = request.args.get("folder")
        subfolder = request.args.get("subfolder")

        if not folder:
            return jsonify({"error": "Missing folder"}), 400

        if subfolder:
            pdfs = list_kb_folder(folder, subfolder)
            if pdfs is None:
                return jsonify({"error": "Folder not found"}), 404
            return jsonify([{"name": f, "is_folder": False} for f in pdfs])

        path = os.path.join(KB_ROOT, folder)
        if not os.path.exists(path):
            return jsonify({"error": "Folder not found"}), 404

        result = []
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if os.path.isdir(full):
                pdf_count = sum(1 for f in os.listdir(full) if f.endswith(".pdf"))
                result.append({ "name": name, "is_folder": True, "pdf_count": pdf_count })
            elif name.endswith(".pdf"):
                result.append({ "name": name, "is_folder": False })

        return jsonify(result)

    @kb_bp.route("/upload-kb-pdf", methods=["POST"])
    def api_upload_kb_pdf():
        folder = request.form.get("folder")
        subfolder = request.form.get("subfolder")
        file = request.files.get("file")

        if not folder or not subfolder or not file:
            return jsonify({"error": "Missing folder, subfolder, or file"}), 400

        safe_folder, safe_subfolder, filename = save_uploaded_pdf(folder, subfolder, file)
        return jsonify({"message": f"✅ Uploaded {filename} to {safe_folder}/{safe_subfolder}"})


    @kb_bp.route("/ask-kb", methods=["POST"])
    @pg13_guard
    def api_ask_kb():
        data = request.get_json()
        path = data.get("path")
        query = data.get("message")

        if not path or not query:
            return jsonify({"error": "Missing path or message"}), 400

        try:
            answer = ask_kb_path(path, query)
            return jsonify({"response": answer})
        except FileNotFoundError as fe:
            return jsonify({"error": str(fe)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @kb_bp.route("/read-kb-pdf", methods=["POST"])
    def read_kb_pdf_route():
        data = request.get_json()
        path = data.get("path")
        text = read_kb_pdf(path)
        if text:
            return jsonify({"text": text})
        else:
            return jsonify({"error": "Failed to read PDF"}), 400


    app.register_blueprint(kb_bp)
