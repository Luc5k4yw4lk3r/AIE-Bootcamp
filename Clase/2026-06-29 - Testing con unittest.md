---
tipo: clase
fecha: 2026-06-29
modulo: 2
tags: [python, testing]
---

# Testing con unittest

## Resumen

- Estructura de un test con `unittest`: heredar de `unittest.TestCase` y nombrar los métodos `test_*`.
- `assertEqual()` para comparar el resultado real con el esperado.
- Pensar los casos borde además del caso feliz: cadena vacía, nombre doble, un solo nombre.

```python
#!/usr/bin/env python3

import unittest

from rearrange import rearrange_name

class TestRearrange(unittest.TestCase):
    
  def test_basic(self):
    testcase = "Lovelace, Ada"
    expected = "Ada Lovelace"
    self.assertEqual(rearrange_name(testcase), expected)

  def test_empty(self):
    testcase = ""
    expected = ""
    self.assertEqual(rearrange_name(testcase), expected)

  def test_double_name(self):
    testcase = "Hopper, Grace M."
    expected = "Grace M. Hopper"
    self.assertEqual(rearrange_name(testcase), expected)

  def test_one_name(self):
    testcase = "Voltaire"
    expected = "Voltaire"
    self.assertEqual(rearrange_name(testcase), expected)

#   def test_book(self):
#     testcase = "Lovelace, Ada"
#     expected = {"name": "El aleph", "puntaje":4, "descripcion": ""}
#     self.assertEqual(rearrange_name(testcase), expected)

# Run the tests
unittest.main()

```

## Relacionado

- [[2026-06-30 - Excepciones - raise y validación]]
- [[Tarea - Excepciones, testing y APIs]] — ejercicios de repaso sobre esta sesión.
- [[Python y Sistemas Operativos]]
