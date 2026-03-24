from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from agent.state import AgentState
from app.config import settings

# CRITICAL: streaming=True must be set during initialization
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=settings.google_api_key,
    streaming=True  # <--- Enables the token flow
)

mistral_llm = ChatOllama(model="mistral", temperature=0.7)

async def synthesiser_node(state: AgentState) -> dict:
    """
    Final synthesis node. 
    Because we use 'astream_events' in the router, 
    this node will now stream tokens to the user in real-time.
    """
    context = "\n\n".join(state.get("graded_docs", []))
    query = state.get("query", "")
    
    prompt = f"Using this research: {context}\n\nAnswer this: {query}"

    try:
        # LangGraph handles the streaming wrap-around for ainvoke 
        # when astream_events is called in the router.
        response = await gemini_llm.ainvoke(prompt)
        return {"final_report": response.content}
    
    except Exception as e:
        print(f"[Synthesiser] Gemini failed. Falling back to local Mistral...")
        # Mistral (Ollama) also supports streaming!
        response = await mistral_llm.ainvoke(prompt)
        return {"final_report": response.content}                                                                                                                           