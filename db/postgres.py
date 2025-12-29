import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True


def init_db():
    """
    Safe to call multiple times.
    Creates required tables only if they don't exist.
    """
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS url_queue (
            id SERIAL PRIMARY KEY,
            source TEXT,
            url TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            retries INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)


init_db()


def insert_urls(urls, source="sitemap"):
    with conn.cursor() as cur:
        for url in urls:
            cur.execute(
                """
                INSERT INTO url_queue (source, url)
                VALUES (%s, %s)
                ON CONFLICT (url) DO NOTHING
                """,
                (source, url)
            )


def fetch_next_url():
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, url
            FROM url_queue
            WHERE status='pending'
            ORDER BY created_at
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """
        )
        row = cur.fetchone()

        if row:
            cur.execute(
                "UPDATE url_queue SET status='processing' WHERE id=%s",
                (row[0],)
            )
        return row


def mark_done(job_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM url_queue WHERE id=%s", (job_id,))


def mark_failed(job_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE url_queue
            SET status='failed', retries=retries+1
            WHERE id=%s
            """,
            (job_id,)
        )
