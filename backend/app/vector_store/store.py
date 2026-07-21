"""
Loads the Pinecone index for serving (no rebuild), and exposes retrievers
with the same defaults as the original pipeline (k=3, similarity search).
Embeddings are computed via the Voyage AI API -- no local model.
"""
from functools import lru_cache
from typing import Optional

from langchain_core.vectorstores import VectorStoreRetriever
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from app.config.settings import get_settings
from app.core.exceptions import VectorStoreNotReadyError
from app.core.logging_config import get_logger
from app.vector_store.builder import get_embeddings, get_pinecone_client

logger = get_logger(__name__)


@lru_cache
def get_vector_store() -> PineconeVectorStore:
    """Attach to the existing Pinecone index (must already be populated)."""
    settings = get_settings()

    if not settings.PINECONE_API_KEY:
        raise VectorStoreNotReadyError(
            "PINECONE_API_KEY is not set. Configure it in the environment or .env file."
        )
    if not settings.VOYAGE_API_KEY:
        raise VectorStoreNotReadyError(
            "VOYAGE_API_KEY is not set. Configure it in the environment or .env file."
        )

    pc = get_pinecone_client()
    existing = {idx["name"] for idx in pc.list_indexes()}
    if settings.PINECONE_INDEX_NAME not in existing:
        raise VectorStoreNotReadyError(
            f"Pinecone index '{settings.PINECONE_INDEX_NAME}' does not exist. "
            "Run `python -m app.vector_store.builder` to create and populate it first."
        )

    index = pc.Index(settings.PINECONE_INDEX_NAME)
    embeddings = get_embeddings()
    store = PineconeVectorStore(index=index, embedding=embeddings, namespace=settings.PINECONE_NAMESPACE)
    logger.info("Connected to Pinecone index '%s' (namespace=%s)", settings.PINECONE_INDEX_NAME, settings.PINECONE_NAMESPACE)
    return store


def get_retriever(k: Optional[int] = None, search_type: Optional[str] = None) -> VectorStoreRetriever:
    """Return a retriever. Defaults match the original pipeline (k=3, similarity)."""
    settings = get_settings()
    store = get_vector_store()
    k = k or settings.RETRIEVER_TOP_K
    search_type = search_type or settings.RETRIEVER_SEARCH_TYPE
    return store.as_retriever(search_type=search_type, search_kwargs={"k": k})


def vector_store_is_ready() -> bool:
    """Check Pinecone connectivity + that the index exists and has vectors."""
    settings = get_settings()
    if not settings.PINECONE_API_KEY or not settings.VOYAGE_API_KEY:
        return False
    try:
        pc: Pinecone = get_pinecone_client()
        existing = {idx["name"] for idx in pc.list_indexes()}
        if settings.PINECONE_INDEX_NAME not in existing:
            return False
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        namespace_stats = stats.get("namespaces", {}).get(settings.PINECONE_NAMESPACE, {})
        return namespace_stats.get("vector_count", 0) > 0
    except Exception:  # noqa: BLE001 -- health check must never raise
        logger.exception("Pinecone readiness check failed")
        return False
