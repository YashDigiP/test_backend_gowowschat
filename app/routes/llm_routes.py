from flask import request, jsonify, Response, stream_with_context
from services.llm_service import handle_prompt, stream_chat_response
from services.pg13_guard import pg13_guard
from services.llm_utils import apply_pg13_prompt


def register_llm_routes(app):
    # @app.route("/chat", methods=["POST", "OPTIONS"])
    # @pg13_guard
    # def chat():
    #     if request.method == "OPTIONS":
    #         return '', 200
    #     return handle_chat(request)

    @app.route("/generate-prompts", methods=["POST", "OPTIONS"])
    def generate_prompts():
        if request.method == "OPTIONS":
            return '', 200
        return handle_prompt(request)

    @app.route("/chat", methods=["POST", "OPTIONS"])
    def handle_chat():
        if request.method == "OPTIONS":
            # Respond to CORS preflight
            return '', 200
        data = request.get_json()
        message = data.get("message")
        task_id = data.get("task_id")
        if not message:
            return jsonify({"error": "No message provided"}), 400

        safe_message = apply_pg13_prompt(message)

        return Response(
            stream_with_context(stream_chat_response(safe_message, task_id)),
            content_type='text/event-stream'
        )