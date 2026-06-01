import os
import openai
from dotenv import load_dotenv
from backend.src.retriever import retrieve

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are a helpful and precise document assistant.
You answer questions strictly based on the context provided from the user's uploaded documents.
If the context does not contain enough information to answer, say:
"I couldn't find relevant information in the uploaded documents for that question."
Be concise and factual. Keep answers to 3-5 sentences unless more detail is clearly needed.
"""


def build_prompt(query: str, chunks: list[dict]) -> str:
    """
    Build a prompt from retrieved chunks.
    """
    if not chunks:
        return query

    context_parts = []
    for i, chunk in enumerate(chunks, start=1):
        doc_name = chunk["metadata"].get("document_name", "Unknown")
        context_parts.append(f"[Source {i} — {doc_name}]\n{chunk['text']}")

    context = "\n\n".join(context_parts)

    return f"""Context from uploaded documents:

{context}

Question: {query}

Answer:"""


def ask(query: str, chat_id: str) -> dict:
    """
    Full pipeline: retrieve → build prompt → call LLM → return response.
    Returns dict with 'answer' and 'sources'.
    """
    chunks = retrieve(query, chat_id)

    if not chunks:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents for that question.",
            "sources": []
        }

    prompt = build_prompt(query, chunks)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    answer = response.choices[0].message.content.strip()

    sources = list({
        chunk["metadata"].get("document_name", "Unknown")
        for chunk in chunks
    })

    return {
        "answer": answer,
        "sources": sources
    }
