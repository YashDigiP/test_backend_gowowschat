from .llm_routes import register_llm_routes
# from .db_routes import register_db_routes
# from .kb_routes import register_kb_routes
# from .export_routes import register_export_routes
# from .web_routes import register_web_routes
# from .pdf_route import register_pdf_routes
from .auth_routes import register_auth_routes  
# from .outline_routes import register_outline_routes
# from .feedback_routes import register_feedback_routes
# from .excel_routes import register_excel_routes
# from .curated_routes import register_curated_routes
from flask import send_file, abort
import os

def register_routes(app):
    register_llm_routes(app)
    # register_pdf_routes(app)
    # register_db_routes(app)
    # register_kb_routes(app)
    # register_export_routes(app)
    # register_web_routes(app)
    register_auth_routes(app) 
    # register_outline_routes(app)
    # register_feedback_routes(app)
    # register_excel_routes(app)
    # register_curated_routes(app)

    app.static_folder = 'kb'

    # @app.route("/preview/<path:folder>/<path:subfolder>/<path:filename>", methods=["GET"])
    # def preview_pdf(folder, subfolder, filename):
    #     kb_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kb"))
    #     print(f"📁 Serving static files from base folder: {kb_base}")
    #     print(f"📥 Requested path: /preview/{folder}/{subfolder}/{filename}")
    #
    #     if not filename.endswith(".pdf"):
    #         possible_path = os.path.join(kb_base, folder, subfolder, f"{filename}.pdf")
    #         print(f"🔍 Trying with .pdf: {possible_path}")
    #         if os.path.exists(possible_path):
    #             filename = f"{filename}.pdf"
    #         else:
    #             possible_path = os.path.join(kb_base, folder, subfolder, filename)
    #             print(f"🔍 Trying without extension: {possible_path}")
    #             if not os.path.exists(possible_path):
    #                 print("❌ File not found even without extension.")
    #                 return abort(404)
    #     else:
    #         possible_path = os.path.join(kb_base, folder, subfolder, filename)
    #         print(f"🔍 Using exact filename: {possible_path}")
    #         if not os.path.exists(possible_path):
    #             print("❌ File with .pdf extension not found.")
    #             return abort(404)
    #
    #     print(f"✅ Sending file: {possible_path}")
    #     return send_file(
    #         possible_path,
    #         mimetype='application/pdf',
    #         download_name=filename,
    #         as_attachment=False
    #     )

