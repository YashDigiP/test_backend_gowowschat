# services/kb_service.py

import hashlib
import os
from flask import jsonify
from langchain_community.vectorstores import FAISS
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.services.kb_service import base_url

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KB_ROOT = os.path.join(BASE_DIR, "kb")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_stores")
Base_url = os.getenv("BASE_URL")

os.makedirs(KB_ROOT, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

embedding_model = OllamaEmbeddings(model="mistral", base_url=Base_url)

def list_kb_folders():
    kb_list = []
    for folder in os.listdir(KB_ROOT):
        folder_path = os.path.join(KB_ROOT, folder)
        if os.path.isdir(folder_path):
            subfolders = []
            for sub in os.listdir(folder_path):
                sub_path = os.path.join(folder_path, sub)
                if os.path.isdir(sub_path):
                    pdfs = [f for f in os.listdir(sub_path) if f.endswith(".pdf")]
                    subfolders.append({
                        "name": sub,
                        "pdfs": pdfs,
                        "pdf_count": len(pdfs)
                    })
            kb_list.append({"folder": folder, "subfolders": subfolders})
    return kb_list

def list_kb_folder(folder, subfolder):
    full_path = os.path.join(KB_ROOT, folder, subfolder)
    if not os.path.exists(full_path):
        return None
    return [f for f in os.listdir(full_path) if f.endswith(".pdf")]

def save_uploaded_pdf(folder, subfolder, file):
    from werkzeug.utils import secure_filename
    safe_folder = secure_filename(folder)
    safe_subfolder = secure_filename(subfolder)
    upload_path = os.path.join(KB_ROOT, safe_folder, safe_subfolder)
    os.makedirs(upload_path, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    return safe_folder, safe_subfolder, filename

def ask_kb_path(path, query):
    if not path or not query:
        return "Missing path or query"

    parts = path.split("/")
    if len(parts) != 3:
        raise FileNotFoundError("Invalid path format. Expected 'folder/subfolder/pdf'")

    folder, subfolder, pdf = parts
    full_path = os.path.join(KB_ROOT, folder, subfolder, pdf)

    if not os.path.exists(full_path):
        raise FileNotFoundError("PDF not found")

    path_hash = hashlib.sha256(path.encode()).hexdigest()
    vector_store_path = os.path.join(VECTOR_STORE_DIR, path_hash)

    if os.path.exists(vector_store_path):
        db = FAISS.load_local(vector_store_path, embeddings=embedding_model, allow_dangerous_deserialization=True)
    else:
        loader = PyPDFLoader(full_path)
        pages = loader.load_and_split()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(pages)
        db = FAISS.from_documents(docs, embedding_model)
        db.save_local(vector_store_path)

    relevant_docs = db.similarity_search(query)
    chain = load_qa_chain(Ollama(model="mistral", base_url=Base_url), chain_type="stuff")
    return chain.run(input_documents=relevant_docs, question=query)

def read_kb_pdf(path):
    parts = path.split("/")
    if len(parts) != 3:
        return None

    folder, subfolder, pdf = parts
    full_path = os.path.join(KB_ROOT, folder, subfolder, pdf)

    if not os.path.exists(full_path):
        return None

    loader = PyPDFLoader(full_path)
    docs = loader.load()
    full_text = "\n".join([page.page_content for page in docs])
    return full_text
