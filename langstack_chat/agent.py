from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI
from langstack_chat.config import CliConfig
from langstack_chat.tools import ALL_TOOLS
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

config = CliConfig()


def build_llm(provider: str, model: str):
    if provider == "Llama.cpp":
        return ChatOpenAI(model=model, base_url=config.base_url, api_key="na")

    elif provider == "OpenAI":
        return ChatOpenAI(model=model, api_key=config.openai_api_key)

    elif provider == "Bedrock":
        return ChatBedrock(model_id=model, region_name=config.aws_region)

    raise ValueError(f"Unsupported provider: {provider}")

def fetch_models(provider: str) -> list[str]:

    try:
        if provider == "Llama.cpp":
            import httpx
            resp = httpx.get(f"{config.base_url}/models")
            return [m["id"] for m in resp.json()["data"]]

        elif provider == "OpenAI":
            if not config.openai_api_key or config.openai_api_key == "no-api-key":
                logger.warning("OpenAI API key not configured.")
                return []
            from openai import OpenAI
            return [m.id for m in OpenAI(api_key=config.openai_api_key).models.list()]

        elif provider == "Bedrock":
            import boto3
            client = boto3.client("bedrock", region_name=config.aws_region)
            models = client.list_foundation_models()["modelSummaries"]
            return [m["modelId"] for m in models]

    except Exception as e:
        logger.error("Failed to fetch models for %s: %s", provider, e)
        return []

def build_agent(llm, checkpointer):
    return create_agent(
        llm,
        tools=ALL_TOOLS,
        system_prompt="You are a helpful assistant",
        checkpointer=checkpointer,
    )
