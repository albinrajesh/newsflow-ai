import httpx
import asyncio
from typing import Dict, Any, List
from agent.state import AgentState
from rag.retriever import retrieve
from app.config import settings

async def researcher_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieves documents from local FAISS and MCP Web Search.
    Handles 'unhashable type' errors by ensuring all docs are strings.
    """
    print(f"\n[Researcher] Processing {len(state.get('sub_questions', []))} sub-questions...")
    all_docs = []
    
    # 1. Local FAISS Retrieval
    # We use asyncio.to_thread because retrieve() in rag/retriever.py is synchronous
    try:
        sub_questions = state.get("sub_questions", [state["query"]])
        retrieval_tasks = [
            asyncio.to_thread(retrieve, query, top_k=2) 
            for query in sub_questions
        ]
        
        retrieval_results = await asyncio.gather(*retrieval_tasks)
        
        for result in retrieval_results:
            if isinstance(result, list):
                # Ensure every item in the list is a string
                all_docs.extend([str(item) for item in result])
            else:
                all_docs.append(str(result))
                
        print(f"[Researcher] Local FAISS found {len(all_docs)} chunks.")
    except Exception as e:
        print(f"[Researcher] Local Retrieval Error: {e}")

    # 2. MCP Web Search (Async HTTPX)
    if settings.mcp_server_url:
        try:
            async with httpx.AsyncClient() as client:
                print(f"[Researcher] Connecting to MCP at {settings.mcp_server_url}...")
                mcp_response = await client.post(
                    f"{settings.mcp_server_url}/tools/web_search",
                    json={"query": state["query"], "max_results": 3},
                    timeout=10.0 
                )
                
                if mcp_response.status_code == 200:
                    web_results = mcp_response.json().get("results", [])
                    for res in web_results:
                        content = res.get('content', '')
                        url = res.get('url', 'unknown')
                        all_docs.append(f"Web Source [{url}]: {content}")
                    print(f"[Researcher] MCP Search added {len(web_results)} results.")
        except Exception as e:
            print(f"[Researcher] MCP Search skipped due to error: {e}")

    # 3. Defensive Duplicate Removal (Fixes 'unhashable type: list')
    unique_docs = []
    seen = set()
    
    for doc in all_docs:
        # Final safety check: if 'doc' is somehow still a list, join it into a string
        clean_doc = " ".join(doc) if isinstance(doc, list) else str(doc)
        
        if clean_doc not in seen:
            unique_docs.append(clean_doc)
            seen.add(clean_doc)
    
    print(f"[Researcher] Total unique documents gathered: {len(unique_docs)}")
    
    # Return the dictionary to update the global LangGraph state
    return {"retrieved_docs": unique_docs}