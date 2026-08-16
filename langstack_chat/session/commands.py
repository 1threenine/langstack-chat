import uuid
import questionary
from langstack_chat.session.threads import get_threads_postgres, get_threads_sqlite
from langstack_chat.utils.console import console
from langstack_chat.config import CliConfig
from langstack_chat.rag import load_document, add_documents

config = CliConfig()
SQLITE_PATH = config.sqlite_path

def handle_slash_command(thread_config: dict, checkpointer, db_choice: str) -> dict:
    action = questionary.select(
        "CLI Options:",
        choices=[
            questionary.Choice("New thread", value="new_thread"),
            questionary.Choice("Switch thread", value="switch_thread"),
            questionary.Choice("Delete thread", value="delete_thread"),
            # questionary.Choice("Change model", value="change_model"),
            # questionary.Choice("Change memory mode", value="change_memory"),
            questionary.Choice("Load document", value="load_doc"),
            questionary.Choice("Cancel", value="cancel"),
        ],
    ).ask()

    def _get_threads():
        return get_threads_sqlite(SQLITE_PATH) if db_choice == "sqlite" else get_threads_postgres()

    if action == "new_thread":
        tid = str(uuid.uuid4())
        thread_config["configurable"]["thread_id"] = tid
        console.print(f"[green]New thread:[/green] [bold]{tid}[/bold]")

    elif action == "switch_thread":
        threads = _get_threads()
        if not threads:
            console.print("[yellow]No saved threads.[/yellow]")
        else:
            selected = questionary.select("Select thread:", choices=threads).ask()
            thread_config["configurable"]["thread_id"] = selected
            console.print(f"[green]Switched to:[/green] [bold]{selected}[/bold]")

    elif action == "delete_thread":
        threads = _get_threads()
        if not threads:
            console.print("[yellow]No saved threads.[/yellow]")
        else:
            selected = questionary.select("Delete which thread?", choices=threads).ask()
            if questionary.confirm(f"Delete '{selected}'?").ask() and checkpointer:
                checkpointer.delete_thread(selected)
                console.print(f"[red]Deleted:[/red] [bold]{selected}[/bold]")

    elif action == "load_doc":
        path = questionary.text("Enter file path:").ask()
        try:
            with console.status("[bold cyan]Loading document...", spinner="dots"):
                chunks = load_document(path)
                count = add_documents(chunks)
            console.print(f"[green]Loaded {count} chunks from {path}[/green]")
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            console.print(f"[red]{e}[/red]")


    return thread_config
