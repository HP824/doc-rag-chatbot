from backend.src.vector_store import query_store
from backend.src.config import TOP_K_RESULTS


def retrieve(query: str, chat_id: str) -> list[dict]:
    """
    Retrieve the most relevant chunks for a query within a specific chat.
    Returns a list of dicts with 'text' and 'metadata'.
    """
    results = query_store(query, chat_id, top_k=TOP_K_RESULTS)

    if not results:
        print(f"[RETRIEVER] No results found for chat '{chat_id}'")
        return []

    print(f"[RETRIEVER] Retrieved {len(results)} chunks for chat '{chat_id}'")
    return results
