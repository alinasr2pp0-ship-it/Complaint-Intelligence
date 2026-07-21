"""
Application configuration.

All values are sourced from environment variables so the exact same codebase
runs unmodified locally, in Docker, or on Replit / any cloud host. Both the
vector store (Pinecone) and the embedding model (Voyage AI) are hosted
services -- nothing is downloaded or run locally, so ingestion and serving
work the same on a resource-constrained container as on a laptop.
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Central application settings, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App metadata ---
    APP_NAME: str = "Consumer Complaints RAG Chatbot API"
    APP_VERSION: str = "2.1.0"
    ENVIRONMENT: str = "development"  # development | production
    LOG_LEVEL: str = "INFO"

    # --- Google Gemini (generation model) ---
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    # --- Embeddings (Voyage AI -- hosted API, no local model download) ---
    VOYAGE_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "voyage-3"
    EMBEDDING_DIMENSION: int = 1024  # voyage-3 output size; must match the Pinecone index
    VOYAGE_BATCH_SIZE: int = 128  # Voyage API accepts up to 128 texts per embed call

    # --- Data path ---
    DATA_CSV_PATH: str = str(PROJECT_ROOT / "data" / "processed_corpus_5000.csv")

    # --- Pinecone (vector store) ---
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "complaints-rag"
    PINECONE_NAMESPACE: str = "default"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    PINECONE_METRIC: str = "cosine"

    # --- Vector store build parameters ---
    MAX_ROWS: Optional[int] = 5000
    BATCH_SIZE: int = 128  # Pinecone upsert batches, matched to VOYAGE_BATCH_SIZE

    # --- Retrieval defaults ---
    RETRIEVER_TOP_K: int = 3
    RETRIEVER_SEARCH_TYPE: str = "similarity"

    # --- CORS ---
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (avoids re-parsing env on every call)."""
    return Settings()
