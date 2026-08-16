from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langstack_chat.rag.embeddings import get_embeddings
from langstack_chat.utils.logging import get_logger
from langstack_chat.config import CliConfig
from langstack_chat.utils.console import console

config = CliConfig()

CHROMA_DIR = str(config.data_dir / "chroma")
CHROMA_BATCH_SIZE = 500


logger = get_logger(__name__)


def get_vectorstore(provider: str = "Llama.cpp") -> Chroma:
    embeddings = get_embeddings(provider)
    return Chroma(
        collection_name="langstack",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

def add_documents(docs: list[Document], provider: str | None = None) -> int:
    vs = get_vectorstore(provider)
    total_batches = -(-len(docs) // CHROMA_BATCH_SIZE)

    for i in range(0, len(docs), CHROMA_BATCH_SIZE):
        batch = docs[i:i + CHROMA_BATCH_SIZE]
        batch_num = i // CHROMA_BATCH_SIZE + 1
        with console.status(f"[bold cyan]Storing batch {batch_num}/{total_batches}...", spinner="dots"):
            vs.add_documents(batch)
        logger.info("Uploaded batch %d/%d", batch_num, total_batches)

    console.print(f"[green]✓ Stored {len(docs)} chunks in vectorstore[/green]")
    logger.info("Added %d chunks to vectorstore", len(docs))
    return len(docs)


def clear_vectorstore(provider: str | None = None) -> None:
    vs = get_vectorstore(provider)
    vs.delete_collection()
    logger.warning("Vectorstore cleared.")
