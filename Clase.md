---
tipo: indice
tags: [bootcamp]
---

# Clase

Apuntes de cada sesión en vivo, en orden cronológico. Cada nota lleva un `## Resumen` arriba con lo que se vio y el código tal como quedó en clase.

> Los archivos se nombran `AAAA-MM-DD - Tema`. Ver [[CONVENCIONES]].
> Los apuntes de referencia de cada sesión viven en `Temas/` con el esquema `MMM·SNN - Tema`; esta tabla los enlaza igual, con la fecha en que se dictaron.

## Módulo 2 — Python y Linux

| Fecha | Sesión | Temas |
|---|---|---|
| 09 jun | [[2026-06-09 - Revisión Python - Iteración, listas y strings]] | `for`, `while`, slicing, `join`, métodos de lista |
| 10 jun | [[2026-06-10 - Revisión Python - Diccionarios e iteración]] | `.items()`, `.keys()`, `.values()`, contador de letras |
| 16 jun | [[2026-06-16 - Revisión Python - Archivos y módulo os]] | `open`, `with`, lectura/escritura, módulo `os` |
| 18 jun | [[2026-06-18 - Revisión Python - Archivos CSV]] | módulo `csv`, desempaquetado de filas |
| 18 jun | [[2026-06-18 - Revisión Python - LLMs y chat con historial]] | API de OpenAI, `.env`, historial de conversación |
| 22 jun | [[2026-06-22 - Python y Linux - Expresiones regulares]] | `re.findall`, `re.sub`, grupos de captura sobre logs |
| 23 jun | [[2026-06-23 - Python y Linux - Datos y procesos]] | `os.environ`, `sys.argv` |
| 24 jun | [[2026-06-24 - Python y Linux - Repaso]] | 6 ejercicios integradores con solución |
| 29 jun | [[2026-06-29 - Testing con unittest]] | `unittest`, casos borde |
| 30 jun | [[2026-06-30 - Excepciones - raise y validación]] | `raise ValueError`, validación de entrada |
| 01 jul | [[2026-07-01 - Linux - Comandos de archivos y procesos]] | `mkdir`, `mv`, `cp`, `rm`, `ps aux`, `kill` |
| 02 jul | [[2026-07-02 - Bash - Scripting inicial]] | shebang, variables, primer script |

## Módulo 3 — APIs y automatización con n8n

| Fecha | Sesión | Temas |
|---|---|---|
| 07 jul | [[2026-07-07 - Python Requests - Consumo de APIs]] | `requests`, `GET`/`POST`, errores, timeouts, headers |
| 03 ago | [[M03·S02 - RAG en n8n]] | chunking, embeddings, retrieval + reranking, metadata |
| 05 ago | [[M03·S04 - Proyectos de n8n con Claude Code]] | n8n vía MCP, pack de skills, vibecoding |

## Módulo A — Ingeniería de Software para AI Engineers

Módulo transversal de 7 sesiones, dictado entre los módulos 6 y 7. Hilo conductor: el proyecto VEGA de Nortia Energía. Las últimas tres todavía no tienen fecha confirmada.

| Fecha | Sesión | Temas |
|---|---|---|
| 24 ago | [[MA·S01 - Gestión de proyectos y ciclo de vida del software]] | ciclo de vida, charter, roles |
| 27 ago | [[MA·S02 - Product discovery ligero]] | stakeholders, journey map, oportunidades |
| 28 ago | [[MA·S03 - Análisis de requerimientos de la elicitación a la especificación]] | elicitación, requisitos, PRD |
| 28 ago | [[MA·S04 - Spec-driven development]] | specs ejecutables, `CLAUDE.md`, agentes de código |
| — | [[MA·S05 - Modelado - UML estructural y dinámico, C4 y ADRs]] | UML, C4, ADRs, Mermaid en el repo |
| — | [[MA·S06 - Metodologías ágiles]] | Scrum, Kanban, gestión con alcance cambiante |
| — | [[MA·S07 - Estimación, costeo y defensa del proyecto]] | estimación, costeo, defensa |

Entregables del caso VEGA: [[MA·S01 - Gestión de proyectos y ciclo de vida del softwar - Solucion - Charter|Charter]] · [[MA·S02 - Oportunidades - Discovery de VEGA|Oportunidades]] · [[MA·S03 - Product Requirements Document (PRD)|PRD]] · [[MA·S04 - SPEC-001 · Respuesta cuando la consulta no está en la base de conocimiento|SPEC-001]]

### Sesiones de análisis

Prácticas sobre los entregables, fuera de la numeración `MA·SNN`.

| Fecha | Sesión | Temas |
|---|---|---|
| 25 ago | [[2026-08-25 - Analisis de proyecto de ejemplo - Vega]] | recorrido por los entregables de VEGA como caso de referencia |
| 01 sep | [[2026-09-01 - Analisis de proyecto de marketing]] | documentación del proyecto de Alberto, pack de tráfico y performance |

## Material de apoyo

- [[M02·S03 - Python y Sistemas Operativos]] — el curso que sigue el módulo 2.
- [[M02·S04 - Using Python to Interact with the Operating System]] — resumen escrito de ese curso completo, hecho por la clase.
- [[Tarea]] — los ejercicios que acompañan estas sesiones.
