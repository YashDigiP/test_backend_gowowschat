import os, hashlib
from flask import jsonify
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_ollama import OllamaEmbeddings
from services.llm_config import LLM_MODELS

embedding_model = OllamaEmbeddings(model="nomic-embed-text")
VECTOR_STORE_DIR = "vector_stores"

def embed_site_handler(request):
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        hashed = hashlib.sha256(url.encode()).hexdigest()
        vs_path = os.path.join(VECTOR_STORE_DIR, f"web_{hashed}")
        if os.path.exists(vs_path):
            return jsonify({"message": "✅ Already embedded", "id": hashed})
        loader = RecursiveUrlLoader(url=url, max_depth=2, extractor=lambda x: x)
        docs = loader.load()
        vectordb = FAISS.from_documents(docs, embedding_model)
        vectordb.save_local(vs_path)
        return jsonify({"message": f"✅ Embedded site: {url}", "id": hashed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_web(request):
    data = request.get_json()
    question = data.get("question", "")
    vector_id = data.get("id", "")
    if not question or not vector_id:
        return jsonify({"error": "Missing question or ID"}), 400
    vs_path = os.path.join(VECTOR_STORE_DIR, f"web_{vector_id}")
    if not os.path.exists(vs_path):
        return jsonify({"error": "Vector store not found. Please embed site first."}), 400
    try:
        vectordb = FAISS.load_local(vs_path, embedding_model, allow_dangerous_deserialization=True)
        retriever = vectordb.as_retriever()
        model = LLM_MODELS["ask_website"]
        print(f"🌐 Using model for Ask Website (handle_web): {model}")
        llm = ChatOllama(model=model)
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        response = qa.invoke({"query": question})["result"]
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_web_live(request):
    data = request.get_json()
    url = data.get("url", "")
    question = data.get("question", "")
    if not url or not question:
        return jsonify({"error": "Missing URL or question"}), 400
    try:
        loader = RecursiveUrlLoader(url=url, max_depth=1, extractor=lambda x: x)
        docs = loader.load()
        vectordb = FAISS.from_documents(docs, embedding_model)
        retriever = vectordb.as_retriever()
        model = LLM_MODELS["ask_website"]
        print(f"🌐 Using model for Ask Website (handle_web_live): {model}")
        llm = ChatOllama(model=model)
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        response = qa.invoke({"query": question})["result"]
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_web_lite(request):
    data = request.get_json()
    url = data.get("url", "")
    question = data.get("question", "")
    if not url or not question:
        return jsonify({"error": "Missing URL or question"}), 400
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        vectordb = FAISS.from_documents(docs, embedding_model)
        retriever = vectordb.as_retriever()
        model = LLM_MODELS["ask_website"]
        print(f"🌐 Using model for Ask Website (handle_web_lite): {model}")
        llm = ChatOllama(model=model)
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        response = qa.invoke({"query": question})["result"]
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
