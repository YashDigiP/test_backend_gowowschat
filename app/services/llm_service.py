import os
from flask import request, jsonify, stream_with_context, Response
from langchain_ollama import ChatOllama
from services.llm_utils import apply_pg13_prompt
from services.llm_config import LLM_MODELS
import json
import requests


# Track active tasks
active_tasks = {}

Base_url = os.getenv("BASE_URL")
OLLAMA_VM_URL = f"{Base_url}/api/chat"

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
        llm = ChatOllama(model=model , base_url= Base_url)
        safe_message = apply_pg13_prompt(message)
        response = llm.invoke(safe_message).content.strip()

        if not active_tasks.get(task_id, True):
            return jsonify({"error": "⛔ Stopped by user."})

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        active_tasks.pop(task_id, None)


def stream_chat_response(safe_message, task_id):
    active_tasks[task_id] = True  # Set the task as active
    # print(task_id)
    payload = {
        "model": LLM_MODELS["normal_chat"],
        "messages": [{"role": "user", "content": safe_message}],
        "stream": True,
    }

    with requests.post(OLLAMA_VM_URL, json=payload, stream=True) as resp:
        for line in resp.iter_lines():
            if not active_tasks.get(task_id, True):
                break

            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue

    active_tasks.pop(task_id, None)

def handle_prompt(request):
    data = request.get_json()
    saathi_reply = data.get("text", "")
    if not saathi_reply:
        return jsonify({"prompts": []})

    try:
        llm = ChatOllama(model=LLM_MODELS["normal_chat"], base_url=Base_url)
        prompt = f"Based on this response, suggest 3 relevant follow-up user questions as a list:\n\n'{saathi_reply}'"
        print(prompt)
        result = llm.invoke(prompt).content.strip()
        suggestions = [line.strip("-• ").strip() for line in result.splitlines() if line.strip()]

        return jsonify({"prompts": suggestions[:3]})

    except Exception as e:
        print(e)
        return jsonify({"prompts": [], "error": str(e)}), 500
