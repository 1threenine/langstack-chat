from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from datetime import datetime
from langchain.tools import tool
from ddgs import DDGS
from typing import List

load_dotenv()

@tool
def web_search(query: str) -> List:
    """For web search"""
    return (DDGS().text(query, max_results=5))

@tool
def get_news(query: str) -> List:
    """Get news about the query"""
    return (DDGS().news(query=query))

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def get_date() -> str:
    """Get current Date+Time"""
    return str(datetime.now())

def main():
    llm = ChatOpenAI(
        model="qwen",
        base_url="http://127.0.0.1:8080/v1", # using Llama.cpp
    )

    agent = create_agent(llm, tools=[get_weather, get_date, get_news, web_search], system_prompt="You are a helpful assistant",)

    try:
        while True:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": input("Enter query: ")}]}
            )
            print(result["messages"][-1].content)

    except KeyboardInterrupt:
        print("\nFin")


if __name__ == "__main__":
    main()
