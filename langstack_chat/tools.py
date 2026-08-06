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
            try:
                with console.status(f"[bold cyan]{message}", spinner="dots"):
                    return func(*args, **kwargs)
            except Exception as e:
                console.print(f"[red]Tool error in `{func.__name__}`:[/red] {e}")
                return f"Error: {str(e)}"
        return wrapper
    return decorator

@tool
@with_loading("Searching the web...")
def web_search(query: str) -> list:
    """Search the web for a query. Use for current events, facts, or anything requiring up-to-date information. Returns top 5 results with title, URL, and snippet."""
    return DDGS().text(query, max_results=5)

@tool
@with_loading("Fetching URL content...")
def get_url(url: str) -> list:
    """Fetch and extract readable text content from a given URL. Use when the user provides a link or you need full page content."""
    return DDGS().extract(url)

@tool
@with_loading("Fetching news...")
def get_news(query: str) -> list:
    """Search for recent news articles on a topic. Use for news, headlines, or recent developments. Returns title, source, date, and URL."""
    return DDGS().news(query=query, max_results=5)

@tool
@with_loading("Fetching weather...")
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use when the user asks about weather, temperature, or forecast."""
    return f"It's always sunny in {city}!"  # replace with real API

@tool
@with_loading("Getting date and time...")
def get_datetime() -> str:
    """Get the current local date and time. Use when the user asks what time or date it is."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

@tool
@with_loading("Getting time...")
def get_time() -> str:
    """Get the current local time only (HH:MM:SS). Use when the user asks only for the time."""
    return datetime.now().strftime("%H:%M:%S")


ALL_TOOLS = [
    web_search, get_url, get_news, get_weather,
    get_datetime, get_time,
]
