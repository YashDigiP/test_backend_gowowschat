# from flask import Blueprint, jsonify, request, send_file
# from flask_jwt_extended import jwt_required, get_jwt
# from services.curated_service import fetch_curated_insights
# from io import BytesIO
# from xhtml2pdf import pisa
# import html  # ✅ NEW
# import pandas as pd
# from openpyxl import Workbook
#
#
#
# def register_curated_routes(app):
#     curated_bp = Blueprint("curated", __name__)
#
#     @curated_bp.route("/curated-insights", methods=["GET"])
#     @jwt_required()
#     def get_curated():
#         jwt_data = get_jwt()
#         user_role = jwt_data.get("role", "")
#         user_company = jwt_data.get("company", "")
#         return fetch_curated_insights(user_role, user_company)
#
#     @curated_bp.route("/export-outline-pdf", methods=["POST"])
#     @jwt_required()
#     def export_outline_pdf():
#         data = request.get_json()
#         outline_html = html.unescape(data.get("outline", ""))  # ✅ FIXED
#
#         if not outline_html:
#             return {"error": "Missing outline content"}, 400
#
#         result = BytesIO()
#         pisa.CreatePDF(src=outline_html, dest=result)
#         result.seek(0)
#
#         return send_file(
#             result,
#             mimetype="application/pdf",
#             as_attachment=True,
#             download_name="curated_insights.pdf"
#         )
#
#
#     @curated_bp.route("/export-outline-excel", methods=["GET"])
#     @jwt_required()
#     def export_outline_excel():
#         jwt_data = get_jwt()
#         user_role = jwt_data.get("role", "")
#         user_company = jwt_data.get("company", "")
#
#         insights_response = fetch_curated_insights(user_role, user_company)
#         insights = insights_response.get_json()
#
#         output = BytesIO()
#         writer = pd.ExcelWriter(output, engine="openpyxl")
#
#         for insight in insights:
#             title = insight.get("title", "Untitled")[:31]  # Excel sheet name max = 31 chars
#             columns = insight.get("columns", [])
#             rows = insight.get("rows", [])
#
#             if not columns or not rows:
#                 continue
#
#             df = pd.DataFrame(rows, columns=columns)
#             df.to_excel(writer, sheet_name=title, index=False)
#
#         writer.close()
#         output.seek(0)
#
#         return send_file(
#             output,
#             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             as_attachment=True,
#             download_name="curated_insights.xlsx"
#         )
#
#
#     app.register_blueprint(curated_bp)
