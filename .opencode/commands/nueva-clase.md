---
description: Crea un apunte de clase nuevo desde la plantilla (uso: /nueva-clase AAAA-MM-DD Tema)
agent: build
allowed-tools: Bash(cat:*), Read, Write, Edit
---

Creá un apunte de clase nuevo para: **$ARGUMENTS**

Pasos:

1. Interpretá los argumentos como fecha y tema. Si no viene fecha, usá la de hoy. Si no viene tema, pedilo antes de crear nada.
2. Copiá `Plantillas/Plantilla - Clase.md` a `Clase/AAAA-MM-DD - Tema.md`. El nombre no lleva día de la semana ni número de sesión — ver `CONVENCIONES.md`.
3. Rellená el frontmatter: `fecha` con la fecha real (no la variable de plantilla), `modulo` y `tags`. Los `tags` salen del vocabulario cerrado de `CONVENCIONES.md`; si hiciera falta uno nuevo, pedilo primero, no lo inventes.
4. Poné el H1 igual al nombre del archivo, sin la fecha.
5. Agregá la fila correspondiente en la tabla del módulo que toca en `Clase.md`, respetando el formato de las filas vecinas.

Dejá el `## Resumen` vacío: se completa al terminar la sesión.
