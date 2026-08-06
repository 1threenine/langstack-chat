import uuid
import psycopg2
import questionary
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver

from langstack_chat.config import CliConfig
from langstack_chat.session.threads import get_threads_postgres, get_threads_sqlite
from langstack_chat.utils.console import console

config = CliConfig()
SQLITE_PATH = "chat_sessions.db"


def _pick_thread(existing: list[str]) -> str:
    if not existing:
        tid = str(uuid.uuid4())
        console.print(f"[green]New thread:[/green] [bold]{tid}[/bold]")
        return tid
    choices = ["-- New thread --"] + existing
    selected = questionary.select("Select a thread:", choices=choices).ask()
    if selected == "-- New thread --":
        tid = str(uuid.uuid4())
        console.print(f"[green]New thread:[/green] [bold]{tid}[/bold]")
        return tid
    console.print(f"[green]Resuming:[/green] [bold]{selected}[/bold]")
    return selected


def setup_checkpointer():
    """Returns (checkpointer, thread_id, saver_ctx, db_choice)."""
    memory_mode = questionary.select(
        "Select session memory mode:",
        choices=[
            questionary.Choice("No memory (stateless)", value="none"),
            questionary.Choice("In-context memory", value="inmemory"),
            questionary.Choice("Permanent memory (database)", value="permanent"),
        ],
    ).ask()

    thread_id = str(uuid.uuid4())
    checkpointer, _saver, db_choice = None, None, None

    if memory_mode == "none":
        console.print("[dim]Stateless mode.[/dim]")

    elif memory_mode == "inmemory":
        checkpointer = InMemorySaver()
        console.print(f"[dim]Thread: [bold]{thread_id}[/bold][/dim]")

    elif memory_mode == "permanent":
        db_choice = questionary.select(
            "Select database:",
            choices=[
                questionary.Choice("SQLite  (local)", value="sqlite"),
                questionary.Choice("PostgreSQL  (server)", value="postgres"),
            ],
        ).ask()

        if db_choice == "sqlite":
            _saver = SqliteSaver.from_conn_string(SQLITE_PATH)
            checkpointer = _saver.__enter__()
            checkpointer.setup()
            thread_id = _pick_thread(get_threads_sqlite(SQLITE_PATH))

        elif db_choice == "postgres":
            psycopg2.connect(config.psql_url).close()
            _saver = PostgresSaver.from_conn_string(config.psql_url)
            checkpointer = _saver.__enter__()
            checkpointer.setup()
            thread_id = _pick_thread(get_threads_postgres())

    return checkpointer, thread_id, _saver, db_choice
