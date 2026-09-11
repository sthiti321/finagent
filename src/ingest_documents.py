import os
import psycopg
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nfl@localhost:5432/finagent_rag"
)

KNOWLEDGE_DIR = "knowledge/raw"


def get_category(file_path):
    """Get the knowledge category from the folder name."""
    return os.path.basename(os.path.dirname(file_path))


def ingest_documents():
    conn = psycopg.connect(DATABASE_URL)

    with conn.cursor() as cur:

        for root, _, files in os.walk(KNOWLEDGE_DIR):

            for file_name in files:

                if not file_name.endswith(".md"):
                    continue

                file_path = os.path.join(root, file_name)

                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                title = content.split("\n", 1)[0].replace("# ", "").strip()
                category = get_category(file_path)

                # Check whether document already exists
                cur.execute(
                    """
                    SELECT document_id
                    FROM documents
                    WHERE file_path = %s
                    """,
                    (file_path,)
                )

                existing = cur.fetchone()

                if existing:
                    print(f"Already exists: {file_path}")
                    continue

                # Insert document
                cur.execute(
                    """
                    INSERT INTO documents
                    (title, category, source, file_path)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        title,
                        category,
                        "Synthetic FinAgent Knowledge Base",
                        file_path,
                    )
                )

                print(f"Inserted: {file_path}")

    conn.commit()
    conn.close()

    print("\nDocument ingestion completed.")


if __name__ == "__main__":
    ingest_documents()