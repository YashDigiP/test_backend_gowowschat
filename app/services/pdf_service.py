import os
import hashlib
from flask import jsonify
from werkzeug.utils import secure_filename
from services.llm_utils import apply_pg13_prompt
from services.llm_config import LLM_MODELS


from langchain_ollama import ChatOllama
import PyPDF2

UPLOAD_FOLDER = "uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
pdf_text_store = {}

def process_pdf_upload(request):
    if "pdf" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["pdf"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            pdf_text_store["latest"] = text
        return jsonify({"message": f"✅ PDF '{filename}' uploaded and processed."})
    except Exception as e:
        return jsonify({"error": f"❌ Failed to read PDF: {str(e)}"}), 500

def process_ask_pdf(request):
    data = request.get_json()
    question = data.get("message")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    if "latest" not in pdf_text_store:
        return jsonify({"error": "No PDF uploaded yet"}), 400
    try:
        model = LLM_MODELS["ask_pdf"]
        print(f"🔍 Using model for Ask PDF: {model}")
        llm = ChatOllama(model=model)
        safe_question = apply_pg13_prompt(question)
        prompt = f"Answer the question based on this PDF:\n\n{pdf_text_store['latest'][:4000]}\n\nQuestion: {safe_question}"
        response = llm.invoke(prompt).content.strip()
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
