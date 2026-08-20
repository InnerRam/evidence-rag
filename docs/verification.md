# Estado de verificación — 2026-08-20

## Baseline técnico y validaciones confirmadas

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
- El lockfile pnpm está versionado. Los commits `1960050` y `21897b8` estabilizaron dependencias y runtime standalone del frontend.
- El operador confirmó en el VPS que PostgreSQL, API y web fueron construidos, levantados y están healthy en modo mock.
- El operador confirmó que Nginx Proxy Manager alcanza `evidence-rag-web:3000` y `evidence-rag-api:8000` por la red externa, sin conectar PostgreSQL a ella.
- Producción usa un checkout separado en `/home/adminuser/web-apps/evidence-rag`; el workspace remoto permanecía sincronizado con `origin/main` en `21897b8` antes de esta rama de trabajo.
- Validación directa mediante el wrapper: Compose válido; commit desplegado `21897b8`; API, base y web healthy; proveedor `mock`; web HTTP 200.
- Gates Docker directos en el VPS: backend 16/16 con 88,66% de cobertura; frontend lint, TypeScript, 1/1 test y build Next.js aprobados.
- Seed público ejecutado con checksum: 388 páginas y 980 fragmentos; smoke aprobado con respuesta sustentada, cinco citas y rechazo sin citas.

Los porcentajes de evaluación pertenecen a datasets versionados y dirigidos. No representan precisión general ni resultados con OpenAI.

## Evidencia y límites de esta auditoría

- `codex-evidence` no puede atravesar `/home/adminuser` ni acceder al socket Docker. Esa separación fue comprobada directamente y es intencional.
- Desde la cuenta no privilegiada solo se observaron Docker/Nginx activos y listeners 80/443; no se atribuyeron puertos o procesos ambiguos a EvidenceRAG ni se leyó `.env`.
- El health de los tres servicios fue comprobado directamente mediante el wrapper delegado. La conectividad interna de NPM consta como validación confirmada por el operador porque NPM permanece deliberadamente fuera del alcance del wrapper.
- `rag.citec.cl` y `rag-api.citec.cl` resuelven al VPS y presentan certificados Let's Encrypt válidos. La web pública sirve EvidenceRAG y fuerza HTTPS; el health HTTPS de la API devuelve `status=ok`, `database=ok` y `provider=mock`. El host API todavía acepta HTTP 200, por lo que Force SSL sigue pendiente.
- El flujo OpenAI no forma parte del cierre mock y sigue sin clave compartida; sus métricas permanecen pendientes por decisión de alcance.
- El wrapper y sudoers de `infra/ops/` fueron instalados como root-owned y validados mediante la cuenta delegada. El wrapper instalado coincide con SHA-256 `381b3b9de97567d809ac7ef5b31dbdd4b547050a994dc626bc1263eae90a3ca5`.

## Gates restantes para cerrar el MVP público mock

1. Revisar y publicar el diff de la rama; solo con autorización explícita: commit, push, merge a `main` y deploy desde `origin/main` usando el wrapper.
2. Confirmar desde un cliente externo certificado válido, Force SSL y `/health` con `provider=mock` por el subdominio API.
3. Ejecutar `scripts/run_live_evals.py` contra HTTPS, versionar el reporte del despliegue y revisar manualmente al menos una respuesta y un rechazo.

OpenAI, OIDC y hardening empresarial pertenecen al roadmap posterior; no bloquean el MVP público controlado en modo mock.
