from typing import TypedDict, List, Dict, Any


class ContentState(TypedDict, total=False):

    topic: str
    content_type: str
    requirements: str

    research: List[str]
    sources: List[str]
    
    research_attempt_count: int
    research_relevance_decision: str
    research_relevance_feedback: str

    draft: str

    editor_decision: str
    editor_feedback: str

    fact_check_results: List[Dict[str, Any]]
    fact_check_decision: str

    revision_count: int
    status: str

    errors: List[str]

    metrics: Dict[str, Any]