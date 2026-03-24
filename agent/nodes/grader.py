import asyncio
from langchain_community.chat_models import ChatOllama
from agent.state import AgentState

# Connect to your local Mistral
# temperature=0 is essential for consistent YES/NO answers
llm = ChatOllama(model="mistral", temperature=0)

async def grader_node(state: AgentState) -> dict:
    """
    Evaluates document relevance using LOCAL Mistral 7B in PARALLEL.
    """
    docs = state.get("retrieved_docs", [])
    query = state.get("query", "")
    
    if not docs:
        print("[Grader] No documents found to grade.")
        return {"graded_docs": [], "needs_retry": True}

    print(f"[Grader] Local Mistral is evaluating {len(docs)} documents in parallel...")

    # --- INTERNAL HELPER FUNCTION ---
    async def grade_single_doc(doc):
        """Helper to grade one document asynchronously."""
        prompt = f"""Is the following document useful for answering this query: '{query}'?
        Answer ONLY 'YES' or 'NO'.
        
        DOCUMENT: {doc}
        """
        try:
            # Note: Using ainvoke for async compatibility
            response = await llm.ainvoke(prompt)
            verdict = response.content.strip().upper()
            
            if "YES" in verdict:
                return doc
            return None
        except Exception as e:
            print(f"[Grader] Error processing doc: {e}")
            # Fallback: keep the doc if model errors to avoid losing potential data
            return doc

    # --- PARALLEL EXECUTION ---
    # asyncio.gather schedules all calls at once
    tasks = [grade_single_doc(doc) for doc in docs]
    results = await asyncio.gather(*tasks)

    # Filter out the 'None' results (irrelevant docs)
    graded_docs = [doc for doc in results if doc is not None]

    print(f"[Grader] Done. Found {len(graded_docs)} relevant docs.")
    
    return {
        "graded_docs": graded_docs,
        "needs_retry": len(graded_docs) == 0
    }