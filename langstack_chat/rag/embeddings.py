from langchain_core.embeddings import Embeddings
from langstack_chat.config import CliConfig
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)
config = CliConfig()


def get_embeddings(provider: str = "Llama.cpp") -> Embeddings:
    provider = provider or config.default_provider
    if provider == "Llama.cpp":
        from langchain_openai import OpenAIEmbeddings
        logger.info("Using Llama.cpp embeddings")
        return OpenAIEmbeddings(api_key=config.openai_api_key, base_url=config.embedding_base_url)

    elif provider == "OpenAI":
        from langchain_openai import OpenAIEmbeddings
        logger.info("Using OpenAI embeddings")
        return OpenAIEmbeddings(api_key=config.openai_api_key)

    elif provider == "Bedrock":
        from langchain_aws import BedrockEmbeddings
        logger.info("Using Bedrock embeddings")
        return BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v1",
            region_name=config.aws_region,
        )

    raise ValueError(f"Unsupported provider for embeddings: {provider}")
