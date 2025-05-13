# # routes/kb_routes.py
#
# import os
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt
# from services.kb_service import (
#     list_kb_folders,
#     list_kb_folder,
#     list_specific_kb_folders,   # NEW import
#     save_uploaded_pdf,
#     ask_kb_path,
#     KB_ROOT,
#     read_kb_pdf,
#     list_cached_questions
# )
# from services.pg13_guard import pg13_guard
#
# def register_kb_routes(app):
#     kb_bp = Blueprint("kb", __name__)
#
#     @kb_bp.route("/list-kb-folders", methods=["GET"])
#     @jwt_required()
#     def api_list_kb_folders():
#         jwt_data = get_jwt()
#         allowed_folders = jwt_data.get('allowed_folders', [])
#         print(f"🪪 JWT allowed_folders: {allowed_folders}")  # <<< add this
#         folders = list_specific_kb_folders(allowed_folders)
#         return jsonify(folders)
#
#     @kb_bp.route("/list-kb-folder", methods=["GET"])
#     @jwt_required()
#     def api_list_kb_folder():
#         folder = request.args.get("folder")
#         jwt_data = get_jwt()
#         allowed_folders = jwt_data.get('allowed_folders', [])
#
#         if not folder:
#             return jsonify({"error": "No folder specified"}), 400
#
#         path = os.path.join(KB_ROOT, folder)
#         if not os.path.exists(path):
#             return jsonify({"error": "Folder not found"}), 404
#
#         contents = []
#
#         for f in os.listdir(path):
#             full_path = os.path.join(path, f)
#
#             if os.path.isdir(full_path):
#                 full_folder_path = f"{folder}/{f}"
#                 # ✅ Only allow subfolder if user has access
#                 if "*" in allowed_folders or full_folder_path in allowed_folders:
#                     pdf_count = len([
#                         pdf for pdf in os.listdir(full_path)
#                         if os.path.isfile(os.path.join(full_path, pdf)) and pdf.endswith(".pdf")
#                     ])
#                     contents.append({
#                         "type": "folder",
#                         "name": f,
#                         "pdf_count": pdf_count
#                     })
#
#             elif f.endswith(".pdf"):
#                 full_file_path = f"{folder}/{f}"
#                 if "*" in allowed_folders or folder in allowed_folders or full_file_path in allowed_folders:
#                     contents.append({
#                         "type": "file",
#                         "name": f
#                     })
#
#         return jsonify(contents)
#
#     @kb_bp.route("/upload-kb-pdf", methods=["POST"])
#     @jwt_required()
#     def api_upload_kb_pdf():
#         folder = request.form.get("folder")
#         subfolder = request.form.get("subfolder")
#         file = request.files.get("file")
#
#         if not folder or not subfolder or not file:
#             return jsonify({"error": "Missing folder, subfolder, or file"}), 400
#
#         safe_folder, safe_subfolder, filename = save_uploaded_pdf(folder, subfolder, file)
#         return jsonify({"message": f"✅ Uploaded {filename} to {safe_folder}/{safe_subfolder}"})
#
#     @kb_bp.route("/ask-kb", methods=["POST"])
#     @jwt_required()
#     @pg13_guard
#     def api_ask_kb():
#         data = request.get_json()
#         path = data.get("path")
#         query = data.get("message")
#
#         if not path or not query:
#             return jsonify({"error": "Missing path or message"}), 400
#
#         try:
#             answer = ask_kb_path(path, query)
#             return jsonify({"response": answer})
#         except FileNotFoundError as fe:
#             return jsonify({"error": str(fe)}), 404
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#
#     @kb_bp.route("/read-kb-pdf", methods=["POST"])
#     @jwt_required()
#     def read_kb_pdf_route():
#         data = request.get_json()
#         path = data.get("path")
#         text = read_kb_pdf(path)
#         if text:
#             return jsonify({"text": text})
#         else:
#             return jsonify({"error": "Failed to read PDF"}), 400
#
#
#     @kb_bp.route("/list-kb-faq", methods=["GET"])
#     @jwt_required()
#     def list_kb_faq():
#         """
#         API endpoint to return list of cached questions for a given PDF.
#         Expects query parameter: pdf_path
#         """
#         pdf_path = request.args.get("pdf_path")
#         if not pdf_path:
#             return jsonify({"error": "Missing pdf_path"}), 400
#
#         try:
#             from services.kb_service import list_cached_questions
#             questions = list_cached_questions(pdf_path)
#             return jsonify({"questions": questions})
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#
#
#
#     app.register_blueprint(kb_bp)
#
#
#
