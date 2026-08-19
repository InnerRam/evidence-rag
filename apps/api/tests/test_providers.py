import numpy as np

from app.providers import MockProvider


def test_mock_embeddings_are_deterministic_and_normalized() -> None:
    provider = MockProvider(dimensions=128)
    first, usage = provider.embed(["energía solar comunitaria"])
    second, _ = provider.embed(["energía solar comunitaria"])
    assert first == second
    assert np.isclose(np.linalg.norm(first[0]), 1.0)
    assert usage.input_tokens > 0


def test_mock_answer_uses_only_context_sentences() -> None:
    provider = MockProvider(dimensions=128)
    generated = provider.answer(
        "¿Cuál es la meta solar?",
        ["La meta solar del programa es instalar 120 kilovatios antes de diciembre."],
    )
    assert "120 kilovatios" in generated.text
