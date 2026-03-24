from langchain_community.chat_models import ChatOllama
from agent.state import AgentState

# Connect to your local Mistral
# Mistral is perfect for binary decisions like YES/NO
llm = ChatOllama(model="mistral", temperature=0)

async def grader_node(state: AgentState) -> dict:
    """
    Evaluates document relevance using LOCAL Mistral 7B.
    This node is now lightning-fast with zero API cost.
    """
    docs = state.get("retrieved_docs", [])
    query = state.get("query", "")
    
    if not docs:
        print("[Grader] No documents found to grade.")
        return {"graded_docs": [], "needs_retry": True}

    print(f"[Grader] Local Mistral is evaluating {len(docs)} documents...")
    
    graded_docs = []
    for doc in docs:
        # NO MORE SLEEPS! Mistral runs as fast as your hardware allows.
        prompt = f"""Is the following document useful for answering this query: '{query}'?
        Answer ONLY 'YES' or 'NO'.
        
        DOCUMENT: {doc}
        """
        
        try:
            response = await llm.ainvoke(prompt)
            verdict = response.content.strip().upper()
            
            if "YES" in verdict:
                graded_docs.append(doc)
        except Exception as e:
            print(f"[Grader] Error processing doc: {e}")
            graded_docs.append(doc) # Fallback: keep the doc if model errors

    print(f"[Grader] Done. Found {len(graded_docs)} relevant docs.")
    
    return {
        "graded_docs": graded_docs,
        "needs_retry": len(graded_docs) == 0
    }