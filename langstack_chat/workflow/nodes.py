from langchain_core.messages import AIMessage, HumanMessage
from langstack_chat.workflow.state import AgentState
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

def classify_intent(state: AgentState, llm) -> AgentState:
    last_message = state["messages"][-1].content

    prompt = f"""Classify this user message into one of: chitchat, tools, unsafe.
- chitchat: general conversation, greetings, opinions
- tools: requires web search, news, weather
- unsafe: harmful, illegal, or malicious requests

Message: {last_message}
Reply with only one word: chitchat, tools, or unsafe."""

    result = llm.invoke([HumanMessage(content=prompt)])
    intent = result.content.strip().lower()

    if intent not in ("chitchat", "tools", "unsafe"):
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
    from langstack_chat.utils.retry import with_retry

    response = with_retry(lambda: llm_with_tools.invoke(state["messages"]))

    logger.info("LLM responded.")
    return {"messages": [response]}
