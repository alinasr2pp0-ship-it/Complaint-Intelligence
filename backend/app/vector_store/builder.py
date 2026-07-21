"""
Vector store builder -- Pinecone + Voyage AI edition.

Builds (or rebuilds) the Pinecone index using Voyage AI's hosted embedding
API (`voyage-3`), upserted in memory-safe batches. Nothing is downloaded or
computed locally: both the embedding model and the vector store are remote
services, so this runs fine on small/resource-constrained hosts (e.g. a free
Replit container).
"""
import gc
from typing import List, Optional

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

from app.config.settings import get_settings
from app.core.exceptions import ConfigurationError
from app.core.logging_config import get_logger
from app.utils.data_loader import load_documents

logger = get_logger(__name__)


def get_embeddings(model_name: Optional[str] = None) -> VoyageAIEmbeddings:
    """Voyage AI hosted embeddings -- no local model download or inference."""
    settings = get_settings()
    if not settings.VOYAGE_API_KEY:
        raise ConfigurationError("VOYAGE_API_KEY is not set. Add it to your environment or .env file.")
    return VoyageAIEmbeddings(
        voyage_api_key=settings.VOYAGE_API_KEY,
        model=model_name or settings.EMBEDDING_MODEL,
        batch_size=settings.VOYAGE_BATCH_SIZE,
    )


def get_pinecone_client() -> Pinecone:
    settings = get_settings()
    if not settings.PINECONE_API_KEY:
        raise ConfigurationError("PINECONE_API_KEY is not set. Add it to your environment or .env file.")
    return Pinecone(api_key=settings.PINECONE_API_KEY)


def ensure_index_exists(pc: Optional[Pinecone] = None) -> None:
    """Create the Pinecone serverless index if it doesn't exist yet."""
    settings = get_settings()
    pc = pc or get_pinecone_client()
    existing = {idx["name"] for idx in pc.list_indexes()}
    if settings.PINECONE_INDEX_NAME in existing:
        logger.info("Pinecone index '%s' already exists.", settings.PINECONE_INDEX_NAME)
        return

    logger.info(
        "Creating Pinecone index '%s' (dim=%s, metric=%s, cloud=%s, region=%s)",
        settings.PINECONE_INDEX_NAME,
        settings.EMBEDDING_DIMENSION,
        settings.PINECONE_METRIC,
        settings.PINECONE_CLOUD,
        settings.PINECONE_REGION,
    )
    pc.create_index(
        name=settings.PINECONE_INDEX_NAME,
        dimension=settings.EMBEDDING_DIMENSION,
        metric=settings.PINECONE_METRIC,
        spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION),
    )


def build_vector_store(
    documents: Optional[List[Document]] = None,
    namespace: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> PineconeVectorStore:
    """
    Build/populate the Pinecone index in fixed-size batches: each batch is
    embedded via one Voyage API call, then upserted to Pinecone.
    """
    settings = get_settings()
    namespace = namespace or settings.PINECONE_NAMESPACE
    batch_size = batch_size or settings.BATCH_SIZE

    if documents is None:
        documents = load_documents()

    logger.info("Building Pinecone index from %s documents (batch_size=%s, namespace=%s)",
                len(documents), batch_size, namespace)

    pc = get_pinecone_client()
    ensure_index_exists(pc)

    embeddings = get_embeddings()
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings, namespace=namespace)

    total = len(documents)
    for i in range(0, total, batch_size):
        batch_docs = documents[i : i + batch_size]
        ids = [doc.metadata.get("complaint_id", f"doc-{i + j}") for j, doc in enumerate(batch_docs)]
        vector_store.add_documents(batch_docs, ids=ids)
        logger.info("Batch %s/%s upserted (%s vectors)", (i // batch_size) + 1, -(-total // batch_size), len(batch_docs))
        del batch_docs
        gc.collect()

    logger.info("Pinecone index '%s' populated successfully.", settings.PINECONE_INDEX_NAME)
    return vector_store


if __name__ == "__main__":
    # Standalone ingestion entry point:
    #   python -m app.vector_store.builder
    build_vector_store()
