from fastapi import APIRouter

from app.schemas.retrieval import RetrievalRequest, RetrievalResponse
from app.services.retrieval_service import retrieve

router = APIRouter(prefix="/api/v1", tags=["Retrieval"])


@router.post("/retrieve", response_model=RetrievalResponse, summary="Run retrieval only (no generation)")
def retrieve_documents(payload: RetrievalRequest) -> RetrievalResponse:
    return retrieve(payload.query, k=payload.k, search_type=payload.search_type)
