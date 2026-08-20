# Despliegue en VPS con Docker Compose

## Requisitos

- Ubuntu 20.04 o posterior con actualizaciones de seguridad.
- Docker Engine con Compose v2.
- DNS de los subdominios públicos `rag.citec.cl` y `rag-api.citec.cl`.
- Nginx Proxy Manager conectado a la red Docker externa indicada en `PROXY_NETWORK`.

## Estado operativo confirmado — 2026-08-20

El stack ya fue construido y levantado en el checkout exclusivo
`/home/adminuser/web-apps/evidence-rag`. PostgreSQL, API y web están healthy en
modo mock, y Nginx Proxy Manager alcanza los aliases de web y API. El lockfile
pnpm y el runtime standalone del frontend están versionados.

El wrapper root-owned desplegó y confirmó directamente el commit `b4cc2603`, health de los tres
servicios, proveedor mock y web HTTP 200. Los gates Docker aprobaron backend y
frontend; el seed dejó 388 páginas y 980 fragmentos, y el smoke verificó respuesta
citada y rechazo sin evidencia.

La comprobación externa del 2026-08-20 confirmó que ambos nombres resuelven al
VPS, presentan certificados Let's Encrypt válidos y sirven EvidenceRAG por
HTTPS. `https://rag-api.citec.cl/health` devuelve base y proveedor mock en estado
correcto. Ambos hosts fuerzan la redirección HTTP→HTTPS y CORS permite únicamente
el origen público de la web para las consultas previstas.

La evaluación live pública aprobó 10/10 casos, con 100% de recall de página,
cobertura de términos y rechazo sin evidencia; la latencia mediana observada fue
45 ms. El reporte versionado está en `evals/results/deployment-mock.md`.

El dato histórico de capacidad no se revalidó desde la cuenta restringida y no
debe usarse para afirmar que el stack sigue pendiente: el despliegue healthy fue
confirmado posteriormente. Antes de un nuevo build, el administrador debe revisar
el margen vigente. Se mantiene la regla de no ejecutar `docker system prune`,
no borrar volúmenes y no rotar o truncar logs a ciegas. Cualquier nueva alerta de disco requiere un
diagnóstico específico y revisión antes de eliminar datos.

## Preparación

1. Mantener el repositorio en una carpeta exclusiva: `/home/adminuser/web-apps/evidence-rag`.
2. Mantener la configuración exclusivamente en `.env`, fuera de Git.
3. Usar una contraseña PostgreSQL URL-safe larga porque forma parte de `DATABASE_URL`.
4. Definir `API_CORS_ORIGINS=https://rag.citec.cl` y `NEXT_PUBLIC_API_URL=https://rag-api.citec.cl/api/v1`.
5. Definir `PROXY_NETWORK` con el nombre exacto de la red externa compartida con Nginx Proxy Manager.
6. Mantener `AI_PROVIDER=mock` para el MVP público. `OPENAI_API_KEY` debe permanecer vacía.

`apps/web/pnpm-lock.yaml` ya está versionado. El Dockerfile usa instalación congelada.

## Gates de cada publicación

Ejecutar desde la raíz del repositorio:

```bash
pwd
git status --short --branch
docker compose -f compose.yaml -f compose.prod.yaml config --quiet
docker build --target test -t evidence-rag-api-test ./apps/api
docker run --rm evidence-rag-api-test
docker build --target test -t evidence-rag-web-test ./apps/web
docker run --rm evidence-rag-web-test
```

Si un gate falla, no continuar al despliegue. La operación delegada debe usar el
wrapper documentado en [operations.md](operations.md), que fija la superficie
Compose/Dockerfile y no permite argumentos Docker libres.

## Acceso operativo mínimo

La cuenta `codex-evidence` no recibe acceso al socket Docker ni sudo general. La
regla versionada autoriza exclusivamente `config`, `status`, logs acotados,
`health`, `tests`, `build`, deploy fast-forward desde `origin/main`, seed
público, smoke, restart del proyecto y rollback al commit previo. Su instalación
es una acción root separada y explícita; Nginx Proxy Manager y otros proyectos
quedan fuera de alcance.

## Primer arranque

```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d --build
docker compose -f compose.yaml -f compose.prod.yaml ps
docker compose -f compose.yaml -f compose.prod.yaml logs --tail=100 api web db
```

Indexar la fuente pública inicial. El comando verifica la huella conocida y, si ya existe para el proveedor activo, no duplica trabajo:

```bash
docker compose -f compose.yaml -f compose.prod.yaml exec -T api python3 -m app.seed_public
```

Validar health dentro de la red del proyecto sin publicar puertos:

```bash
docker compose -f compose.yaml -f compose.prod.yaml exec -T api \
  python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
```

## Persistencia y respaldo

- `postgres_data` conserva base y vectores.
- `upload_data` conserva originales por hash.
- Respaldar ambos volúmenes; validar restauración antes de considerar que existe un respaldo operativo.
- No usar `docker compose down -v` salvo que se quiera eliminar de forma intencional toda la información.

## Actualización segura

1. Confirmar checkout limpio sobre `main`.
2. Obtener únicamente un fast-forward desde `origin/main`.
3. Ejecutar tests API/web y validar Compose.
4. Construir sin detener los contenedores activos.
5. Activar solo `db`, `api` y `web`, esperar health y conservar el commit anterior.
6. Si health falla, volver al commit anterior sin eliminar volúmenes.

El wrapper automatiza exactamente este flujo y serializa las operaciones con un lock.

## Nginx Proxy Manager

Crear dos Proxy Hosts:

| Host | Forward hostname/port | Websockets | SSL |
| --- | --- | --- | --- |
| `rag.citec.cl` | `evidence-rag-web:3000` | activado | Let's Encrypt + Force SSL |
| `rag-api.citec.cl` | `evidence-rag-api:8000` | activado | Let's Encrypt + Force SSL |

Añadir en “Advanced” del API:

```nginx
client_max_body_size 10m;
proxy_read_timeout 120s;
proxy_send_timeout 120s;
add_header X-Content-Type-Options nosniff always;
add_header Referrer-Policy no-referrer always;
```

Para una entrevista pública, proteger ambos hosts con Access List. Una demo sin autenticación no debe recibir documentos privados.

Después de crear ambos Proxy Hosts, comprobar desde un cliente externo:

```bash
curl -fsS https://rag-api.citec.cl/health
```

La respuesta debe indicar `status=ok`, `database=ok` y `provider=mock`. Luego
comprobar desde la web una pregunta sustentada y una sin evidencia. Reiniciar
solamente EvidenceRAG para validar persistencia; no reiniciar Nginx Proxy Manager
ni contenedores de otros proyectos.

Ejecutar el set live desde una máquina con acceso al subdominio API:

```bash
python3 scripts/run_live_evals.py \
  --api-url https://rag-api.citec.cl/api/v1 \
  --output-prefix evals/results/deployment-mock
```

Versionar el reporte solo después de revisar que corresponde al hostname,
proveedor y commit desplegados.

## Cambio controlado de mock a OpenAI

1. Guardar la clave solo en `.env` o un secret del backend; nunca en Git, la web o capturas.
2. Cambiar `AI_PROVIDER=openai` y registrar explícitamente modelos y tarifas vigentes.
3. Recrear únicamente API.
4. Confirmar `/health` con `provider=openai`.
5. Ejecutar nuevamente el seed público dentro del contenedor API.
6. Correr la evaluación live y revisar manualmente respuesta, citas, latencia, tokens y costo antes de habilitar la demo.

La huella de embedding aísla los índices mock y OpenAI dentro de la misma base; retrieval y listado usan solo el índice activo. Si cambia `EMBEDDING_DIMENSIONS`, se requiere una base/migración nueva porque la columna pgvector tiene dimensión fija.
