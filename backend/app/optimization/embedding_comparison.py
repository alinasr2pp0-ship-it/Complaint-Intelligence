"""Embedding model comparison, backed by throwaway Pinecone namespaces and Voyage AI's hosted models."""
import time
from typing import List
from uuid import uuid4

import pandas as pd
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings

from app.config.settings import get_settings
from app.core.exceptions import ConfigurationError
from app.evaluation.retrieval_metrics import evaluate_retrieval
from app.vector_store.builder import ensure_index_exists, get_pinecone_client

# The Pinecone index's dimension is fixed at creation time (EMBEDDING_DIMENSION=1024),
# so only Voyage models producing 1024-dim vectors can be compared against it here.
# voyage-3 is 1024-dim by default; voyage-3-large supports an explicit output_dimension.
EMBEDDING_MODELS = ["voyage-3", "voyage-3-large"]
_MODEL_KWARGS = {
    "voyage-3-large": {"output_dimension": 1024},
}


def build_temp_retriever(docs: List[Document], embedding_model: str, search_type: str = "similarity", k: int = 5):
    """
    Builds a retriever backed by a disposable Pinecone namespace (namespaced
    under the same index) so experiments don't touch the production
    'default' namespace.
    """
    settings = get_settings()
    if not settings.VOYAGE_API_KEY:
        raise ConfigurationError("VOYAGE_API_KEY is not set. Add it to your environment or .env file.")

    emb = VoyageAIEmbeddings(
        voyage_api_key=settings.VOYAGE_API_KEY,
        model=embedding_model,
        **_MODEL_KWARGS.get(embedding_model, {}),
    )

    pc = get_pinecone_client()
    ensure_index_exists(pc)
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    namespace = f"exp-{uuid4().hex[:12]}"
    store = PineconeVectorStore(index=index, embedding=emb, namespace=namespace)
    ids = [d.metadata.get("complaint_id", f"tmp-{i}") for i, d in enumerate(docs)]
    store.add_documents(docs, ids=ids)
    time.sleep(1)  # brief settle time for Pinecone's eventual-consistency indexing

    return store.as_retriever(search_type=search_type, search_kwargs={"k": k})


def run_embedding_comparison(documents_sample: List[Document], test_queries, ground_truth_ids, embedding_models=None) -> pd.DataFrame:
    embedding_models = embedding_models or EMBEDDING_MODELS
    documents_sample = documents_sample[:500]
    embedding_results = []
    for model_name in embedding_models:
        temp_retriever = build_temp_retriever(docs=documents_sample, embedding_model=model_name, k=5)
        metrics = evaluate_retrieval(temp_retriever, test_queries, ground_truth_ids, k=5)
        metrics["Embedding Model"] = model_name
        embedding_results.append(metrics)
    return pd.DataFrame(embedding_results)
