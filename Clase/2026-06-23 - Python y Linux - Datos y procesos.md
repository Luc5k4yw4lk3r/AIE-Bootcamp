---
tipo: clase
fecha: 2026-06-23
modulo: 2
tags: [python, linux]
---

# Python y Linux — Datos y procesos

## Resumen

- Leer variables de entorno del sistema con `os.environ.get("FRUIT", "NO_FRUTA")` y su valor por defecto.
- Exportarlas desde la shell con `export FRUIT=Manzana`.
- Recibir argumentos de línea de comandos con `sys.argv` y ramificar con `if`/`elif` para construir subcomandos.

## Variables de entornos

Se leen variables de entorno del sistema operativo desde el script

```jsx
import os

fruta = os.environ.get("FRUIT", "NO_FRUTA")
print(f"Esta es la fruta del sistema operativo {fruta}")

```

Ejecucion

```jsx
export FRUIT=Manzana
echo $FRUIT

```

## Pasar argumentos a un script

```jsx
import os
import sys

# filename = sys.argv[1]

# print(sys.argv)

if sys.argv[1] == "force":
    print("Voy a eliminar todo sin preguntar")
elif sys.argv[1] == "help":
    print("Te voy a proveer de ayuda")
    print("Opciones especiales")
    print("Tengo el comando force que elimina todo")
    print("Tengo el comando notificar que notifica a los admins")
    print("Tengo el comando notificar que notifica a los admins")
elif sys.argv[1] == "notificar":
    print("Notificando")
```

Ejecucion

```jsx
python3 data_and_process.py notificar
```

## Relacionado

- [[2026-07-02 - Bash - Scripting inicial]]
