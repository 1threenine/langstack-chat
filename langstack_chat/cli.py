from openai import APIConnectionError, APIError, OpenAIError
from psycopg2 import OperationalError
import questionary
from rich.panel import Panel
from rich.markdown import Markdown

from langstack_chat.config import CliConfig
from langstack_chat.agent import build_llm, build_agent, fetch_models
from langstack_chat.session.memory import setup_checkpointer
from langstack_chat.session.commands import handle_slash_command
from langstack_chat.utils.console import console
from langstack_chat.utils.logging import setup_logging, get_logger
from langstack_chat.utils.retry import with_retry


setup_logging()
logger = get_logger(__name__)


config = CliConfig()

console.print(Panel(f"[bold cyan]Chat CLI Using {config.default_provider}[/bold cyan]"))


def main():
    _saver = None
    try:
        while True:
            provider = questionary.select(
                "Select provider:", choices=["Llama.cpp", "OpenAI", "Bedrock"]
            ).ask()

            models = fetch_models(provider)
            if models:
                break
            console.print("[red]Could not connect to provider or invalid API key. Try another.[/red]")

        model = questionary.select("Select model:", choices=models).ask()

        llm = build_llm(provider, model)

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
                try:
                    result = with_retry(
                        lambda: agent.invoke(
                            {"messages": [{"role": "user", "content": q}]},
                            thread_config,
                        )["messages"][-1].content
                    )
                except RuntimeError as e:
                    logger.error("Agent failed: %s", e)
                    console.print("[red]Could not get a response. Try again.[/red]")
                    continue

            console.print(":robot: Agent: ", Markdown(result))

    except OperationalError:
        logger.error("PostgreSQL is not running or connection failed.", exc_info=False)
    except (APIConnectionError, APIError, OpenAIError) as e:
        logger.error("LLM provider error: %s", e, exc_info=False)
    except KeyboardInterrupt:
        pass
    finally:
        if _saver is not None:
            _saver.__exit__(None, None, None)
        logger.info("Fin")
        console.print("\n[bold green]Fin")
