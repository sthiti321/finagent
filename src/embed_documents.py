import os
import psycopg
from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nfl@localhost:5432/finagent_rag"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def generate_embeddings():

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    conn = psycopg.connect(DATABASE_URL)

    register_vector(conn)

    with conn.cursor() as cur:

        cur.execute("""
            SELECT chunk_id, content
            FROM document_chunks
            WHERE embedding IS NULL
            ORDER BY chunk_id;
        """)

        rows = cur.fetchall()

        print(f"Chunks needing embeddings: {len(rows)}")

        if not rows:
            print("All chunks already have embeddings.")
            conn.close()
            return

        texts = [row[1] for row in rows]

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        for (chunk_id, _), embedding in zip(rows, embeddings):

            cur.execute(
                """
                UPDATE document_chunks
                SET embedding = %s
                WHERE chunk_id = %s
                """,
                (embedding.tolist(), chunk_id)
            )

    conn.commit()
    conn.close()

    print("Embedding generation completed.")


if __name__ == "__main__":
    generate_embeddings()