import sys
import os

# Force the project root into the python path
sys.path.append(os.getcwd())

from agent.graph import agent
from agent.state import AgentState

def run_manual_test():
    print("\n[DEBUG] Starting the Agent Test Script...")
    
    # 1. Define Initial State
    initial_state = {
        "query": "What are the latest AI trends in 2026?",
        "sub_questions": [],
        "retrieved_docs": [],
        "graded_docs": [],
        "needs_retry": False,
        "retry_count": 0,
        "final_report": "",
        "has_hallucination": False,
        "fallback_triggered": False
    }

    print(f"[DEBUG] Invoking Graph with query: {initial_state['query']}")
    
    try:
        # 2. Run the Graph
        # We use a recursion_limit to ensure it doesn't loop forever
        config = {"recursion_limit": 50}
        final_output = agent.invoke(initial_state, config=config)

        # 3. Print Results
        print("\n" + "="*50)
        print("FINAL AGENT REPORT")
        print("="*50)
        print(final_output["final_report"])
        print("="*50)
        print(f"Total Sources Used: {len(final_output['graded_docs'])}")
        
    except Exception as e:
        print(f"\n[FATAL ERROR] The agent crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_manual_test()