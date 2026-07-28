from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from datetime import datetime
from langchain.tools import tool

load_dotenv()

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

    agent = create_agent(llm, tools=[get_weather, get_date], system_prompt="You are a helpful assistant",)

    while True:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": input("Enter query: ")}]}
        )
        print(result["messages"][-1].content_blocks)


if __name__ == "__main__":
    main()
