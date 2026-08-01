import logging
from typing import List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from openai import APIConnectionError, APIError, OpenAIError
import psycopg2
from psycopg2 import OperationalError
import questionary
from rich.panel import Panel
from rich.markdown import Markdown

from langstack_chat.config import CliConfig
from langstack_chat.tools import *
from langstack_chat.utils.console import console


config = CliConfig()

console.print(Panel(f"[bold cyan]Chat CLI Using {config.default_provider}[/bold cyan]"))

logger = logging.getLogger(__name__)

DB_URI = config.psql_url

def main():
    try:

        llm = ChatOpenAI(
            model="qwen",
            base_url=config.base_url,
            api_key=config.openai_api_key,
        )

        conn = psycopg2.connect(DB_URI)
        conn.close()

        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            checkpointer.setup()  # auto create tables in PostgreSQL

            agent = create_agent(
                llm,
                tools=[get_weather, get_date, get_news, web_search, get_url],
                system_prompt="You are a helpful assistant",
                checkpointer=checkpointer,
            )

            thread_config = {"configurable": {"thread_id": "3"}}
            while True:
                q = questionary.text(" User:").ask()

                if q.lower() == "exit!" or q.lower() == "!q": break

                with console.status(f"[bold yellow]Agent thinking...", spinner="dots"):
                    result = agent.invoke(
                        {"messages": [{"role": "user", "content": q}]},
                        thread_config,
                    )["messages"][-1].content

                    result_md = Markdown(result)

                console.print(":robot: Agent: ", result_md)

    except OperationalError as e:
        logger.error("PSQL is not running")

    except APIConnectionError as e:
        logger.error(e)

    except APIError as e:
        logger.error(e)

    except OpenAIError as e:
        logger.error(e)

    finally:
        console.print("\n[bold green]Fin")
