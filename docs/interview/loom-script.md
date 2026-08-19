# Guion de demo — 3 a 5 minutos

## Antes de grabar

- Confirmar que `/health` muestre base y proveedor operativos.
- Tener indexada `Memoria-Integrada-Los-Heroes-2025.pdf`.
- Usar ventana limpia, zoom legible y no mostrar `.env`, terminales con secretos ni paneles del VPS.
- Mantener visible el disclaimer de demostración no oficial.
- Si la instancia está en mock, decirlo expresamente; no simular que se usó OpenAI.

## 0:00–0:35 — Problema y alcance

“Esta es EvidenceRAG, una demostración conceptual no oficial construida exclusivamente con información pública. En dominios regulados no basta con una respuesta convincente: necesitamos saber qué documento y qué página la respaldan, y abstenernos cuando el corpus no sabe. Para demostrarlo uso como fuente inicial la Memoria Integrada Los Héroes 2025; no es un producto ni una implementación de Caja Los Héroes.”

## 0:35–1:10 — Ingestión y procedencia

“El cargador descarga una URL pública explícita, controla el máximo de 10 MiB, valida el PDF y su SHA-256, y deduplica por contenido y huella de embedding. Extrae texto por página, genera 980 fragmentos y persiste metadatos, vectores y archivo original. La huella separa mock de OpenAI para impedir que se mezclen índices incompatibles.”

Mostrar el documento disponible y su conteo. No volver a cargarlo en vivo si el tiempo es limitado.

## 1:10–2:00 — Respuesta verificable

Seleccionar: “¿Cómo se utilizaron la IA y Machine Learning durante 2025?”

“El retrieval combina similitud vectorial y cobertura léxica. Antes de generar aplica umbral, cobertura de términos, acrónimos y alcance nominal. La respuesta indica que el documento reporta mejoras en la validación automática de créditos sociales y en el servicio. La aplicación adjunta la página 66 y el fragmento original; las citas no se delegan al modelo.”

Abrir la primera fuente y leer solo el fragmento relevante.

## 2:00–2:45 — Operación y regulación

Seleccionar: “¿Cómo se gestionan y trazan las solicitudes y los reclamos?”

“Aquí recupera el sistema formal de reclamos, la Circular 3796, el SLA y la trazabilidad. Esto muestra cómo el mismo patrón puede apoyar consulta institucional y regulatoria sin ocultar el contexto. En una solución real agregaría identidad, roles, retención aprobada, auditoría y supervisión humana antes de usar datos sensibles.”

## 2:45–3:25 — Abstención deliberada

Seleccionar: “¿Qué servicios ofrece específicamente Los Héroes Digital?”

“Esta pregunta comparte palabras con el corpus, pero el documento no contiene una descripción oficial suficiente de esa unidad. El gate de alcance nominal evita convertir información general de Caja Los Héroes en una afirmación sobre Los Héroes Digital. Por eso responde que no existe evidencia suficiente y no fabrica citas.”

Como segundo ejemplo opcional: “¿Qué proveedor de nube y qué modelos de IA usa la organización?”.

## 3:25–4:10 — Medición y límites

“Cada consulta registra request ID, latencia, tokens y costo cuando hay tarifas configuradas. El corpus público completo se verificó con 10 casos: ocho respondibles y dos de rechazo; el baseline mock dirigido obtuvo 10 de 10 y una mediana local cercana a 412 milisegundos. Es un gate reproducible de esta demo, no una afirmación de precisión general ni una evaluación de OpenAI.”

## 4:10–4:45 — Arquitectura y cierre

“La solución separa Next.js, FastAPI, retrieval, proveedor y PostgreSQL con pgvector. Está preparada para validar primero en mock y reindexar el mismo corpus con OpenAI sin mezclar vectores. Mi foco fue construir un vertical slice defendible: procedencia, seguridad, evaluación, observabilidad, despliegue y límites explícitos. El siguiente paso es entender los casos prioritarios, restricciones de datos y resultados de 90 días de la unidad antes de agregar complejidad.”

## Versión de 3 minutos

Recortar la segunda consulta y resumir arquitectura/medición en 25 segundos. Mantener siempre: disclaimer, una respuesta con página, un rechazo y el límite del baseline.
