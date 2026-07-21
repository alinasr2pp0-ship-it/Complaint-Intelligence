from fastapi import APIRouter

from app.schemas.evaluation import (
    EvaluationSummaryResponse,
    GenerationMetricsResponse,
    QualitativeEvalResponse,
    RetrievalMetricsResponse,
)
from app.services.evaluation_service import (
    run_generation_metrics,
    run_qualitative,
    run_retrieval_metrics,
)

router = APIRouter(prefix="/api/v1/evaluation", tags=["Evaluation"])


@router.get("/generation", response_model=GenerationMetricsResponse, summary="BLEU / ROUGE generation metrics")
def generation_metrics() -> GenerationMetricsResponse:
    return GenerationMetricsResponse(rows=run_generation_metrics())


@router.get("/retrieval", response_model=RetrievalMetricsResponse, summary="Recall@K / MRR retrieval metrics")
def retrieval_metrics() -> RetrievalMetricsResponse:
    return RetrievalMetricsResponse(rows=run_retrieval_metrics())


@router.post("/qualitative", response_model=QualitativeEvalResponse, summary="Run the 9 fixed test queries and save a report")
def qualitative_eval() -> QualitativeEvalResponse:
    result = run_qualitative()
    return QualitativeEvalResponse(**result)


@router.get("/summary", response_model=EvaluationSummaryResponse, summary="Combined generation + retrieval metrics")
def evaluation_summary() -> EvaluationSummaryResponse:
    return EvaluationSummaryResponse(
        generation_metrics=run_generation_metrics(),
        retrieval_metrics=run_retrieval_metrics(),
    )
