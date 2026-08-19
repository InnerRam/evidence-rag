# EvidenceRAG — IA aplicada con respuestas verificables

## Desafío

Las organizaciones reguladas acumulan memorias, normas, políticas y procedimientos. Encontrar una respuesta confiable es lento, y un chatbot genérico puede completar vacíos con texto plausible. El problema exige procedencia, rechazo explícito, revisión humana y métricas operativas.

## Solución

Construí un asistente documental que ingiere PDF/TXT/MD, conserva página o sección, deduplica por SHA-256 y almacena embeddings en PostgreSQL con pgvector. El retrieval híbrido combina señal vectorial y léxica; luego aplica gates de score, cobertura, acrónimos y alcance nominal. Solo con evidencia suficiente genera una respuesta y adjunta citas creadas por la aplicación.

La demo usa la Memoria Integrada Los Héroes 2025 como fuente institucional pública. EvidenceRAG mantiene identidad y arquitectura propias. Es una demostración conceptual no oficial; no representa un producto, encargo ni implementación de Caja Los Héroes.

## Decisiones clave

- FastAPI y Next.js/Material UI para separar API, experiencia y evolución.
- Proveedor OpenAI intercambiable con un mock determinístico sin secretos.
- Huella de embedding por proveedor/modelo/dimensión para no mezclar índices.
- PostgreSQL/pgvector por operación sencilla y control de metadatos.
- Rechazo antes de generación para reducir falsos positivos y costo.
- Documentos como contenido no confiable, sin autoridad ni tools.
- Corpus, preguntas y reportes versionados antes de agregar complejidad.

## Evidencia de funcionamiento

- PDF público: 8.665.067 bytes, SHA-256 verificado, 388 páginas extraíbles y 980 fragmentos.
- Set live mock: 10 casos, con 100% de aprobación, recall de página, cobertura de términos y rechazo; mediana local de 412,06 ms.
- Set sintético de regresión: 18 casos, 100% en los gates definidos y mediana local de 4,03 ms.
- Backend: el estado vigente de pruebas y cobertura está en `docs/verification.md`.

Estas cifras validan recorridos concretos y reproducibles. No equivalen a precisión general, no sustituyen revisión humana y no representan todavía resultados con OpenAI.

## Relevancia empresarial

El patrón reduce tiempo de búsqueda y facilita auditoría porque la persona puede revisar de inmediato el fragmento que sostiene la respuesta. En seguridad social y servicios financieros, el valor depende además de privacidad, accesibilidad, explicabilidad, seguridad, cumplimiento y supervisión humana. La demo hace visibles esos requisitos sin afirmar cómo opera internamente una organización específica.

## Próximo paso medible

Desplegar mock con acceso controlado, ejecutar el set live, activar OpenAI y reindexar el corpus bajo una huella separada. Comparar fidelidad, citas, rechazos, latencia, tokens y costo con revisión humana. Solo después decidir reranking, OCR, nuevas fuentes o automatizaciones según errores observados y prioridades de negocio.
