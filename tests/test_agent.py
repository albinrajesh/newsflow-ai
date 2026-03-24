import sys
import os
from dotenv import load_dotenv # ADD THIS
from langfuse.langchain import CallbackHandler 

# 1. LOAD ENV BEFORE ANYTHING ELSE
load_dotenv() 

# Force project root into path
sys.path.append(os.getcwd())

from agent.graph import agent
from agent.state import AgentState

def run_manual_test():
    # 2. This will now find LANGFUSE_PUBLIC_KEY and LANGFUSE_HOST automatically
    langfuse_handler = CallbackHandler() 

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

    try:
        # 3. Use 'configurable' to give your trace a name in the dashboard
        config = {
            "callbacks": [langfuse_handler], 
            "recursion_limit": 50,
            "configurable": {"thread_id": "manual_test_01"}
        }
        
        print("[DEBUG] Running agent with Langfuse tracing...")
        final_output = agent.invoke(initial_state, config=config)

        print("\n" + "="*50)
        print("FINAL AGENT REPORT")
        print("="*50)
        print(final_output.get("final_report", "No report generated."))
        print("="*50)
        print(f"Total Sources Used: {len(final_output.get('graded_docs', []))}")
        
        print("\n[SUCCESS] Trace sent to Langfuse!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_manual_test()