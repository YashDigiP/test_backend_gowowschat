# services/kb_service.py

import hashlib
import os
from flask import jsonify
from datetime import datetime
from pymongo import MongoClient
from langchain_community.vectorstores import FAISS
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

# === Paths ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
KB_ROOT = os.path.join(BASE_DIR, "kb")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_stores")
os.makedirs(KB_ROOT, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# === Embedding & Mongo Setup ===
embedding_model = OllamaEmbeddings(model="mistral")
client = MongoClient("mongodb://localhost:27017/")
db = client["gowowschat_db"]
cache_col = db["kb_answer_cache"]

# === Cosine Similarity ===
def cosine_similarity(vec1, vec2):
    dot = sum(x * y for x, y in zip(vec1, vec2))
    norm1 = sum(x * x for x in vec1) ** 0.5
    norm2 = sum(y * y for y in vec2) ** 0.5
    return dot / (norm1 * norm2)

# === Semantic Match with Cached Embeddings ===
def get_semantic_match(pdf_path, query, threshold=0.9):
    all_docs = list(cache_col.find({"pdf_path": pdf_path, "embedding": {"$exists": True}}))
    if not all_docs:
        return None

    query_vector = embedding_model.embed_query(query)
    best_match = None
    best_score = -1

    for doc in all_docs:
        doc_vector = doc.get("embedding", [])
        if not doc_vector: continue
        score = cosine_similarity(query_vector, doc_vector)
        if score > best_score:
            best_score = score
            best_match = doc["answer"]

    return best_match + " (From Semantic Cache)" if best_score >= threshold else None

# === Cache Ops ===
def get_cached_answer(pdf_path, query):
    doc = cache_col.find_one_and_update(
        {"pdf_path": pdf_path, "query": query},
        {"$inc": {"hit_count": 1}},
        return_document=True
    )
    return doc["answer"] + " (From Cache)" if doc else None


def store_cached_answer(pdf_path, query, answer):
    embedding = embedding_model.embed_query(query)
    existing = cache_col.find_one({"pdf_path": pdf_path, "query": query})

    if existing:
        cache_col.update_one(
            {"pdf_path": pdf_path, "query": query},
            {
                "$set": {
                    "answer": answer,
                    "embedding": embedding,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"hit_count": 1}
            }
        )
    else:
        cache_col.insert_one({
            "pdf_path": pdf_path,
            "query": query,
            "answer": answer,
            "embedding": embedding,
            "created_at": datetime.utcnow(),
            "hit_count": 1
        })


# === Folder Listing ===
def list_kb_folders():
    kb_list = []

    print(f"📂 Scanning KB Root Path3: {KB_ROOT}")
    print(f"📂 KB Root Contents: {os.listdir(KB_ROOT)}")

    for top in os.listdir(KB_ROOT):
        top_path = os.path.join(KB_ROOT, top)
        if not os.path.isdir(top_path):
            continue

        subfolders = []
        for sub in os.listdir(top_path):
            sub_path = os.path.join(top_path, sub)
            if os.path.isdir(sub_path):
                pdfs = [f for f in os.listdir(sub_path) if f.endswith(".pdf")]
                subfolders.append({
                    "name": sub,
                    "pdfs": pdfs,
                    "pdf_count": len(pdfs)
                })

        if subfolders:
            kb_list.append({"folder": top, "subfolders": subfolders})

    return kb_list






def list_kb_folder(folder, subfolder):
    full_path = os.path.join(KB_ROOT, folder, subfolder)
    if not os.path.exists(full_path):
        return None
    return [f for f in os.listdir(full_path) if f.endswith(".pdf")]

# === Upload ===
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

# === Ask KB ===
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

    # 1. Exact Cache
    cached = get_cached_answer(full_path, query)
    if cached:
        return cached

    # 2. Semantic Match
    semantic_match = get_semantic_match(full_path, query)
    if semantic_match:
        return semantic_match

    # 3. Vector Search (Fallback)
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
    chain = load_qa_chain(Ollama(model="mistral"), chain_type="stuff")
    answer = chain.run(input_documents=relevant_docs, question=query)

    store_cached_answer(full_path, query, answer)
    return answer + " (From LLM)"

# === Read PDF Text for TTS ===
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
    return "\n".join([page.page_content for page in docs])

# === List KB Folders Based on Allowed Access ===
def list_specific_kb_folders(allowed_folders):
    all_folders = list_kb_folders()
    if "*" in allowed_folders:
        return all_folders

    filtered_kb_list = []
    for folder in all_folders:
        allowed_subfolders = [
            subfolder for subfolder in folder["subfolders"]
            if f"{folder['folder']}/{subfolder['name']}" in allowed_folders
        ]
        if allowed_subfolders:
            filtered_kb_list.append({
                "folder": folder["folder"],
                "subfolders": allowed_subfolders
            })
    return filtered_kb_list


# === New: List Cached Questions for a PDF ===
def list_cached_questions(pdf_path):
    """
    Given a PDF path, fetch all cached questions (queries) asked for that PDF.
    """
    # If incoming pdf_path is relative (like Standard/Standard1/story.pdf), convert to full path
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(KB_ROOT, pdf_path.replace("/", os.sep))
    
    questions = []
    docs = cache_col.find({"pdf_path": pdf_path})
    for doc in docs:
        questions.append({
            "query": doc.get("query", ""),
            "hit_count": doc.get("hit_count", 1)
        })
    return questions




