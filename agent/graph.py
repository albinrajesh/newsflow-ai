from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver # <--- Use MemorySaver
from app.config import settings

from agent.state import AgentState
from agent.nodes.planner import planner_node
from agent.nodes.researcher import researcher_node
from agent.nodes.grader import grader_node
from agent.nodes.synthesiser import synthesiser_node
from agent.nodes.hallucination_checker import hallucination_checker_node

# --- Router logic ---
def route_after_grader(state: AgentState) -> str:
    if state.get("needs_retry") and state.get("retry_count", 0) < settings.max_retries:
        return "researcher"
    return "synthesiser"

def route_after_checker(state: AgentState) -> str:
    if state.get("has_hallucination") and state.get("retry_count", 0) < settings.max_retries:
        return "researcher"
    return END

def build_graph():
    workflow = StateGraph(AgentState)
    
    # 1. Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("grader", grader_node)
    workflow.add_node("synthesiser", synthesiser_node)
    workflow.add_node("checker", hallucination_checker_node)

    # 2. Define Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "grader")
    
    workflow.add_conditional_edges(
        "grader",
        route_after_grader,
        {"researcher": "researcher", "synthesiser": "synthesiser"}
    )
    
    workflow.add_edge("synthesiser", "checker")
    
    workflow.add_conditional_edges(
        "checker",
        route_after_checker,
        {"researcher": "researcher", END: END}
    )

    # 3. Persistence Setup (Memory Version)
    # This works perfectly with async nodes and requires no setup
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)

# Create the compiled agent instance
agent = build_graph()