from langchain_core.messages import AIMessage, HumanMessage
from langstack_chat.workflow.state import AgentState
from langstack_chat.utils.logging import get_logger
from langstack_chat.rag import retrieve, format_context
from langstack_chat.utils.retry import with_retry

logger = get_logger(__name__)

def classify_intent(state: AgentState, llm) -> AgentState:
    last_message = state["messages"][-1].content

    prompt = f"""Classify this user message into one of: chitchat, tools, rag, unsafe.
- chitchat: general conversation, greetings, opinions
- tools: requires web search, news, weather
- rag: questions about uploaded documents or files
- unsafe: harmful, illegal, or malicious requests

Message: {last_message}
Reply with only one word: chitchat, tools, rag, or unsafe."""

    result = llm.invoke([HumanMessage(content=prompt)])
    intent = result.content.strip().lower()

    if intent not in ("chitchat", "tools", "rag", "unsafe"):
        intent = "chitchat"

    logger.info("Intent classified: %s", intent)
    return {"intent": intent}

def retry_llm(state: AgentState, llm, tools) -> AgentState:
    retries = state.get("retries", 0)
    logger.warning("Retrying LLM... attempt %d", retries + 1)
    return {"retries": retries + 1}

def guardrail(state: AgentState) -> AgentState:
    """Block unsafe messages."""
    logger.warning("Unsafe input blocked.")
    return {
        "messages": [AIMessage(content="I can't help with that.")]
    }


def run_llm(state: AgentState, llm, tools) -> AgentState:
    """Main LLM node with tools bound."""
    llm_with_tools = llm.bind_tools(tools)
    # response = llm_with_tools.invoke(state["messages"])
    response = with_retry(lambda: llm_with_tools.invoke(state["messages"]))

    logger.info("LLM responded.")
    return {"messages": [response]}


def rag_node(state: AgentState, llm) -> AgentState:
    query = state["messages"][-1].content

    docs = retrieve(query)

    if not docs:
        logger.warning("No relevant documents found for query.")
        return {"messages": [AIMessage(content="I couldn't find relevant information in the loaded documents.")]}

    context = format_context(docs)

    prompt = f"""Answer the user's question using only the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question: {query}"""

    response = with_retry(lambda: llm.invoke([HumanMessage(content=prompt)]))
    logger.info("RAG node responded.")
    return {"messages": [response]}
