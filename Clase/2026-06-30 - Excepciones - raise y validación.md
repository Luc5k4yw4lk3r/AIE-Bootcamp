---
tipo: clase
fecha: 2026-06-30
modulo: 2
tags: [python, excepciones, testing]
---

# Excepciones — raise y validación

## Resumen

- Diferencia entre **devolver** `False` (el dato es inválido) y **lanzar** una excepción (la llamada en sí no tiene sentido).
- `raise ValueError(...)` cuando el parámetro recibido es imposible, antes de hacer ningún trabajo.
- Validar primero y salir pronto, en vez de anidar condicionales.

```python
#!/usr/bin/env python3

def validate_user(username, minlen):
  if minlen < 1:
    raise ValueError("minlen must be at least 1")

  if len(username) < minlen:
    return False
  if not username.isalnum():
    return False
  return True
```

## Relacionado

- [[2026-06-29 - Testing con unittest]]
- [[Tarea - Excepciones, testing y APIs]] — ejercicios de repaso sobre esta sesión.
