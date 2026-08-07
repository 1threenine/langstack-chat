import sqlite3
import psycopg2
from langstack_chat.config import CliConfig
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

config = CliConfig()

def get_threads_postgres() -> list[str]:
    try:
        with psycopg2.connect(config.psql_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
                return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.warning("Failed to fetch PostgreSQL threads: %s", e)
        return []

def get_threads_sqlite(path: str) -> list[str]:
    try:
        with sqlite3.connect(path) as conn:
            cur = conn.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.warning("Failed to fetch SQLite threads: %s", e)
        return []
