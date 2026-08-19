import argparse
import json
import statistics
import unicodedata
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = REPO_ROOT / "evals" / "los_heroes_2025.jsonl"


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def load_dataset() -> list[dict]:
    return [
        json.loads(line)
        for line in DATASET_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def post_query(api_url: str, question: str, top_k: int) -> dict:
    payload = json.dumps({"question": question, "top_k": top_k}).encode()
    request = urllib.request.Request(
        f"{api_url.rstrip('/')}/query",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"API respondió HTTP {exc.code}: {body}") from exc


def run(api_url: str, top_k: int) -> dict:
    cases: list[dict] = []
    for expected in load_dataset():
        response = post_query(api_url, expected["question"], top_k)
        citations = response["citations"]
        cited_pages = [citation["page"] for citation in citations if citation["page"]]
        should_answer = bool(expected["expected_pages"])
        page_hit = (
            bool(set(cited_pages).intersection(expected["expected_pages"]))
            if should_answer
            else None
        )
        answer = normalize(response["answer"])
        term_coverage = (
            sum(normalize(term) in answer for term in expected["key_terms"])
            / len(expected["key_terms"])
            if expected["key_terms"]
            else None
        )
        passed = (
            response["evidence_sufficient"] and page_hit and term_coverage == 1
            if should_answer
            else not response["evidence_sufficient"]
        )
        cases.append(
            {
                "id": expected["id"],
                "type": expected["type"],
                "question": expected["question"],
                "should_answer": should_answer,
                "passed": bool(passed),
                "evidence_sufficient": response["evidence_sufficient"],
                "page_hit": page_hit,
                "term_coverage": term_coverage,
                "cited_pages": cited_pages,
                "latency_ms": response["metrics"]["total_ms"],
                "answer": response["answer"],
            }
        )

    answerable = [case for case in cases if case["should_answer"]]
    unanswerable = [case for case in cases if not case["should_answer"]]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "api_url": api_url,
        "top_k": top_k,
        "metrics": {
            "case_count": len(cases),
            "pass_rate": sum(case["passed"] for case in cases) / len(cases),
            "answerable_page_recall": sum(case["page_hit"] for case in answerable)
            / len(answerable),
            "mean_key_term_coverage": statistics.mean(
                case["term_coverage"] for case in answerable
            ),
            "unanswerable_rejection_rate": sum(
                not case["evidence_sufficient"] for case in unanswerable
            )
            / len(unanswerable),
            "median_latency_ms": statistics.median(case["latency_ms"] for case in cases),
        },
        "cases": cases,
    }


def render_report(result: dict) -> str:
    metrics = result["metrics"]
    rows = "\n".join(
        f"| {case['id']} | {'sí' if case['passed'] else 'no'} | "
        f"{'sí' if case['evidence_sufficient'] else 'no'} | "
        f"{case['cited_pages'] or '—'} | "
        f"{case['term_coverage'] if case['term_coverage'] is not None else 'n/a'} |"
        for case in result["cases"]
    )
    return f"""# Evaluación live — Memoria Integrada Los Héroes 2025

- Generado: {result['generated_at']}
- API: `{result['api_url']}`
- `top_k`: {result['top_k']}
- Casos: {metrics['case_count']}

| Métrica | Resultado |
| --- | ---: |
| Casos aprobados | {metrics['pass_rate']:.1%} |
| Recall de página esperada | {metrics['answerable_page_recall']:.1%} |
| Cobertura media de términos | {metrics['mean_key_term_coverage']:.1%} |
| Rechazo sin evidencia | {metrics['unanswerable_rejection_rate']:.1%} |
| Latencia mediana | {metrics['median_latency_ms']:.2f} ms |

| Caso | Aprobó | Respondió | Páginas citadas | Cobertura |
| --- | --- | --- | --- | ---: |
{rows}

## Lectura correcta

- Esta evaluación usa una fuente pública concreta y debe ejecutarse después de indexar el PDF oficial.
- Los números dependen del proveedor, modelos, umbral y fecha registrados en la ejecución.
- Una aprobación automática no sustituye la revisión humana de fidelidad, contexto y accesibilidad.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalúa una instancia EvidenceRAG ya desplegada.")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="URL base terminada en /api/v1",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output-prefix", type=Path)
    args = parser.parse_args()

    result = run(args.api_url, args.top_k)
    report = render_report(result)
    if args.output_prefix:
        args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
        args.output_prefix.with_suffix(".json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        args.output_prefix.with_suffix(".md").write_text(report, encoding="utf-8")
    print(report)
    return 0 if result["metrics"]["pass_rate"] == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
