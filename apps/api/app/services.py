import re
import time
import unicodedata
import uuid

from sqlalchemy.orm import Session

from app.config import Settings
from app.models import QueryLog
from app.providers import AIProvider, ProviderUsage, meaningful_tokens
from app.retrieval import fuzzy_term_coverage, retrieve
from app.schemas import Citation, QueryMetrics, QueryResponse

INSUFFICIENT_ANSWER = "No existe evidencia suficiente en los documentos cargados para responder."
AMBIGUOUS_TERMS = {"responsable", "encargado", "persona", "plazo", "fecha"}
NAMED_PHRASE_RE = re.compile(
    r"\b[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9-]*"
    r"(?:\s+(?:(?:de|del|la|las|los|y)\s+)?"
    r"[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9-]*)+\b"
)
ACRONYM_RE = re.compile(r"\b[A-ZÁÉÍÓÚÜÑ]{2,8}\b")


def is_underspecified(question: str) -> bool:
    terms = set(meaningful_tokens(question))
    return len(terms) <= 2 and bool(terms.intersection(AMBIGUOUS_TERMS))


def normalize_for_match(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", without_accents))


def named_scope_is_supported(question: str, contexts: list[str]) -> bool:
    """Reject named scopes that do not appear verbatim in the retrieved evidence."""
    phrases = NAMED_PHRASE_RE.findall(question)
    if not phrases:
        return True
    evidence = normalize_for_match("\n".join(contexts))
    return all(normalize_for_match(phrase) in evidence for phrase in phrases)


def acronyms_are_supported(question: str, contexts: list[str]) -> bool:
    required = {acronym.casefold() for acronym in ACRONYM_RE.findall(question)}
    if not required:
        return True
    evidence_tokens = set(meaningful_tokens("\n".join(contexts)))
    return required.issubset(evidence_tokens)


def estimate_cost(
    settings: Settings, embedding_usage: ProviderUsage, answer_usage: ProviderUsage
) -> float | None:
    rates = (
        settings.openai_embedding_usd_per_million,
        settings.openai_input_usd_per_million,
        settings.openai_output_usd_per_million,
    )
    if settings.ai_provider != "openai" or not any(rates):
        return None
    cost = (
        embedding_usage.input_tokens * rates[0]
        + answer_usage.input_tokens * rates[1]
        + answer_usage.output_tokens * rates[2]
    ) / 1_000_000
    return round(cost, 8)


def answer_question(
    database: Session,
    provider: AIProvider,
    settings: Settings,
    question: str,
    top_k: int,
    session_id: str | None,
) -> QueryResponse:
    total_started = time.perf_counter()
    retrieval_started = time.perf_counter()
    vectors, embedding_usage = provider.embed([question])
    retrieved = retrieve(
        database, vectors[0], question, top_k, provider.embedding_fingerprint
    )
    retrieval_ms = round((time.perf_counter() - retrieval_started) * 1000, 2)

    retrieved_contexts = [item.chunk.content for item in retrieved]
    best_lexical_coverage = max(
        (fuzzy_term_coverage(question, context) for context in retrieved_contexts), default=0.0
    )
    sufficient = bool(
        retrieved
        and retrieved[0].score >= settings.min_evidence_score
        and best_lexical_coverage >= settings.min_lexical_coverage
        and not is_underspecified(question)
        and named_scope_is_supported(question, retrieved_contexts)
        and acronyms_are_supported(question, retrieved_contexts)
    )
    citations: list[Citation] = []
    generation_ms = 0.0
    answer_usage = ProviderUsage()

    if sufficient:
        generation_started = time.perf_counter()
        generated = provider.answer(question, retrieved_contexts)
        generation_ms = round((time.perf_counter() - generation_started) * 1000, 2)
        answer = generated.text or INSUFFICIENT_ANSWER
        answer_usage = generated.usage
        if answer == INSUFFICIENT_ANSWER:
            sufficient = False
        else:
            citations = [
                Citation(
                    id=f"E{index}",
                    document_id=item.document.id,
                    document=item.document.filename,
                    page=item.chunk.page_number,
                    section=item.chunk.section,
                    score=item.score,
                    snippet=item.chunk.content[:700],
                )
                for index, item in enumerate(retrieved, start=1)
            ]
    else:
        answer = INSUFFICIENT_ANSWER

    resolved_session_id = session_id or uuid.uuid4().hex
    total_ms = round((time.perf_counter() - total_started) * 1000, 2)
    cost = estimate_cost(settings, embedding_usage, answer_usage)
    log = QueryLog(
        session_id=resolved_session_id,
        question=question,
        answer=answer,
        evidence_sufficient=sufficient,
        citation_ids=[citation.id for citation in citations],
        provider=provider.name,
        retrieval_ms=retrieval_ms,
        generation_ms=generation_ms,
        total_ms=total_ms,
        embedding_tokens=embedding_usage.input_tokens,
        input_tokens=answer_usage.input_tokens,
        output_tokens=answer_usage.output_tokens,
        estimated_cost_usd=cost,
    )
    database.add(log)
    database.commit()
    database.refresh(log)

    return QueryResponse(
        query_id=log.id,
        session_id=resolved_session_id,
        answer=answer,
        evidence_sufficient=sufficient,
        citations=citations,
        metrics=QueryMetrics(
            retrieval_ms=retrieval_ms,
            generation_ms=generation_ms,
            total_ms=total_ms,
            embedding_tokens=embedding_usage.input_tokens,
            input_tokens=answer_usage.input_tokens,
            output_tokens=answer_usage.output_tokens,
            estimated_cost_usd=cost,
        ),
        provider=provider.name,
    )
