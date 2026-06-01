import sqlite3
import uuid
from datetime import datetime
from backend.src.config import DB_PATH
import os


def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create tables if they don't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT,
            created_at  TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id          TEXT PRIMARY KEY,
            chat_id     TEXT NOT NULL,
            name        TEXT NOT NULL,
            file_path   TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables initialised.")


# ── Chat CRUD ──────────────────────────────────────────────────────────────

def create_chat(name: str, description: str = None) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    chat = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }
    cursor.execute(
        "INSERT INTO chats (id, name, description, created_at) VALUES (?, ?, ?, ?)",
        (chat["id"], chat["name"], chat["description"], chat["created_at"])
    )
    conn.commit()
    conn.close()
    return chat


def get_all_chats() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_chat(chat_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_chat(chat_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()


def update_chat(chat_id: str, name: str, description: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET name = ?, description = ? WHERE id = ?",
        (name, description, chat_id)
    )
    conn.commit()
    conn.close()


# ── Document CRUD ──────────────────────────────────────────────────────────

def create_document(chat_id: str, name: str, file_path: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    doc = {
        "id": str(uuid.uuid4()),
        "chat_id": chat_id,
        "name": name,
        "file_path": file_path,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    cursor.execute(
        "INSERT INTO documents (id, chat_id, name, file_path, uploaded_at) VALUES (?, ?, ?, ?, ?)",
        (doc["id"], doc["chat_id"], doc["name"], doc["file_path"], doc["uploaded_at"])
    )
    conn.commit()
    conn.close()
    return doc


def get_documents_for_chat(chat_id: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM documents WHERE chat_id = ? ORDER BY uploaded_at DESC",
        (chat_id,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def delete_document(document_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    