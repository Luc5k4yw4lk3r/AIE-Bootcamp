---
tipo: clase
fecha: 2026-07-02
modulo: 2
tags: [bash, linux]
---

# Bash — Scripting inicial

## Resumen

- Primer script: shebang `#!/bin/bash` y un informe del sistema con `date`, `uptime`, `free` y `who`.
- Variables en Bash: se asignan sin espacios (`example=hello`) y se leen con `$example`.
- Sustitución de comandos con `$(date)`.
- Refactor: guardar el separador en una variable y encadenar con `;` para acortar el script.

Probando comandos bash

[gather-information.sh](http://gather-information.sh/) 

```bash
#!/bin/bash
echo "Starting at: $(date)"
echo

echo "UPTIME"
uptime
echo

echo "FREE"
free
echo

echo "WHO"
who
echo

echo "Finishing at: $(date)"
```

## Variables

```bash
example=hello
echo $example
```

```bash
#!/bin/bash

line="-------------------------------------------------"

echo "Starting at: $(date)"; echo $line

echo "UPTIME"; uptime; echo $line

echo "FREE"; free; echo $line

echo "WHO"; who; echo $line

echo "Finishing at: $(date)"
```

## Relacionado

- [[2026-07-01 - Linux - Comandos de archivos y procesos]]
- [[2026-06-23 - Python y Linux - Datos y procesos]]
