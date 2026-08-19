# Defensa técnica — preguntas y respuestas sugeridas

## Arquitectura y RAG

**¿Por qué RAG y no fine-tuning?**

Porque el problema es recuperar hechos cambiantes y citables. RAG permite actualizar el conocimiento reingiriendo documentos y conservar la procedencia. Fine-tuning sirve para comportamiento o estilo, no para convertir un modelo en una base documental confiable.

**¿Por qué PostgreSQL con pgvector?**

Combina metadatos transaccionales, filtros y búsqueda vectorial en una operación conocida. Para el volumen del MVP reduce piezas operativas. Si la escala o el perfil de consulta lo exige, la interfaz de retrieval permite migrar a un motor especializado.

**¿Cómo eligió chunk size y overlap?**

Partí con 1.200 caracteres y 180 de solapamiento para conservar contexto sin inflar demasiado el índice. Son parámetros, no verdades universales: deben calibrarse con recall, precisión de citas, costo y latencia del corpus objetivo.

**¿Por qué no agregó reranking?**

El baseline controlado no justificaba otra dependencia. Primero mido errores. Lo incorporaría si aumenta de forma consistente la recuperación/cita en casos difíciles con un costo aceptable.

**¿Cómo combina dos fragmentos?**

Recupera `top_k` fragmentos y los entrega delimitados al proveedor. La evaluación incluye preguntas multi-fragmento y multi-documento. En producción agregaría diversidad por documento o MMR si observo duplicación excesiva.

## Fidelidad y evaluación

**¿Cómo evita alucinaciones?**

No existe garantía absoluta. Reduzco el riesgo con recuperación híbrida, umbral previo, cobertura mínima de términos, validación de acrónimos y alcance nominal, prompt de evidencia cerrada, ausencia de tools, rechazo definido y citas construidas por la aplicación. Luego evalúo falsos positivos y fidelidad con revisión humana.

**¿Qué significa el 100% del reporte?**

Es un baseline sobre 18 casos controlados usando proveedor determinístico. Demuestra que el recorrido y las expectativas son reproducibles. No significa 100% de precisión general ni evalúa la calidad de OpenAI en otro dominio.

**¿Cómo mide precisión de citas?**

Automáticamente verifico que la primera cita corresponda al documento esperado y que los documentos necesarios estén en top‑5. La relación exacta entre cada afirmación y fragmento requiere revisión humana; el reporte lo declara.

**¿Cómo calibraría el rechazo?**

Con preguntas respondibles y no respondibles representativas, analizando distribución de scores, margen entre resultados y costo de falsos positivos versus falsos negativos. El umbral se versiona junto al dataset.

## Seguridad

**¿Cómo trata prompt injection en documentos?**

El contenido se delimita como evidencia no confiable, carece de autoridad y el modelo no dispone de tools. La aplicación controla citas y localizadores. Para riesgos mayores sumaría clasificación, políticas de salida y pruebas adversariales continuas.

**¿Dónde vive la API key?**

Solo en variables o secrets del entorno del backend. Nunca se compila en Next.js, se registra, se versiona o se solicita por chat.

**¿Está listo para datos privados?**

No como demo pública. Antes agregaría OIDC/RBAC, aislamiento, cifrado administrado, retención, borrado, redacción de logs, antimalware, auditoría y revisión contractual del proveedor.

## Costos y escalabilidad

**¿Cómo calcula costo?**

Registro tokens de embeddings y generación. Las tarifas son configuración explícita por millón de tokens; si no están configuradas devuelvo `n/a` para no inventar precios.

**¿Cómo reduciría costos?**

Deduplicación por hash, batching de embeddings, rechazo antes de generación, modelos adecuados al riesgo, caché de consultas estables y límites de contexto. Optimizaría según datos, no solo por intuición.

**¿Qué cambiaría para un millón de documentos?**

Ingestión asíncrona con cola, object storage, migraciones, índices pgvector ajustados, particionamiento por tenant/dominio, observabilidad distribuida y evaluación de un vector DB especializado. También separar jobs de API interactiva.

## Operación y evolución

**¿Por qué procesamiento síncrono?**

Mantiene el vertical slice verificable dentro del alcance de 12–16 horas y archivos pequeños. La respuesta expone estado; el paso natural es una cola cuando el tiempo de ingestión afecte UX o confiabilidad.

**¿Qué limitación corregiría primero?**

Ejecutaría evaluación con OpenAI y revisión humana, luego autenticación y jobs asíncronos. Son más valiosos que agregar funciones vistosas sin evidencia de calidad.

**¿Qué aportó personalmente?**

Arquitectura, implementación full-stack, definición del dataset, gates de evidencia, pruebas, seguridad, observabilidad, Docker y narrativa técnica. El foco fue transformar experiencia autodidacta en una demostración pública que se puede ejecutar y cuestionar.

## Contexto sectorial

**¿Por qué usar una memoria institucional pública?**

Permite demostrar procedencia, páginas y rechazo sobre un corpus real sin acceder a datos privados ni asumir una relación con la organización. La fuente contiene complejidad suficiente —tablas, regulación, canales, métricas y narrativa— para revelar errores que un corpus sintético pequeño no muestra.

**¿Qué aprendió al pasar del corpus sintético al PDF real?**

Que el score vectorial solo era insuficiente: aparecían fragmentos plausibles pero fuera de alcance. Incorporé señal léxica, cobertura, acrónimos y alcance nominal, y separé un set live del baseline sintético. También detecté que mock y OpenAI no pueden compartir vectores aunque tengan igual dimensión, por lo que añadí una huella de índice.

**¿Por qué la pregunta sobre Los Héroes Digital se rechaza?**

Porque la fuente inicial describe servicios y canales de Caja Los Héroes, pero no entrega una definición oficial suficiente de los servicios específicos de esa unidad. Transferir hechos por similitud de nombre sería una inferencia no autorizada. El rechazo es parte del producto, no un error de UX.

**¿Cómo abordaría IA en seguridad social y crédito?**

Partiría por el proceso y el riesgo: propósito, base legal, minimización de datos, calidad, sesgos, explicabilidad proporcional, controles de acceso, auditoría, intervención humana y canal de reclamación. Separaría apoyo a decisión de decisión automatizada y acordaría métricas de negocio, servicio y riesgo antes del modelo.

**¿Qué haría en los primeros 90 días?**

Primero mapearía stakeholders, casos, datos, restricciones y métricas; luego priorizaría uno o dos casos con datos disponibles y riesgo controlable. Entregaría un vertical slice evaluado con usuarios y controles mínimos, y cerraría con decisión documentada de escalar, ajustar o detener. No prometería producción antes de conocer gobierno, seguridad y operación.

## Preguntas estratégicas para realizar

### Mandato y éxito

1. ¿Cuál es el mandato exacto de la unidad y por qué este rol es prioritario ahora?
2. ¿Qué resultados concretos esperan de la persona durante los primeros 30, 60 y 90 días?
3. ¿Qué casos de uso ya están priorizados y con qué métricas de negocio, experiencia, riesgo o eficiencia se evaluarán?
4. ¿Qué porcentaje del rol esperan que sea hands-on, arquitectura, estrategia, liderazgo de equipo y gestión de proveedores?

### Equipo y decisiones

5. ¿A quién reporta el rol y con qué áreas trabajará semanalmente?
6. ¿Qué capacidades existen hoy en producto, datos, ML/IA, ingeniería, seguridad, riesgo y cumplimiento?
7. ¿Cómo se decide que un experimento pasa a piloto y que un piloto pasa a producción?
8. ¿Qué autonomía tendrá el rol para seleccionar patrones, herramientas y proveedores?

### Tecnología, datos y gobierno

9. Sin entrar en información sensible, ¿qué stack y plataformas de datos/nube están estandarizados?
10. ¿Qué restricciones de residencia, privacidad, seguridad y terceros condicionan el uso de modelos?
11. ¿Existe un marco de gobierno de IA, inventario de modelos, evaluación, monitoreo y retiro?
12. ¿Cómo se incorporan accesibilidad, personas mayores, explicabilidad y supervisión humana al diseño de canales digitales?

### Operación y relación laboral

13. ¿Cómo se mide hoy la calidad en producción: precisión, abandono, SLA, reclamos, costo, incidentes o impacto de negocio?
14. ¿Cuál es la modalidad de trabajo, ubicación habitual, tipo de contrato y etapas restantes del proceso?
15. Al terminar esta conversación, ¿hay alguna duda sobre mi experiencia o encaje que convenga abordar directamente?
