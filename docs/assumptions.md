# Supuestos y exclusiones activas

## Supuestos

- La primera audiencia es una entrevista técnica en Chile; la interfaz y documentación principal están en español.
- Los tres documentos sintéticos se conservan para gates rápidos; la demo inicial usa además la Memoria Integrada Los Héroes 2025, descargada desde su URL pública y verificada por SHA-256.
- El volumen del MVP permite procesamiento síncrono y carga completa del archivo hasta 10 MB.
- Una instalación representa un único espacio documental; no hay aislamiento multi-tenant.
- En producción se usa PostgreSQL 16 con pgvector; SQLite solo es una ruta de desarrollo y pruebas.
- Nginx Proxy Manager alcanza web y API mediante una red Docker externa; PostgreSQL no se conecta a esa red ni publica puerto.
- Los precios se configuran explícitamente porque cambian por modelo, contrato y fecha. Un valor cero produce costo `n/a`, no un costo ficticio.
- “Los Héroes Digital” puede ser la unidad contratante, pero su forma, servicios, stack y mandato exactos no están confirmados; la demo no los inventa.

## Exclusiones del MVP

- OCR, reranking, agentes, fine-tuning, autenticación empresarial, colas distribuidas y multi-tenancy.
- Documentos confidenciales y acciones externas ordenadas desde el contenido recuperado.
- Escalamiento para millones de fragmentos; primero se medirá la necesidad.
- Representar una implementación, producto oficial o arquitectura interna de Caja Los Héroes.

## Restricciones operativas vigentes

- Docker existe y el stack de producción ya fue construido y validado en el VPS, pero `codex-evidence` no pertenece al grupo Docker ni tiene sudo general.
- El frontend dispone de lockfile pnpm versionado y su imagen standalone está desplegada; lint, tipos, tests y build siguen siendo gates obligatorios de cada cambio mediante los targets Docker.
- El checkout de producción pertenece a `adminuser` y no es legible por `codex-evidence`. Esta separación se conserva; la operación delegada pasa exclusivamente por el wrapper root-owned descrito en `docs/operations.md`.
- No existe una `OPENAI_API_KEY` compartida. El cierre público actual usa `AI_PROVIDER=mock`; OpenAI y sus métricas quedan fuera de alcance hasta una autorización separada.
- Nginx Proxy Manager ya alcanza web y API por la red externa. Certificado, Force SSL y health externo deben quedar evidenciados antes de declarar cerrado HTTPS.
- No se autorizan commit, push, merge, instalación privilegiada ni deploy implícitos; cada transición requiere el checkpoint y la autorización definidos para este cierre.
