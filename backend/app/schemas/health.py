from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    vector_store_ready: bool
    vector_store_backend: str
    pinecone_index: str
    embedding_model: str
    embedding_backend: str
    generation_backend: str
    generation_model_chain: list[str]
    openrouter_api_key_configured: bool
    pinecone_api_key_configured: bool
    voyage_api_key_configured: bool
    version: str
