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

## Bloqueos reales del entorno de construcción

- No hay binario Docker accesible, por lo que Compose se revisa estáticamente pero su arranque debe verificarse en una máquina con Docker.
- El registro de paquetes JavaScript no fue accesible; la instalación, el lockfile y los gates `lint/typecheck/test/build` del frontend deben ejecutarse en un entorno con acceso al registro.
- No existe `OPENAI_API_KEY`; el flujo OpenAI real y sus métricas quedan pendientes. La clave debe configurarse localmente o en el servidor, nunca compartirse por chat.
- El VPS reporta 96% de uso de disco y 3 GB disponibles; no se autoriza construir o desplegar hasta realizar un diagnóstico de solo lectura y recuperar margen sin afectar otros servicios.
