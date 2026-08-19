# Evolución transparente

## Siguiente validación

- Ejecutar los 18 casos sintéticos y los 10 casos del PDF público con OpenAI; registrar modelo, fecha, tokens, costo y fallos por separado.
- Revisión humana ciega de fidelidad y citas.
- Calibrar `MIN_EVIDENCE_SCORE` por dominio.
- Incorporar fuentes públicas adicionales de SUSESO/CMF solo después de estabilizar y revisar el corpus inicial.

## Producción inicial

- OIDC, roles simples y aislamiento de corpus.
- Ingestión asíncrona con reintentos e idempotencia.
- Alembic y política de retención/borrado.
- Object storage, antimalware y límites de recursos.
- Métricas Prometheus/OpenTelemetry y alertas.
- CI con lint, tipos, pruebas, build, SCA y escaneo de imágenes.

## Solo con evidencia de necesidad

- OCR para documentos escaneados.
- Reranking o MMR para mejorar resultados difíciles.
- Reranker dedicado o índice lexical avanzado si el retrieval híbrido actual no alcanza en nuevos corpus.
- Redis para caché y rate limiting.
- Multi-tenancy y motor vectorial especializado.
- Evaluadores LLM, siempre complementados por muestras humanas.
