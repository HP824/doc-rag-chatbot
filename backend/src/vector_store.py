import os
from dotenv import load_dotenv
from huggingface_hub import login
from backend.src.config import EMBEDDING_MODEL, CHROMA_DIR

load_dotenv()
login(token=os.getenv("HF_TOKEN"), add_to_git_credential=False)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_embedding_function():
    """
    Load the embedding model. Cached after first call by LangChain internally.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_collection_name(chat_id: str) -> str:
    """
    Each chat gets its own ChromaDB collection.
    """
    return f"chat_{chat_id}"


def add_chunks_to_store(chunks: list[dict], chat_id: str):
    """
    Embed and store chunks into the chat's ChromaDB collection.
    chunks: list of dicts with 'text' and 'metadata' keys.
    """
    os.makedirs(CHROMA_DIR, exist_ok=True)

    embeddings = get_embedding_function()
    collection_name = get_collection_name(chat_id)

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    vector_store.add_texts(texts=texts, metadatas=metadatas)

    print(f"[VECTOR STORE] Added {len(chunks)} chunks to collection '{collection_name}'")


def query_store(query: str, chat_id: str, top_k: int = 3) -> list[dict]:
    """
    Search a chat's ChromaDB collection for relevant chunks.
    Returns list of dicts with 'text' and 'metadata'.
    """
    embeddings = get_embedding_function()
    collection_name = get_collection_name(chat_id)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    results = vector_store.similarity_search(query, k=top_k)

    return [
        {
            "text": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]


def delete_document_from_store(chat_id: str, document_id: str):
    """
    Remove all chunks belonging to a specific document from the collection.
    """
    embeddings = get_embedding_function()
    collection_name = get_collection_name(chat_id)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    vector_store._collection.delete(
        where={"document_id": document_id}
    )

    print(f"[VECTOR STORE] Deleted chunks for document '{document_id}' from '{collection_name}'")


def delete_chat_collection(chat_id: str):
    """
    Delete the entire ChromaDB collection for a chat.
    Called when a chat is deleted.
    """
    embeddings = get_embedding_function()
    collection_name = get_collection_name(chat_id)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    vector_store._client.delete_collection(collection_name)

    print(f"[VECTOR STORE] Deleted collection '{collection_name}'")
    