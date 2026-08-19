import json
import os
import statistics
import tempfile
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
temporary_root = tempfile.mkdtemp(prefix="evidence_rag_eval_")
os.environ["DATABASE_URL"] = f"sqlite:///{temporary_root}/eval.db"
os.environ["UPLOAD_DIR"] = f"{temporary_root}/uploads"
os.environ.setdefault("AI_PROVIDER", "mock")
os.environ.setdefault("EMBEDDING_DIMENSIONS", "1536")


def load_dataset() -> list[dict]:
    path = REPO_ROOT / "evals" / "dataset.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def normalize(value: str) -> str:
    return value.casefold().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def run() -> dict:
    from app.config import get_settings
    from app.db import SessionLocal, init_db
    from app.ingestion import ingest_document
    from app.providers import create_provider
    from app.services import answer_question

    settings = get_settings()
    provider = create_provider(settings)
    init_db()
    database = SessionLocal()
    try:
        for document_path in sorted((REPO_ROOT / "data" / "sample").glob("*.txt")):
            ingest_document(
                database,
                provider,
                settings,
                document_path.name,
                "text/plain",
                document_path.read_bytes(),
            )

        cases = []
        for case in load_dataset():
            response = answer_question(
                database,
                provider,
                settings,
                case["question"],
                top_k=5,
                session_id="evaluation-session",
            )
            cited_documents = [citation.document for citation in response.citations]
            expected_documents = case["expected_documents"]
            should_answer = bool(expected_documents)
            retrieval_hit = all(name in cited_documents for name in expected_documents) if should_answer else None
            top1_correct = bool(cited_documents and cited_documents[0] in expected_documents) if should_answer else None
            answer_normalized = normalize(response.answer)
            key_term_coverage = (
                sum(normalize(term) in answer_normalized for term in case["key_terms"])
                / len(case["key_terms"])
                if case["key_terms"]
                else None
            )
            cases.append(
                {
                    "id": case["id"],
                    "type": case["type"],
                    "should_answer": should_answer,
                    "evidence_sufficient": response.evidence_sufficient,
                    "retrieval_hit": retrieval_hit,
                    "top1_citation_correct": top1_correct,
                    "key_term_coverage": key_term_coverage,
                    "latency_ms": response.metrics.total_ms,
                    "answer": response.answer,
                    "cited_documents": cited_documents,
                }
            )

        answerable = [case for case in cases if case["should_answer"]]
        unanswerable = [case for case in cases if not case["should_answer"]]
        metrics = {
            "case_count": len(cases),
            "retrieval_recall_at_5": sum(case["retrieval_hit"] for case in answerable) / len(answerable),
            "top1_citation_accuracy": sum(case["top1_citation_correct"] for case in answerable) / len(answerable),
            "mean_key_term_coverage": statistics.mean(
                case["key_term_coverage"] for case in answerable if case["key_term_coverage"] is not None
            ),
            "answerable_acceptance_rate": sum(case["evidence_sufficient"] for case in answerable) / len(answerable),
            "unanswerable_rejection_rate": sum(not case["evidence_sufficient"] for case in unanswerable) / len(unanswerable),
            "median_latency_ms": statistics.median(case["latency_ms"] for case in cases),
            "p95_latency_ms": sorted(case["latency_ms"] for case in cases)[int(len(cases) * 0.95) - 1],
        }
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "provider": provider.name,
            "settings": {"top_k": 5, "min_evidence_score": settings.min_evidence_score},
            "metrics": metrics,
            "cases": cases,
        }
    finally:
        database.close()


def render_report(result: dict) -> str:
    metrics = result["metrics"]
    failed = [
        case
        for case in result["cases"]
        if (case["should_answer"] and not case["retrieval_hit"])
        or (not case["should_answer"] and case["evidence_sufficient"])
        or (case["key_term_coverage"] is not None and case["key_term_coverage"] < 1)
    ]
    rows = "\n".join(
        f"| {case['id']} | {case['type']} | {'sí' if case['evidence_sufficient'] else 'no'} | "
        f"{case['retrieval_hit'] if case['retrieval_hit'] is not None else 'n/a'} | "
        f"{case['key_term_coverage'] if case['key_term_coverage'] is not None else 'n/a'} |"
        for case in result["cases"]
    )
    failed_lines = "\n".join(f"- `{case['id']}`: {case['answer']}" for case in failed) or "- Ninguno."
    return f"""# Reporte de evaluación reproducible

- Generado: {result['generated_at']}
- Proveedor: `{result['provider']}`
- Casos: {metrics['case_count']}
- `top_k`: {result['settings']['top_k']}
- Umbral de evidencia: {result['settings']['min_evidence_score']}

## Resultados

| Métrica | Resultado |
| --- | ---: |
| Recall de documentos esperados @5 | {metrics['retrieval_recall_at_5']:.1%} |
| Precisión de cita Top-1 | {metrics['top1_citation_accuracy']:.1%} |
| Cobertura media de términos esperados | {metrics['mean_key_term_coverage']:.1%} |
| Aceptación de preguntas respondibles | {metrics['answerable_acceptance_rate']:.1%} |
| Rechazo de preguntas sin evidencia/ambiguas | {metrics['unanswerable_rejection_rate']:.1%} |
| Latencia mediana | {metrics['median_latency_ms']:.2f} ms |
| Latencia p95 | {metrics['p95_latency_ms']:.2f} ms |

## Detalle

| Caso | Tipo | Respondió | Retrieval hit | Cobertura |
| --- | --- | --- | --- | ---: |
{rows}

## Casos que requieren revisión

{failed_lines}

## Interpretación y límites

- La ejecución usa embeddings y respuestas determinísticos; valida integración y reproducibilidad, no la calidad de un LLM comercial.
- La cobertura de términos comprueba completitud contra expectativas, no equivalencia semántica exhaustiva.
- La precisión de cita se mide como documento correcto en la primera cita; una revisión humana debe comprobar que el fragmento sostiene cada afirmación.
- Para un informe OpenAI, ejecute con `AI_PROVIDER=openai` y registre modelos, precios configurados y fecha. Las métricas no deben mezclarse entre proveedores.
"""


if __name__ == "__main__":
    output = run()
    results_dir = REPO_ROOT / "evals" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "latest.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    (results_dir / "latest.md").write_text(render_report(output), encoding="utf-8")
    print(render_report(output))
