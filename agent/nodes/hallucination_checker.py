from openai import OpenAI
from agent.state import AgentState
from app.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

def hallucination_checker_node(state: AgentState) -> AgentState:
    print("[HallucinationChecker] Verifying report accuracy...")
    
    context = "\n\n".join(state["graded_docs"])
    report = state["final_report"]

    prompt = f"""You are a Fact-Checker. Compare the REPORT to the SOURCES.
Does the report contain facts NOT present in the sources? 
Answer only 'FAIL' if there is a hallucination, or 'PASS' if it is accurate.

SOURCES:
{context}

REPORT:
{report}

Verdict:"""

    response = client.chat.completions.create(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Deep Research Agent",
        }
    )
    
    verdict = response.choices[0].message.content.strip().upper()
    has_hallucination = "FAIL" in verdict
    
    # Logic: if hallucination found, we increment retry_count 
    retry_count = state["retry_count"] + (1 if has_hallucination else 0)
    
    print(f"[HallucinationChecker] Verdict: {verdict}")
    return {
        **state, 
        "has_hallucination": has_hallucination, 
        "retry_count": retry_count
    }