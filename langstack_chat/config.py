from pydantic_settings import BaseSettings
from typing import Optional

class CliConfig(BaseSettings):
    # Required
    psql_url: str

    # Optional with defaults
    openai_api_key: str = ""
    aws_bearer_token_bedrock: str = ""


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
