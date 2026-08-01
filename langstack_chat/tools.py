from datetime import datetime
from ddgs import DDGS
from typing import List
from langchain.tools import tool
from langstack_chat.utils.console import console
from functools import wraps


def with_loading(message="Calling tool..."):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with console.status(f"[bold cyan]{message}", spinner="dots"):
                return func(*args, **kwargs)
        return wrapper
    return decorator

@tool
@with_loading("Searching On Web")
def web_search(query: str) -> List:
    """For web search"""
    return DDGS().text(query, max_results=5)

@tool
@with_loading("Fetching website content")
def get_url(url: str) -> List:
    """Fetch a URL and extract its content."""
    return DDGS().extract(url)

@tool
@with_loading("Searching On Web")
def get_news(query: str) -> List:
    """Get news about the query"""
    return DDGS().news(query=query)

@tool
@with_loading()
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
@with_loading()
def get_date() -> str:
    """Get current Date+Time"""
    return str(datetime.now())
