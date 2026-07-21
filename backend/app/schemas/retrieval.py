from typing import List, Optional

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: Optional[int] = Field(default=None, ge=1, le=20)
    search_type: Optional[str] = Field(default=None, description="'similarity' or 'mmr'")


class RetrievedDocument(BaseModel):
    complaint_id: str
    company: str
    content: str


class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievedDocument]
