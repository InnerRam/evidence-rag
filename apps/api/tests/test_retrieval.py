from app.retrieval import fuzzy_term_coverage, lexical_coverage


def test_lexical_coverage_accepts_close_inflections() -> None:
    exact_score = lexical_coverage(
        "¿Con qué frecuencia se respaldan los datos?",
        "La frecuencia del respaldo de datos es diaria y la base se respalda cada día.",
    )
    fuzzy_score = fuzzy_term_coverage(
        "¿Con qué frecuencia se respaldan los datos?",
        "La frecuencia del respaldo de datos es diaria y la base se respalda cada día.",
    )
    assert exact_score < 1
    assert fuzzy_score == 1


def test_lexical_coverage_does_not_infer_absent_compound_claim() -> None:
    score = fuzzy_term_coverage(
        "¿Qué proveedor de nube y qué modelos de IA usa la organización?",
        "La organización formaliza criterios para el desarrollo de modelos propios.",
    )
    assert score < 0.35
