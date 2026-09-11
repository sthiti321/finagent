import os
import psycopg
from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nfl@localhost:5432/finagent_rag"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def retrieve(query, top_k=3):

    # Load embedding model
    model = SentenceTransformer(MODEL_NAME)

    # Convert query into embedding
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    # Connect to PostgreSQL
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


if __name__ == "__main__":

    query = "What are the indicators for network investigation?"

    results = retrieve(query)

    print("\nQuery:")
    print(query)

    print("\nTop Retrieved Documents:\n")

    for rank, (chunk_id, document_id, content, similarity) in enumerate(
        results, start=1
    ):

        print("=" * 70)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk_id}")
        print(f"Document ID: {document_id}")
        print(f"Similarity: {similarity:.4f}")
        print("\nContent:")
        print(content)