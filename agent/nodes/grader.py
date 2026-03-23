from openai import OpenAI
from agent.state import AgentState
from app.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

def grader_node(state: AgentState) -> AgentState:
    print(f"[Grader] Evaluating {len(state['retrieved_docs'])} documents...")
    
    graded_docs = []
    for doc in state["retrieved_docs"]:
        prompt = f"""Is this document relevant to the user query? 
Query: {state["query"]}
Document: {doc}
Answer ONLY 'YES' or 'NO'."""

        response = client.chat.completions.create(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        verdict = response.choices[0].message.content.strip().upper()
        if "YES" in verdict:
            graded_docs.append(doc)

    # Logic for retry if no docs are found
    needs_retry = len(graded_docs) == 0
    print(f"[Grader] {len(graded_docs)} relevant docs — needs_retry: {needs_retry}")
    
    return {**state, "graded_docs": graded_docs, "needs_retry": needs_retry}