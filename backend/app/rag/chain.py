"""
RAG chain: Pinecone retriever -> prompt -> generation.

Generation is entirely via OpenRouter's free-tier models (no Gemini, no
paid provider). A fixed model chain is tried in order until one succeeds:

    PRIMARY_MODEL   = "meta-llama/llama-3.2-3b-instruct:free"
    FALLBACK_MODELS = ["mistralai/mistral-small-2506",
                        "deepseek/deepseek-chat",
                        "google/gemma-3-4b-it:free"]
"""
import httpx
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.config.settings import get_settings
from app.core.exceptions import ConfigurationError, GenerationError
from app.core.logging_config import get_logger
from app.rag.prompts import build_default_prompt, format_docs
from app.vector_store.store import get_retriever

logger = get_logger(__name__)

PRIMARY_MODEL = "openai/gpt-oss-20b:free"
FALLBACK_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-nano-9b-v2:free",
]
MODEL_CHAIN = [PRIMARY_MODEL, *FALLBACK_MODELS]


def _call_openrouter(full_prompt: str, model: str) -> str:
    settings = get_settings()
    if not settings.OPENROUTER_API_KEY:
        raise ConfigurationError("OPENROUTER_API_KEY is not set. Add it to your environment or .env file.")

    response = httpx.post(
        settings.OPENROUTER_BASE_URL,
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": full_prompt}],
        },
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def generate_completion(full_prompt: str) -> str:
    """Walks MODEL_CHAIN in order, returning the first successful response."""
    last_error = None
    for model in MODEL_CHAIN:
        try:
            answer = _call_openrouter(full_prompt, model)
            logger.info("Answered via OpenRouter model '%s'.", model)
            return answer
        except Exception as e:  # noqa: BLE001 -- try the next model in the chain
            logger.warning("OpenRouter model '%s' failed (%s); trying next.", model, e)
            last_error = e

    logger.error("All OpenRouter models in the chain failed.")
    raise GenerationError(f"All OpenRouter models failed. Last error: {last_error}")


def generate_answer_from_context(input_dict: dict) -> str:
    """
    Generation entry point used by the RAG chain and the qualitative-eval
    generation itself runs entirely through the OpenRouter chain above.
    """
    context = input_dict["context"]
    question = input_dict["question"]
    full_prompt = build_default_prompt(context, question)
    try:
        return generate_completion(full_prompt)
    except GenerationError as e:
        return f"Error: {e.message}"


def build_rag_chain():
    retriever = get_retriever()
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RunnableLambda(generate_answer_from_context)
    )
    return rag_chain


def answer_question(question: str) -> str:
    chain = build_rag_chain()
    return chain.invoke(question)
