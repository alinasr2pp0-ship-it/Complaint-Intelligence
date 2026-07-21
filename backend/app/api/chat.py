from fastapi import APIRouter, Query

from app.core.logging_config import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ask_question

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse, summary="Ask the RAG chatbot a question")
def chat(
    payload: ChatRequest,
    k: int = Query(default=None, ge=1, le=20, description="Override top-K retrieval"),
) -> ChatResponse:
    logger.info("Chat request: %s", payload.question[:80])
    return ask_question(payload.question, k=k)
