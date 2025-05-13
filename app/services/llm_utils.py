# services/llm_utils.py

# PG-13 Safety Prompt for Language Models
PG13_PROMPT = (
    "You are a respectful and helpful assistant. "
    "All your responses must comply with PG-13 guidelines. "
    "Avoid any adult, explicit, violent, abusive, or offensive content.\n\n"
)

def apply_pg13_prompt(user_query: str) -> str:
    """
    Prepend PG-13 safety prompt to user query.
    """
    return PG13_PROMPT + user_query
