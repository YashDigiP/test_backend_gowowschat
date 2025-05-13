from flask import request, jsonify
from langchain_ollama import ChatOllama
from services.llm_utils import apply_pg13_prompt
from services.llm_config import LLM_MODELS


# Track active tasks
active_tasks = {}

def handle_chat(request, use_gemma=False):
    data = request.get_json()
    message = data.get("message")
    task_id = data.get("task_id", "default")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    active_tasks[task_id] = True

    try:
        model = LLM_MODELS["normal_chat"]
        print(f"🔍 Using model for Normal Chat: {model}")
        llm = ChatOllama(model=model)
        safe_message = apply_pg13_prompt(message)
        response = llm.invoke(safe_message).content.strip()

        if not active_tasks.get(task_id, True):
            return jsonify({"error": "⛔ Stopped by user."})
        
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        active_tasks.pop(task_id, None)



def handle_prompt(request):
    data = request.get_json()
    saathi_reply = data.get("text", "")
    if not saathi_reply:
        return jsonify({"prompts": []})

    try:
        llm = ChatOllama(model=LLM_MODELS["normal_chat"])
        prompt = f"Based on this response, suggest 3 relevant follow-up user questions as a list:\n\n'{saathi_reply}'"
        print(prompt)
        result = llm.invoke(prompt).content.strip()
        print(3)
        suggestions = [line.strip("-• ").strip() for line in result.splitlines() if line.strip()]
        print(4)

        return jsonify({"prompts": suggestions[:3]})

    except Exception as e:
        print(e)
        return jsonify({"prompts": [], "error": str(e)}), 500
