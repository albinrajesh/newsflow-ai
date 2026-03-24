import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import AgentState
from app.config import settings

# Direct Gemini connection
llm = ChatGoogleGenerativeAI(
    model=settings.ollama_model,
    google_api_key=settings.google_api_key,
    temperature=0  # Zero temperature for factual consistency
)

async def hallucination_checker_node(state: AgentState) -> dict:
    """
    Verifies report accuracy. Skips strict checking for creative tasks (jokes)
    to prevent infinite retry loops.
    """
    query = state.get("query", "").lower()
    report = state.get("final_report", "")
    context = "\n\n".join(state.get("graded_docs", []))
    
    print(f"[HallucinationChecker] Verifying report for: '{query[:30]}...'")

    # 1. THE "CREATIVE TASK" SHORT-CIRCUIT
    # Jokes aren't 'facts' found in research docs. We skip the check here.
    creative_keywords = ["joke", "humor", "poem", "story", "creative"]
    if any(word in query for word in creative_keywords):
        print("[HallucinationChecker] Creative task detected. Skipping verification.")
        return {"has_hallucination": False}

    # 2. Safety Check: If the report or context is missing
    if not report or not context:
        print("[HallucinationChecker] Missing context/report. Passing to avoid loops.")
        return {"has_hallucination": False}

    # 3. Fact-Checking Prompt for serious Research Queries
    prompt = f"""You are a professional Fact-Checker. 
Compare the REPORT against the original SOURCES.

SCORING CRITERIA:
- PASS: Every factual claim in the report is supported by the sources.
- FAIL: The report contains specific facts or numbers NOT found in the sources.

SOURCES:
{context}

REPORT:
{report}

Answer ONLY with 'PASS' or 'FAIL'.
Verdict:"""

    for attempt in range(3):
        try:
            response = await llm.ainvoke(prompt)
            verdict = response.content.strip().upper()
            
            has_hallucination = "FAIL" in verdict
            current_retry = state.get("retry_count", 0)
            new_retry_count = current_retry + (1 if has_hallucination else 0)
            
            print(f"[HallucinationChecker] Verdict: {verdict} (Retries: {new_retry_count})")
            
            return {
                "has_hallucination": has_hallucination, 
                "retry_count": new_retry_count
            }

        except Exception as e:
            if "429" in str(e) and attempt < 2:
                print(f"[HallucinationChecker] Rate limited. Retrying in 5s...")
                await asyncio.sleep(5)
            else:
                print(f"[HallucinationChecker] Error: {e}")
                # Fallback: Assume no hallucination to prevent infinite loops
                return {"has_hallucination": False}