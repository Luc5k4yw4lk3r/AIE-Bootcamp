# AIE-Bootcamp

Vault de [Obsidian](https://obsidian.md) con los apuntes del bootcamp de AI Engineering de Neoland: notas de clase en `Clase/`, ejercicios en `Tarea/`, referencia por módulo en `Temas/` y documentos de proyecto en `Proyectos/`. Los adjuntos se reparten entre `Adjuntos/` (PDFs y entregables) y `Multimedia/` (imágenes).

**No es un proyecto de software.** No hay build, ni tests, ni dependencias que instalar. Todo es Markdown y se edita como Markdown.

## Abrir el vault

1. Cloná el repo.
2. En Obsidian: **Abrir carpeta como vault** → elegí la carpeta del clon.

`.obsidian/` no se versiona, así que cada uno tiene su propia configuración: tema, plugins y ajustes son tuyos y no se pisan entre máquinas. Si querés usar las plantillas de `Plantillas/`, activá el plugin **Templates** y apuntalo a esa carpeta.

## Antes de escribir: CONVENCIONES.md

`CONVENCIONES.md` es la regla del vault: cómo se nombran las notas, qué lleva el frontmatter, qué tags existen y cómo se enlaza. **Leelo antes de crear o renombrar una nota.** Casi todo lo que se rompe en silencio acá —backlinks, el grafo, el panel de tags— sale de saltarse alguna de esas reglas.

## Chequear que el vault esté sano

```bash
python3 .scripts/verificar-vault.py     # Windows: python .scripts\verificar-vault.py
```

Busca residuo de la migración de Notion, enlaces Markdown donde tendría que haber wikilinks, URLs sin etiqueta, wikilinks rotos y notas sin frontmatter. Sale con código 1 si encuentra algo.

No requiere instalar nada. Si tenés `pyyaml` (`pip install pyyaml`), el chequeo de frontmatter además valida el YAML; sin él lo chequea por estructura.

Corrélo después de cualquier edición grande, y sobre todo antes de commitear renombrados o movimientos.

## Trabajar con agentes de IA

El repo está configurado para que funcione igual con distintos agentes, sin que tengas que instalar ninguno:

| | |
|---|---|
| **Instrucciones** | `AGENTS.md`. Es la única fuente; `CLAUDE.md` solo la importa. |
| **Claude Code** | Carga `CLAUDE.md` → `AGENTS.md`. Comandos en `.claude/commands/`. |
| **opencode** | Carga `AGENTS.md` y, vía `opencode.json`, también `CONVENCIONES.md`. Comandos en `.opencode/commands/`. |
| **Comandos** | `/verificar` y `/nueva-clase`, disponibles en los dos. |

Los comandos canónicos viven en `.opencode/commands/`; los de `.claude/commands/` apuntan ahí. Si editás uno, editá el de `.opencode/`.

`AGENTS.md` tiene una sección de gotchas específicos de la máquina del dueño del vault. Está marcada como tal: si estás en otra máquina, ignorala.
