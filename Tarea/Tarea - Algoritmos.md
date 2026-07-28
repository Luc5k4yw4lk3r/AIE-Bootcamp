---
tipo: tarea
modulo: 2
estado: pendiente
tags: [python, algoritmos, poo]
---

# Tarea — Algoritmos

## Resumen

- 12 ejercicios en tres niveles, todos con solución.
- Algoritmos básicos: contadores, acumuladores, búsqueda del máximo y variables bandera.
- POO: métodos que modifican estado, herencia y composición.
- Avanzado: diagonal de una matriz, agrupación con diccionarios, bucles anidados y bubble sort.

## **Algoritmos Básicos (Contadores, Acumuladores y Banderas)**

### 1. Contador: Vocales en una frase

**Consigna:** Escribe un script que recorra una cadena de texto y cuente cuántas vocales (a, e, i, o, u) contiene. Utiliza una variable contador que se incremente cada vez que encuentres una vocal.
**Respuesta:**

```python
texto = "Aprender python es fascinante"
contador_vocales = 0
vocales = "aeiouAEIOU"

for letra in texto:
    if letra in vocales:
        contador_vocales += 1

print("El texto tiene", contador_vocales, "vocales.")
```

### 2. Acumulador: Suma de números impares

**Consigna:** Utiliza un bucle `for` para sumar todos los números impares comprendidos entre 1 y 50. Utiliza una variable acumuladora para ir guardando el total.
**Respuesta:**

```python
suma_impares = 0

for numero in range(1, 51):
    if numero % 2 != 0:
        suma_impares += numero # Esto es equivalente a: suma_impares = suma_impares + numero

print("La suma de los números impares del 1 al 50 es:", suma_impares)
```

### 3. Búsqueda del Mayor (Algoritmo de máximo)

**Consigna:** Dada una lista de números `[15, 42, 8, 99, 23, 7]`, encuentra el número mayor iterando sobre la lista sin utilizar la función incorporada `max()`.
**Respuesta:**

```python
numeros = [15, 42, 8, 99, 23, 7]
numero_mayor = numeros[0] # Asumimos que el primero es el mayor para empezar

for num in numeros:
    if num > numero_mayor:
        numero_mayor = num

print("El número mayor es:", numero_mayor)
```

### 4. Acumulador y Contador: Promedio con Filtro

**Consigna:** Tienes una lista de calificaciones: `[55, 80, 92, 45, 70, 65]`. Calcula el promedio **solo** de las calificaciones que están aprobadas (es decir, que sean 60 o más). Necesitarás un acumulador para la suma de las notas y un contador para saber cuántas notas aprobadas hay.
**Respuesta:**

Python

```
calificaciones = [55, 80, 92, 45, 70, 65]
suma_aprobados = 0
cantidad_aprobados = 0

for nota in calificaciones:
    if nota >= 60:
        suma_aprobados += nota
        cantidad_aprobados += 1

if cantidad_aprobados > 0:
    promedio = suma_aprobados / cantidad_aprobados
    print("El promedio de los aprobados es:", promedio)
else:
    print("No hay calificaciones aprobadas.")
```

### 5. Variable de Estado (Bandera/Interruptor)

**Consigna:** Dada una lista de nombres de servidores `["web01", "db01", "app01", "proxy01"]`, verifica si el servidor `"app01"` está en la lista usando un bucle y una variable booleana como "bandera" (flag). Imprime un mensaje al final indicando si se encontró o no.
**Respuesta:**

Python

```python
servidores = ["web01", "db01", "app01", "proxy01"]
servidor_buscado = "app01"
encontrado = False # Nuestra variable bandera

for servidor in servidores:
    if servidor == servidor_buscado:
        encontrado = True
        break # Salimos del bucle anticipadamente porque ya lo encontramos

if encontrado:
    print("El servidor", servidor_buscado, "está en la lista.")
else:
    print("El servidor", servidor_buscado, "NO está en la lista.")
```

## **Programación Orientada a Objetos (POO)**

### 6. POO: Métodos que modifican estado

**Consigna:** Crea una clase `CuentaBancaria` que se inicialice con un `titular` y un `saldo` inicial (por defecto 0). Define dos métodos: `depositar(cantidad)` que sume al saldo, y `retirar(cantidad)` que reste al saldo (solo si hay fondos suficientes). Realiza un par de operaciones e imprime el saldo final.
**Respuesta:**

Python

```
class CuentaBancaria:
    def __init__(self, titular, saldo_inicial=0):
        self.titular = titular
        self.saldo = saldo_inicial

    def depositar(self, cantidad):
        if cantidad > 0:
            self.saldo += cantidad
            print(f"Depósito exitoso. Nuevo saldo: {self.saldo}")

    def retirar(self, cantidad):
        if 0 < cantidad <= self.saldo:
            self.saldo -= cantidad
            print(f"Retiro exitoso. Nuevo saldo: {self.saldo}")
        else:
            print("Fondos insuficientes o cantidad inválida.")

# Uso de la clase
mi_cuenta = CuentaBancaria("Laura", 100)
mi_cuenta.depositar(50)
mi_cuenta.retirar(30)
mi_cuenta.retirar(200) # Debería fallar
```

### 7. POO: Herencia Básica

**Consigna:** Define una clase padre llamada `Dispositivo` con los atributos `marca` y `modelo`, y un método `encender()`. Luego, crea una clase hija llamada `Telefono` que herede de `Dispositivo` y añada un atributo `numero` y un método `llamar()`. Crea una instancia de `Telefono` y prueba ambos métodos.
**Respuesta:**

Python

```python
class Dispositivo:
    def __init__(self, marca, modelo):
        self.marca = marca
        self.modelo = modelo

    def encender(self):
        print(f"El {self.marca} {self.modelo} se está encendiendo.")

class Telefono(Dispositivo):
    def __init__(self, marca, modelo, numero):
        # Usamos super() para inicializar los atributos de la clase padre
        super().__init__(marca, modelo)
        self.numero = numero

    def llamar(self):
        print(f"Llamando desde el número {self.numero}...")

# Uso de las clases
mi_telefono = Telefono("Samsung", "Galaxy S21", "555-1234")
mi_telefono.encender() # Método heredado
mi_telefono.llamar()   # Método propio
```

### 8. POO: Composición (Objetos dentro de objetos)

**Consigna:** Crea una clase `Jugador` que tenga un `nombre` y un `puntaje`. Luego crea una clase `Equipo` que tenga un `nombre_equipo` y una lista de jugadores (inicialmente vacía). La clase `Equipo` debe tener un método `agregar_jugador(jugador)` y otro método `mostrar_jugadores()` que imprima los nombres y puntajes de todos sus integrantes.
**Respuesta:**

Python

```python
class Jugador:
    def __init__(self, nombre, puntaje):
        self.nombre = nombre
        self.puntaje = puntaje

class Equipo:
    def __init__(self, nombre_equipo):
        self.nombre_equipo = nombre_equipo
        self.lista_jugadores = [] # Lista para almacenar objetos Jugador

    def agregar_jugador(self, jugador):
        self.lista_jugadores.append(jugador)

    def mostrar_jugadores(self):
        print(f"--- Equipo: {self.nombre_equipo} ---")
        for jug in self.lista_jugadores:
            print(f"Jugador: {jug.nombre} | Puntaje: {jug.puntaje}")

# Uso de las clases
jugador1 = Jugador("Marcos", 1500)
jugador2 = Jugador("Elena", 2300)

mi_equipo = Equipo("Los Dragones")
mi_equipo.agregar_jugador(jugador1)
mi_equipo.agregar_jugador(jugador2)

mi_equipo.mostrar_jugadores()
```

### 9. Suma de la Diagonal de una Matriz (Nivel Avanzado)

**Consigna:** Dada una matriz 3x3 representada como una lista de listas, calcula la suma de los elementos de su diagonal principal (es decir, los elementos donde el índice de la fila es igual al índice de la columna: `matriz[0][0]`, `matriz[1][1]`, etc.).
**Respuesta:**

Python

```python
matriz = [
    [5, 2, 8],
    [9, 4, 1],
    [3, 7, 6]
]

suma_diagonal = 0

for i in range(len(matriz)):
    # El índice de la fila (i) es igual al de la columna (i) en la diagonal principal
    suma_diagonal += matriz[i][i]

print("La suma de la diagonal principal es:", suma_diagonal)
```

### 10. Agrupación de Datos con Diccionarios (Nivel Avanzado)

**Consigna:** Tienes una lista de palabras: `["gato", "perro", "sol", "luna", "pez", "ave"]`. Crea un diccionario donde las claves sean las longitudes de las palabras (3, 4, 5) y los valores sean listas con las palabras que tienen esa longitud.
**Respuesta:**

Python

```python
palabras = ["gato", "perro", "sol", "luna", "pez", "ave"]
agrupacion = {}

for palabra in palabras:
    longitud = len(palabra)
    # Si la longitud no existe en el diccionario, creamos una lista vacía
    if longitud not in agrupacion:
        agrupacion[longitud] = []

    # Agregamos la palabra a la lista correspondiente
    agrupacion[longitud].append(palabra)

print("Palabras agrupadas por longitud:", agrupacion)
```

### 11. Búsqueda de Pares (Bucles Anidados) (Nivel Avanzado)

**Consigna:** Dada una lista de números `[2, 7, 11, 15]` y un objetivo `objetivo = 9`, encuentra los dos números en la lista que sumados den el objetivo. Utiliza dos bucles `for` anidados para comparar todas las combinaciones.
**Respuesta:**

Python

```python
numeros = [2, 7, 11, 15]
objetivo = 9
encontrado = False

for i in range(len(numeros)):
    for j in range(i + 1, len(numeros)):
        if numeros[i] + numeros[j] == objetivo:
            print("Los números que suman el objetivo son:", numeros[i], "y", numeros[j])
            encontrado = True
            break
    if encontrado:
        break
```

### 12. Ordenamiento Burbuja (Bubble Sort) (Nivel Desafío)

**Consigna:** Implementa el clásico algoritmo de "Ordenamiento Burbuja" para ordenar una lista de números `[64, 34, 25, 12, 22, 11, 90]` de menor a mayor. No puedes usar la función `.sort()`. Debes usar bucles anidados y comparar elementos adyacentes, intercambiándolos si el primero es mayor que el segundo.
**Respuesta:**

Python

```python
lista = [64, 34, 25, 12, 22, 11, 90]
n = len(lista)

for i in range(n):
    # La variable 'intercambio' actúa como bandera para optimizar el algoritmo
    intercambio = False

    # El último elemento i ya estará en su lugar correcto, no necesitamos revisarlo
    for j in range(0, n - i - 1):
        # Si el elemento actual es mayor que el siguiente, se intercambian
        if lista[j] > lista[j + 1]:
            lista[j], lista[j + 1] = lista[j + 1], lista[j]
            intercambio = True

    # Si no hubo intercambios en esta pasada, la lista ya está ordenada
    if not intercambio:
        break

print("Lista ordenada:", lista)
```

## Relacionado

- [[2026-06-24 - Python y Linux - Repaso]]
- [[Tarea - Python POO]]
