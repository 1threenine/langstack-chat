import sqlite3
import psycopg2
from langstack_chat.config import CliConfig

config = CliConfig()

def get_threads_postgres() -> list[str]:
    try:
        with psycopg2.connect(config.psql_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
                return [row[0] for row in cur.fetchall()]
    except Exception:
        return []

def get_threads_sqlite(path: str) -> list[str]:
    try:
        with sqlite3.connect(path) as conn:
            cur = conn.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
            return [row[0] for row in cur.fetchall()]
    except Exception:
        return []
