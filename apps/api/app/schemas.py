from datetime import datetime

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    filename: str
    sha256: str
    size_bytes: int
    status: str
    page_count: int
    chunk_count: int
    embedding_tokens: int
    processing_ms: float
    error_message: str | None
    created_at: datetime
    deduplicated: bool = False

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=25)
    session_id: str | None = Field(default=None, min_length=8, max_length=64)


class Citation(BaseModel):
    id: str
    document_id: str
    document: str
    page: int | None
    section: str | None
    score: float
    snippet: str


class QueryMetrics(BaseModel):
    retrieval_ms: float
    generation_ms: float
    total_ms: float
    embedding_tokens: int
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float | None


class QueryResponse(BaseModel):
    query_id: str
    session_id: str
    answer: str
    evidence_sufficient: bool
    citations: list[Citation]
    metrics: QueryMetrics
    provider: str


class HistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    evidence_sufficient: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicConfig(BaseModel):
    provider: str
    max_upload_bytes: int
    allowed_extensions: list[str]
    default_top_k: int
    max_top_k: int
