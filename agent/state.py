from typing import TypedDict

class AgentState(TypedDict):
    query: str
    sub_questions: list[str]
    retrieved_docs: list[str]
    graded_docs: list[str]
    needs_retry: bool
    retry_count: int
    final_report: str
    has_hallucination: bool
    fallback_triggered: bool