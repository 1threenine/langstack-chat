from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langstack_chat.config import CliConfig
from langstack_chat.tools import ALL_TOOLS

config = CliConfig()


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="qwen",
        base_url=config.base_url,
        api_key=config.openai_api_key,
    )


def build_agent(llm, checkpointer):
    return create_agent(
        llm,
        tools=ALL_TOOLS,
        system_prompt="You are a helpful assistant",
        checkpointer=checkpointer,
    )
