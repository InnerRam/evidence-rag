import pytest

from app.config import Settings
from app.db import SessionLocal, init_db
from app.ingestion import (
    IngestionError,
    chunk_text,
    ingest_document,
    sanitize_filename,
    validate_upload,
)
from app.providers import MockProvider


def test_sanitize_filename_removes_paths_and_unsafe_characters() -> None:
    assert sanitize_filename("../../Informe cliente (final).txt") == "Informe_cliente_final_.txt"


def test_validate_upload_rejects_spoofed_pdf() -> None:
    with pytest.raises(IngestionError, match="PDF válido"):
        validate_upload("report.pdf", b"not a pdf", Settings())


def test_chunking_preserves_content_with_overlap() -> None:
    text = "Primera oración con evidencia. " * 30
    chunks = chunk_text(text, size=300, overlap=50)
    assert len(chunks) > 1
    assert all(chunks)
    assert chunks[0].startswith("Primera")


def test_same_content_is_isolated_by_embedding_fingerprint() -> None:
    init_db()
    settings = Settings()
    first_provider = MockProvider(settings.embedding_dimensions)
    second_provider = MockProvider(settings.embedding_dimensions)
    second_provider.embedding_fingerprint = (
        f"mock:alternate-v1:{settings.embedding_dimensions}"
    )
    content = (
        "Este documento público permite comprobar que cada proveedor mantiene un índice "
        "independiente y evita mezclar espacios vectoriales incompatibles."
    ).encode()

    with SessionLocal() as database:
        first, first_duplicate = ingest_document(
            database, first_provider, settings, "isolation.txt", "text/plain", content
        )
        second, second_duplicate = ingest_document(
            database, second_provider, settings, "isolation.txt", "text/plain", content
        )

    assert first_duplicate is False
    assert second_duplicate is False
    assert first.id != second.id
    assert first.sha256 == second.sha256
    assert first.embedding_fingerprint != second.embedding_fingerprint
