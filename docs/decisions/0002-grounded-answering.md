# ADR 0002 — Rechazo previo y citas controladas por la aplicación

- Estado: aceptada
- Fecha: 2026-08-18

## Decisión

La API reordena candidatos con score híbrido y rechaza cuando no alcanza `MIN_EVIDENCE_SCORE`, cobertura mínima de términos, acrónimos citados o alcance nominal explícito. Cuando existe evidencia, el proveedor genera una respuesta limitada al contexto y la aplicación agrega citas con identificadores, documento, página/sección, score y fragmento.

## Razones

- Una respuesta fluida sin respaldo no cumple el objetivo de evidencia verificable.
- El localizador de una cita no debe depender de la obediencia del LLM.
- Un gate explícito se puede evaluar, calibrar y explicar en entrevista.

## Alternativas descartadas

- Pedir al modelo que invente citas inline: difícil de verificar.
- Responder siempre y mostrar fuentes parecidas: oculta ausencia de evidencia.
- Reranking en el MVP: añade costo y variables antes de medir si es necesario.
