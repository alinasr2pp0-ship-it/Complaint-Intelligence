from fastapi import APIRouter

from app.config.settings import get_settings
from app.schemas.health import HealthResponse
from app.vector_store.store import vector_store_is_ready

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        vector_store_ready=vector_store_is_ready(),
        vector_store_backend="pinecone",
        pinecone_index=settings.PINECONE_INDEX_NAME,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_backend="voyageai",
        gemini_model=settings.GEMINI_MODEL,
        google_api_key_configured=bool(settings.GOOGLE_API_KEY),
        pinecone_api_key_configured=bool(settings.PINECONE_API_KEY),
        voyage_api_key_configured=bool(settings.VOYAGE_API_KEY),
        version=settings.APP_VERSION,
    )
