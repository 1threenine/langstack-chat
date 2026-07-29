import os
from datetime import datetime
import logging
from typing import List

from ddgs import DDGS
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from openai import APIConnectionError, APIError

from .config import CliConfig

config = CliConfig()

logger = logging.getLogger(__name__)

load_dotenv()

@tool
def web_search(query: str) -> List:
    """For web search"""
    return DDGS().text(query, max_results=5)

@tool
def get_news(query: str) -> List:
    """Get news about the query"""
    return DDGS().news(query=query)

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def get_date() -> str:
    """Get current Date+Time"""
    return str(datetime.now())

def main():
    try:
        llm = ChatOpenAI(
            model="qwen",
            base_url="http://127.0.0.1:8080/v1",  # using Llama.cpp
        )

        DB_URI = config.psql_url
        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            checkpointer.setup()  # auto create tables in PostgreSQL

            agent = create_agent(
                llm,
                tools=[get_weather, get_date, get_news, web_search],
                system_prompt="You are a helpful assistant",
                checkpointer=checkpointer,
            )

            thread_config = {"configurable": {"thread_id": "2"}}
            while True:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": input("User: ")}]},
                    thread_config,
                )["messages"][-1].content

                print("Agent: ", result)

    except APIConnectionError as e:
        logger.error(e)

    except APIError as e:
        logger.error(e)

    except KeyboardInterrupt:
        print("\nFin")


if __name__ == "__main__":
    main()
