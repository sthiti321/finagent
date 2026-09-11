import os
import psycopg
import requests
from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nfl@localhost:5432/finagent_rag"
)

MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"


def retrieve_context(query, top_k=3):

    model = SentenceTransformer(MODEL_NAME)

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                chunk_id,
                document_id,
                content,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (
                query_embedding.tolist(),
                query_embedding.tolist(),
                top_k
            )
        )

        results = cur.fetchall()

    conn.close()

    return results


def build_context(results):

    context_parts = []

    for rank, (chunk_id, document_id, content, similarity) in enumerate(
        results, start=1
    ):

        context_parts.append(
            f"""
SOURCE {rank}
Chunk ID: {chunk_id}
Document ID: {document_id}
Similarity: {similarity:.4f}

{content}
"""
        )

    return "\n".join(context_parts)


def ask_llm(question, context):

    prompt = f"""
You are FinAgent, a financial crime investigation assistant.

Answer the user's question using ONLY the knowledge provided in the context.

Rules:
- Do not invent facts.
- Do not assume an alert means confirmed financial crime.
- Clearly distinguish evidence from conclusions.
- If the context does not contain enough information, say so.
- Give a concise professional investigation-oriented answer.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]


def answer_question(question):

    results = retrieve_context(question)

    if not results:
        return "No relevant information was found in the knowledge base."

    context = build_context(results)

    answer = ask_llm(question, context)

    return answer


if __name__ == "__main__":

    question = "What are the indicators for network investigation?"

    print("\nQUESTION:")
    print(question)

    print("\nFINAGENT ANSWER:")
    print(answer_question(question))