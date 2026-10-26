---
tipo: tema
tags:
  - agentes
  - claude
---
# Claude Code: dos enfoques en video

Oct 26, 2026 · @Luciano

Dos videos muestran Claude Code desde ángulos opuestos: uno como asistente de programación en la terminal y otro como equipo de marketing automatizado. Verlos juntos ayuda a entender que las mismas piezas (contexto, skills, subagentes, MCP) sirven tanto para escribir código como para orquestar trabajo de negocio.

| Video | Autor | Enfoque | Enlace |
| --- | --- | --- | --- |
| Claude Code: Curso completo desde cero en 3 horas | MoureDev | Ingeniería de software | [Ver en YouTube](https://www.youtube.com/watch?v=TCq7eZ9Lhc8) |
| Claude Code: Build Your Full AI Marketing Team | Grace Leung | Automatización de marketing | [Ver en YouTube](https://www.youtube.com/watch?v=yLXLHnD4fco) |

**Cómo usar este material:** recomendamos ver primero el video de MoureDev para entender los fundamentos y después el de Grace Leung para ver cómo esos fundamentos se combinan en un sistema multiagente.

## Video 1 — Curso completo desde cero (MoureDev)

Tutorial técnico de unas 3 horas para instalar, configurar y usar Claude Code como asistente de programación en la terminal. [Ver video](https://www.youtube.com/watch?v=TCq7eZ9Lhc8)

### 1. Conceptos básicos y el bucle agéntico

Claude Code lleva los LLM directamente al entorno de trabajo (terminal o editor). No es un chat: tiene acceso a los archivos del proyecto y puede ejecutar comandos.

El **bucle agéntico** describe cómo razona el agente:

1. Recibe un objetivo.
2. Explora los archivos y el contexto.
3. Propone un plan de acción.
4. Ejecuta el plan: escribe código, lee archivos, usa la terminal.
5. Verifica el resultado y corrige errores, iterando hasta terminar.

### 2. Configuración y modos de uso

Se instala desde la terminal y requiere autenticarse con una cuenta de Anthropic. Permite elegir entre modelos como Sonnet, Opus o Fable.

| Modo | Qué hace | Cuándo usarlo |
| --- | --- | --- |
| Manual | Pide permiso antes de cada acción (leer, escribir, ejecutar) | Al empezar, para entender qué hace el agente |
| Auto | Decide y ejecuta por su cuenta | Tareas conocidas y de bajo riesgo |
| Plan | No escribe código: analiza y arma un plan estructurado | Tareas complejas, antes de ejecutarlas |

### 3. Gestión de memoria y contexto (guardarraíles)

- **Ventana de contexto:** la memoria del modelo es limitada. `/context` muestra cuánto se consumió y `/compact` resume la conversación para liberar espacio sin perder el hilo.
- **Archivo de reglas (`CLAUDE.md` o `AGENTS.md`):** va en la raíz del proyecto con el stack, las convenciones y el estilo. El agente lo lee antes de actuar, lo que hace su comportamiento más predecible.
- **Menciones con `@`:** referenciar archivos concretos (por ejemplo `@index.html`) evita que el agente lea todo el proyecto y ahorra tokens.

### 4. Extender Claude Code

- **Comandos personalizados:** prompts predefinidos guardados en `.claude/commands` que se invocan a mano (por ejemplo `/idea`) para automatizar tareas repetitivas.
- **Skills:** a diferencia de los comandos, el agente las invoca solo cuando detecta que las necesita (por ejemplo, un revisor de textos).
- **MCP (Model Context Protocol):** el equivalente a "enchufar un USB" al agente. Conecta herramientas externas como bases de datos, Playwright para testing o Slack.
- **Subagentes:** agentes especializados (por ejemplo un "Auditor de Accesibilidad") que trabajan en segundo plano mientras el agente principal orquesta.

### 5. Modelos locales y control de versiones

- **Ollama:** permite conectar Claude Code a modelos locales (como Gemma o Qwen) que corren en la propia máquina, sin costo de API.
- **`/rewind` (o doble Esc):** deshace cambios y vuelve a un estado anterior del código, como una máquina del tiempo cuando el agente se equivoca.

## Video 2 — Equipo de marketing con IA (Grace Leung)

Muestra cómo convertir Claude Code en un equipo de marketing automatizado para una marca ficticia de viajes (Go Travel). [Ver video](https://www.youtube.com/watch?v=yLXLHnD4fco)

### 1. Metodología en 4 pasos

1. **Mapear** las funciones de marketing repetitivas.
2. **Convertir** cada tarea en una skill.
3. **Agrupar** las skills en roles (subagentes).
4. **Conectar** a los agentes con reglas de enrutamiento.

### 2. Configuración del espacio de trabajo

- Trabaja en Visual Studio Code con una estructura de carpetas que imita una empresa real.
- **Carpetas de sistema:** plantillas, guías de estilo y tono de marca.
- **Carpetas de trabajo:** donde se guardan los resultados.
- Un `CLAUDE.md` inicial da al agente el contexto global de la marca.

### 3. Skills de marketing

| Skill | Cómo se construye | Resultado |
| --- | --- | --- |
| Presentaciones | A partir de una plantilla corporativa de PowerPoint como referencia | Decks que respetan colores, márgenes y diseño de la marca |
| Diseño de imágenes | Conectada por `mcp.json` a un generador de imágenes | Carruseles de Instagram basados en la librería de estilos de la marca |

### 4. El equipo (subagentes)

Se crean con el comando `/agents`, cada uno con un rol y sus skills:

- **Analista de datos:** toma datos de campañas y genera reportes sintetizados o dashboards interactivos.
- **Creador de contenido:** equipado con skills de SEO y redacción. En el ejemplo produce un post optimizado y un PDF descargable (lead magnet) con el tono de la marca.

### 5. Orquestación y casos avanzados

- **Campañas complejas:** el `CLAUDE.md` define qué agente usar en cada caso. Para una campaña sobre Japón, el agente principal delega en orden: investigación de mercado, brief, landing page y posts sociales, todo conectado temáticamente.
- **Integración con Notion (Taskbot):** el agente lee un tablero Kanban, toma las tareas pendientes, las asigna al agente correcto, guarda los archivos y mueve la tarjeta a "Completado".
- **Control remoto desde el móvil:** el comando de remote control vincula la sesión local con el teléfono para pedir tareas desde cualquier lugar.

## Comparativa y conceptos clave

Los dos videos usan las mismas piezas; cambia el tipo de trabajo que orquestan.

| Concepto | Qué es | En MoureDev | En Grace Leung |
| --- | --- | --- | --- |
| `CLAUDE.md` | Archivo de reglas que el agente lee antes de actuar | Stack, convenciones y estilo del proyecto | Contexto de marca y reglas de enrutamiento entre agentes |
| Comando | Prompt predefinido que se invoca a mano | `/idea` en `.claude/commands` | — |
| Skill | Capacidad que el agente activa solo cuando la necesita | Revisor de textos | Presentaciones y diseño de carruseles |
| MCP | Protocolo para conectar herramientas externas | Bases de datos, Playwright, Slack | Generador de imágenes, Notion |
| Subagente | Agente especializado al que el principal delega | Auditor de accesibilidad | Analista de datos y creador de contenido |
| Gestión de contexto | Control de la memoria limitada del modelo | `/context`, `/compact`, menciones con `@` | Carpetas de sistema separadas de las de trabajo |
