from flask import request, jsonify
from services.llm_service import handle_chat, handle_prompt
from services.pg13_guard import pg13_guard


def register_llm_routes(app):
    @app.route("/chat", methods=["POST", "OPTIONS"])
    @pg13_guard
    def chat():
        if request.method == "OPTIONS":
            return '', 200
        return handle_chat(request)

    @app.route("/generate-prompts", methods=["POST", "OPTIONS"])
    def generate_prompts():
        if request.method == "OPTIONS":
            return '', 200
        return handle_prompt(request)
