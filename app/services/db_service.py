import re
import os
import traceback
from io import BytesIO
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from fpdf import FPDF
from flask import jsonify, send_file
from langchain_ollama import ChatOllama
from services.llm_utils import apply_pg13_prompt
from services.llm_config import LLM_MODELS


DB_URI = "postgresql://postgres:admin@localhost:5432/mfdb"
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)
engine = create_engine(DB_URI)
Base_url = os.getenv("BASE_URL")

similar_map = {
    "clients": "client",
    "tasks": "tasks",
    "clients_audit": "client_audit",
    "tasks_audit": "tasks_audit"
}

def handle_db_query(request):
    data = request.get_json()
    question = data.get("message")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    system_prompt = """
    You are a senior PostgreSQL assistant. Generate only SQL queries.
    Always follow these rules:
    1. Only generate SQL — no explanations, no comments.
    2. Never use INSERT, UPDATE, DELETE, DROP or ALTER.
    3. Use only the table and column names from the provided schema hints.
    4. If a plural table like 'clients' is mentioned, map it to singular like 'client'.
    5. Use LEFT OUTER JOIN when combining multiple tables.
    6. If both 'tasks' and 'client' tables are used, always join via: tasks.client_id = client.client_id.
    7. If asked to count, use COUNT(*). Use GROUP BY when appropriate.
    8. Always qualify columns when multiple tables are used, e.g., tasks.name.
    9. Prefer COALESCE() or NULLIF() for null-handling, if needed.
    10. Never use "SELECT *". Always specify relevant columns, unless it's explicitly asked.
    11. Never use column names that aren't present in the schema — validate using 'information_schema.columns'.
    """

    try:
        safe_question = apply_pg13_prompt(question)
        prompt = f"{system_prompt}\n\nQuestion: {safe_question}"
        model = LLM_MODELS["ask_db"]
        print(f"🧠 Using model for Ask DB: {model}")
        llm = ChatOllama(model=model, base_url=Base_url)
        raw_response = llm.invoke(prompt)
        print("🧠 Raw LLM SQL:\n", raw_response.content if hasattr(raw_response, "content") else str(raw_response))
        response = raw_response.content.strip() if hasattr(raw_response, "content") else str(raw_response)

        for wrong, correct in similar_map.items():
            response = re.sub(rf"\b{wrong}\b", correct, response)

        cleaned_sql = response.strip().removeprefix("```sql").removesuffix("```").strip()
        print("🧾 Final SQL to be executed:\n", cleaned_sql)

        tables_in_query = set(re.findall(r"\b(?:from|join)\s+(\w+)", cleaned_sql, re.IGNORECASE))
        valid_tables = get_valid_table_names()
        cte_names = get_cte_names(cleaned_sql)

        for table in tables_in_query:
            if table.lower() not in valid_tables and table.lower() not in cte_names:
                return jsonify({ "error": f"❌ Table '{table}' not found. Available: {', '.join(valid_tables)}" }), 400

        response_payload = {}
        statements = [s.strip() for s in cleaned_sql.split(";") if s.strip()]
        for stmt in statements:
            if not stmt.lower().startswith("select"):
                continue
            with engine.connect() as conn:
                try:
                    result = conn.execute(text(stmt))
                    rows = [{key: value for key, value in zip(result.keys(), row)} for row in result.fetchall()]
                    response_payload["rows"] = rows

                    if len(rows) > 0 and len(rows[0]) == 2:
                        x, y = zip(*[(row[k], row[v]) for row in rows for k, v in [list(row.keys())[:2]]])
                        if all(isinstance(val, (int, float)) for val in y):
                            chart_type = "bar"
                            if "pie" in question.lower():
                                chart_type = "pie"
                            elif "donut" in question.lower():
                                chart_type = "doughnut"
                            response_payload["chart"] = {
                                "type": chart_type, "x": x, "y": y,
                                "x_label": list(rows[0].keys())[0],
                                "y_label": list(rows[0].keys())[1]
                            }
                            total = sum(y)
                            top_label = x[y.index(max(y))]
                            response_payload["summary"] = f"📊 Total: {total}. Highest: '{top_label}' with {max(y)}."

                except Exception as e:
                    print("⚠️ SQL execution failed, falling back. Error:", str(e))
                    conn.rollback()
                    fallback_result = conn.execute(text("SELECT * FROM tasks"))
                    fallback_rows = [
                        {key: value for key, value in zip(fallback_result.keys(), row)}
                        for row in fallback_result.fetchall()
                    ]
                    response_payload = {
                        "rows": fallback_rows,
                        "warning": f"Original query failed: {str(e)}. Showing fallback from tasks."
                    }
        return jsonify(response_payload)

    except Exception as e:
        print("[Traceback]:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def get_valid_table_names():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        return {row[0].lower() for row in result.fetchall()}

def get_cte_names(sql):
    return set(re.findall(r'\bwith\s+([a-zA-Z0-9_]+)\s+as\s*\(', sql, re.IGNORECASE))

def get_all_column_names():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public'"))
        table_cols = {}
        for table, col in result.fetchall():
            table_cols.setdefault(table, set()).add(col)
        return table_cols

# export_to_pdf and export_to_excel stay unchanged

def export_to_excel():
    df = pd.read_sql("SELECT * FROM tasks", engine)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="export.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def export_to_pdf():
    df = pd.read_sql("SELECT * FROM tasks", engine)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for i, row in df.iterrows():
        line = ", ".join([f"{col}: {val}" for col, val in row.items()])
        pdf.cell(200, 10, txt=line, ln=True)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="export.pdf", mimetype="application/pdf")
