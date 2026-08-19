# Contexto público y límites de la demo

## Propósito

EvidenceRAG se presenta como un **asistente documental verificable para consultar información institucional y regulatoria utilizando únicamente fuentes públicas**. La arquitectura, el código y la identidad del producto permanecen genéricos; Los Héroes funciona como corpus demostrativo inicial.

> **Demostración conceptual no oficial construida exclusivamente con información pública. No corresponde a un producto ni implementación de Caja Los Héroes.**

## Confirmado por fuentes públicas

Fuente primaria inicial: [Memoria Integrada Los Héroes 2025](https://porpub2.storage.googleapis.com/wp-content/uploads/2026/05/20152448/Memoria-LH_2025_8M-Oficial.pdf).

| Hecho | Localización en el PDF |
| --- | --- |
| 1.176.162 afiliados(as), 9.387 empresas afiliadas y 1.626 colaboradores(as) | página PDF 9 |
| 688.538 pensionados(as), 151 sucursales, 12 puntos de atención y 1.319 puntos de pago rural | páginas PDF 9 y 62 |
| 7.249.375 pagos de pensiones IPS en sucursales | páginas PDF 9 y 63 |
| 305.949 llamadas de call center para consultas, solicitudes, sugerencias y reclamos | página PDF 64 |
| Sistema formal de reclamos con trazabilidad, SLA, plataforma centralizada y canales de reguladores | página PDF 65 |
| SERNAC, SUSESO y CMF aparecen vinculados a la gestión de requerimientos | página PDF 65 |
| Uso de IA y Machine Learning para mejorar la validación automática de créditos sociales y el servicio | página PDF 66 |
| Actualización de sucursal virtual y aplicación móvil e integración de portales de beneficios y transacciones remotas | página PDF 66 |
| Innovación mediante equipos multidisciplinarios, experimentación, partners y aprobación de fondos por Comité de Inversiones | página PDF 66 |

La web pública de [Caja Los Héroes](https://www.losheroes.cl/) permite contrastar que existen canales digitales y que las Cajas de Compensación son entidades de seguridad social supervisadas por la SUSESO. Para hechos del demo se prioriza la memoria, que conserva página y contexto citables.

## Integridad y procedencia de la fuente

- URL fija y explícita; no se hace scraping autenticado.
- Tamaño observado el 2026-08-18: `8.665.067` bytes.
- SHA-256 verificado: `19f8fa3876fe32a7b1c9a5a8fa473c5a9567d56a0841afa77c67a11fa69b3b11`.
- El cargador detiene la ingestión si el archivo oficial cambia; una persona debe revisar y actualizar la huella.
- La extracción local con pypdf produjo 388 páginas con texto y 980 fragmentos. Algunas numeraciones editoriales internas no coinciden con el índice físico del PDF; la cita de la aplicación usa la página física extraída.

## Inferencias de diseño, no afirmaciones organizacionales

Por el dominio de seguridad social, crédito y atención de personas, una solución empresarial futura debería priorizar privacidad, seguridad, trazabilidad, explicabilidad, auditoría, accesibilidad, supervisión humana y cumplimiento regulatorio. Esto es criterio de diseño de EvidenceRAG; no describe controles internos ni una implementación real de Los Héroes.

El corpus permite demostrar casos como búsqueda regulatoria, atención asistida y consulta de políticas. No implica que la organización use EvidenceRAG ni que este diseño corresponda a su arquitectura objetivo.

## Pendiente de validar en entrevista

- Forma organizacional, mandato y servicios específicos de Los Héroes Digital.
- Título contractual, alcance y resultados esperados del cargo.
- Balance entre ejecución hands-on, estrategia, liderazgo y gestión de proveedores.
- Equipo, dependencia, stakeholders y mecanismos de decisión.
- Stack, nube, modelos, datos, seguridad, gobierno de IA y procesos de puesta en producción.
- Casos de uso priorizados, métricas de éxito, restricciones regulatorias y horizonte de 90 días.
- Modalidad, tipo de contrato y proceso de selección.

La pregunta “¿Qué servicios ofrece específicamente Los Héroes Digital?” pertenece intencionalmente al set de rechazo: la fuente inicial no contiene una descripción oficial suficiente y el sistema no debe completarla por semejanza con Caja Los Héroes.

## Backlog priorizado

- **P0 completado:** PDF oficial, RAG, páginas, citas y rechazo explícito.
- **P1 completado:** preguntas sugeridas, disclaimer, documentación y evaluación live.
- **P2 listo para VPS:** subdominios separados, health checks, red externa de proxy y proveedor mock; OpenAI queda tras validación operacional.
- **P3 preparado:** guion de demo, pitch, arquitectura, limitaciones, roadmap y preguntas de entrevista.
- **Después de validar necesidad:** fuentes adicionales de SUSESO/CMF y FAQs públicas, con registro de procedencia y evaluación separada.
