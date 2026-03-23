import requests
from agent.state import AgentState
from rag.retriever import retrieve
from app.config import settings

def researcher_node(state: AgentState) -> AgentState:
    all_docs = []
    
    # 1. First, check local FAISS (Week 1 logic)
    for question in state["sub_questions"]:
        chunks = retrieve(question, top_k=2)
        all_docs.extend(chunks)

    # 2. Second, call the MCP Web Search tool (Week 3 logic)
    try:
        mcp_response = requests.post(
            f"{settings.mcp_server_url}/tools/web_search",
            json={"query": state["query"], "max_results": 3},
            timeout=15
        )
        if mcp_response.status_code == 200:
            web_results = mcp_response.json().get("results", [])
            for res in web_results:
                all_docs.append(f"Web Source [{res['url']}]: {res['content']}")
    except Exception as e:
        print(f"[Researcher] MCP Search failed: {e}")

    # Remove duplicates
    unique_docs = list(dict.fromkeys(all_docs))
    print(f"[Researcher] Gathered {len(unique_docs)} total chunks (Local + Web)")
    
    return {**state, "retrieved_docs": unique_docs}