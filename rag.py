"""Local RAG Pipeline (100% Offline) using pdfplumber, langchain, sentence-transformers, and faiss-cpu."""

import os
import pickle
from typing import List, Dict, Any

import numpy as np
import pdfplumber
import faiss
from sentence_transformers import SentenceTransformer

try:
    from langchain_text_splitters import TokenTextSplitter
except ImportError:
    from langchain_community.document_transformers import TokenTextSplitter

# Storage paths for local FAISS index and chunk metadata
INDEX_PATH = "faiss_index.bin"
METADATA_PATH = "faiss_metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level cached embedding model
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    """Retrieve or initialize the cached local SentenceTransformer model."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(MODEL_NAME)
    return _embedding_model


def ingest_pdf(file_path: str) -> bool:
    """
    Reads the PDF, extracts text while tracking page numbers, chunks text using
    langchain TokenTextSplitter (500 tokens, 50 overlap), generates embeddings
    locally via all-MiniLM-L6-v2, saves the FAISS index locally, and returns True.

    Args:
        file_path (str): Path to the input PDF file.

    Returns:
        bool: True when ingestion and vector indexing are complete.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")

    # 1. Extract text and track page numbers using pdfplumber
    pages_data: List[Dict[str, Any]] = []
    with pdfplumber.open(file_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages_data.append({"page": page_idx, "text": text})

    if not pages_data:
        # If no extractable text found, create an empty placeholder to prevent indexing errors
        pages_data.append({"page": 1, "text": "No extractable text found in document."})

    # 2. Chunk text using langchain token splitter (500 tokens, 50 overlap)
    splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks: List[Dict[str, Any]] = []

    for item in pages_data:
        page_num = item["page"]
        page_text = item["text"]
        split_texts = splitter.split_text(page_text)
        for chunk_idx, chunk_str in enumerate(split_texts, start=1):
            chunk_clean = chunk_str.strip()
            if chunk_clean:
                chunks.append({
                    "text": chunk_clean,
                    "page": page_num,
                    "id": f"p{page_num}-c{chunk_idx}",
                    "heading": f"Page {page_num} Clause",
                })

    if not chunks:
        chunks.append({
            "text": "Empty document.",
            "page": 1,
            "id": "p1-c1",
            "heading": "Page 1 Clause",
        })

    # 3. Generate embeddings locally using sentence-transformers (all-MiniLM-L6-v2)
    model = _get_embedding_model()
    texts_to_embed = [c["text"] for c in chunks]
    embeddings = model.encode(texts_to_embed, convert_to_numpy=True, normalize_embeddings=True)

    # 4. Save local FAISS index (IndexFlatIP with normalized vectors = cosine similarity)
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings.astype("float32"))

    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(chunks, f)

    return True


def search_clauses(query: str, top_k: int = 3) -> list[dict]:
    """
    Loads the local FAISS index, searches the query using local embeddings,
    and returns a list of dictionaries with 'text' and 'page' keys.

    Args:
        query (str): The search query.
        top_k (int, optional): Number of top matching clauses to return. Defaults to 3.

    Returns:
        list[dict]: List of matching dictionaries, each containing 'text' and 'page'.
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        return []

    # 1. Load FAISS index and chunk metadata
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        chunks: List[Dict[str, Any]] = pickle.load(f)

    if not chunks:
        return []

    # 2. Embed query locally
    model = _get_embedding_model()
    query_vector = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)

    # 3. Search FAISS index
    k = min(top_k, len(chunks))
    distances, indices = index.search(query_vector.astype("float32"), k)

    # 4. Format and return results
    results: list[dict] = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            item = chunks[idx]
            results.append({
                "text": item["text"],
                "page": item["page"],
                "id": item.get("id", f"clause-{idx}"),
                "heading": item.get("heading", f"Page {item['page']} Excerpt"),
            })

    return results
