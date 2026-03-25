import httpx
import asyncio
from typing import Dict, Any, List
from agent.state import AgentState
from rag.retriever import retrieve
from app.config import settings

async def researcher_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieves documents from local FAISS with source-filtering and MCP Web Search.
    """
    query = state.get("query", "")
    # New: Check if the user specified a specific source in the state
    current_source = state.get("current_source") 
    
    print(f"\n[Researcher] Planning {len(state.get('sub_questions', []))} sub-questions...")
    if current_source:
        print(f"[Researcher] Context restricted to source: {current_source}")

    all_docs = []
    
    # 1. Local FAISS Retrieval
    try:
        sub_questions = state.get("sub_questions", [query])
        
        # We pass the 'source' filter to our updated retrieve function
        retrieval_tasks = [
            asyncio.to_thread(retrieve, q, top_k=3, source=current_source) 
            for q in sub_questions
        ]
        
        retrieval_results = await asyncio.gather(*retrieval_tasks)
        
        for result in retrieval_results:
            for doc in result:
                # If 'doc' is a LangChain Document object, extract content + source
                if hasattr(doc, 'page_content'):
                    source_info = doc.metadata.get('source', 'Local Index')
                    content = doc.page_content
                    all_docs.append(f"Source [{source_info}]: {content}")
                else:
                    all_docs.append(str(doc))
                
        print(f"[Researcher] Local FAISS found {len(all_docs)} relevant chunks.")
    except Exception as e:
        print(f"[Researcher] Local Retrieval Error: {e}")

    # 2. MCP Web Search (Only if local search doesn't find enough or if no specific source is set)
    if settings.mcp_server_url and not current_source:
        try:
            async with httpx.AsyncClient() as client:
                print(f"[Researcher] Searching web via MCP...")
                mcp_response = await client.post(
                    f"{settings.mcp_server_url}/tools/web_search",
                    json={"query": query, "max_results": 3},
                    timeout=10.0 
                )
                
                if mcp_response.status_code == 200:
                    web_results = mcp_response.json().get("results", [])
                    for res in web_results:
                        all_docs.append(f"Web Source [{res.get('url')}]: {res.get('content')}")
        except Exception as e:
            print(f"[Researcher] MCP Search skipped: {e}")

    # 3. Final Cleaning & Deduplication
    unique_docs = []
    seen = set()
    for doc in all_docs:
        if doc not in seen:
            unique_docs.append(doc)
            seen.add(doc)
    
    print(f"[Researcher] Total unique documents gathered: {len(unique_docs)}")
    
    return {"retrieved_docs": unique_docs}