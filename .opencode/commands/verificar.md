---
description: Corre los chequeos de integridad del vault e interpreta el resultado
agent: build
allowed-tools: Bash(.scripts/verificar-vault.py)
---

Corré `.scripts/verificar-vault.py` e interpretá la salida contra las convenciones del vault.

Al reportar:

- **Wikilinks rotos** y **notas sin frontmatter válido** son invariantes: si alguno falla, hay que arreglarlo antes de commitear. Decilo explícitamente.
- Los otros cuatro chequeos son deriva a saldar, no bloqueantes.
- Si un hallazgo te parece un falso positivo, no toques el regex sin leer antes la sección "Verificación" de `AGENTS.md`: cada exclusión del script está ahí por un caso concreto de este vault.

No arregles nada sin que te lo pidan: primero reportá qué hay y cuánto es.
