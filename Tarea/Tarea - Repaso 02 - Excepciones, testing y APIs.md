---
tipo: tarea
modulo: 3
estado: pendiente
tags: [python, excepciones, testing, apis]
---

# Tarea — Excepciones, testing y APIs

## Resumen

- 13 ejercicios de repaso sobre lo visto entre el 29 de junio y el 7 de julio: excepciones, `unittest` y `requests`.
- Primero van todas las consignas y después todas las soluciones, así podés intentarlos sin espiar.
- El último es un integrador que junta los tres temas.

## Parte 1: Las consignas

### Excepciones y validación

- **Ejercicio 1:** Escribí una función `calcular_promedio(notas)` que devuelva el promedio de una lista de números. Si la lista viene vacía, tiene que lanzar un `ValueError` con un mensaje claro. Pensá por qué acá corresponde lanzar y no devolver `None`.
- **Ejercicio 2:** Escribí una función `dividir(a, b)` que devuelva `a / b`, pero que atrape el `ZeroDivisionError` con `try`/`except`, avise por pantalla y devuelva `None`. Acá sí corresponde devolver en vez de lanzar: ¿por qué?
- **Ejercicio 3:** Escribí `validar_edad(edad)` que lance `TypeError` si no recibe un entero, `ValueError` si la edad es negativa o mayor que 120, y devuelva `True` si pasa todo. Poné las validaciones al principio y salí pronto, sin anidar condicionales.
- **Ejercicio 4:** Dada la lista `["10", "20", "treinta", "40"]`, convertí a entero lo que se pueda. Los que se convierten van a una lista `validos` y los que fallan a otra `fallidos`. Ojo dónde ponés el `try`: si envuelve todo el bucle, el primer fallo te corta el resto.

### Testing con unittest

- **Ejercicio 5:** Escribí la clase de tests para el `calcular_promedio` del ejercicio 1. Necesitás un test del caso feliz con `assertEqual` y otro para la lista vacía usando `assertRaises(ValueError)`.
- **Ejercicio 6:** Escribí `contar_palabras(frase)` y sus tests. Además del caso normal, cubrí los casos borde: cadena vacía, una sola palabra, y espacios de más al principio, al final y entre palabras.
- **Ejercicio 7:** Escribí `normalizar_nombre(nombre)` que tome `"  ana PÉREZ "` y devuelva `"Ana Pérez"`. Testeá espacios sobrantes, mayúsculas mezcladas, un nombre que ya venía bien y una cadena de solo espacios.
- **Ejercicio 8:** Te dan esta función, que tiene un bug:

  ```python
  def es_par(n):
      return n % 2 == 1
  ```

  Escribí primero los tests que deberían pasar según el nombre de la función, corrélos para verlos fallar, y recién entonces arreglá la función. Es el ciclo de test-primero en chiquito.

### APIs con requests

- **Ejercicio 9:** Hacé un `GET` a `https://pokeapi.co/api/v2/pokemon/ditto`, convertí la respuesta con `.json()` e imprimí el nombre y el peso del pokémon.
- **Ejercicio 10:** Repetí la petición pero con un pokémon que no existe (`ditto333`). Comprobá `response.status_code` con un `if` e imprimí un mensaje de error si no es 200. Fijate que `requests` no lanza ninguna excepción sola: si no comprobás, seguís de largo con datos que no existen.
- **Ejercicio 11:** La misma petición fallida, ahora con `response.raise_for_status()` dentro de un `try`, capturando `requests.exceptions.HTTPError`. Este es el nivel 2 de manejo de errores: el 404 se convierte en excepción y ya no te lo podés olvidar de mirar.
- **Ejercicio 12:** Tres pruebas contra httpbin, que devuelve lo que le mandás:
  1. Un `POST` a `https://httpbin.org/post` enviando un diccionario con `json=`, e imprimí lo que el servidor dice haber recibido.
  2. Un `GET` a `https://httpbin.org/delay/10` con `timeout=5`, capturando `requests.exceptions.Timeout`.
  3. Un `GET` a `https://httpbin.org/headers` mandando una cabecera `Authorization: Bearer <token>`, e imprimí la cabecera tal como llegó.
- **Ejercicio 13 (desafío, integrador):** Escribí `obtener_pokemon(nombre)` que:
  - lance `TypeError` si el nombre no es un string y `ValueError` si viene vacío o son solo espacios;
  - haga el `GET` con `timeout` y `raise_for_status()`;
  - devuelva un diccionario con `nombre`, `peso` y `tipos` si todo salió bien, y `None` si la API responde 404;

  y sus tests con `assertRaises` para las tres validaciones. Fijate que esos tests no tocan la red, porque la excepción salta antes del `requests.get`.

## Parte 2: Las soluciones

### Soluciones: Excepciones y validación

```python
# Ejercicio 1: lanzar en vez de devolver
# La lista vacía no es "un promedio inválido": es una llamada que no tiene
# sentido, así que se lanza en vez de devolver None.
def calcular_promedio(notas):
    if len(notas) == 0:
        raise ValueError("la lista de notas no puede estar vacía")
    return sum(notas) / len(notas)

print(calcular_promedio([7, 8, 10]))

try:
    calcular_promedio([])
except ValueError as err:
    print("Error controlado:", err)


# Ejercicio 2: atrapar en vez de lanzar
# Acá sí devolvemos None, porque quien llama puede seguir trabajando sin eso.
def dividir(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("No se puede dividir por cero.")
        return None

print(dividir(10, 2))
print(dividir(10, 0))


# Ejercicio 3: validar primero y salir pronto
# Todas las validaciones arriba, sin anidar. El cuerpo real queda al final.
def validar_edad(edad):
    if not isinstance(edad, int):
        raise TypeError("la edad tiene que ser un número entero")
    if edad < 0:
        raise ValueError("la edad no puede ser negativa")
    if edad > 120:
        raise ValueError("la edad no puede ser mayor que 120")
    return True

print(validar_edad(35))

for caso in ["treinta", -5, 200]:
    try:
        validar_edad(caso)
    except (TypeError, ValueError) as err:
        print(f"{caso!r} ->", err)


# Ejercicio 4: el try dentro del bucle
# Si el try envolviera todo el for, el primer fallo cortaría el resto.
crudos = ["10", "20", "treinta", "40"]
validos = []
fallidos = []

for dato in crudos:
    try:
        validos.append(int(dato))
    except ValueError:
        fallidos.append(dato)

print("Convertidos:", validos)
print("No se pudieron convertir:", fallidos)
```

### Soluciones: Testing con unittest

```python
#!/usr/bin/env python3

import unittest


# --- Las funciones que vamos a testear ---

def calcular_promedio(notas):
    if len(notas) == 0:
        raise ValueError("la lista de notas no puede estar vacía")
    return sum(notas) / len(notas)


# Ejercicio 6: .split() sin argumentos ya colapsa los espacios de más
# y devuelve [] con la cadena vacía. Los tests lo confirman.
def contar_palabras(frase):
    return len(frase.split())


# Ejercicio 7: .split() + .capitalize() en cada palabra, y .join() para rearmar
def normalizar_nombre(nombre):
    palabras = nombre.split()
    return " ".join(palabra.capitalize() for palabra in palabras)


# Ejercicio 8: la versión ya corregida. El bug era `n % 2 == 1`,
# que devuelve lo contrario de lo que promete el nombre.
def es_par(n):
    return n % 2 == 0


# --- Los tests ---

class TestCalcularPromedio(unittest.TestCase):

    def test_basico(self):
        # Elegimos números que dan un promedio exacto: comparar floats con
        # decimales infinitos con assertEqual trae problemas de redondeo.
        self.assertEqual(calcular_promedio([6, 8, 10]), 8.0)

    def test_un_solo_elemento(self):
        self.assertEqual(calcular_promedio([5]), 5)

    def test_lista_vacia(self):
        # assertRaises comprueba que la excepción se lanza. Si no se lanza,
        # el test falla igual que si el valor devuelto fuera incorrecto.
        with self.assertRaises(ValueError):
            calcular_promedio([])


class TestContarPalabras(unittest.TestCase):

    def test_basico(self):
        self.assertEqual(contar_palabras("hola mundo cruel"), 3)

    def test_vacia(self):
        self.assertEqual(contar_palabras(""), 0)

    def test_una_palabra(self):
        self.assertEqual(contar_palabras("hola"), 1)

    def test_espacios_de_mas(self):
        self.assertEqual(contar_palabras("  hola    mundo  "), 2)


class TestNormalizarNombre(unittest.TestCase):

    def test_basico(self):
        self.assertEqual(normalizar_nombre("  ana PÉREZ "), "Ana Pérez")

    def test_ya_normalizado(self):
        self.assertEqual(normalizar_nombre("Ana Pérez"), "Ana Pérez")

    def test_todo_mayusculas(self):
        self.assertEqual(normalizar_nombre("JUAN CARLOS GÓMEZ"), "Juan Carlos Gómez")

    def test_vacio(self):
        self.assertEqual(normalizar_nombre("   "), "")


class TestEsPar(unittest.TestCase):

    # Estos cuatro fallan con la versión buggeada y pasan con la corregida.
    def test_par(self):
        self.assertEqual(es_par(4), True)

    def test_impar(self):
        self.assertEqual(es_par(7), False)

    def test_cero(self):
        self.assertEqual(es_par(0), True)

    def test_negativo_par(self):
        self.assertEqual(es_par(-2), True)


unittest.main()
```

### Soluciones: APIs con requests

```python
#!/usr/bin/env python3

import requests

# Ejercicio 9: GET y lectura del JSON
# .json() convierte la respuesta en un diccionario de Python. .text te daría
# el mismo contenido pero como string, y habría que parsearlo a mano.
url = "https://pokeapi.co/api/v2/pokemon/ditto"
response = requests.get(url, timeout=5)

datos = response.json()
print("Nombre:", datos["name"])
print("Peso:", datos["weight"])


# Ejercicio 10: nivel 1 de manejo de errores, el if
# requests NO lanza excepción con un 404: te devuelve la respuesta igual.
# Si no comprobás el código, seguís trabajando con datos que no existen.
response = requests.get("https://pokeapi.co/api/v2/pokemon/ditto333", timeout=5)

if response.status_code != 200:
    print(f"Hubo un problema con el request. Código: {response.status_code}")
else:
    print(response.json()["name"])


# Ejercicio 11: nivel 2, raise_for_status() dentro de try
# raise_for_status() convierte el 404 en una excepción, así el error deja de
# ser algo que te podés olvidar de mirar.
try:
    response = requests.get("https://pokeapi.co/api/v2/pokemon/ditto333", timeout=5)
    response.raise_for_status()
    print(response.json()["name"])
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")


# Ejercicio 12a: POST con json=
# El parámetro json= serializa el diccionario y pone el Content-Type solo.
data = {"nombre": "Ada", "mensaje": "Hola!"}
response = requests.post("https://httpbin.org/post", json=data, timeout=5)
print("Lo que recibió el servidor:", response.json()["json"])


# Ejercicio 12b: nivel 3, el timeout
# /delay/10 tarda 10 segundos a propósito. Sin timeout el script se cuelga
# esperando; con timeout=5 corta a los 5 y lo tratamos como cualquier error.
try:
    response = requests.get("https://httpbin.org/delay/10", timeout=5)
    print(response.status_code)
except requests.exceptions.Timeout:
    print("El servidor tardó demasiado en responder.")


# Ejercicio 12c: cabecera de autenticación
# El token va en el header, nunca en la URL: las URLs quedan en los logs.
auth_token = "XXXXXXXX"
headers = {"Authorization": f"Bearer {auth_token}"}

response = requests.get("https://httpbin.org/headers", headers=headers, timeout=5)
print("Cabecera que llegó:", response.json()["headers"]["Authorization"])
```

### Solución: Ejercicio 13 (desafío)

```python
#!/usr/bin/env python3

import unittest

import requests


def obtener_pokemon(nombre):
    # Validación primero: si el nombre viene vacío no hay nada que pedir,
    # y armar la URL igual sería pegarle a la API para nada.
    if not isinstance(nombre, str):
        raise TypeError("el nombre tiene que ser un string")
    if nombre.strip() == "":
        raise ValueError("el nombre no puede estar vacío")

    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.strip().lower()}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        # 404 = ese pokémon no existe. Eso no es un error del programa,
        # así que devolvemos None en vez de dejar que reviente.
        return None
    except requests.exceptions.Timeout:
        print("La API tardó demasiado en responder.")
        return None

    datos = response.json()
    return {
        "nombre": datos["name"],
        "peso": datos["weight"],
        "tipos": [t["type"]["name"] for t in datos["types"]],
    }


class TestObtenerPokemon(unittest.TestCase):

    # Estos tres no tocan la red: la excepción salta antes del requests.get.
    # Por eso se pueden correr sin internet y son instantáneos.
    def test_nombre_vacio(self):
        with self.assertRaises(ValueError):
            obtener_pokemon("")

    def test_nombre_solo_espacios(self):
        with self.assertRaises(ValueError):
            obtener_pokemon("   ")

    def test_nombre_no_es_string(self):
        with self.assertRaises(TypeError):
            obtener_pokemon(42)


if __name__ == "__main__":
    print(obtener_pokemon("ditto"))
    print(obtener_pokemon("noexiste123"))
    unittest.main()
```

## Relacionado

- [[Tarea]]
- [[2026-06-29 - Testing con unittest]]
- [[2026-06-30 - Excepciones - raise y validación]]
- [[2026-07-07 - Python Requests - Consumo de APIs]]
