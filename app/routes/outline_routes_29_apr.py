# # routes/outline_routes.py
#
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required
# from services.outline_service import generate_outline
# from flask import send_file
# from services.outline_service import generate_outline, export_outline_to_pptx
#
# def register_outline_routes(app):
#     outline_bp = Blueprint("outline", __name__)
#
#     @outline_bp.route("/generate-outline", methods=["POST"])
#     @jwt_required()
#     def api_generate_outline():
#         data = request.get_json()
#         text = data.get("text")
#
#         if not text:
#             return jsonify({"error": "Missing text input"}), 400
#
#         try:
#             outline = generate_outline(text)
#             return jsonify({"outline": outline})
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#
#     app.register_blueprint(outline_bp)
#
# @outline_bp.route("/export-outline-ppt", methods=["POST"])
# @jwt_required()
# def api_export_outline_ppt():
#     data = request.get_json()
#     text = data.get("text")
#
#     if not text:
#         return jsonify({"error": "Missing text input"}), 400
#
#     try:
#         outline = generate_outline(text)
#         ppt_path = export_outline_to_pptx(outline)
#         return send_file(ppt_path, as_attachment=True)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500