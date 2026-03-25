import asyncio
from langchain_community.chat_models import ChatOllama
from agent.state import AgentState

llm = ChatOllama(model="mistral", temperature=0)
# Limit to 3 concurrent requests to keep local inference stable
sem = asyncio.Semaphore(3) 

async def grader_node(state: AgentState) -> dict:
    docs = state.get("retrieved_docs", [])
    query = state.get("query", "")
    
    if not docs:
        return {"graded_docs": [], "needs_retry": True}

    print(f"[Grader] Evaluating {len(docs)} docs (Concurrency Limit: 3)...")

    async def grade_single_doc(doc):
        # The semaphore ensures only 3 docs hit Mistral at once
        async with sem:
            prompt = f"Query: {query}\nDocument: {doc}\nRelevant? YES/NO:"
            try:
                response = await llm.ainvoke(prompt)
                return doc if "YES" in response.content.upper() else None
            except Exception as e:
                print(f"Grader Error: {e}")
                return doc # Fallback: keep doc

    results = await asyncio.gather(*[grade_single_doc(d) for d in docs])
    graded_docs = [r for r in results if r is not None]
    
    print(f"[Grader] Done. {len(graded_docs)} relevant docs found.")
    return {"graded_docs": graded_docs, "needs_retry": len(graded_docs) == 0}