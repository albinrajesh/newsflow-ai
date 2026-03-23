from openai import OpenAI
from agent.state import AgentState
from app.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

def planner_node(state: AgentState) -> AgentState:
    prompt = f"""You are a research planner. Break this query into exactly 3 focused sub-questions.
Query: {state["query"]}
Return ONLY a numbered list like:
1. sub question one
2. sub question two
3. sub question three"""

    response = client.chat.completions.create(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "http://localhost:8000", 
            "X-Title": "Deep Research Agent",
        }
    )
    
    raw = response.choices[0].message.content.strip()
    sub_questions = []
    for line in raw.split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            question = line.split(".", 1)[-1].split(")", 1)[-1].strip()
            sub_questions.append(question)
            
    if len(sub_questions) == 0:
        sub_questions = [state["query"]]
        
    print(f"[Planner] Generated {len(sub_questions)} sub-questions")
    return {**state, "sub_questions": sub_questions}