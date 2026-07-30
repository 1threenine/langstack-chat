from pathlib import Path
from typing import Optional
import tomllib
from pydantic_settings import BaseSettings
import tomlkit
import questionary
from rich.console import Console


class AppConfig(BaseSettings):
    """User-specific CLI configuration (stored in TOML)"""
    psql_url: str = ""
    openai_api_key: str = ""
    aws_bearer_token_bedrock: str = ""
    default_model: str = ""
    default_provider: str = "Llama.cpp"
    base_url: str = "http://127.0.0.1:8080/v1"

    class Config:
        env_prefix = ""  # No prefix for env vars
        env_file = ".env"
        env_file_encoding = "utf-8"


class ConfigManager:
    """Manages TOML config file creation and loading"""

    def __init__(self):
        self.config_dir = Path.cwd() / ".config"
        self.config_file = self.config_dir / "config.toml"

    def load_or_create(self) -> dict:
        """Load existing config or create default on first run"""
        if self.config_file.exists():
            with open(self.config_file, "rb") as f:
                return tomllib.load(f)
        else:
            return self._create_default_config()

    def _create_default_config(self) -> dict:
        """Create default config file with user prompts"""

        console = Console()
        console.print("\n[bold cyan]First-time setup - Creating configuration...[/bold cyan]\n")

        provider = questionary.select(
            "Default LLM Provider:",
            choices=["Llama.cpp", "Bedrock", "OpenAI"]
        ).ask()

        # psql_url = questionary.text(
        #     "PostgreSQL connection URL:",
        #     default=""
        # ).ask()

        # openai_key = questionary.text(
        #     "OpenAI API Key (optional, press Enter to skip):",
        #     default=""
        # ).ask()

        default_config = {
            "app": {
                "default_provider": provider,
                "default_model": "qwen"
            },
            "database": {
                "psql_url": ""
            },
            "api_keys": {
                "openai_api_key": "",
                "aws_bearer_token_bedrock": ""
            }
        }

        self.config_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w") as f:
            tomlkit.dump(default_config, f)

        console.print(f"\n[green]✓ Configuration created at: {self.config_file}[/green]\n")

        return default_config


class CliConfig:
    """Main config class - combines TOML file + env vars"""

    def __init__(self):
        manager = ConfigManager()
        config_data = manager.load_or_create()

        # Flatten TOML structure for Pydantic
        flat_config = {
            k : v for k, v in {
                **config_data.get("app", {}),
                **config_data.get("database", {}),
                **config_data.get("api_keys", {})
            }.items() if v
        }

        # Override with env vars (env vars take precedence)
        self.settings = AppConfig(**flat_config)


    @property
    def psql_url(self) -> str:
        return self.settings.psql_url

    @property
    def openai_api_key(self) -> str:
        return self.settings.openai_api_key

    @property
    def default_provider(self) -> str:
        return self.settings.default_provider

    @property
    def base_url(self) -> str:
        return self.settings.base_url
