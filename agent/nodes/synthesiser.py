from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from agent.state import AgentState
from app.config import settings

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=settings.google_api_key,
    streaming=True 
)

# Added streaming=True here for the local fallback
mistral_llm = ChatOllama(
    model="mistral", 
    temperature=0.7, 
    streaming=True 
)

async def synthesiser_node(state: AgentState) -> dict:
    context = "\n\n".join(state.get("graded_docs", []))
    query = state.get("query", "")
    prompt = f"Context: {context}\n\nQuestion: {query}"

    try:
        response = await gemini_llm.ainvoke(prompt)
        return {"final_report": response.content}
    except Exception:
        print("[Synthesiser] Gemini limit hit. Streaming via Mistral...")
        # Now Mistral will also stream tokens to the UI instantly
        response = await mistral_llm.ainvoke(prompt)
        return {"final_report": response.content}