from langgraph.graph import StateGraph, END
from app.config import settings

from agent.state import AgentState
from agent.nodes.planner import planner_node
from agent.nodes.researcher import researcher_node
from agent.nodes.grader import grader_node
from agent.nodes.synthesiser import synthesiser_node
from agent.nodes.hallucination_checker import hallucination_checker_node

# --- Router logic ---
def route_after_grader(state: AgentState) -> str:
    # If no relevant docs found, go back to PLANNER to try new keywords
    if state.get("needs_retry") and state.get("retry_count", 0) < settings.max_retries:
        print(f"!!! No relevant docs found. Re-planning (Retry {state['retry_count']+1})...")
        return "re_plan"
    return "synthesiser"

def route_after_checker(state: AgentState) -> str:
    # If hallucination detected, start fresh from PLANNER
    if state.get("has_hallucination") and state.get("retry_count", 0) < settings.max_retries:
        print("!!! Hallucination detected. Re-starting research...")
        return "re_plan"
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
    
    # Standard linear flow
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "grader")
    
    # --- The Re-Planning Loop ---
    workflow.add_conditional_edges(
        "grader",
        route_after_grader,
        {
            "re_plan": "planner", # Loops back to the beginning
            "synthesiser": "synthesiser"
        }
    )
    
    workflow.add_edge("synthesiser", "checker")
    
    # --- The Hallucination Loop ---
    workflow.add_conditional_edges(
        "checker",
        route_after_checker,
        {
            "re_plan": "planner", 
            END: END
        }
    )

    # 3. Compilation (Stateless)
    return workflow.compile()

# Create the compiled agent instance
agent = build_graph()