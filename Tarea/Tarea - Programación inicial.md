---
tipo: tarea
modulo: 2
estado: pendiente
tags: [python, algoritmos]
---

# Tarea — Programación inicial

## Resumen

- 16 ejercicios repartidos en cuatro bloques: loops, strings, listas y diccionarios.
- Cada bloque trae primero las consignas y después las soluciones comentadas.

## 📋 Parte 1: Las Consignas

### 🔁 Loops (Bucles)

- **Ejercicio 1:** Escribir un programa que muestre por pantalla los números del 1 al 10 utilizando un bucle `for`.
- **Ejercicio 2:** Utilizar un bucle `while` para sumar los números del 1 al 5 y mostrar el resultado final por pantalla.
- **Ejercicio 3:** Recorrer la cadena de texto `"Python"` y mostrar cada letra en una línea distinta.
- **Ejercicio 4:** Escribir un bucle que muestre únicamente los números pares entre el 1 y el 10.

### 🔤 Strings (Cadenas de texto)

- **Ejercicio 1:** Crear una variable con una palabra en minúsculas y transformarla completamente a mayúsculas usando un método de strings.
- **Ejercicio 2:** Calcular y mostrar cuántos caracteres tiene la frase `"Aprender a sprogramar"`.
- **Ejercicio 3:** Tomar la palabra `"Hola"` e imprimirla invertida (`"aloH"`).
- **Ejercicio 4:** Contar cuántas veces aparece la letra `"a"` en la frase `"Mi mamá me mima"`.

### 📋 Lists (Listas)

- **Ejercicio 1:** Crear una lista con 5 frutas. Luego, mostrar por pantalla únicamente la primera y la última fruta de la lista utilizando sus índices.
- **Ejercicio 2:** Dada la lista `[10, 20, 30]`, agregar el número `40` al final de la lista y modificar el primer elemento para que ahora sea `5`.
- **Ejercicio 3:** Crear una lista de números y calcular la suma de todos sus elementos utilizando un bucle.
- **Ejercicio 4:** Eliminar el último elemento de una lista de nombres y mostrar cómo quedó la lista.

### 📖 Dictionaries (Diccionarios)

- **Ejercicio 1:** Crear un diccionario que represente a una persona, con las claves: `"nombre"`, `"edad"` y `"ciudad"`. Mostrar por pantalla solo el valor de la edad.
- **Ejercicio 2:** Tomar el diccionario anterior y modificar la `"ciudad"` por una nueva. Además, agregar una nueva clave llamada `"profesion"`.
- **Ejercicio 3:** Dado un diccionario de productos y precios (por ejemplo: `{"manzana": 150, "banana": 100}`), mostrar todas las claves (los nombres de los productos) usando un bucle.
- **Ejercicio 4:** Verificar si la clave `"descuento"` existe dentro de un diccionario determinado e imprimir un mensaje que diga si existe o no.
- 

### 💡 Parte 2: Las Soluciones

Acá tenés el código de resolución para cada uno, con comentarios sencillos para entender el "por qué".

### 🔁 Soluciones: Loops

Python

## 

```
# Ejercicio 1: Números del 1 al 10
for i in range(1, 11):
    print(i)

# Ejercicio 2: Sumar del 1 al 5 con while
suma = 0
numero = 1
while numero <= 5:
    suma += numero
    numero += 1
print("La suma total es:", suma)

# Ejercicio 3: Deletrear una palabra
palabra = "Python"
for letra in palabra:
    print(letra)

# Ejercicio 4: Números pares
for i in range(1, 11):
    if i % 2 == 0:
        print(i)
```

### 🔤 Soluciones: Strings

Python

## 

```
# Ejercicio 1: Pasar a mayúsculas
palabra = "programación"
print(palabra.upper())

# Ejercicio 2: Contar longitud
frase = "Aprender a programar"
print("La longitud es:", len(frase))

# Ejercicio 3: Invertir un string (usando slicing)
saludo = "Hola"
print(saludo[::-1])

# Ejercicio 4: Contar caracteres específicos
texto = "Mi mamá me mima"
# Usamos .count() o .lower().count() por si hay mayúsculas
print("La letra 'a' aparece:", texto.lower().count("a"), "veces")
```

### 📋 Soluciones: Lists

Python

## 

```
# Ejercicio 1: Acceder por índices
frutas = ["manzana", "banana", "frutilla", "naranja", "pera"]
print("Primera:", frutas[0])
print("Última:", frutas[-1])

# Ejercicio 2: Agregar y modificar
numeros = [10, 20, 30]
numeros.append(40)  # Agrega al final
numeros[0] = 5      # Modifica el primero
print(numeros)

# Ejercicio 3: Sumar elementos de una lista
valores = [5, 10, 15, 20]
total = 0
for v in valores:
    total += v
print("Suma de la lista:", total)

# Ejercicio 4: Eliminar el último elemento
nombres = ["Ana", "Juan", "Pedro"]
nombres.pop()  # Elimina 'Pedro'
print(nombres)
```

### 📖 Soluciones: Dictionaries

```
# Ejercicio 1: Crear y acceder
persona = {"nombre": "Lucas", "edad": 28, "ciudad": "Córdoba"}
print("Edad:", persona["edad"])

# Ejercicio 2: Modificar y agregar
persona["ciudad"] = "Mendoza"  # Modifica
persona["profesion"] = "Programador"  # Agrega
print(persona)

# Ejercicio 3: Recorrer claves
precios = {"manzana": 150, "banana": 100, "naranja": 120}
for producto in precios.keys():
    print("Producto disponible:", producto)

# Ejercicio 4: Validar si existe una clave
carrito = {"item": "remera", "precio": 2500}
if "descuento" in carrito:
    print("¡Tiene descuento aplicado!")
else:
    print("No tiene descuento.")
```

## Relacionado

- [[2026-06-09 - Revisión Python - Iteración, listas y strings]]
- [[2026-06-10 - Revisión Python - Diccionarios e iteración]]
