import os
import pandas as pd
import duckdb
from flask import jsonify
from werkzeug.utils import secure_filename
from services.llm_utils import apply_pg13_prompt
from langchain_ollama import ChatOllama
from langchain.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile

Base_url = os.getenv("BASE_URL")

# 🧠 In-memory stores
excel_data_store = {}
duckdb_connection = duckdb.connect(database=':memory:')
vectorstore = None

def process_excel_upload(request):
    if "excel" not in request.files:
        return jsonify({"error": "No Excel file uploaded"}), 400

    file = request.files["excel"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        # ✅ Read all sheets into Pandas and DuckDB
        all_sheets = pd.read_excel(file, sheet_name=None)
        excel_data_store["latest"] = all_sheets

        for sheet_name, df in all_sheets.items():
            clean_df = df.dropna(how="all")
            duckdb_connection.register(sheet_name, clean_df)

        # 🧠 Build vectorstore from text version of data
        global vectorstore
        text_chunks = []
        for name, df in all_sheets.items():
            df_str = df.astype(str).to_string()
            text_chunks.append(f"Sheet: {name}\n{df_str}")

        full_text = "\n\n".join(text_chunks)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.create_documents([full_text])
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=Base_url)
        vectorstore = FAISS.from_documents(docs, embeddings)

        return jsonify({"message": f"✅ Excel uploaded and processed successfully."})
    except Exception as e:
        return jsonify({"error": f"❌ Failed to read Excel: {str(e)}"}), 500

def process_ask_excel(request):
    data = request.get_json()
    question = data.get("message")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    if "latest" not in excel_data_store:
        return jsonify({"error": "No Excel uploaded yet"}), 400

    try:
        safe_question = apply_pg13_prompt(question)

        # 👀 Attempt DuckDB execution using LLM-generated SQL
        try:
            table_list = list(excel_data_store["latest"].keys())
            table_defs = ", ".join([f"{t}" for t in table_list])

            sql_prompt = f"""
You are a SQL Analyst helping users query DuckDB in-memory tables based on Excel sheets.

Tables Available: {table_defs}
User Question: {safe_question}

Write a concise SQL query that answers this question using DuckDB syntax. Only include one SQL statement and no explanations.
"""
            llm = ChatOllama(model="mistral", base_url=Base_url)
            sql_query = llm.invoke(sql_prompt).content.strip()

            duck_result = duckdb_connection.execute(sql_query).fetchdf()
            return jsonify({"response": f"💡 Interpreted SQL:\n```sql\n{sql_query}\n```\n\n📊 Result:\n{duck_result.to_markdown(index=False)}"})
        
        except Exception as e:
            print("❌ DuckDB execution failed:", e)

            # 🤖 Fall back to vectorstore if SQL fails
            if not vectorstore:
                return jsonify({"error": "No vector store available"}), 500

            relevant_docs = vectorstore.similarity_search(safe_question, k=4)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])

            prompt = f"""
You are a highly intelligent Excel Analyst working for a team of users ranging from data scientists to complete beginners.

Task:
- Answer the user's question strictly based on the Excel content provided below.
- Do NOT assume external data or user knowledge.
- Provide exact numbers, totals, comparisons, etc.
- Do NOT explain Excel formulas or steps unless explicitly asked.

Excel Data (semantic excerpts):
{context}

User Question:
{safe_question}

Answer:
"""
            llm = ChatOllama(model="mistral", base_url=Base_url)
            response = llm.invoke(prompt).content.strip()
            return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
