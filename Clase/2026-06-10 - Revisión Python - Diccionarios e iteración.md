---
tipo: clase
fecha: 2026-06-10
modulo: 2
tags: [python]
---

# Revisión Python — Diccionarios e iteración

## Resumen

- Las tres formas de recorrer un diccionario: `.items()`, `.values()` y `.keys()`.
- Función `count_letters()`: contar apariciones de cada carácter construyendo un diccionario sobre la marcha.
- El patrón «si la clave ya existe, sumo; si no, la creo en 1».

```python
###################
###################
#### Miercoles 10 ####

# Iterar e imprimir valor o clave
file_counts = {"jpg":10, "txt":14, "csv":2, "py":23}

# Es lo mismo
# file_counts = {
#     "jpg":10, 
#     "txt":14, 
#     "csv":2, 
#     "py":23
#     }

print("-----------------------")
for clave, valor in file_counts.items():
    print(f"{clave}: {valor}")
print("-----------------------")
for x in file_counts.values():
    print(f"{x}")
print("-----------------------")
for clave in file_counts.keys():
    print(f"{clave}")

# Contador de letras

def count_letters(texto):
    letras = {}
    for caracter in texto:
        if caracter in letras:
            letras[caracter] = letras[caracter] + 1
        else: 
            letras[caracter] = 1
    return letras

print(count_letters("tenant"))
print(count_letters("a long string with a lot of letters"))
print(count_letters("aaaaa"))

```

## Relacionado

- [[2026-06-09 - Revisión Python - Iteración, listas y strings]]
- [[Tarea - Programación inicial]]
