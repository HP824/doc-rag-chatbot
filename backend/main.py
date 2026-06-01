# backend/main.py

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

load_dotenv()

from backend.src.database import (
    init_db, create_chat, get_all_chats, get_chat,
    update_chat, delete_chat, create_document,
    get_documents_for_chat, delete_document
)
from backend.src.document_processor import process_uploaded_file
from backend.src.vector_store import (
    add_chunks_to_store, delete_document_from_store, delete_chat_collection
)
from backend.src.chatbot import ask

# ── Init ───────────────────────────────────────────────────────────────────
load_dotenv()
init_db()
os.makedirs("data/uploads", exist_ok=True)

app = FastAPI(title="Document RAG Chatbot")

# ── Serve frontend static files ────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# ── Pydantic models ────────────────────────────────────────────────────────
class ChatCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ChatUpdate(BaseModel):
    name: str
    description: Optional[str] = None

class AskRequest(BaseModel):
    question: str

# ── Frontend routes ────────────────────────────────────────────────────────
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/chat/{chat_id}")
def serve_chat(chat_id: str):
    return FileResponse("frontend/chat.html")

# ── Chat endpoints ─────────────────────────────────────────────────────────
@app.get("/api/chats")
def api_get_chats():
    return get_all_chats()

@app.post("/api/chats", status_code=201)
def api_create_chat(body: ChatCreate):
    return create_chat(body.name, body.description)

@app.get("/api/chats/{chat_id}")
def api_get_chat(chat_id: str):
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.put("/api/chats/{chat_id}")
def api_update_chat(chat_id: str, body: ChatUpdate):
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    update_chat(chat_id, body.name, body.description)
    return get_chat(chat_id)

@app.delete("/api/chats/{chat_id}", status_code=204)
def api_delete_chat(chat_id: str):
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    delete_chat_collection(chat_id)
    delete_chat(chat_id)

# ── Document endpoints ─────────────────────────────────────────────────────
@app.get("/api/chats/{chat_id}/documents")
def api_get_documents(chat_id: str):
    return get_documents_for_chat(chat_id)

@app.post("/api/chats/{chat_id}/documents", status_code=201)
async def api_upload_document(chat_id: str, file: UploadFile = File(...)):
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    doc_id = str(uuid.uuid4())

    try:
        file_path, chunks = process_uploaded_file(file, chat_id, doc_id, file.filename)
        add_chunks_to_store(chunks, chat_id)
        doc = create_document(chat_id, file.filename, file_path)
        return {"document": doc, "chunks_embedded": len(chunks)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/documents/{document_id}", status_code=204)
def api_delete_document(document_id: str):
    from backend.src.database import get_connection
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM documents WHERE id = ?", (document_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document_from_store(row["chat_id"], document_id)
    delete_document(document_id)

# ── Ask endpoint ───────────────────────────────────────────────────────────
@app.post("/api/chats/{chat_id}/ask")
def api_ask(chat_id: str, body: AskRequest):
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    docs = get_documents_for_chat(chat_id)
    if not docs:
        raise HTTPException(status_code=400, detail="No documents uploaded to this chat.")
    result = ask(body.question, chat_id)
    return result
