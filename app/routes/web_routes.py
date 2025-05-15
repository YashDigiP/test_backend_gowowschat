from flask import request, jsonify
from services.web_service import handle_web, handle_web_live, handle_web_lite, embed_site_handler
import traceback

def register_web_routes(app):
    @app.route("/embed-site", methods=["POST"])
    def embed_site():
        return embed_site_handler(request)

    @app.route("/ask-web", methods=["POST"])
    def ask_web():
        return handle_web(request)

    @app.route("/ask-web-live", methods=["POST"])
    def ask_web_live():
        return handle_web_live(request)

    @app.route("/ask-web-lite", methods=["POST"])
    def ask_web_lite():
        try:
            print("🔍 Received request in /ask-web-lite")
            response = handle_web_lite(request)
            print("✅ Successfully processed the request")
            return response
        except Exception as e:
            print("❌ An error occurred:")
            traceback.print_exc()  # This will show the full stack trace in logs
            return jsonify({"error": str(e)}), 500
        # return handle_web_lite(request)
