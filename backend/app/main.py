"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, evaluation, health, retrieval
from app.config.settings import get_settings
from app.core.exceptions import AppException, app_exception_handler, unhandled_exception_handler
from app.core.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Production API for the Consumer Complaints RAG Chatbot. "
            "Wraps the RAG pipeline (Pinecone + HuggingFace embeddings + Gemini), "
            "evaluation (BLEU/ROUGE, Recall@K/MRR), and optimization experiments."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(retrieval.router)
    app.include_router(evaluation.router)

    return app


app = create_app()
