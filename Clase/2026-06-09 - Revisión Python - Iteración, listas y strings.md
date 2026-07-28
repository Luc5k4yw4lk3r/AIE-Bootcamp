---
tipo: clase
fecha: 2026-06-09
modulo: 2
tags: [python]
---

# Revisión Python — Iteración, listas y strings

## Resumen

- Acumulador y contador dentro de un `for` para calcular suma y promedio de una lista.
- Bucles anidados con `range()` para recorrer una cuadrícula.
- Strings: recorrido con `for` y por índice con `while`, *slicing* (`[4:8]`, `[::-1]`), concatenación y `join()`.
- Listas: `append()`, `insert()`, `remove()`, el operador `in` y un `try`/`except` para el borrado de un elemento que no existe.

```python
###################
###################
#### Martes 09#####

# Valor total de los elementos de la lista
# El promedio total
values = [23, 52, 59, 37, 48]
acum = 0
i = 0
for value in values:
    acum = value + acum
    i = i + 1
print(f"El acumulado es: {acum}")
print(f"El promedio es: {acum/i}")

# Ejemplo de while donde se define la condicion de fin
# j = 0
# while j < 55:
#     j = j + 1

# for n in range(7):
#     print(n)

# Recorrido de un excel
for left in range(7):
    for right in range(7):
        print("[" + str(left) + "|" + str(right) + "]", end=" ")
    print()

## Strings
greeting = "Hello"  # ["h", "e", "l", "l", "o"]
for char in greeting:
    print(char)

# Manejo de strings por indice
# print(greeting[0])
i = 0
while i < len(greeting):
    print(greeting[i])
    i = i + 1

# Manejo de string
# string1 = "Greetings, Earthlings"
print(string1[0])   # Prints “G”
print(string1[4:8]) # Prints “ting”
print(string1[11:]) # Prints “Earthlings”
print(string1[:5])  # Prints “Greet”
print(string1[::-1])  # Prints “sgnilhtraE ,sgniteerG”

# Unificaciones de strings
print("Hello" + " " + "world")

greetings = ["Hello", "world", "Esp"]

print(" ".join(greetings))

# Listas
fruits = ["Pineapple", "Banana", "Apple", "Melon"]
# "Kiwi"
fruits.append("kiwi")
print(fruits)

# Insetar en posicion 0  el valor "Orange"
# fruits[0] = "Orange"
fruits.insert(0, "Orange")
print(fruits)

# Remover el valor melon
fruits.remove("Melon")
print(fruits)

# Remover el valor Pear
# fruits.append("Pear")
try:
    # if "Pear" in fruits:
    print("Pear" in fruits)
    fruits.remove("Pear")
except:
    print("Error al eliminar Pear")
print(fruits)

```

## Relacionado

- [[2026-06-10 - Revisión Python - Diccionarios e iteración]]
- [[Tarea - Programación inicial]]
