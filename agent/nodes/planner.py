from langchain_community.chat_models import ChatOllama
from agent.state import AgentState

# Local Mistral for fast, cost-effective planning
llm = ChatOllama(model="mistral", temperature=0.7)

async def planner_node(state: AgentState) -> dict:
    """
    Analyzes the user query and generates 3 sub-questions for research.
    If it's a retry, it adjusts the strategy to find better results.
    """
    query = state.get("query", "")
    # Current total of retries from the state
    current_retries = state.get("retry_count", 0)
    
    # Adaptive prompting: If we've failed before, tell the LLM to change tactics
    retry_context = ""
    if current_retries > 0:
        retry_context = (
            f"\nNOTE: This is attempt #{current_retries + 1}. "
            "Previous searches yielded no relevant results. "
            "Please generate BROADER or ALTERNATIVE search queries to find information.\n"
        )

    print(f"[Planner] Planning for: '{query}' (Total Retries so far: {current_retries})")

    prompt = f"""{retry_context}
    The user wants to know: {query}
    
    Task: Generate 3 distinct search sub-questions that will help a researcher find the most accurate answer.
    Format: Provide only the questions, one per line. No introduction or numbering.
    """
    
    try:
        response = await llm.ainvoke(prompt)
        # Parse the lines into a list
        questions = [q.strip() for q in response.content.split("\n") if q.strip() and "?" in q]
        
        # If the LLM failed to give lines with questions, fallback to the original query
        if not questions:
            questions = [query]

        return {
            "sub_questions": questions, 
            "retry_count": 1,  # This ADDS 1 to the state's total via operator.add
            "needs_retry": False # Reset the flag so we don't loop infinitely
        }

    except Exception as e:
        print(f"[Planner] Error: {e}")
        return {
            "sub_questions": [query], 
            "retry_count": 1,
            "needs_retry": False
        }