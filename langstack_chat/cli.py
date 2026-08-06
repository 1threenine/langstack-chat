import logging
from openai import APIConnectionError, APIError, OpenAIError
from psycopg2 import OperationalError
import questionary
from rich.panel import Panel
from rich.markdown import Markdown

from langstack_chat.config import CliConfig
from langstack_chat.agent import build_llm, build_agent
from langstack_chat.session.memory import setup_checkpointer
from langstack_chat.session.commands import handle_slash_command
from langstack_chat.utils.console import console

config = CliConfig()
logger = logging.getLogger(__name__)

console.print(Panel(f"[bold cyan]Chat CLI Using {config.default_provider}[/bold cyan]"))


def main():
    _saver = None
    try:
        llm = build_llm()
        checkpointer, thread_id, _saver, db_choice = setup_checkpointer()
        agent = build_agent(llm, checkpointer)
        thread_config = {"configurable": {"thread_id": thread_id}}

        while True:
            q = questionary.text(" User:").ask()
            if q is None or q.lower() in ("exit!", "!q", "q!"):
                break

            if q.startswith("/"):
                thread_config = handle_slash_command(thread_config, checkpointer, db_choice)
                continue

            with console.status("[bold yellow]Agent thinking...", spinner="dots"):
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": q}]},
                    thread_config,
                )["messages"][-1].content

            console.print(":robot: Agent: ", Markdown(result))

    except OperationalError:
        logger.error("PostgreSQL is not running or connection failed.")
    except (APIConnectionError, APIError, OpenAIError) as e:
        logger.error(e)
    finally:
        if _saver is not None:
            _saver.__exit__(None, None, None)
        console.print("\n[bold green]Fin")
