# services/pg13_guard.py

import re
from functools import wraps
from flask import jsonify, request

# Basic list of banned words/phrases for PG-13 enforcement
BANNED_WORDS = [
    "sex", "rape", "nude", "drugs", "kill", "murder", "violence", "assault", "explicit",
    "porn", "weapon", "abuse"
]

def is_safe_text(text: str) -> bool:
    """
    Return False if text contains any banned PG-13 content.
    """
    for word in BANNED_WORDS:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return False
    return True

def pg13_guard(func):
    """
    Flask route decorator that checks the LLM response for PG-13 safety violations.
    If unsafe, replaces the output with a warning message.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ✅ Skip safety check for OPTIONS (preflight) requests
        if request.method == "OPTIONS":
            return '', 200

        result = func(*args, **kwargs)

        try:
            response_json = result.get_json() if hasattr(result, "get_json") else result[0].get_json()
            response_text = response_json.get("response", "")

            if not is_safe_text(response_text):
                return jsonify({
                    "response": "⚠️ This response was blocked to comply with PG-13 safety guidelines."
                })

        except Exception as e:
            return jsonify({"error": f"PG-13 guard failed: {str(e)}"}), 500

        return result
    return wrapper
