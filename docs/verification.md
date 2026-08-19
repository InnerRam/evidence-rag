# Estado de verificación — 2026-08-18

## Completado en este workspace

- Backend importable con Python 3.12 y Ruff limpio.
- 16 pruebas pytest aprobadas.
- Cobertura backend: 88,66%, superior al gate de 85%.
- Vertical slice con TestClient: health, carga, deduplicación, persistencia SQLite, pregunta, cita, métricas, historial, rechazo y errores visibles.
- Aislamiento de índice por huella de proveedor/modelo/dimensión cubierto por implementación y pruebas de dominio.
- Evaluación sintética: 18/18 casos, 100% en los gates definidos, mediana local 4,03 ms.
- Fuente pública verificada por tamaño y SHA-256; ingestión real: 388 páginas extraíbles y 980 fragmentos.
- Evaluación live del PDF completo en mock: 10/10 casos, 100% en aprobación, página, términos y rechazo; mediana local 412,06 ms.
- Smoke HTTP y reinicio real de Uvicorn contra persistencia SQLite aprobados en una validación previa.
- OpenAI SDK implementado con embeddings por lotes y Responses API; los índices quedan aislados del mock.
- Compose y Dockerfiles revisados estáticamente: base sin puertos, perfil local solo loopback, PostgreSQL fuera de la red proxy y aliases NPM únicos.

Los porcentajes de evaluación pertenecen a datasets versionados y dirigidos. No representan precisión general ni resultados con OpenAI.

## Pendiente por entorno

- `docker compose up --build`: Docker no está disponible en este workspace.
- Frontend `pnpm install`, lint, typecheck, test y build: no hay dependencias instaladas ni lockfile en este workspace; los gates están definidos en el target Docker.
- Flujo real con OpenAI: no hay API key configurada y no se solicitó compartirla.
- VPS: el diagnóstico recibido muestra 96% de uso de disco y solo 3 GB libres. El despliegue queda bloqueado hasta revisar ocupación y recuperar margen de manera controlada.

## Gates antes de publicar

1. Diagnosticar disco sin eliminar datos; acordar una limpieza dirigida y confirmar al menos 8 GB libres, idealmente 10 GB.
2. Ejecutar los targets Docker de prueba y `docker compose -f compose.yaml -f compose.prod.yaml config --quiet` en el VPS.
3. Generar/versionar `apps/web/pnpm-lock.yaml` y aprobar lint, tipos, tests y build.
4. Levantar solo EvidenceRAG y comprobar health, logs y persistencia sin reiniciar proyectos ajenos.
5. Indexar el PDF con `python3 -m app.seed_public` y ejecutar el set live por el subdominio API.
6. Configurar Nginx Proxy Manager y acceso controlado para web/API.
7. Solo después, activar OpenAI, reindexar bajo la nueva huella y comparar resultados con revisión humana.
