from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class GenerationMetricsResponse(BaseModel):
    rows: List[Dict[str, Any]]


class RetrievalMetricsResponse(BaseModel):
    rows: List[Dict[str, Any]]


class QualitativeEvalResponse(BaseModel):
    report_path: str
    num_queries: int


class EvaluationSummaryResponse(BaseModel):
    generation_metrics: Optional[List[Dict[str, Any]]] = None
    retrieval_metrics: Optional[List[Dict[str, Any]]] = None
