from pydantic import BaseModel

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    chunks: list[str] = []
    report: str = ""
    eval_scores: dict = {}