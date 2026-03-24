from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    query: str
    # Use Annotated and operator.add so new data APPENDS to the list
    sub_questions: Annotated[List[str], operator.add]
    retrieved_docs: Annotated[List[str], operator.add]
    graded_docs: Annotated[List[str], operator.add]
    needs_retry: bool
    retry_count: int
    final_report: str
    has_hallucination: bool
    fallback_triggered: bool