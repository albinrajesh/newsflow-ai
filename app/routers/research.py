from fastapi import APIRouter
from app.schemas.research import ResearchRequest, ResearchResponse
from agent.graph import agent
from agent.state import AgentState

router = APIRouter()

@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    initial_state: AgentState = {
        "query": request.query,
        "sub_questions": [],
        "retrieved_docs": [],
        "graded_docs": [],
        "needs_retry": False,
        "retry_count": 0,
        "final_report": "",
        "has_hallucination": False,
        "fallback_triggered": False
    }

    result = agent.invoke(initial_state)

    return ResearchResponse(
        query=result["query"],
        chunks=result["graded_docs"],
        report=result["final_report"]
    )