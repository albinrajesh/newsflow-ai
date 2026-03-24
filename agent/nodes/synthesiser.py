from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import AgentState
from app.config import settings
import asyncio

async def synthesiser_node(state: AgentState) -> dict:
    print("[Synthesiser] Generating final report...")
    
    # Use the specific 1.5-flash model
    llm = ChatGoogleGenerativeAI(
        model=settings.ollama_model, 
        google_api_key=settings.google_api_key,
        streaming=True
    )

    context = "\n\n".join(state.get("graded_docs", []))
    prompt = f"Write a joke about AI based on this context: {context}"

    full_content = ""
    try:
        # Using ainvoke instead of astream for a quick test 
        # to see if the 404 disappears
        response = await llm.ainvoke(prompt)
        full_content = response.content
        
        print("[Synthesiser] Success!")
        return {"final_report": full_content}
    except Exception as e:
        print(f"[Synthesiser] Error: {e}")
        return {"final_report": "Why did the AI cross the road? To optimize the path! (API Error fallback)"}