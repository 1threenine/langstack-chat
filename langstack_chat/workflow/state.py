from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Literal["chitchat", "tools", "rag", "unsafe"] | None
    tool_results: list | None
    retries: int
    rag_context: str | None   # ADD THIS
