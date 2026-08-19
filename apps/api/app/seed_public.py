import argparse
import hashlib
import sys
import urllib.error
import urllib.request

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.ingestion import IngestionError, ingest_document
from app.providers import create_provider

LOS_HEROES_2025_URL = (
    "https://porpub2.storage.googleapis.com/wp-content/uploads/2026/05/20152448/"
    "Memoria-LH_2025_8M-Oficial.pdf"
)
LOS_HEROES_2025_FILENAME = "Memoria-Integrada-Los-Heroes-2025.pdf"
EXPECTED_SHA256 = "19f8fa3876fe32a7b1c9a5a8fa473c5a9567d56a0841afa77c67a11fa69b3b11"


def download_document(url: str, max_bytes: int) -> bytes:
    request = urllib.request.Request(  # noqa: S310 - URL is an explicit operator input
        url,
        headers={"User-Agent": "EvidenceRAG/0.1 public-corpus-loader"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                raise IngestionError("La fuente remota supera MAX_UPLOAD_BYTES.")
            content = response.read(max_bytes + 1)
    except (TimeoutError, urllib.error.URLError) as exc:
        raise IngestionError(f"No fue posible descargar la fuente pública: {exc}") from exc
    if len(content) > max_bytes:
        raise IngestionError("La fuente remota supera MAX_UPLOAD_BYTES.")
    return content


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Descarga e indexa una fuente pública explícitamente autorizada."
    )
    parser.add_argument("--url", default=LOS_HEROES_2025_URL)
    parser.add_argument("--filename", default=LOS_HEROES_2025_FILENAME)
    parser.add_argument(
        "--skip-known-checksum",
        action="store_true",
        help="Omite la verificación SHA-256 al usar una URL distinta a la fuente oficial conocida.",
    )
    args = parser.parse_args()

    settings = get_settings()
    content = download_document(args.url, settings.max_upload_bytes)
    if args.url == LOS_HEROES_2025_URL and not args.skip_known_checksum:
        digest = hashlib.sha256(content).hexdigest()
        if digest != EXPECTED_SHA256:
            raise IngestionError(
                "La fuente oficial cambió desde la última verificación. "
                "Revise el documento antes de indexar."
            )

    init_db()
    provider = create_provider(settings)
    with SessionLocal() as database:
        document, deduplicated = ingest_document(
            database=database,
            provider=provider,
            settings=settings,
            filename=args.filename,
            content_type="application/pdf",
            content=content,
        )
    state = "reutilizado" if deduplicated else "indexado"
    print(
        f"Documento {state}: {document.filename} | "
        f"{document.page_count} páginas | {document.chunk_count} fragmentos"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IngestionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
