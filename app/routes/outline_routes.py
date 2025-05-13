# # routes/outline_routes.py
#
# from flask import Blueprint, request, jsonify, send_file
# from flask_jwt_extended import jwt_required
# from services.outline_service import generate_outline, export_outline_to_pptx, export_outline_to_pdf
# from flask import Blueprint, request, jsonify, send_file
# from services.outline_service import generate_outline, export_outline_to_pptx
#
# outline_bp = Blueprint("outline", __name__)
#
#
#
# @outline_bp.route("/generate-outline", methods=["POST"])
# @jwt_required()
# def generate_outline_route():
#     """
#     Accepts plain text from the frontend and returns a formatted outline.
#     """
#     data = request.get_json()
#     text = data.get("text")
#
#     if not text:
#         return jsonify({"error": "Missing input text"}), 400
#
#     outline = generate_outline(text)
#     return jsonify({"outline": outline})
#
#
#
#
# # ✅ NEW endpoint for PPT export
#
#
# @outline_bp.route("/export-outline-ppt", methods=["POST"])
# def export_outline_ppt():
#     try:
#         data = request.get_json()
#         outline_text = data.get("outline")
#
#         if not outline_text:
#             return jsonify({"error": "Missing outline text"}), 400
#
#         print("🔍 Request received to /export-outline-ppt")
#         print(f"📦 Raw JSON: {data}")
#
#         ppt_file_path = export_outline_to_pptx(outline_text)
#
#         # ✅ Correct way to return temporary file
#         return send_file(
#             ppt_file_path,
#             as_attachment=True,
#             download_name="outline_output.pptx",
#             mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
#         )
#
#     except Exception as e:
#         print("❌ Error in export-outline-ppt:", e)
#         return jsonify({"error": str(e)}), 500
#
# @outline_bp.route("/export-outline-pdf", methods=["POST"])
# def export_outline_pdf():
#     data = request.get_json()
#     outline_text = data.get("outline", "")
#
#     if not outline_text:
#         return jsonify({"error": "Missing outline text"}), 400
#
#     try:
#         pdf_buffer = export_outline_to_pdf(outline_text)
#         return send_file(
#             pdf_buffer,
#             mimetype='application/pdf',
#             as_attachment=True,
#             download_name="outline_output.pdf"
#         )
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
#
# # ✅ Register blueprint
# def register_outline_routes(app):
#     app.register_blueprint(outline_bp)
