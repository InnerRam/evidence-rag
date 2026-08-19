from app.services import acronyms_are_supported, named_scope_is_supported, normalize_for_match


def test_normalize_for_match_ignores_case_accents_and_punctuation() -> None:
    assert normalize_for_match("Caja Los Héroes, S.A.") == "caja los heroes s a"


def test_named_scope_requires_full_phrase_in_evidence() -> None:
    question = "¿Qué servicios ofrece específicamente Los Héroes Digital?"
    generic_context = "Los Héroes amplió sus servicios y canales digitales durante 2025."
    scoped_context = "Los Héroes Digital ofrece una descripción institucional verificable."

    assert named_scope_is_supported(question, [generic_context]) is False
    assert named_scope_is_supported(question, [scoped_context]) is True


def test_question_without_named_phrase_is_not_blocked() -> None:
    assert named_scope_is_supported("¿Cuántas llamadas atendió el call center?", []) is True


def test_acronyms_must_appear_as_complete_evidence_tokens() -> None:
    question = "¿Qué modelos de IA usa la organización?"
    assert acronyms_are_supported(question, ["Se describen modelos de riesgo."]) is False
    assert acronyms_are_supported(question, ["Se profundizó el uso de IA."]) is True
