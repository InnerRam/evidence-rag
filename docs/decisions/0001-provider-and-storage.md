# ADR 0001 — Proveedores intercambiables y dos modos de persistencia

- Estado: aceptada
- Fecha: 2026-08-18

## Decisión

El dominio depende de interfaces `EmbeddingProvider` y `AnswerProvider`. `OpenAIProvider` implementa producción; `MockProvider` ofrece embeddings y respuestas determinísticos sin red. PostgreSQL con pgvector es la persistencia objetivo; SQLite es el modo local y de pruebas.

Cada proveedor publica una huella formada por proveedor, implementación/modelo y dimensión. Documento, deduplicación, listado y retrieval se segmentan por esa huella para impedir que una consulta OpenAI use vectores mock o de otro modelo.

## Razones

- La demo debe funcionar sin exponer ni exigir una API key.
- Las evaluaciones deben ser repetibles.
- La arquitectura debe admitir otro proveedor sin reescribir ingestión, retrieval o API.
- PostgreSQL/pgvector demuestra la ruta empresarial, mientras SQLite reduce la fricción de evaluación local.

## Consecuencias

- El modo mock prueba el sistema, pero no demuestra calidad generativa de un modelo real.
- Las métricas con OpenAI deben ejecutarse separadamente y registrar el modelo exacto.
- La dimensionalidad del vector es configuración de despliegue y no debe cambiarse sobre una base ya ingerida sin reindexar.
- Cambiar de proveedor o modelo con la misma dimensión requiere reingestión, pero no borrar el índice anterior; cambiar dimensión requiere migración o base nueva.
