"""Pydantic schemas for the /api/v1/evaluation endpoints."""
from typing import Any, Dict, List

from pydantic import BaseModel


class GenerationMetricsResponse(BaseModel):
    rows: List[Dict[str, Any]] = []


class RetrievalMetricsResponse(BaseModel):
    rows: List[Dict[str, Any]] = []


class QualitativeEvalResponse(BaseModel):
    report_path: str
    num_queries: int


class EvaluationSummaryResponse(BaseModel):
    generation_metrics: List[Dict[str, Any]] = []
    retrieval_metrics: List[Dict[str, Any]] = []
