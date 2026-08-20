# Operación delegada y restringida

El MVP usa un único punto de entrada privilegiado: `evidence-rag-ops`. Su copia
versionada vive en `infra/ops/`; para operar debe instalarse como
`/usr/local/sbin/evidence-rag-ops`, propiedad `root:root` y modo `0755`. La regla
`infra/ops/evidence-rag.sudoers` se instala como `/etc/sudoers.d/evidence-rag`,
propiedad `root:root` y modo `0440`.

La instalación requiere una única intervención root y debe hacerse solo después
de revisar el diff. No se instala automáticamente desde la aplicación ni durante
un deploy.

## Acciones permitidas

| Acción | Alcance exacto |
| --- | --- |
| `config` | Valida en silencio la combinación Compose de producción. |
| `status` | Muestra commit y estado de los tres servicios del proyecto. |
| `logs` | Muestra solo `api`, `web` y `db`: máximo 200 líneas y 30 minutos. |
| `health` | Verifica API/base y web desde sus propios contenedores. |
| `tests` | Construye y ejecuta los targets de prueba API/web sin red en runtime. |
| `build` | Construye únicamente las imágenes `api` y `web`. |
| `deploy` | Acepta solo un fast-forward desde la rama remota `main`, prueba, construye, activa y comprueba health. |
| `seed-public` | Ejecuta el cargador fijo de la fuente institucional con SHA-256 conocido. |
| `smoke` | Comprueba modo mock, corpus, respuesta citada y rechazo sin evidencia. |
| `restart` | Reinicia únicamente `db`, `api` y `web` de EvidenceRAG. |
| `rollback` | Vuelve una vez al commit anterior registrado por un deploy exitoso. |

No se aceptan argumentos adicionales. No existe acción para shell, `docker exec`
genérico, `down`, `prune`, eliminación de contenedores/volúmenes o acceso a otro
proyecto.

## Invariantes de seguridad

- El wrapper rechaza ejecución fuera de su ruta root-owned y registra actor/acción en syslog.
- El checkout debe pertenecer a `adminuser`; `codex-evidence` no puede ser propietario, tener escritura por grupo ni encontrar archivos world-writable.
- El origen debe ser exactamente `https://github.com/InnerRam/evidence-rag.git` o su forma SSH `git@github.com:InnerRam/evidence-rag.git`; el deploy obtiene `main` desde la URL HTTPS fijada. Producción debe estar limpia sobre `main` para toda mutación.
- `compose.yaml`, `compose.prod.yaml` y ambos Dockerfiles están fijados por SHA-256. Cambiarlos requiere revisión root y reinstalar una versión actualizada del wrapper.
- Git se ejecuta como el propietario del deploy, sin hooks ni configuración Git global/sistema; Docker recibe solo comandos y servicios cerrados.
- Un lock serializa operaciones. El deploy conserva el commit previo únicamente después de health exitoso y revierte automáticamente si falla la activación.
- El rollback nunca elimina volúmenes ni usa `compose down`; si falla, intenta restaurar el commit que estaba activo.

`make ops-check` valida sintaxis Bash, sintaxis sudoers, igualdad de acciones,
hashes fijados y ausencia de operaciones Docker destructivas. La validación no
instala archivos ni accede a producción.

## Flujo de publicación

Tras revisión y autorización explícita: instalar el wrapper, aprobar y publicar
los cambios de la rama, fusionarlos a `main`, ejecutar `tests`, `deploy`,
`seed-public` y `smoke`, y finalmente correr la evaluación live contra la URL
HTTPS pública. Nginx Proxy Manager y otros proyectos quedan fuera del wrapper.
