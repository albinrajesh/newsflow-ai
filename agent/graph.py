from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.planner import planner_node
from agent.nodes.researcher import researcher_node
from agent.nodes.grader import grader_node
from agent.nodes.synthesiser import synthesiser_node
from agent.nodes.hallucination_checker import hallucination_checker_node

def route_after_grader(state: AgentState) -> str:
    if state["needs_retry"] and state["retry_count"] < 3:
        print(f"[Router] Grader requested more data... Retrying.")
        return "researcher"
    return "synthesiser"

def route_after_checker(state: AgentState) -> str:
    if state["has_hallucination"] and state["retry_count"] < 3:
        print(f"[Router] Hallucination detected! Sending back for better research.")
        return "researcher"
    return END

def build_graph():
    graph = StateGraph(AgentState)
    
    # Add Nodes
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("grader", grader_node)
    graph.add_node("synthesiser", synthesiser_node)
    graph.add_node("checker", hallucination_checker_node)

    # Define Edges
    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "grader")
    
    graph.add_conditional_edges(
        "grader",
        route_after_grader,
        {"researcher": "researcher", "synthesiser": "synthesiser"}
    )
    
    graph.add_edge("synthesiser", "checker")
    
    graph.add_conditional_edges(
        "checker",
        route_after_checker,
        {"researcher": "researcher", END: END}
    )

    return graph.compile()

agent = build_graph()