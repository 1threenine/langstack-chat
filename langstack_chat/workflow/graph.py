from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langstack_chat.workflow.state import AgentState
from langstack_chat.workflow.nodes import classify_intent, guardrail, run_llm, retry_llm
from langstack_chat.tools import ALL_TOOLS
from langstack_chat.utils.logging import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3

def _route(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "unsafe":
        return "guardrail"
    return "llm"

def _should_retry(state: AgentState) -> str:
    last = state["messages"][-1]
    retries = state.get("retries", 0)

    if last.tool_calls:
        return "tools"

    # retry if response is empty or too short
    if len(last.content.strip()) < 5 and retries < MAX_RETRIES:
        return "retry"

    return END

def build_graph(llm, checkpointer):
    graph = StateGraph(AgentState)

    graph.add_node("classifier", partial(classify_intent, llm=llm))
    graph.add_node("guardrail", guardrail)
    graph.add_node("llm", partial(run_llm, llm=llm, tools=ALL_TOOLS))
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_node("retry", partial(retry_llm, llm=llm, tools=ALL_TOOLS))


    graph.set_entry_point("classifier")

    graph.add_conditional_edges("classifier", _route, {
        "guardrail": "guardrail",
        "llm": "llm",
    })

    # if LLM calls a tool, execute it then come back to LLM
    # graph.add_conditional_edges("llm", lambda s: "tools" if s["messages"][-1].tool_calls else END, {
    #     "tools": "tools",
    #     END: END,
    # })

    graph.add_conditional_edges("llm", _should_retry, {
        "tools": "tools",
        "retry": "retry",
        END: END,
    })

    graph.add_edge("tools", "llm")
    graph.add_edge("retry", "llm")
    graph.add_edge("guardrail", END)

    return graph.compile(checkpointer=checkpointer)
