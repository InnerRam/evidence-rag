from fastapi.testclient import TestClient

from app.main import app

SAMPLE = """# Programa Solar Andino
El programa instalará 120 kilovatios de capacidad solar antes de diciembre de 2027.
La primera etapa contempla tres escuelas rurales y un centro comunitario.

# Operación
Las baterías tendrán una autonomía objetivo de ocho horas para cargas críticas.
""".encode()


def test_vertical_slice_upload_query_citations_and_history() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200

        upload = client.post(
            "/api/v1/documents",
            files={"file": ("programa.txt", SAMPLE, "text/plain")},
        )
        assert upload.status_code == 201, upload.text
        body = upload.json()
        assert body["status"] == "available"
        assert body["chunk_count"] >= 2

        duplicate = client.post(
            "/api/v1/documents",
            files={"file": ("programa-copia.txt", SAMPLE, "text/plain")},
        )
        assert duplicate.status_code == 201
        assert duplicate.json()["deduplicated"] is True
        assert duplicate.json()["id"] == body["id"]

        query = client.post(
            "/api/v1/query",
            json={"question": "¿Cuántos kilovatios instalará el programa?", "top_k": 3},
        )
        assert query.status_code == 200, query.text
        answer = query.json()
        assert answer["evidence_sufficient"] is True
        assert "120 kilovatios" in answer["answer"]
        assert answer["citations"][0]["document"] == "programa.txt"
        assert "120 kilovatios" in answer["citations"][0]["snippet"]
        assert answer["metrics"]["total_ms"] >= 0

        history = client.get(f"/api/v1/sessions/{answer['session_id']}/history")
        assert history.status_code == 200
        assert len(history.json()) == 1


def test_unanswerable_question_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/query",
            json={"question": "¿Cuál es el menú del restaurante lunar?"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["evidence_sufficient"] is False
        assert body["citations"] == []
        assert body["metrics"]["generation_ms"] == 0
        assert "No existe evidencia suficiente" in body["answer"]


def test_ambiguous_question_is_rejected() -> None:
    with TestClient(app) as client:
        client.post(
            "/api/v1/documents",
            files={"file": ("programa.txt", SAMPLE, "text/plain")},
        )
        response = client.post("/api/v1/query", json={"question": "¿Quién es el responsable?"})
        assert response.status_code == 200
        assert response.json()["evidence_sufficient"] is False


def test_invalid_extension_is_visible_error() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents",
            files={"file": ("payload.exe", b"unsafe", "application/octet-stream")},
        )
        assert response.status_code == 400
        assert response.json()["error"] == "invalid_document"
