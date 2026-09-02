---
tipo: indice
tags: [bootcamp]
---

# Convenciones del vault

Reglas para que el vault no vuelva a degradarse. Si dudás, mirá una nota existente del mismo tipo y copiá su forma.

## Estructura de carpetas

| Carpeta | Qué va | Nota índice |
|---|---|---|
| `Clase/` | Un apunte por sesión en vivo | [[Clase]] |
| `Tarea/` | Ejercicios con enunciado y solución | [[Tarea]] |
| `Temas/` | Referencia por tema, independiente de la fecha | — |
| `Proyectos/` | Documentos de proyecto largos | [[Proyectos]] |
| `Recursos/` | Enlaces y material externo sin elaborar | — |
| `Espacio de alumnos/` | Material aportado por compañeros | [[Espacio de alumnos]] |
| `Plantillas/` | Plantillas del plugin Templates | — |
| `Adjuntos/` | Imágenes y PDFs | — |

La raíz solo tiene [[Home]], [[CONVENCIONES]] y las notas índice. Única excepción: el `README.md` y los archivos de configuración de agentes (`AGENTS.md`, `CLAUDE.md`, `opencode.json`), que tienen que estar en la raíz para que las herramientas los encuentren. No son notas del vault.

## Nombres de archivo

- **Clases:** `AAAA-MM-DD - Tema.md` → `2026-06-22 - Python y Linux - Expresiones regulares.md`
  La fecha ordena sola y evita el lío de numerar sesiones. **No** se pone el día de la semana ni el número de sesión en el nombre; van en las propiedades.
- **Todo lo demás:** título descriptivo en castellano, con tildes, sin fecha.
- Nunca sufijos de ID ni códigos. Si aparece un hash de 32 caracteres al final de un archivo, viene de una exportación de Notion y hay que quitarlo.

## Propiedades (frontmatter)

Toda nota empieza con un bloque YAML. `tipo` es obligatorio; el resto depende del tipo.

```yaml
---
tipo: clase          # clase | tarea | tema | proyecto | recurso | indice
fecha: 2026-06-22    # solo en clase
modulo: 2            # solo en clase y tarea; `A` es el módulo transversal
estado: pendiente    # solo en tarea y proyecto
tags: [python, regex, linux]
---
```

| Propiedad | Valores |
|---|---|
| `tipo` | `clase` · `tarea` · `tema` · `proyecto` · `recurso` · `indice` |
| `estado` (tarea) | `pendiente` · `en-progreso` · `hecha` |
| `estado` (proyecto) | `idea` · `en-progreso` · `terminado` |
| `modulo` | `1` · `2` · `3` · `4` · `A` |

> [!important] La propiedad se llama `tags`, no `temas`
> Obsidian trata `tags` como propiedad especial: alimenta el panel de tags, el autocompletado y la búsqueda `tag:#python`. Con cualquier otro nombre eso no funciona.

### Vocabulario cerrado de `tags`

Usá solo estos. Si hace falta uno nuevo, agregalo primero a esta lista.

`python` · `bash` · `linux` · `regex` · `archivos` · `csv` · `poo` · `testing` · `excepciones` · `apis` · `git` · `llm` · `rag` · `prompting` · `agentes` · `n8n` · `web` · `algoritmos` · `proyectos` · `requisitos` · `modelado` · `agil` · `estimacion` · `bootcamp`

## Enlaces

- **Entre notas:** siempre wikilink → `[[Nombre de la nota]]`, o `[[Nombre|texto visible]]` si necesitás otro texto.
  Nunca `[texto](ruta/al/archivo.md)`: rompe los backlinks y el grafo.
- **Adjuntos:** embed → `![[imagen.png]]`, `![[documento.pdf]]`.
- **Enlaces externos:** nunca dejes una URL desnuda. Siempre con etiqueta y una frase de por qué está ahí:

  ```md
  - [Learn Python - Full Course for Beginners — freeCodeCamp](url) — 4 h de sintaxis desde cero.
  ```

  Una URL suelta dentro de seis meses no dice nada sobre por qué la guardaste.

## Cómo añadir una clase nueva

1. `Ctrl+N` dentro de `Clase/`.
2. `Ctrl+P` → **Insert template** → `Plantilla - Clase`.
3. Renombrar el archivo a `AAAA-MM-DD - Tema`.
4. Rellenar `fecha`, `modulo` y `temas` en las propiedades, y el `## Resumen` con 2–4 viñetas al terminar la sesión.
5. Añadir la fila en la tabla de [[Clase]].

## Marcas de trabajo pendiente

- `#revisar` — algo que hay que verificar o completar.
- Bloque `> [!question] Pendiente` — hueco conocido dentro de una nota.

Buscá `#revisar` cada tanto para ir saldando deuda.
