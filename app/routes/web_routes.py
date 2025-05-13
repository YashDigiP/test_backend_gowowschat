from flask import request
from services.web_service import handle_web, handle_web_live, handle_web_lite, embed_site_handler

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
        return handle_web_lite(request)
