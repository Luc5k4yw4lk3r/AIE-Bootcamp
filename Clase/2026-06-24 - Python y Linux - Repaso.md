---
tipo: clase
fecha: 2026-06-24
modulo: 2
tags: [python, algoritmos]
---

# Python y Linux — Repaso

## Resumen

- Seis ejercicios integradores con consigna y solución, para repasar antes de seguir.
- Variables y operaciones, condicionales `if`/`elif`/`else`, bucles `while`.
- Devolver varios valores en una tupla y desempaquetarlos.
- Iterar un diccionario con `.items()` y contar vocales en una frase.

### 1. Variables y Operaciones Básicas

**Consigna:** Escribe un script que calcule el área de un rectángulo. Define dos variables, `longitud` con valor 10 y `ancho` con valor 5, calcula el área multiplicándolas y usa la función `print` para mostrar el resultado.
**Respuesta:**

```jsx
longitud = 10
ancho = 5
area = longitud * ancho
print("El área es:", area)
```

### 2. Condicionales (if, elif, else)

**Consigna:** Crea una función `evaluar_numero` que reciba un número por parámetro. Usa la estructura `if`, `elif` y `else` para imprimir `"Positivo"` si es mayor que cero, `"Negativo"` si es menor, y `"Cero"` si es exactamente cero.
**Respuesta:**

```jsx
def evaluar_numero(num):
    if num > 0:
        print("Positivo")
    elif num < 0:
        print("Negativo")
    else:
        print("Cero")

evaluar_numero(-3)
evaluar_numero(0)
```

### 3. Bucles While (While Loops)

**Consigna:** Escribe un bucle `while` que inicialice una variable `x` en 1 y la imprima iteración tras iteración incrementándola en 1, hasta que el valor de `x` llegue a 5 (inclusive).
**Respuesta:**

```jsx
i = 0
while i <= 5:
        i = i + 1
        print(i)
```

### 4. Horas a minutos (Unpacking)

**Consigna:** Escribe una función `horas_a_minutos_segundos` que reciba una cantidad de horas y devuelva una **tupla** con su equivalente en minutos y en segundos. Luego llama a la función y  los resultados en dos variables separadas imprimiéndolas.
**Respuesta:**

```jsx
def horas_a_minutos_segundos(hora):
    minutos = hora * 60
    segundos = hora * 3600
    return minutos, segundos

print(horas_a_minutos_segundos(13))
```

### 5. Diccionarios y su Iteración

**Consigna:** Crea un diccionario llamado `inventario` con los pares clave-valor: `"manzanas": 10` y `"bananas": 5`. Usa un bucle `for` junto con el método `.items()` para iterar sobre el diccionario e imprimir el mensaje: `"[cantidad] unidades de [fruta]"` para cada elemento.
**Respuesta:**

```jsx
inventario = {
    "manzanas":"10",
    "bananas":"5"
}
for clave, valor in inventario.items():
       print(f"{valor} unidades de {clave}")
```

### 6. Contador: Vocales en una frase

**Consigna:** Escribe un script que recorra una cadena de texto y cuente cuántas vocales (a, e, i, o, u) contiene. Utiliza una variable contador que se incremente cada vez que encuentres una vocal.
**Respuesta:**

```jsx
texto = "Aprender python es fascinante"
contador_vocales = 0
vocales = "aeiouAEIOU"

for letra in texto:
    if letra in vocales:
        contador_vocales = contador_vocales + 1

print("El texto tiene", contador_vocales, "vocales.")
```

[[2026-06-23 - Python y Linux - Datos y procesos|Session 14 - Martes 23 Junio -  Python y Linux - Datos y procesos]]

## Relacionado

- [[Tarea - Algoritmos]]
