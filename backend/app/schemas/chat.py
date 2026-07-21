from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's question about the complaints corpus.")


class SourceDocument(BaseModel):
    complaint_id: str
    company: str
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    question: str
    sources: List[SourceDocument] = Field(default_factory=list)
