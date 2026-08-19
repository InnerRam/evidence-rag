import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db, init_db
from app.ingestion import ALLOWED_EXTENSIONS, IngestionError, ingest_document
from app.models import Document, QueryLog
from app.providers import create_provider
from app.schemas import (
    DocumentResponse,
    HistoryItem,
    PublicConfig,
    QueryRequest,
    QueryResponse,
)
from app.services import answer_question

settings = get_settings()
provider = create_provider(settings)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=settings.log_level.upper(), handlers=[handler], force=True)
logger = logging.getLogger("evidence_rag")
DatabaseDep = Annotated[Session, Depends(get_db)]
UploadedFile = Annotated[UploadFile, File()]


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    init_db()
    logger.info("application_started")
    yield


app = FastAPI(
    title="EvidenceRAG API",
    version="0.1.0",
    description="Asistente documental RAG con citas verificables y rechazo por falta de evidencia.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "unhandled_request_error",
            extra={"request_id": request_id, "method": request.method, "path": request.url.path},
        )
        raise
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        },
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "La solicitud contiene datos inválidos.",
            "details": exc.errors(),
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(IngestionError)
async def ingestion_exception_handler(request: Request, exc: IngestionError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "invalid_document",
            "message": str(exc),
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"name": "EvidenceRAG API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health(database: DatabaseDep) -> dict[str, str]:
    database.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok", "provider": provider.name}


@app.get("/api/v1/config", response_model=PublicConfig)
def public_config() -> PublicConfig:
    return PublicConfig(
        provider=provider.name,
        max_upload_bytes=settings.max_upload_bytes,
        allowed_extensions=sorted(ALLOWED_EXTENSIONS),
        default_top_k=settings.default_top_k,
        max_top_k=settings.max_top_k,
    )


@app.post(
    "/api/v1/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadedFile, database: DatabaseDep
) -> DocumentResponse:
    filename = file.filename or "document"
    content = await file.read(settings.max_upload_bytes + 1)
    document, deduplicated = ingest_document(
        database=database,
        provider=provider,
        settings=settings,
        filename=filename,
        content_type=file.content_type or "application/octet-stream",
        content=content,
    )
    response = DocumentResponse.model_validate(document)
    response.deduplicated = deduplicated
    return response


@app.get("/api/v1/documents", response_model=list[DocumentResponse])
def list_documents(database: DatabaseDep) -> list[DocumentResponse]:
    documents = database.scalars(
        select(Document)
        .where(Document.embedding_fingerprint == provider.embedding_fingerprint)
        .order_by(Document.created_at.desc())
    ).all()
    return [DocumentResponse.model_validate(document) for document in documents]


@app.post("/api/v1/query", response_model=QueryResponse)
def query(request: QueryRequest, database: DatabaseDep) -> QueryResponse:
    top_k = request.top_k or settings.default_top_k
    if top_k > settings.max_top_k:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"top_k no puede superar {settings.max_top_k}",
        )
    return answer_question(
        database=database,
        provider=provider,
        settings=settings,
        question=request.question.strip(),
        top_k=top_k,
        session_id=request.session_id,
    )


@app.get("/api/v1/sessions/{session_id}/history", response_model=list[HistoryItem])
def session_history(session_id: str, database: DatabaseDep) -> list[HistoryItem]:
    if not (8 <= len(session_id) <= 64):
        raise HTTPException(status_code=422, detail="session_id inválido")
    logs = database.scalars(
        select(QueryLog)
        .where(QueryLog.session_id == session_id)
        .order_by(QueryLog.created_at.asc())
    ).all()
    return [HistoryItem.model_validate(log) for log in logs]
