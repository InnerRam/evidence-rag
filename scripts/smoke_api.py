import os
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = os.getenv("EVIDENCE_RAG_API_URL", "http://localhost:8000")


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=30, trust_env=False) as client:
        health = client.get("/health")
        health.raise_for_status()
        sample = REPO_ROOT / "data" / "sample" / "programa_solar_andino.txt"
        with sample.open("rb") as handle:
            uploaded = client.post(
                "/api/v1/documents",
                files={"file": (sample.name, handle, "text/plain")},
            )
        uploaded.raise_for_status()
        answer = client.post(
            "/api/v1/query",
            json={"question": "¿Cuál es la meta de capacidad solar?", "top_k": 3},
        )
        answer.raise_for_status()
        payload = answer.json()
        assert payload["evidence_sufficient"] is True
        assert payload["citations"]
        print(
            f"SMOKE OK | document={uploaded.json()['filename']} "
            f"| query_id={payload['query_id']} | citations={len(payload['citations'])}"
        )


if __name__ == "__main__":
    main()
