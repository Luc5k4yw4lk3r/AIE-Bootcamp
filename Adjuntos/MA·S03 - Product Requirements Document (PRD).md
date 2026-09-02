---
tipo: proyecto
estado: en-progreso
modulo: A
tags: [proyectos, requisitos]
---

# Proyecto VEGA — Product Requirements Document (PRD)

---

Documento: docs/03-prd.md
Módulo / Asignatura: MA·S03 — De la elicitación a la especificación
Caso: Proyecto VEGA — Nortia Energía
Estado: Aprobado para Spec-Driven Development (MA·S04)
Autores: Equipo de Ingeniería de Software para IA

## 1. Contexto y Problema de Negocio

Nortia Energía es una comercializadora de electricidad y gas con 380 empleados y aproximadamente 210.000 clientes residenciales en España. El departamento de Atención al Cliente cuenta con 42 agentes que gestionan una media de 1.900 contactos diarios, con picos de hasta 3.400 tras la emisión de ciclos de facturación.

Actualmente, el tiempo medio de resolución (TMR) es de 11 minutos por contacto. El 60 % del tiempo del agente en llamada se consume buscando información dispersa en una intranet estática de 4.100 documentos no estructurados (tarifas históricas, condiciones contractuales, circulares regulatorias) y consultando un CRM propietario legacy. Adicionalmente, la curva de aprendizaje es crítica: un agente nuevo requiere 7 semanas para operar de forma autónoma. El 23 % de los contactos totales corresponden a consultas tipificadas como "no entiendo mi factura", donde los errores de interpretación generan segundas llamadas, degradación del CSAT y sobrecostes operativos.

## 2. Objetivos y Métricas de Éxito

El proyecto VEGA busca dotar a los agentes de un copiloto conversacional RAG que reduzca la fricción en la consulta de normativas y facturas, garantizando respuestas precisas y referenciadas documentalmente.

|Objetivo de Negocio|Métrica (SLI / KPI)|Línea Base (Actual)|Meta de Éxito (SLO)|
|---|---|---|---|
|Reducción del tiempo medio de atención|TMR en consultas de facturación y normativa|11 minutos|≤ 7,5 minutos (reducción ≥ 31,8 %) en 90 días post-lanzamiento|
|Aceleración de la autonomía de agentes noveles|Tiempo hasta alcanzar autonomía operativa|7 semanas|≤ 3 semanas para nuevas incorporaciones|
|Precisión y contención de alucinaciones|Tasa de veracidad documental verificada (eval binario)|N/A (búsqueda manual)|≥ 98,0 % de respuestas respaldadas por el corpus de 4.100 docs|
|Eficiencia económica por interacción|Coste medio de inferencia por consulta resuelta|0,00 € (coste humano puro)|≤ 0,025 € por interacción asistida|

## 3. Personas y Usuarios

- Agente Novel (Persona Primaria — 'Laura'): Agente con menos de 2 meses en Nortia. Atiende llamadas en tiempo real, no domina las 4.100 circulares y necesita desgloses inmediatos y citas normativas exactas para explicar conceptos de factura sin poner al cliente en espera.
- Supervisor de Operaciones (Persona de Gestión — 'Iván Ferreras'): Vela por la calidad de atención y el bienestar del equipo. Necesita que el sistema no degrade la valoración percibida ni penalice individualmente al agente.
- Directora de Operaciones (Stakeholder Clave — 'Marta Sedano'): Enfocada en la optimización del coste por contacto y la reducción global del TMR.

## 4. Alcance del Producto y User Stories Principales

El alcance de la primera versión funcional (v1.0) se restringe a la asistencia al agente dentro del entorno de escritorio (interfaz web complementaria). Las historias están priorizadas bajo MoSCoW y ordenadas internamente por riesgo técnico decreciente:

### US-001 [MUST HAVE / Alto Riesgo]: Consulta sobre desglose de facturación

Como agente de atención, quiero consultar el desglose y cálculo de un concepto de factura introduciendo su identificador o tipología contractual,para explicárselo al cliente en llamada de forma clara y sin ponerlo en espera prolongada.

Scenario: Consulta exitosa de concepto de factura con cita de origen Given un agente de atención autenticado And un contrato con factura emitida en el último periodo de facturación When el agente solicita el desglose del importe del término de potencia o energía Then VEGA devuelve la explicación del cálculo y la tarifa aplicada And la respuesta cita textualmente el documento o registro contractual de origen And el tiempo de respuesta p95 es ≤ 3,0 segundos

### US-002 [MUST HAVE / Alto Riesgo]: Detección de ausencia de información (No Alucinación)

Como agente de atención, quiero que VEGA declare explícitamente cuando una consulta no tiene respaldo en la base documental, para no comunicar información errónea o inventada al cliente.

Scenario: Consulta sin respaldo en el corpus documental Given un agente de atención autenticado And una consulta cuya respuesta no existe en los 4.100 documentos indexados When el agente envía la consulta a VEGA Then VEGA responde formalmente que no dispone de información suficiente And no emite ninguna cifra ni respuesta especulativa And ofrece el canal o protocolo de escalado correspondiente

### US-003 [MUST HAVE / Riesgo Medio]: Búsqueda y síntesis de circulares normativas

Como agente de atención, quiero formular dudas sobre procedimientos de corte, bono social o cambios de titularidad, para obtener la circular vigente aplicable sin navegar manualmente por la intranet.

Scenario: Consulta de procedimiento regulatorio vigente Given un agente de atención autenticado And una duda sobre el protocolo de bono social térmico When el agente consulta el procedimiento aplicable Then VEGA devuelve el resumen del procedimiento vigente And enlaza el ID del documento oficial de la intranet de Nortia

### US-004 [SHOULD HAVE / Riesgo Bajo]: Registro y auditoría seudonimizada de consultas

Como oficial de cumplimiento normativo (DPO), quiero que las consultas y respuestas se almacenen seudonimizadas con purga automática a los 30 días, para auditar la calidad y cumplir con el RGPD sin retener datos sensibles.

## 5. Requisitos del Sistema (FR & NFR)

### 5.1 Requisitos Funcionales (FR)

- RF-001: El sistema debe indexar vectorialmente y permitir recuperación semántica sobre el corpus de 4.100 documentos de la intranet de Nortia Energía.
- RF-002: El sistema debe desglosar importes y reglas de facturación asociadas a las tarifas vigentes e históricas (últimos 24 meses).
- RF-003: El sistema debe incluir la cita documental obligatoria (título, sección y versión) en toda respuesta que contenga importes, porcentajes o procedimientos.
- RF-004: El sistema debe clasificar consultas fuera de dominio o sin respaldo y emitir un mensaje determinista de abstención.
- RF-005: El sistema debe proporcionar un mecanismo de retroalimentación rápida (pulgar arriba / pulgar abajo + motivo) para el agente.

### 5.2 Requisitos No Funcionales (NFR) y Criterios de Evaluación (Evals)

| ID     | Atributo (arc42)       | Fit Criterion / Enunciado Verificable                                                                                                                                | Método de Verificación / Eval                                                          |
| ------ | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| NFR-01 | Eficiencia / Latencia  | El p95 de latencia hasta el primer token es ≤ 1,8 s; el p95 hasta la respuesta completa es ≤ 3,5 s en franja pico (100 req/min concurrentes).                        | Pruebas de carga sintéticas (Locust/k6) sobre endpoint RAG.                            |
| NFR-02 | Coste Económico        | El coste medio de tokens por consulta resuelta es ≤ 0,025 €, medido sobre lote de 1.000 consultas tipo con caching de contexto activado.                             | Métricas de telemetría de API y cálculo financiero en pipeline.                        |
| NFR-03 | Safety / Alucinación   | En un banco de 200 consultas sin respuesta en KB, VEGA se abstiene de inventar en ≥ 98,0 % de los casos.                                                             | Eval de LLM-as-judge binario con modelo desacoplado sobre dataset de prueba reservado. |
| NFR-04 | Fiabilidad / Retrieval | Recall@5 ≥ 92,0 % sobre un conjunto de 500 preguntas anotadas de facturación y normativa.                                                                            | Eval de ranking y métrica de recuperación documental.                                  |
| NFR-05 | Explicabilidad         | El 100 % de las respuestas con datos numéricos o tarifarios contienen al menos un identificador de documento válido.                                                 | Test de aserción determinista por código (expresiones regulares y validación de IDs).  |
| NFR-06 | Privacidad / RGPD      | Las trazas de interacción son anonimizadas en memoria (eliminación de DNI, IBAN, nombres) y los logs de auditoría se purgan automáticamente a los 30 días naturales. | Test unitario de sanitización PII + verificación automatizada de cronjob de borrado.   |

## 6. Restricciones Técnicas y de Negocio (RES)

- RES-01 (Arquitectura / IT): VEGA es un sistema de solo lectura respecto al CRM y sistemas de facturación. Queda terminantemente prohibida cualquier operación de escritura, actualización o mutación en las bases de datos transaccionales de producción (fuente: Diego Amat).
- RES-02 (Regulatorio / RGPD): No se enviarán datos de carácter personal (PII) directos de clientes a las APIs de modelos fundacionales externos. Cualquier contextualización debe seudonimizarse previamente (fuente: Cristina Roa).
- RES-03 (Presupuesto y Despliegue): El servicio debe operar sobre la infraestructura cloud existente de Nortia en región UE (Frankfurt/Madrid) para garantizar soberanía de datos.

## 7. Fuera de Alcance (Exclusiones Explícitas del Sistema)

Para evitar el scope creep y delimitar inequívocamente la responsabilidad del agente de código y del equipo:

1. VEGA no interactúa con el cliente final: Es un copiloto interno de uso exclusivo para agentes humanos. En ningún caso responderá chats de clientes ni emitirá correos de forma desatendida.
2. No realiza transacciones ni modificaciones en facturas: No emitirá notas de abono, refacturaciones, cambios de tarifa ni altas/bajas de contratos en los sistemas core.
3. No incluye reconocimiento o transcripción de voz en tiempo real (STT) en v1.0: La interacción del agente con VEGA se realiza exclusivamente mediante texto estructurado o chat web.
4. No reemplaza al CRM ni al gestor documental: VEGA no almacenará el historial canónico del cliente ni actuará como repositorio maestro de documentación de Nortia.
5. No soporta idiomas distintos al castellano: Las consultas y la base documental se procesan en español peninsular normativo.
6. No realiza entrenamiento ni fine-tuning de modelos fundacionales desde cero: La arquitectura se basa en RAG (Retrieval-Augmented Generation) sobre modelos preentrenados comerciales o de código abierto con prompt engineering y context stuffing.
7. No procesa archivos adjuntos arbitrarios subidos por el agente durante la llamada: Solo responde sobre el corpus oficial de 4.100 documentos previamente ingestados e indexados por el pipeline de datos.

## 8. Gestión de Riesgos y Mitigación

|Riesgo Identificado|Impacto|Probabilidad|Estrategia de Mitigación|
|---|---|---|---|
|R-01: Alucinación en tarifas reguladas (cálculo erróneo transmitido al cliente).|Alto|Media|Prompting restrictivo con few-shot de abstención + Eval NFR-03 continuo en CI/CD + forzado de citas directas por regex.|
|R-02: Rechazo de adopción por parte de los agentes (temor a monitorización punitiva / despidos).|Alto|Media|Desacoplamiento total de métricas individuales de rendimiento; foco en VEGA como herramienta de ahorro de tiempo; inclusión de agentes en pruebas alfa.|
|R-03: Desactualización del corpus documental (circulares derogadas aún indexadas).|Medio|Alta|Pipeline de ingesta con metadatos de vigencia temporal y filtro estricto de documentos con fecha de caducidad superada.|
|R-04: Latencia excesiva en inferencia en horas pico (agente abandona la consulta).|Alto|Baja|Implementación de semantic cache para el 20 % de consultas más frecuentes (representan el 70 % del tráfico) y streaming de tokens.|

## 9. Dependencias Críticas

- DEP-01: Volcado y estructuración inicial del corpus de 4.100 documentos de la intranet por parte del equipo de Gestión del Conocimiento.
- DEP-02: Provisión de endpoint de lectura (read-only replica) de esquemas de facturación por parte del equipo de IT (Diego Amat).
- DEP-03: Validación y firma formal de la política de retención y seudonimización por parte de Legal / DPO (Cristina Roa) para cerrar CONF-002.

Control de Trazabilidad: Este PRD mapea directamente contra los requisitos RF-001 a RF-005, NFR-01 a NFR-06, las restricciones RES-01 a RES-03 y los conflictos documentados en docs/02-requirements.md.