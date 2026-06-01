# backend/src/document_processor.py

import os
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.src.config import CHUNK_SIZE, CHUNK_OVERLAP, UPLOAD_DIR


def save_uploaded_file(file, chat_id: str) -> str:
    chat_upload_dir = os.path.join(UPLOAD_DIR, chat_id)
    os.makedirs(chat_upload_dir, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(chat_upload_dir, unique_filename)
    contents = file.file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    print(f"[SAVED] {file_path}")
    return file_path


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return _extract_txt(file_path)
    elif ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _extract_pdf(file_path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
    return "\n\n".join(pages)


def _extract_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def chunk_text(text: str, document_id: str, chat_id: str, document_name: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    raw_chunks = splitter.split_text(text)
    return [
        {
            "text": chunk,
            "metadata": {
                "document_id": document_id,
                "chat_id": chat_id,
                "document_name": document_name,
                "chunk_index": i
            }
        }
        for i, chunk in enumerate(raw_chunks)
    ]


def process_uploaded_file(file, chat_id: str, document_id: str, document_name: str):
    file_path = save_uploaded_file(file, chat_id)
    text = extract_text(file_path)
    if len(text.strip()) < 50:
        raise ValueError(f"Could not extract meaningful text from '{document_name}'.")
    chunks = chunk_text(text, document_id, chat_id, document_name)
    return file_path, chunks
