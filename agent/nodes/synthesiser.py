from openai import OpenAI
from agent.state import AgentState
from app.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

def synthesiser_node(state: AgentState) -> AgentState:
    print("[Synthesiser] Generating final report...")
    
    context = "\n\n".join(state["graded_docs"])
    prompt = f"""Write a comprehensive research report on: {state["query"]}
Use the following sources:
{context}

Format the report in professional Markdown with headers and bullet points."""

    response = client.chat.completions.create(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    report = response.choices[0].message.content
    return {**state, "final_report": report}