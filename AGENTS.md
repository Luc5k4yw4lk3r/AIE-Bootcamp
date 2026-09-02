# AGENTS.md

Instrucciones para cualquier agente que trabaje este repositorio.

Para la puesta en marcha —clonar, abrir en Obsidian, correr el chequeo— está `README.md`.

## Agentes

Este archivo es la **fuente canónica**. No dupliques su contenido en otro lado.

| Archivo | Para qué |
|---|---|
| `AGENTS.md` | Estas instrucciones. Lo cargan opencode y cualquier agente que siga la convención `AGENTS.md`. |
| `CLAUDE.md` | Un stub: importa `AGENTS.md` con `@AGENTS.md`. Claude Code resuelve el import. |
| `opencode.json` | Suma `CONVENCIONES.md` al contexto de opencode y desactiva los formatters. |
| `.opencode/commands/` | Comandos slash, **versión canónica**. Editá acá. |
| `.claude/commands/` | Punteros de tres líneas a los de `.opencode/commands/`. Son archivos reales, no symlinks: un symlink se rompe en silencio en Windows. |
| `.scripts/verificar-vault.py` | Los chequeos de integridad del vault. |
| `.opencode/.gitignore` | Lo genera opencode solo. No lo toques; no afecta a los comandos, que sí se versionan. |

opencode carga `AGENTS.md` con prioridad sobre `CLAUDE.md`, así que no hay contenido duplicado. Lo que **no** hace opencode es seguir referencias a otros archivos desde dentro de `AGENTS.md`: por eso `CONVENCIONES.md` se declara en `instructions` de `opencode.json`.

Verificado: los dos agentes descubren los comandos (`opencode debug config` lista `verificar` y `nueva-clase`; Claude Code también). opencode aplicaría formatters al Markdown que edita — de ahí `formatter: false`, que protege wikilinks, callouts y tablas de que se los reflowee.

## Qué es este repositorio

Un **vault de Obsidian**, no un proyecto de software. No hay build, ni suite de tests, ni linter, ni dependencias. El contenido son apuntes de estudio en castellano del bootcamp de AI Engineering de Neoland (junio–julio 2026): apuntes de clase, ejercicios, temas de referencia y documentos de proyecto de compañeros.

Todo es Markdown más tres binarios (un PNG y un PDF en `Adjuntos/`, una imagen pegada en `Multimedia/`). Los cambios se hacen editando archivos `.md` directamente.

El vault se migró desde una exportación cruda de Notion. Esa migración está terminada — si aparece un sufijo hexadecimal de 32 caracteres en un nombre de archivo, un enlace Markdown con `%20` a un archivo local, o una URL desnuda sola en su línea, es una regresión, no el estado normal.

## Las convenciones viven en CONVENCIONES.md

`CONVENCIONES.md` es la spec autoritativa de nombres, frontmatter, tags y enlaces. **Leelo antes de crear o renombrar cualquier nota.** No repitas sus reglas acá ni inventes nuevas; si una regla tiene que cambiar, cambiala ahí.

Las tres que rompen en silencio si se ignoran:

- Los apuntes de clase se llaman `AAAA-MM-DD - Tema.md`. Sin día de la semana, sin número de sesión — eran inconsistentes en el origen y se quitaron a propósito. Excepción viva: las sesiones del módulo A sin fecha confirmada se llaman `MA·SNN - Tema.md`, y una mezcla las dos formas (`2026-08-28 - MA·S04 - ...`). Es deuda de nombrado conocida, decidida por el dueño del vault; no la renombres sin que te lo pidan.
- Los tags de tema van en la propiedad de frontmatter **`tags`**, nunca `temas`. Obsidian solo alimenta el panel de tags, el autocompletado y la búsqueda `tag:` desde `tags`. El vocabulario es cerrado (19 valores); agregar uno significa agregarlo antes a `CONVENCIONES.md`.
- Los enlaces entre notas son wikilinks (`[[Nota]]`), los adjuntos son embeds (`![[archivo.png]]`). Un enlace Markdown a un archivo local rompe los backlinks y el grafo.

## Verificación

No hay tests, pero sí un script que cubre los modos de fallo que este vault tiene de verdad. Corrélo después de cualquier edición masiva:

```bash
.scripts/verificar-vault.py
```

Chequea residuo de Notion (en nombres y en contenido), enlaces Markdown a archivos locales, URLs desnudas, wikilinks rotos y notas sin frontmatter válido. Sale con código 1 si encuentra algo. Solo necesita Python 3; PyYAML es opcional y el propio script te dice en qué modo corrió.

Dos cosas que hay que entender antes de tocar los regex del script:

- Hay que neutralizar bloques cerrados y code spans **en todos** los chequeos, no solo en el de wikilinks: `CONVENCIONES.md` documenta los antipatrones citándolos, así que sin eso se denuncia a sí misma. Aparte hay que descartar el patrón `[[00:00](url)]` — ese último es un artefacto de Notion presente en todo `Temas/Prompting - *` y `Temas/n8n.md`. Es un enlace Markdown normal envuelto en corchetes literales, no un wikilink; un regex ingenuo de `\[\[` reporta ~22 falsos positivos. Aparece además en forma múltiple: `[[03:29](url), [03:51](url)]`.
- El hexadecimal de 32 caracteres y el `%20` también matchean **dentro de URLs externas** (nombres de PDFs de NeurIPS, de Fraunhofer, de Cockburn). Por eso el script excluye las líneas con `http`.

Línea base en el commit inicial `df59b95`: 37 notas, 118 wikilinks, 0 rotos, todo el frontmatter YAML válido. La cantidad de notas va cambiando; los invariantes que tienen que valer son **0 wikilinks rotos** y **0 notas sin frontmatter válido**.

Estado al 2026-09-02: 54 notas, **6/6 chequeos sin hallazgos**. La deuda de agosto —8 URLs desnudas y 13 notas sin frontmatter— quedó saldada. Si el script te da rojo, es algo que se introdujo después: arreglalo, no lo documentes acá.

## Gotchas del vault

Valen en cualquier máquina:

- **Obsidian reescribe enlaces al renombrar.** Con `alwaysUpdateLinks: true` —el default— y la app abierta, renombrar un archivo hace que Obsidian toque otras notas por debajo. Cerralo antes de un renombrado o movimiento masivo.
- **Detectar si Obsidian está corriendo:** `pgrep -f obsidian` matchea su propia línea de comando, así que reporta un hit aunque Obsidian esté cerrado. Usá `ps -eo comm= | grep -ixc obsidian`, que matchea nombres de proceso exactos.
- **`.scripts/verificar-vault.py` no necesita que instales nada.** PyYAML es opcional: si está, el chequeo de frontmatter valida el YAML; si no, lo chequea por estructura y avisa. No lo vuelvas a hacer obligatorio — no todo el equipo lo tiene.
- **Nada de symlinks en el árbol.** Hay máquinas Windows en el equipo, donde un symlink versionado se materializa como un archivo de texto con la ruta adentro y lo que apuntaba desaparece sin error.

## Gotchas de la máquina del dueño del vault

**Si estás en otra máquina, ignorá esta sección entera.** Nada de esto viaja en el clon; son particularidades de un entorno concreto, anotadas porque cuestan tiempo real ahí.

- **opencode no está en el `PATH`.** Se invoca como `~/.opencode/bin/opencode`.
- **`gh` está instalado como snap.** `gh repo create --push` y similares fallan con `git: 'remote-https' is not a git command`, porque git corre dentro del confinamiento del snap y no ve `/usr/lib/git-core/`. El repo y el remote quedan bien creados igual — hacé el push aparte con el git del sistema.
- **El credential helper global de git está roto.** `credential.helper=libsecret` está seteado globalmente pero `git-credential-libsecret` no está instalado. Se soluciona con una entrada vacía seguida de `!gh auth git-credential` en la config **local** del repo. Esa config no se clona: cada uno resuelve su propia autenticación con GitHub.
- **git es 2.25.1** — no hay `git init -b <rama>`.

## Estructura

Las notas índice están en la raíz del repositorio, al lado de la carpeta que describen (`Clase.md` ↔ `Clase/`); esto refleja la estructura de páginas de Notion de la que viene el vault y es intencional. La excepción es `Proyectos/Proyectos.md`, que vive dentro de su carpeta: el wikilink `[[Proyectos]]` resuelve igual, pero rompe la simetría con el resto. `Home.md` es el punto de entrada. `Temas/` y `Recursos/` no tienen nota índice y se llegan desde `Home.md`.

`Clases.base` es una vista de Obsidian Bases sobre `tipo: clase`. Su YAML parsea y Obsidian 1.12.7 soporta Bases, pero la vista **nunca se renderizó** — tratala como no verificada.

## Defectos conocidos sin arreglar

Reportados y dejados sin arreglar a la espera de la decisión del dueño del vault. No asumas que fueron descuidos del material original; la mayoría se introdujeron durante la migración.

1. `Espacio de alumnos/Resumen - Using Python to Interact with the Operating System.md` — bajar de nivel los H1 de Notion aplanó el esquema: las ocho secciones `📹 Vídeo N` y sus subsecciones quedaron todas en `##`, así que las subsecciones renderizan como hermanas del vídeo al que pertenecen. Se arregla bajando a `###` los `##` que no son de vídeo.
2. `Tarea/Tarea - Programación inicial.md` — tres encabezados `##` vacíos (artefactos de Notion) más "Parte 2" en `###` mientras "Parte 1" está en `##`.
3. `Tarea/Tarea - Python POO.md` — errata "Ejerc**ic**o 2".
4. `Clase/2026-07-02 - Bash - Scripting inicial.md` — `[gather-information.sh](http://gather-information.sh/)` es un enlace muerto; Notion auto-enlazó un nombre de archivo. Debería ser código inline.
5. `Tarea.md` — la columna "Estado" repite "ver propiedad `estado`" en cada fila y no aporta información.
6. `Espacio de alumnos.md` — un embed de PDF dentro de una viñeta renderiza un visor completo dentro del ítem de lista.
7. `Home.md` — una sección `## Marketing` (encabezado más el placeholder "Sugerencia") de la nota raíz original se perdió durante la reescritura y nunca se repuso.
8. `Proyectos/Historias de usuario - Nash Equilibrium Lounge.md` — el H1 sigue diciendo "Historias de usuario de ejemplo" y no coincide con el nombre del archivo.

## Idioma

Las notas, los encabezados y los mensajes de commit van en castellano. Respetá el registro de lo que hay alrededor al editar. El código, los comentarios de código de los apuntes y los nombres de propiedades quedan como están — son transcripciones de lo que se enseñó.
