import math
from dataclasses import dataclass

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.providers import meaningful_tokens


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    document: Document
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    left_array = np.asarray(left, dtype=np.float32)
    right_array = np.asarray(right, dtype=np.float32)
    denominator = float(np.linalg.norm(left_array) * np.linalg.norm(right_array))
    if math.isclose(denominator, 0.0):
        return 0.0
    return float(np.dot(left_array, right_array) / denominator)


def lexical_coverage(query: str, content: str) -> float:
    query_terms = set(meaningful_tokens(query))
    if not query_terms:
        return 0.0
    content_terms = set(meaningful_tokens(content))
    return len(query_terms.intersection(content_terms)) / len(query_terms)


def fuzzy_term_coverage(query: str, content: str) -> float:
    query_terms = set(meaningful_tokens(query))
    if not query_terms:
        return 0.0
    content_terms = set(meaningful_tokens(content))
    supported = 0
    for query_term in query_terms:
        exact = query_term in content_terms
        same_prefix = len(query_term) >= 7 and any(
            len(content_term) >= 7 and content_term[:5] == query_term[:5]
            for content_term in content_terms
        )
        supported += exact or same_prefix
    return supported / len(query_terms)


def hybrid_score(vector_score: float, query: str, content: str) -> float:
    lexical_score = lexical_coverage(query, content)
    bounded_vector_score = max(0.0, min(1.0, vector_score))
    return round(0.55 * bounded_vector_score + 0.45 * lexical_score, 6)


def retrieve(
    database: Session,
    query_vector: list[float],
    query: str,
    top_k: int,
    embedding_fingerprint: str,
) -> list[RetrievedChunk]:
    if database.bind and database.bind.dialect.name == "postgresql":
        distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
        rows = database.execute(
            select(Chunk, Document, distance)
            .join(Document, Document.id == Chunk.document_id)
            .where(
                Document.status == "available",
                Document.embedding_fingerprint == embedding_fingerprint,
            )
            .order_by(distance)
            .limit(max(100, top_k * 20))
        ).all()
        ranked = [
            RetrievedChunk(
                chunk=row[0],
                document=row[1],
                score=hybrid_score(1 - float(row[2]), query, row[0].content),
            )
            for row in rows
        ]
        return sorted(ranked, key=lambda item: item.score, reverse=True)[:top_k]

    rows = database.execute(
        select(Chunk, Document)
        .join(Document, Document.id == Chunk.document_id)
        .where(
            Document.status == "available",
            Document.embedding_fingerprint == embedding_fingerprint,
        )
    ).all()
    ranked = [
        RetrievedChunk(
            chunk=chunk,
            document=document,
            score=hybrid_score(
                cosine_similarity(query_vector, list(chunk.embedding)), query, chunk.content
            ),
        )
        for chunk, document in rows
    ]
    return sorted(ranked, key=lambda item: item.score, reverse=True)[:top_k]
