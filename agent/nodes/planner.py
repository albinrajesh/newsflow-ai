from langchain_community.chat_models import ChatOllama
from agent.state import AgentState

llm = ChatOllama(model="mistral", temperature=0)

async def planner_node(state: AgentState) -> dict:
    """
    Uses Mistral to break the query into search steps.
    """
    query = state["query"]
    print(f"[Planner] Local Mistral is planning for: {query}")

    prompt = f"""Break this research query into 3 specific search sub-questions.
    Query: {query}
    Output ONLY the questions, one per line."""

    try:
        response = await llm.ainvoke(prompt)
        sub_questions = [q.strip() for q in response.content.split("\n") if q.strip()]
        
        # Limit to top 3 for speed
        return {"sub_questions": sub_questions[:3]}
    except Exception as e:
        print(f"[Planner] Error: {e}")
        return {"sub_questions": [query]} # Fallback to original query