# services/curated_service.py

from sqlalchemy import text
from flask import jsonify
from services.db_service import engine
from services.llm_config import LLM_MODELS

def fetch_curated_insights(user_role, user_company):
    try:
        model = LLM_MODELS["generate_insights"]
        print(f"📊 Using model for Generate Insights: {model}")
        with engine.connect() as conn:
            query = """
                SELECT * FROM curated_insights
                WHERE 
                    (roles IS NULL OR :role = ANY(roles)) AND
                    (company IS NULL OR :company = ANY(company))
                ORDER BY display_order
            """
            result = conn.execute(text(query), {"role": user_role, "company": user_company})
            insights = result.fetchall()

            response = []

            for row in insights:
                (
                    _id, insight_id, title, description, sql_query,
                    insight_type, chart_type, roles, companies, display_order
                ) = row

                try:
                    query_result = conn.execute(text(sql_query))
                    records = [dict(zip(query_result.keys(), r)) for r in query_result.fetchall()]
                    columns = list(query_result.keys())

                    response.append({
                        "id": insight_id,
                        "type": insight_type,
                        "chart_type": chart_type,  # ✅ ADD THIS LINE
                        "title": title,
                        "description": description,
                        "columns": columns,
                        "rows": records
                    })
                except Exception as e:
                    response.append({
                        "id": insight_id,
                        "type": insight_type,
                        "title": title,
                        "description": f"{description} (⚠️ SQL Error: {str(e)})",
                        "columns": [],
                        "rows": []
                    })

            return jsonify(response)

    except Exception as e:
        print("❌ Error loading curated insights:", str(e))
        return jsonify({"error": str(e)}), 500
