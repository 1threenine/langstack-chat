from langchain_core.documents import Document
from langstack_chat.rag.vectorstore import get_vectorstore
from langstack_chat.utils.logging import get_logger
from langstack_chat.utils.console import console

logger = get_logger(__name__)


def retrieve(query: str, k: int = 4, provider: str | None = None) -> list[Document]:
    with console.status("[bold cyan]Retrieving from knowledge base...", spinner="dots"):
        vs = get_vectorstore(provider)
        docs = vs.similarity_search(query, k=k)

    console.print(f"[dim]Retrieved {len(docs)} chunks[/dim]")
    logger.info("Retrieved %d chunks for query: %s", len(docs), query[:50])
    return docs


def format_context(docs: list[Document]) -> str:
    """Format retrieved docs into a single context string for LLM prompt."""
    chunks = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        chunks.append(f"[{i}] Source: {source}\n{doc.page_content}")
    return "\n\n".join(chunks)
