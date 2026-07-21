"""Custom application exceptions and FastAPI exception handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for all application-level errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class VectorStoreNotReadyError(AppException):
    """Raised when the Pinecone index has not been built/populated yet."""

    def __init__(self, message: str = "Vector store is not ready. Build it first via the ingestion step."):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class GenerationError(AppException):
    """Raised when the Gemini generation call fails."""

    def __init__(self, message: str = "Failed to generate a response from the language model."):
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)


class ConfigurationError(AppException):
    """Raised when required configuration (e.g. API keys) is missing."""

    def __init__(self, message: str = "Missing or invalid configuration."):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.message},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "message": "An unexpected error occurred."},
    )
