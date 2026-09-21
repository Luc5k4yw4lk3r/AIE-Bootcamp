
Sos mi asistente de **inicialización de proyecto**. Vas a dejar el entorno de trabajo listo siguiendo EXACTAMENTE las reglas de abajo.

**Reglas globales, no negociables:**

- **No escribas código de la aplicación todavía.** Solo andamiaje: reglas de agentes, estructura de carpetas, specs, plantillas, config y archivos de entorno.
- **Empezá por el Pre-flight (sección 1) y respetá el gate de Clarify (sección 3).** Son paradas obligatorias: no avances si no las cumpliste.
- Trabajá de forma incremental y contame qué vas creando.
- Todos los **archivos del repo en inglés** (nombres, contenido, comentarios). Hablame a mí en español.
- Al final, mostrame el **checklist de verificación** (última sección) marcando cada punto.

**Contexto del proyecto:**

- Nombre: `Gemelos digitales para eventos`
- Descripción: `Es un juego de gemelos digitales para eventos de fiestas o bares`
- Stack: `TBD`

---

### 1. Pre-flight (idempotencia) — HACÉ ESTO PRIMERO

Antes de crear o modificar **nada**:

1. Inspeccioná el estado actual del directorio: `git status` (si hay repo), y verificá si ya existen `AGENTS.md`, `CLAUDE.md`, `README.md`, `specs/`, `.env`, `.env.example`, `.gitignore`.
2. **Si algún archivo ya existe, NO lo sobrescribas.** Mostrame una lista de lo que encontraste y preguntame cómo seguir para cada caso:
    - **completar solo lo que falta** (merge no destructivo), o
    - **dejar intacto** lo existente y saltarlo.
3. Solo creá archivos **nuevos**, o los que yo autorice explícitamente. Cualquier cambio destructivo (sobrescribir, borrar, mover) requiere mi OK explícito antes.
4. Si el directorio ya estaba inicializado, ajustá el resto de los pasos para **rellenar huecos**, no para rehacer todo.

---

### 2. Reglas de agentes: `AGENTS.md` + `CLAUDE.md`

Creá dos archivos en la raíz. **`AGENTS.md` es la fuente única de verdad** de cómo debe operar cualquier agente en este repo; **`CLAUDE.md` solo apunta a `AGENTS.md`** (sin duplicar reglas).

**`AGENTS.md`**

```markdown
# Agent operating instructions

These rules apply to ANY AI agent working in this repository (Claude Code, and others).
Project principles live in `specs/constitution.md` (OKF) — read that first; this file is the
operational layer on top of it.

## Golden rules
- Spec-first: never write application code before its spec/plan/tasks exist under
  `specs/NNN-<feature>/`.
- Clarify before specifying: ask open questions and WAIT for human answers before writing a spec.
- TDD: a failing test precedes every implementation task.
- Secrets: live only in `.env` (never committed). Document keys in `.env.example`.
- Knowledge artifacts use the Open Knowledge Format (OKF): markdown + YAML frontmatter.

## Workflow
Constitution → Clarify → Spec (EARS) → Plan → Tasks → Implement (TDD) → Validate → Change

## Git
- Do NOT commit unless the human explicitly asks.
- Never add Claude / any AI as co-author or collaborator. No `Co-Authored-By` lines.
  Commits are authored by the human.

## Layout
- `specs/`               SDD artifacts (OKF)
- `.env` / `.env.example`  environment variables
- `AGENTS.md`            this file — single source of truth for agent behavior
- `CLAUDE.md`            pointer to this file
```

**`CLAUDE.md`**

```markdown
# CLAUDE.md

The operating instructions for this repository are defined in **[AGENTS.md](./AGENTS.md)**.
Read and follow that file. Do not duplicate rules here — `AGENTS.md` is the single source of truth.
```

---

### 3. Spec-Driven Development (SDD) + gate de Clarify

Adoptamos SDD. El flujo es:

> **Constitution → Clarify → Spec → Plan → Tasks → Implement (TDD) → Validate → Change**

Los artefactos se escriben **antes** que el código de la app.

#### 3.1 Clarify — GATE OBLIGATORIO (antes de escribir cualquier spec)

Antes de redactar `spec.md`, `plan.md` o `tasks.md`:

1. Haceme entre **3 y 7 preguntas puntuales** sobre lo ambiguo del feature `{{FEATURE_SLUG}}`: alcance, usuarios/actores, datos, edge cases, restricciones y criterios de aceptación.
2. **PARÁ y esperá mis respuestas.** No escribas ningún spec hasta que yo responda.
3. Registrá las preguntas y mis respuestas en `clarifications.md` (frontmatter OKF `type: clarifications`).
4. Si respondo _"seguí con supuestos"_, documentá los **supuestos explícitos** en `clarifications.md` y recién ahí avanzá.

#### 3.2 Estructura de specs

Creá esta estructura:

```
specs/
  constitution.md                 # reglas y principios del proyecto (transversal)
  index.md                        # índice OKF que enlaza todos los specs
  001-{{FEATURE_SLUG}}/
    clarifications.md             # preguntas del gate de Clarify + respuestas/supuestos
    spec.md                       # requisitos funcionales en notación EARS
    plan.md                       # arquitectura técnica + contratos
    tasks.md                      # tareas granulares y testeables
```

Convención de carpetas: prefijo numérico incremental (`001-`, `002-`, …) + slug del feature.

`spec.md` usa **notación EARS** (Easy Approach to Requirements Syntax):

- Ubicuo: `The system SHALL <requisito>.`
- Evento: `WHEN <disparador>, the system SHALL <respuesta>.`
- Estado: `WHILE <estado>, the system SHALL <requisito>.`
- Opcional/feature: `WHERE <feature presente>, the system SHALL <requisito>.`
- Condición no deseada: `IF <condición de error>, THEN the system SHALL <respuesta>.`

Usá **exactamente** estas plantillas (cada spec lleva frontmatter OKF; ver sección 4):

**`specs/constitution.md`**

```markdown
---
type: constitution
title: {{PROJECT_NAME}} — Project Constitution
description: Non-negotiable principles, constraints and conventions for this project.
tags: [governance, sdd]
status: draft
sources: []
generated: { by: claude-code, at: <ISO-8601> }
verified: { by: human, at: null }
stale_after: null
---

# {{PROJECT_NAME}} — Constitution

## Principles
- Spec-first: no application code is written before its spec, plan and tasks exist.
- Clarify-first: ambiguities are resolved with the human before specifying.
- Test-Driven: every task ships with a failing test first.
- Clean boundaries: domain logic stays independent of frameworks, ORM and I/O.

## Constraints
- Stack: {{STACK}}
- All secrets live in `.env` (never committed).

## Conventions
- Specs live under `specs/NNN-<feature>/`.
- Requirements use EARS notation.
- Knowledge artifacts follow the Open Knowledge Format (OKF).
- Agent behavior is governed by `AGENTS.md`.
```

**`specs/001-{{FEATURE_SLUG}}/clarifications.md`**

```markdown
---
type: clarifications
title: {{FEATURE_SLUG}} — Clarifications
description: Open questions resolved with the human before writing the spec, plus assumptions.
tags: [clarify, {{FEATURE_SLUG}}]
status: draft
sources: []
generated: { by: claude-code, at: <ISO-8601> }
verified: { by: human, at: null }
stale_after: null
---

# {{FEATURE_SLUG}} — Clarifications

## Questions & answers
- Q1: <pregunta> → A: <respuesta>

## Assumptions
- <supuesto explícito si se avanzó sin respuesta>
```

**`specs/001-{{FEATURE_SLUG}}/spec.md`**

```markdown
---
type: spec
title: {{FEATURE_SLUG}} — Functional Spec
description: Functional requirements for the {{FEATURE_SLUG}} feature, in EARS notation.
tags: [spec, {{FEATURE_SLUG}}]
status: draft
sources: [./clarifications.md]
generated: { by: claude-code, at: <ISO-8601> }
verified: { by: human, at: null }
stale_after: null
---

# {{FEATURE_SLUG}} — Specification

## Context
<qué problema resuelve, en 2-3 líneas>

## Requirements (EARS)
- R1. The system SHALL ...
- R2. WHEN <trigger>, the system SHALL ...
- R3. IF <error condition>, THEN the system SHALL ...

## Acceptance criteria
- [ ] ...

## Out of scope
- ...
```

**`specs/001-{{FEATURE_SLUG}}/plan.md`**

```markdown
---
type: plan
title: {{FEATURE_SLUG}} — Technical Plan
description: Architecture, module boundaries and contracts mapping each requirement.
tags: [plan, {{FEATURE_SLUG}}]
status: draft
sources: [./spec.md]
generated: { by: claude-code, at: <ISO-8601> }
verified: { by: human, at: null }
stale_after: null
---

# {{FEATURE_SLUG}} — Plan

## Architecture
<capas / módulos / dependencias>

## Contracts
<interfaces, endpoints o comandos CLI; entradas/salidas>

## Requirement → Component map
| Requirement | Component | Notes |
|-------------|-----------|-------|
| R1          |           |       |

## Data model
<entidades y su relación con la DB (Neon)>
```

**`specs/001-{{FEATURE_SLUG}}/tasks.md`**

```markdown
---
type: tasks
title: {{FEATURE_SLUG}} — Task Breakdown
description: Granular, testable tasks derived from the plan.
tags: [tasks, {{FEATURE_SLUG}}]
status: draft
sources: [./plan.md]
generated: { by: claude-code, at: <ISO-8601> }
verified: { by: human, at: null }
stale_after: null
---

# {{FEATURE_SLUG}} — Tasks

- [ ] T1 — <tarea> · test: <qué verifica> · covers: R1
- [ ] T2 — <tarea> · test: <qué verifica> · covers: R2
```

---

### 4. Formato de las specs: Open Knowledge Format (OKF)

Todos los artefactos de conocimiento (specs, constitution, docs) siguen **OKF** (`https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf`): **markdown plano con frontmatter YAML**, enlazados entre sí con links markdown relativos.

Campos de frontmatter que usamos (ya reflejados en las plantillas de arriba):

- `type` — clasificación del documento (`constitution`, `clarifications`, `spec`, `plan`, `tasks`, `index`).
- `title`, `description` — humano-legibles.
- `tags` — etiquetas categóricas.
- `status` — `draft` | `active` | `verified` | `deprecated`.
- `sources` — orígenes / documentos de los que deriva (rutas relativas o URLs).
- `generated` — `{ by, at }` metadata de creación.
- `verified` — `{ by, at }` (queda `null` hasta que un humano lo confirme).
- `stale_after` — fecha/condición de caducidad (o `null`).

Reglas OKF:

- Un concepto = un archivo markdown.
- Enlaces entre documentos con links markdown relativos (`[plan](./plan.md)`).
- Generá `specs/index.md` (`type: index`) que liste y enlace todos los specs por carpeta.
- El formato es extensible: podés agregar claves extra al frontmatter sin romper nada.

---

### 5. Variables de entorno (`.env`)

- **Todas** las variables de entorno van en un único archivo `.env` en la raíz.
- `.env` **nunca se commitea** (va en `.gitignore`, ver sección 7).
- Creá también un `.env.example` **sí versionado**, con las mismas claves pero **sin valores** (o con placeholders), para documentar qué necesita el proyecto.

Estructura inicial de claves (ajustala al stack real):

```dotenv
# .env.example  (committed — placeholders only)
DATABASE_URL=
DIRECT_URL=
NEON_API_KEY=
APP_ENV=development
LOG_LEVEL=info
# n8n (only if USE_N8N=true)
N8N_MCP_TOKEN=
N8N_BASE_URL={{N8N_BASE_URL}}
```

Cargá las variables desde `.env` en el código (p. ej. `python-dotenv` / `pydantic-settings` según el stack). Nunca hardcodees secretos.

---

### 6. Base de datos: Neon (Postgres serverless)

Vamos a usar **Neon**. Hacé lo siguiente:

1. Inicializá Neon en el proyecto:
    
    ```bash
    npx neon@latest init
    ```
    
    Seguí el flujo (login / creación de proyecto). Esto scaffoldea la config de conexión.
    
2. Guardá las connection strings en `.env` (no en el código ni en git):
    
    - `DATABASE_URL` → conexión **pooled** (host con `-pooler`), para la app.
    - `DIRECT_URL` → conexión **directa** (unpooled), para migraciones/DDL. Formato:
    
    ```
    postgresql://USER:PASSWORD@HOST/neondb?sslmode=require&channel_binding=require
    ```
    
3. Verificá la conexión (usando la variable, sin pegar credenciales en el chat):
    
    ```bash
    psql "$DATABASE_URL"
    ```
    
4. En el código, mantené la conexión detrás de la capa de infraestructura (repositorios), separada del dominio — coherente con Clean Architecture / DDD.
    

> Si `psql` no está instalado o el token todavía no existe, dejá la variable como placeholder en `.env` / `.env.example` y avisame qué falta; no bloquees el resto del setup.

---

### 7. Git

1. **Inicializá el repo** (`git init`) si no existe.
2. **Generá un `.gitignore`** apropiado para el stack. Como mínimo debe incluir:
    
    ```gitignore
    # Secrets / env.env.env.*!.env.example# Python__pycache__/*.py[cod].venv/venv/.mypy_cache/.pytest_cache/.ruff_cache/# Neon / DB.neon*.sqlite3# OS / editor.DS_Store.idea/.vscode/# Node (si aplica, p. ej. tooling de Neon / n8n)node_modules/
    ```
    
3. **No commitees nada por ahora.** Dejá todo en el working tree / staging a mi criterio. No corras `git commit` salvo que yo te lo pida explícitamente.
4. **No agregues a Claude como colaborador ni como co-autor:**
    - No incluyas líneas `Co-Authored-By: Claude ...` ni firmas de asistente en commits.
    - Configurá el repo para que los commits queden a mi nombre.
    - Si en algún momento se agregó un usuario/bot de Claude como **collaborator** del repo remoto, quitalo (o indicame el comando `gh` exacto para hacerlo).

---

### 8. n8n — OPCIONAL (solo si `USE_N8N=true`)

Si `USE_N8N=false`, **saltá esta sección** y dejá anotado en el checklist que quedó pendiente.

Si `USE_N8N=true`:

1. **MCP server de n8n** (`https://docs.n8n.io/connect/connect-to-n8n-mcp-server`). Requisitos: instancia n8n accesible con _Instance-level MCP_ habilitado y un token. Agregalo a Claude Code:
    
    ```bash
    claude mcp add --transport http n8n-mcp {{N8N_BASE_URL}}/mcp-server/http \
      --header "Authorization: Bearer <TU_TOKEN_N8N_MCP>"
    ```
    
    Guardá el token en `.env` como `N8N_MCP_TOKEN` (no lo pegues literal en comandos versionados).
    
2. **Skills de n8n** (`https://github.com/czlonkowski/n8n-skills`) — 14 skills para construir workflows n8n. Requisito previo: el MCP `n8n-mcp` ya instalado (paso anterior).
    
    ```bash
    /plugin install czlonkowski/n8n-skills
    ```
    
    (o clonando el repo y copiando las carpetas a `~/.claude/skills/`).
    
3. Verificá con `claude mcp list` que `n8n-mcp` aparezca conectado.
    

---

### 9. README de onboarding

Generá un `README.md` (en inglés) que sirva para vos-futuro, colaboradores o alumnos. Debe cubrir:

- **What is this** — el one-liner del proyecto.
- **How we work (SDD)** — el flujo Constitution → Clarify → Spec → Plan → Tasks → Implement (TDD) → Validate → Change, y qué es cada artefacto/carpeta.
- **Add a new feature** — crear `specs/NNN-<feature>/`, pasar por el gate de Clarify, luego Spec (EARS) → Plan → Tasks.
- **OKF** — una tabla corta con los campos de frontmatter y qué significan.
- **Setup** — copiar `.env` desde `.env.example`, inicializar Neon (`npx neon@latest init`), correr los tests.
- **Git rule** — sin commits automáticos, sin co-autoría de IA.
- **Agent rules** — apuntar a `AGENTS.md` como fuente de verdad.

---

### 10. Verificación final (mostrame este checklist marcado)

- [ ] **Pre-flight** hecho: inspeccioné el directorio y no sobrescribí nada sin tu OK.
- [ ] `AGENTS.md` creado (reglas operativas) y `CLAUDE.md` apuntando a `AGENTS.md`.
- [ ] **Clarify gate** cumplido: te hice preguntas, esperé respuestas y las registré en `clarifications.md`.
- [ ] Estructura `specs/` creada: `constitution.md`, `index.md`, `001-{{FEATURE_SLUG}}/` con `clarifications.md`, `spec.md` (EARS), `plan.md`, `tasks.md`.
- [ ] Todos los specs tienen frontmatter **OKF** válido (YAML) y enlaces relativos correctos.
- [ ] `.env` creado (no versionado) y `.env.example` versionado con las mismas claves.
- [ ] Neon inicializado; `DATABASE_URL` (pooled) y `DIRECT_URL` (directa) en `.env`; conexión verificada (o pendiente anotado).
- [ ] `.gitignore` generado e ignorando `.env` (pero **no** `.env.example`).
- [ ] Repo `git init` hecho; **sin commits**; sin co-autoría/colaborador de Claude.
- [ ] `README.md` de onboarding generado.
- [ ] n8n: MCP + skills instalados **o** marcado como pendiente (`USE_N8N=false`).
- [ ] No se escribió código de la aplicación.

Cuando termines, resumime qué quedó listo y qué necesita input mío (tokens, decisiones de arquitectura, etc.).