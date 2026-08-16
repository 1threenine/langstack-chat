from datetime import datetime
from unittest import result
from ddgs import DDGS
from langchain.tools import tool
from langstack_chat.utils.console import console
from functools import wraps
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

# def with_loading(message="Calling tool..."):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 with console.status(f"[bold cyan]{message}", spinner="dots"):
#                     return func(*args, **kwargs)
#             except Exception as e:
#                 logger.error("Tool `%s` failed: %s", func.__name__, e, exc_info=False)
#                 return f"Error: {str(e)}"
#         return wrapper
#     return decorator

@tool
def web_search(query: str) -> list:
    """Search the web for a query. Use for current events, facts, or anything requiring up-to-date information. Returns top 5 results with title, URL, and snippet."""
    try:
        with console.status(f"[bold cyan]Searching for '{query}'...", spinner="dots"):
            results = DDGS().text(query, max_results=5)

        if results:
            console.print("[dim]Sources:[/dim]")
            for i, r in enumerate(results, 1):
                console.print(f"[dim]  {i}. {r.get('title', 'No title')} — {r.get('href', '')}[/dim]")

        return results
    except Exception as e:
        logger.error("Tool `web_search` failed: %s", e)
        return f"Error: {str(e)}"

@tool
def get_url(url: str) -> list:
    """Fetch and extract readable text content from a given URL. Use when the user provides a link or you need full page content."""
    try:
        with console.status(f"[bold cyan]Fetching {url}...", spinner="dots"):
            return DDGS().extract(url)
    except Exception as e:
        logger.error("Tool `get_url` failed: %s", e)
        return f"Error: {str(e)}"

@tool
def get_news(query: str) -> list:
    """Search for recent news articles on a topic. Use for news, headlines, or recent developments. Returns title, source, date, and URL."""
    try:
        with console.status(f"[bold cyan]Searching for news about '{query}'...", spinner="dots"):
            return DDGS().news(query=query, max_results=5)
    except Exception as e:
        logger.error("Tool `get_news` failed: %s", e)
        return f"Error: {str(e)}"

@tool
# @with_loading("Fetching weather...")
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use when the user asks about weather, temperature, or forecast."""
    return f"It's always sunny in {city}!"  # replace with real API

@tool
def get_datetime() -> str:
    """Get the current local date and time. Use when the user asks what time or date it is."""
    try:
        with console.status("[bold cyan]Getting date and time...", spinner="dots"):
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        logger.error("Tool `get_datetime` failed: %s", e)
        return f"Error: {str(e)}"

@tool
def get_time() -> str:
    """Get the current local time only (HH:MM:SS). Use when the user asks only for the time."""
    try:
        with console.status("[bold cyan]Getting time...", spinner="dots"):
            return datetime.now().strftime("%H:%M:%S")
    except Exception as e:
        logger.error("Tool `get_time` failed: %s", e)
        return f"Error: {str(e)}"


ALL_TOOLS = [
    web_search, get_url, get_news, get_datetime, get_time,
]
