
import os
import hashlib
from pathlib import Path
from typing import List
import argparse

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

Base_url = os.getenv("BASE_URL")

def get_hashed_path(relative_path: str) -> str:
    normalized = os.path.normpath(relative_path).replace("\\", "/")
    return hashlib.sha256(normalized.encode()).hexdigest()


KB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "KB"))
VECTOR_STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vector_stores"))
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
embedding_model = OllamaEmbeddings(model="nomic-embed-text", base_url=Base_url)

def get_all_pdfs_recursively(folder: str) -> List[str]:
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(folder)
        for file in files
        if file.lower().endswith(".pdf")
    ]

def hash_path(filepath: str) -> str:
    return hashlib.sha256(filepath.encode()).hexdigest()

def hash_file_contents(filepath: str) -> str:
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    return hashlib.sha256(file_bytes).hexdigest()

def embed_pdf(pdf_path: str, force=False):
    relative_path = os.path.relpath(pdf_path, KB_ROOT)
    doc_id = get_hashed_path(os.path.join("KB", relative_path))
    out_dir = os.path.join(VECTOR_STORE_DIR, doc_id)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n🔗 {pdf_path} → {out_dir}")
    checksum_file = os.path.join(out_dir, "checksum.txt")
    current_checksum = hash_file_contents(pdf_path)

    if not force and os.path.exists(checksum_file):
        with open(checksum_file, "r") as f:
            old_checksum = f.read().strip()
        if current_checksum == old_checksum:
            print(f"✅ Skipped (no change): {pdf_path}")
            return
        else:
            print(f"🔁 Updated: {pdf_path}")
    else:
        print(f"🆕 New: {pdf_path}")

    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        print(f"📄 Loaded {len(pages)} pages")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        docs = splitter.split_documents(pages)
        print(f"✂️ Split into {len(docs)} chunks")

        vectordb = FAISS.from_documents(docs, embedding_model)
        vectordb.save_local(out_dir)

        with open(checksum_file, "w") as f:
            f.write(current_checksum)

        print(f"💾 Embedded and saved: {out_dir}")

    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")

def list_embedded_files():
    print("\n📦 Embedded PDFs:")
    for folder in os.listdir(VECTOR_STORE_DIR):
        path = os.path.join(VECTOR_STORE_DIR, folder, "checksum.txt")
        if os.path.exists(path):
            print("•", folder)

def find_orphans():
    print("\n🧹 Orphan Vectors (no matching PDF):")
    known_hashes = {hash_path(p): p for p in get_all_pdfs_recursively(KB_ROOT)}
    for folder in os.listdir(VECTOR_STORE_DIR):
        if folder not in known_hashes:
            print("•", folder)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force re-embedding all PDFs")
    parser.add_argument("--file", type=str, help="Path to a specific PDF")
    parser.add_argument("--list", action="store_true", help="List embedded PDFs")
    parser.add_argument("--orphans", action="store_true", help="List orphaned vector stores")
    args = parser.parse_args()

    if args.list:
        return list_embedded_files()
    if args.orphans:
        return find_orphans()
    if args.file:
        return embed_pdf(args.file, force=args.force)

    pdfs = get_all_pdfs_recursively(KB_ROOT)
    print(f"\n🔍 Found {len(pdfs)} PDFs under '{KB_ROOT}'")
    for path in pdfs:
        embed_pdf(path, force=args.force)

if __name__ == "__main__":
    main()