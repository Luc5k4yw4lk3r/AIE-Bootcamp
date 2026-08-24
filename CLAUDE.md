# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

An **Obsidian vault**, not a software project. There is no build, no test suite, no linter, no dependencies. The content is Spanish-language study notes for a Neoland AI Engineering bootcamp (June–July 2026): class notes, exercises, reference topics and classmates' project write-ups.

Everything is Markdown plus two attachments. Changes are made by editing `.md` files directly.

The vault was migrated from a raw Notion export. That migration is done — if you find a 32-character hex suffix on a filename, a `%20`-encoded Markdown link to a local file, or a bare URL on its own line, it is a regression, not the status quo.

## Conventions live in CONVENCIONES.md

`CONVENCIONES.md` is the authoritative spec for naming, frontmatter, tags and linking. **Read it before creating or renaming any note.** Do not restate its rules here or invent new ones; if a rule needs to change, change it there.

The three that break things silently if ignored:

- Class notes are named `AAAA-MM-DD - Tema.md`. No weekday, no session number — those were inconsistent in the source and were deliberately removed.
- Topic tags go in the frontmatter property named **`tags`**, never `temas`. Obsidian only feeds its tag pane, autocomplete and `tag:` search from `tags`. The vocabulary is closed (19 values); adding one means adding it to `CONVENCIONES.md` first.
- Links between notes are wikilinks (`[[Note]]`), attachments are embeds (`![[file.png]]`). A Markdown link to a local file breaks backlinks and the graph.

## Verification

There are no tests, but these checks catch the failure modes this vault actually has. Run them after any bulk edit.

```bash
# Notion residue: all three must return nothing
find . -not -path './.git/*' -not -path './.obsidian/*' | grep -E '[0-9a-f]{32}'
grep -rlE '[0-9a-f]{32}' --include="*.md" .
grep -rnE '\]\([^)]*%20[^)]*\.(md|png|pdf)\)' --include="*.md" .

# Bare URLs (every external link must carry a label and a reason)
grep -rnE '^https?://' --include="*.md" .
```

For wikilink and YAML integrity, strip fenced blocks, inline code spans, **and** the `[[00:00](url)]` timestamp pattern before matching — that last one is a Notion artifact present throughout `Temas/Prompting - *` and `Temas/n8n.md`. It is a normal Markdown link wrapped in literal brackets, not a wikilink; a naive `\[\[` regex reports ~22 false positives.

Baseline at the initial commit `df59b95`: 37 notes, 118 wikilinks, 0 broken, all frontmatter valid YAML. The note count drifts as notes are added; the invariants that must hold are **0 broken wikilinks** and **0 notes without valid frontmatter**.

## Environment gotchas

These cost real time in this specific environment:

- **Obsidian Sync is enabled.** Close Obsidian before any bulk rename or move. Renaming many files underneath a running Obsidian propagates to Sync as deletes plus creates.
- **Detecting whether Obsidian runs:** `pgrep -f obsidian` matches its own command line, so it reports a hit even when Obsidian is closed. Use `ps -eo comm= | grep -ixc obsidian`, which matches process names exactly.
- **`gh` is installed as a snap.** `gh repo create --push` and similar fail with `git: 'remote-https' is not a git command`, because git runs inside snap confinement and cannot see `/usr/lib/git-core/`. The repo and remote are still created correctly — push separately with the system git.
- **The global git credential helper is broken.** `credential.helper=libsecret` is set globally but `git-credential-libsecret` is not installed. This repo overrides it locally with an empty entry followed by `!gh auth git-credential`; do not remove that local config.
- **git is 2.25.1** — no `git init -b <branch>`.

## Structure

Index notes sit at the repository root next to the folder they describe (`Clase.md` ↔ `Clase/`); this mirrors the Notion page structure the vault came from and is intentional. `Home.md` is the entry point. `Temas/` and `Recursos/` have no index note and are reached from `Home.md`.

`Clases.base` is an Obsidian Bases view over `tipo: clase`. Its YAML parses and Obsidian 1.12.7 supports Bases, but the view **has never been rendered** — treat it as unverified.

## Known unfixed defects

Reported and left unfixed pending the vault owner's decision. Do not assume they were oversights in the source material; most were introduced during the migration.

1. `Espacio de alumnos/Resumen - Using Python…md` — demoting the Notion H1s flattened the outline: the eight `📹 Vídeo N` sections and their subsections are all `##`, so subsections render as siblings of the video they belong to. Fix by demoting the non-video `##` headings to `###`.
2. `Tarea/Tarea - Programación inicial.md` — three empty `##` headings (Notion artifacts) plus "Parte 2" at `###` while "Parte 1" is at `##`.
3. `Tarea/Tarea - Python POO.md` — typo "Ejerc**ic**o 2".
4. `Clase/2026-07-02 - Bash - Scripting inicial.md` — `[gather-information.sh](http://gather-information.sh/)` is a dead link; Notion auto-linked a filename. Should be inline code.
5. `Tarea.md` — the "Estado" column repeats "ver propiedad `estado`" on every row and carries no information.
6. `Espacio de alumnos.md` — a PDF embed inside a bullet renders a full viewer in a list item.
7. `Home.md` — a `## Marketing` section (heading plus the placeholder "Sugerencia") from the original root note was dropped during the rewrite and never reinstated.
8. `Proyectos/Historias de usuario - Nash Equilibrium Lounge.md` — the H1 still reads "Historias de usuario de ejemplo" and does not match the filename.

## Language

Notes, headings and commit messages are in Spanish. Match the surrounding register when editing. Code, code comments in class notes and property names stay as they are — they are transcripts of what was taught.
