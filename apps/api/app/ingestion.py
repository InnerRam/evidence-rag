import hashlib
import io
import re
import time
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Chunk, Document
from app.providers import AIProvider

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class IngestionError(ValueError):
    pass


@dataclass(frozen=True)
class TextUnit:
    content: str
    page_number: int | None
    section: str | None


def sanitize_filename(filename: str) -> str:
    basename = Path(filename).name
    safe = SAFE_FILENAME_RE.sub("_", basename).strip("._")
    return safe[:200] or "document"


def validate_upload(filename: str, content: bytes, settings: Settings) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise IngestionError("Tipo no permitido. Use PDF, TXT o MD.")
    if not content:
        raise IngestionError("El archivo está vacío.")
    if len(content) > settings.max_upload_bytes:
        raise IngestionError(
            f"El archivo supera el máximo de {settings.max_upload_bytes // (1024 * 1024)} MB."
        )
    if suffix == ".pdf" and not content.startswith(b"%PDF-"):
        raise IngestionError("El contenido no corresponde a un PDF válido.")
    return suffix


def extract_units(suffix: str, content: bytes) -> list[TextUnit]:
    if suffix == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            units = [
                TextUnit(
                    content=(page.extract_text() or "").strip(),
                    page_number=index,
                    section=None,
                )
                for index, page in enumerate(reader.pages, start=1)
            ]
        except Exception as exc:
            raise IngestionError("No fue posible leer el PDF.") from exc
    else:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IngestionError("El archivo de texto debe usar codificación UTF-8.") from exc
        units = split_text_sections(text)
    usable = [unit for unit in units if unit.content.strip()]
    if sum(len(unit.content) for unit in usable) < 40:
        raise IngestionError("No se encontró texto suficiente para indexar.")
    return usable


def split_text_sections(text: str) -> list[TextUnit]:
    units: list[TextUnit] = []
    heading = "Documento"
    buffer: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            if "\n".join(buffer).strip():
                units.append(TextUnit("\n".join(buffer).strip(), None, heading))
            heading = line.lstrip("# ").strip() or "Sección"
            buffer = []
        else:
            buffer.append(line)
    if "\n".join(buffer).strip():
        units.append(TextUnit("\n".join(buffer).strip(), None, heading))
    return units or [TextUnit(text.strip(), None, "Documento")]


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if len(normalized) <= size:
        return [normalized]
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + size, len(normalized))
        if end < len(normalized):
            boundary = max(normalized.rfind(". ", start, end), normalized.rfind("\n", start, end))
            if boundary > start + size // 2:
                end = boundary + 1
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest_document(
    database: Session,
    provider: AIProvider,
    settings: Settings,
    filename: str,
    content_type: str,
    content: bytes,
) -> tuple[Document, bool]:
    started = time.perf_counter()
    suffix = validate_upload(filename, content, settings)
    digest = hashlib.sha256(content).hexdigest()
    existing = database.scalar(
        select(Document).where(
            Document.sha256 == digest,
            Document.embedding_fingerprint == provider.embedding_fingerprint,
        )
    )
    if existing:
        return existing, True

    safe_name = sanitize_filename(filename)
    document = Document(
        filename=filename[:255],
        safe_filename=safe_name,
        content_type=content_type[:100] or "application/octet-stream",
        sha256=digest,
        embedding_fingerprint=provider.embedding_fingerprint,
        size_bytes=len(content),
        status="processing",
    )
    database.add(document)

    try:
        database.flush()
        units = extract_units(suffix, content)
        pieces: list[tuple[TextUnit, str]] = []
        for unit in units:
            pieces.extend(
                (unit, chunk)
                for chunk in chunk_text(
                    unit.content, settings.chunk_size_chars, settings.chunk_overlap_chars
                )
            )
        vectors, usage = provider.embed([piece[1] for piece in pieces])
        for position, ((unit, chunk), vector) in enumerate(zip(pieces, vectors, strict=True)):
            database.add(
                Chunk(
                    document_id=document.id,
                    position=position,
                    page_number=unit.page_number,
                    section=unit.section,
                    content=chunk,
                    token_estimate=max(1, len(chunk) // 4),
                    embedding=vector,
                )
            )
        document.status = "available"
        document.page_count = len(units)
        document.chunk_count = len(pieces)
        document.embedding_tokens = usage.input_tokens
        document.processing_ms = round((time.perf_counter() - started) * 1000, 2)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        (settings.upload_dir / f"{digest}{suffix}").write_bytes(content)
        database.commit()
        database.refresh(document)
        return document, False
    except IntegrityError:
        database.rollback()
        duplicate = database.scalar(
            select(Document).where(
                Document.sha256 == digest,
                Document.embedding_fingerprint == provider.embedding_fingerprint,
            )
        )
        if duplicate:
            return duplicate, True
        raise
    except Exception as exc:
        database.rollback()
        failed_document = Document(
            id=document.id,
            filename=document.filename,
            safe_filename=document.safe_filename,
            content_type=document.content_type,
            sha256=document.sha256,
            embedding_fingerprint=document.embedding_fingerprint,
            size_bytes=document.size_bytes,
            status="failed",
            error_message=str(exc)[:1000],
            processing_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        database.add(failed_document)
        database.commit()
        raise
