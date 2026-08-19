# Reporte de evaluación reproducible

- Generado: 2026-08-18T20:07:52.726697+00:00
- Proveedor: `mock`
- Casos: 18
- `top_k`: 5
- Umbral de evidencia: 0.18

## Resultados

| Métrica | Resultado |
| --- | ---: |
| Recall de documentos esperados @5 | 100.0% |
| Precisión de cita Top-1 | 100.0% |
| Cobertura media de términos esperados | 100.0% |
| Aceptación de preguntas respondibles | 100.0% |
| Rechazo de preguntas sin evidencia/ambiguas | 100.0% |
| Latencia mediana | 4.03 ms |
| Latencia p95 | 5.08 ms |

## Detalle

| Caso | Tipo | Respondió | Retrieval hit | Cobertura |
| --- | --- | --- | --- | ---: |
| solar-01 | answerable | sí | True | 1.0 |
| solar-02 | answerable | sí | True | 1.0 |
| solar-03 | answerable | sí | True | 1.0 |
| solar-04 | multi_fragment | sí | True | 1.0 |
| solar-05 | answerable | sí | True | 1.0 |
| continuidad-01 | answerable | sí | True | 1.0 |
| continuidad-02 | answerable | sí | True | 1.0 |
| continuidad-03 | multi_fragment | sí | True | 1.0 |
| continuidad-04 | answerable | sí | True | 1.0 |
| ia-01 | answerable | sí | True | 1.0 |
| ia-02 | answerable | sí | True | 1.0 |
| ia-03 | multi_fragment | sí | True | 1.0 |
| ia-04 | answerable | sí | True | 1.0 |
| cross-01 | multi_document | sí | True | 1.0 |
| ambiguous-01 | ambiguous | no | n/a | n/a |
| unanswerable-01 | unanswerable | no | n/a | n/a |
| unanswerable-02 | unanswerable | no | n/a | n/a |
| unanswerable-03 | unanswerable | no | n/a | n/a |

## Casos que requieren revisión

- Ninguno.

## Interpretación y límites

- La ejecución usa embeddings y respuestas determinísticos; valida integración y reproducibilidad, no la calidad de un LLM comercial.
- La cobertura de términos comprueba completitud contra expectativas, no equivalencia semántica exhaustiva.
- La precisión de cita se mide como documento correcto en la primera cita; una revisión humana debe comprobar que el fragmento sostiene cada afirmación.
- Para un informe OpenAI, ejecute con `AI_PROVIDER=openai` y registre modelos, precios configurados y fecha. Las métricas no deben mezclarse entre proveedores.
