from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,           # .pdf
    Docx2txtLoader,        # .docx
    TextLoader,            # .txt
    UnstructuredMarkdownLoader,  # .md
    CSVLoader,             # .csv
    UnstructuredExcelLoader,     # .xlsx
    UnstructuredPowerPointLoader, # .pptx
    UnstructuredHTMLLoader,      # .html
    PythonLoader,          # .py
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

LOADERS = {
    ".pdf":  PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt":  TextLoader,
    ".md":   UnstructuredMarkdownLoader,
    ".csv":  CSVLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".pptx": UnstructuredPowerPointLoader,
    ".html": UnstructuredHTMLLoader,
    ".htm":  UnstructuredHTMLLoader,
    ".json": TextLoader,
    ".py":   PythonLoader,
}

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)


def load_document(path: str) -> list[Document]:
    file = Path(path).expanduser().resolve()

    if not file.exists():
        logger.error("File not found: %s", path)
        raise FileNotFoundError(f"File not found: {path}")

    ext = file.suffix.lower()
    loader_cls = LOADERS.get(ext)

    if not loader_cls:
        logger.error("Unsupported file type: %s", ext)
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(LOADERS.keys())}")

    try:
        logger.info("Loading %s (%s)", file.name, ext)
        loader = loader_cls(str(file))
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        logger.info("Loaded %d chunks from %s", len(chunks), file.name)
        return chunks
    except Exception as e:
        logger.error("Failed to load %s: %s", file.name, e)
        raise RuntimeError(f"Failed to load {file.name}: {e}")
