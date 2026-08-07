import logging
from pathlib import Path
from rich.logging import RichHandler

LOG_DIR = Path.cwd() / ".logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging(level: str = "INFO") -> None:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    file_handler = logging.FileHandler(LOG_DIR / "langstack.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))

    rich_handler = RichHandler(rich_tracebacks=True, show_path=False, level=logging.WARNING)

    logging.basicConfig(level=level, handlers=[file_handler, rich_handler])

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
