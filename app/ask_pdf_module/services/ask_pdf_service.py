import os
from flask import request, jsonify
from PyPDF2 import PdfReader

def extract_pdf_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"❌ Error reading PDF: {e}"

def handle_pdf_query(req):
    data = req.get_json()
    pdf_path = data.get("pdf_path")
    question = data.get("question")

    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({"error": f"❌ PDF file not found: {pdf_path}"}), 400

    text = extract_pdf_text(pdf_path)
    response = f"🤖 Extracted text from PDF. Here's a sample:\n\n{text[:500]}...\n\n(Answering '{question}' will come later)"

    return jsonify({"answer": response})