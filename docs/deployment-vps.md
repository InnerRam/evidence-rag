# Despliegue en VPS con Docker Compose

## Requisitos

- Ubuntu 20.04 o posterior con actualizaciones de seguridad.
- Docker Engine con Compose v2.
- DNS de dos subdominios, por ejemplo `rag.example.com` y `rag-api.example.com`.
- Nginx Proxy Manager conectado a la red Docker externa indicada en `PROXY_NETWORK`.

## Gate previo de capacidad

El servidor informado tiene 61 GB, 96% ocupado y solo 3 GB disponibles. **No construir ni desplegar en ese estado.** Una compilación web, capas Docker y logs temporales pueden agotar el filesystem y afectar servicios existentes. Antes de decidir qué liberar, ejecutar únicamente diagnóstico de lectura:

```bash
df -h /
df -ih /
free -h
docker system df
journalctl --disk-usage
du -xhd1 /var/lib/docker /var/log /home/adminuser /root /opt 2>/dev/null | sort -h
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}'
docker volume ls
```

Revisar el resultado antes de eliminar nada. No ejecutar `docker system prune`, no borrar volúmenes y no rotar o truncar logs a ciegas. Para este despliegue se recomienda recuperar al menos 8 GB disponibles —idealmente 10 GB— y confirmar inodos y memoria suficientes.

## Preparación

1. Clonar el repositorio en una carpeta exclusiva, recomendada: `/home/adminuser/web-apps/evidence-rag`.
2. Copiar `.env.example` a `.env`.
3. Cambiar la contraseña PostgreSQL únicamente en `.env`; usar una contraseña URL-safe larga porque forma parte de `DATABASE_URL`.
4. Definir `API_CORS_ORIGINS=https://rag.example.com` y `NEXT_PUBLIC_API_URL=https://rag-api.example.com/api/v1`.
5. Definir `PROXY_NETWORK` con el nombre exacto de la red externa compartida con Nginx Proxy Manager.
6. Mantener `AI_PROVIDER=mock` para el primer despliegue. `OPENAI_API_KEY` debe permanecer vacía.

Antes del primer commit definitivo, generar y versionar `apps/web/pnpm-lock.yaml` en un entorno con acceso al registro. El Dockerfile usa instalación congelada automáticamente cuando el lockfile existe.

## Gates antes de levantar servicios

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

Si un gate falla, no continuar al despliegue ni hacer commit de correcciones no verificadas.

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

1. Respaldar base y archivos.
2. Construir imágenes con un tag de versión.
3. Ejecutar pruebas y smoke en staging.
4. Publicar y revisar health checks.
5. Conservar la imagen anterior para rollback.

## Nginx Proxy Manager

Crear dos Proxy Hosts:

| Host | Forward hostname/port | Websockets | SSL |
| --- | --- | --- | --- |
| `rag.example.com` | `evidence-rag-web:3000` | activado | Let's Encrypt + Force SSL |
| `rag-api.example.com` | `evidence-rag-api:8000` | activado | Let's Encrypt + Force SSL |

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
curl -fsS https://rag-api.example.com/health
```

La respuesta debe indicar `status=ok`, `database=ok` y `provider=mock`. Luego cargar un documento de muestra desde la web, responder una pregunta sustentada, comprobar una pregunta sin evidencia y reiniciar solamente este proyecto para validar persistencia:

```bash
docker compose -f compose.yaml -f compose.prod.yaml restart
docker compose -f compose.yaml -f compose.prod.yaml ps
```

No reiniciar Nginx Proxy Manager ni contenedores de otros proyectos. Si NPM se recrea, confirmar que continúe conectado a `PROXY_NETWORK`.

Ejecutar el set live desde una máquina con acceso al subdominio API:

```bash
python3 scripts/run_live_evals.py \
  --api-url https://rag-api.example.com/api/v1 \
  --output-prefix evals/results/deployment-mock
```

## Cambio controlado de mock a OpenAI

1. Guardar la clave solo en `.env` o un secret del backend; nunca en Git, la web o capturas.
2. Cambiar `AI_PROVIDER=openai` y registrar explícitamente modelos y tarifas vigentes.
3. Recrear únicamente API: `docker compose -f compose.yaml -f compose.prod.yaml up -d --build api`.
4. Confirmar `/health` con `provider=openai`.
5. Ejecutar nuevamente `python3 -m app.seed_public` dentro del contenedor API.
6. Correr la evaluación live y revisar manualmente respuesta, citas, latencia, tokens y costo antes de habilitar la demo.

La huella de embedding aísla los índices mock y OpenAI dentro de la misma base; retrieval y listado usan solo el índice activo. Si cambia `EMBEDDING_DIMENSIONS`, se requiere una base/migración nueva porque la columna pgvector tiene dimensión fija.
