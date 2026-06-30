from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocumentRead(BaseModel):
    id: int
    filename: str
    document_type: str
    content_type: str | None
    status: str
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeDocumentListResponse(BaseModel):
    items: list[KnowledgeDocumentRead]


class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=10)


class RAGSource(BaseModel):
    document_id: int
    filename: str
    document_type: str
    chunk_id: int
    chunk_index: int
    content: str
    score: float


class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[RAGSource]
