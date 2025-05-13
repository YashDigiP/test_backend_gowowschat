# from flask import request
# from services.excel_service import process_excel_upload, process_ask_excel
# from services.pg13_guard import pg13_guard
#
# def register_excel_routes(app):
#     @app.route("/upload-excel", methods=["POST"])
#     def upload_excel():
#         return process_excel_upload(request)
#
#     @app.route("/ask-excel", methods=["POST"])
#     @pg13_guard
#     def ask_excel():
#         return process_ask_excel(request)
