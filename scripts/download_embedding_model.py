# scripts/download_embedding_model.py   -- SETUP ONLY: online, no user document
from pathlib import Path
from sentence_transformers import SentenceTransformer

TARGET = Path("models/all-MiniLM-L6-v2")
TARGET.parent.mkdir(parents=True, exist_ok=True)
SentenceTransformer("all-MiniLM-L6-v2").save_pretrained(str(TARGET))
print(f"saved -> {TARGET}")