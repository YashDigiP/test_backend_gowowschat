import os

LLM_MODELS = {
    "normal_chat": os.environ["NORMAL_CHAT_MODEL"],
    "ask_pdf": os.environ["ASK_PDF_MODEL"],
    "ask_kb": os.environ["ASK_KB_MODEL"],
    "ask_db": os.environ["ASK_DB_MODEL"],
    "ask_website": os.environ["ASK_WEBSITE_MODEL"],
    "generate_insights": os.environ["GENERATE_INSIGHTS_MODEL"],
}
