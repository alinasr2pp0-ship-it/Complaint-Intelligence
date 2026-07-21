"""RAG chain: Pinecone retriever -> prompt -> Gemini generation."""
from functools import lru_cache

from google import genai
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.config.settings import get_settings
from app.core.exceptions import ConfigurationError
from app.core.logging_config import get_logger
from app.rag.prompts import build_default_prompt, format_docs
from app.vector_store.store import get_retriever

logger = get_logger(__name__)


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        raise ConfigurationError("GOOGLE_API_KEY is not set. Add it to your environment or .env file.")
    return genai.Client(api_key=settings.GOOGLE_API_KEY)


def direct_gemini_call(input_dict: dict) -> str:
    settings = get_settings()
    context = input_dict["context"]
    question = input_dict["question"]
    full_prompt = build_default_prompt(context, question)
    try:
        client = get_gemini_client()
        response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=full_prompt)
        return response.text
    except Exception as e:  # noqa: BLE001 -- keep the chatbot resilient to upstream failures
        logger.exception("Gemini generation failed")
        return f"Error calling Gemini: {str(e)}"


def build_rag_chain():
    retriever = get_retriever()
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RunnableLambda(direct_gemini_call)
    )
    return rag_chain


def answer_question(question: str) -> str:
    chain = build_rag_chain()
    return chain.invoke(question)
