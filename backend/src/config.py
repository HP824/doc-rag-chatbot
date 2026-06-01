import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 3

DB_PATH      = os.path.join(BASE_DIR, "data", "database.db")
UPLOAD_DIR   = os.path.join(BASE_DIR, "data", "uploads")
CHROMA_DIR   = os.path.join(BASE_DIR, "data", "chroma_db")
