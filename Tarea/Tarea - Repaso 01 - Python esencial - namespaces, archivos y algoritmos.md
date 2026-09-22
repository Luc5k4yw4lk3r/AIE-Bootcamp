---
tipo: tarea
modulo: 2
estado: pendiente
tags: [python, archivos, csv, algoritmos, excepciones]
---

# Tarea — Python esencial: namespaces, archivos y algoritmos

## Resumen

- 24 ejercicios cortos (5 a 15 min cada uno) sobre lo que más se usa sin darse cuenta: dónde vive cada nombre, cómo se leen y escriben archivos, algoritmos de base, datos anidados y cómo leer un error.
- Muchos son de **"predecí antes de correr"**: primero escribís qué creés que va a pasar, después lo corrés. La diferencia entre lo que predijiste y lo que pasó es exactamente lo que te falta entender.
- Hacelos **sin agente**. Si te trabás más de 10 minutos, mirá el material del bloque antes de mirar la solución.
- Primero van todas las consignas y después todas las soluciones, así podés intentarlos sin espiar.

## Material para hacer los ejercicios

Antes de cada bloque, mirá lo que le corresponde. No hace falta verlo entero: al lado de cada link dice qué parte sirve.

**Para todos los bloques**

- [Python Tutor](https://pythontutor.com/) — pegás el código y lo ejecutás paso a paso viendo cada variable y cada función como cajas. Es la mejor herramienta para los bloques 1 y 4: vas a *ver* los namespaces.
- [Curso de PYTHON desde CERO (Completo) — Soy Dalto](https://www.youtube.com/watch?v=nKPbfIU442g) — el curso base del bootcamp; usá el índice del vídeo para saltar a funciones, archivos o diccionarios según el bloque.

**Bloque 1 — Funciones, namespaces y scope**

- [El alcance (Scope) de las variables: global, nonlocal y funciones anidadas — cctmexico](https://www.youtube.com/watch?v=pecwfhc8pu8) — en castellano, cubre justo `global` y `nonlocal`.
- [Alcance de variables — El Libro de Python](https://ellibrodepython.com/alcance-variables-python) — lectura corta en castellano con los mismos ejemplos que vas a ver acá.
- [Python Scope and the LEGB Rule — Real Python](https://realpython.com/python-scope-legb-rule/) — en inglés, la explicación más completa de la regla LEGB; leé hasta "Modifying the Behavior of a Python Scope".
- [Ámbitos y espacios de nombres — tutorial oficial de Python](https://docs.python.org/es/3/tutorial/classes.html#python-scopes-and-namespaces) — la definición oficial, en castellano. Solo la sección 9.2.
- [Módulos en Python — El Libro de Python](https://ellibrodepython.com/modulos-python) — `import`, `from ... import` y `__name__`, para el ejercicio 6.

**Bloque 2 — Archivos**

- [Cómo abrir, leer y escribir archivos — Programa Con Arnau](https://www.youtube.com/watch?v=yPwbJ6zFfA0) — en castellano, los modos `r`, `w` y `a`.
- [Leer archivos](https://ellibrodepython.com/leer-archivos-python) y [Escribir archivos — El Libro de Python](https://ellibrodepython.com/escribir-archivos-python) — dos lecturas cortas con `with open`.
- [Lectura y escritura de archivos — tutorial oficial de Python](https://docs.python.org/es/3/tutorial/inputoutput.html#reading-and-writing-files) — incluye `json.dump` y `json.load` (sección 7.2.2).
- [`csv` — documentación oficial](https://docs.python.org/es/3/library/csv.html) — mirá los ejemplos de `DictReader` y `DictWriter`.
- [`pathlib` — documentación oficial](https://docs.python.org/es/3/library/pathlib.html) — solo la tabla de uso básico, para el ejercicio 9.
- Los apuntes de clase: [[2026-06-16 - Revisión Python - Archivos y módulo os]] y [[2026-06-18 - Revisión Python - Archivos CSV]].

**Bloque 3 — Algoritmos básicos**

- [Curso COMPLETO de LÓGICA DE PROGRAMACIÓN desde cero — MoureDev](https://www.youtube.com/watch?v=TdITcVD64zI) — contadores, acumuladores y cómo pensar el problema antes de escribirlo.
- [Tutorial: Algoritmo Búsqueda Binaria (Python) — La Carpeta Raíz](https://www.youtube.com/watch?v=8B4FH1BtaiA) — en castellano, para el ejercicio 16.
- [Búsqueda binaria — Picuino](https://www.picuino.com/es/python-busqueda-binaria.html) — la misma idea por escrito.
- [Cómo ordenar — documentación oficial](https://docs.python.org/es/3/howto/sorting.html) — `sorted` con `key` y `reverse`, para el ejercicio 17.
- Repaso previo: [[Tarea - Algoritmos]].

**Bloque 4 — Datos anidados y referencias**

- [Mutabilidad en Python — El Libro de Python](https://ellibrodepython.com/mutabilidad-python) — por qué `b = a` no copia una lista.
- [`copy` — documentación oficial](https://docs.python.org/es/3/library/copy.html) — la diferencia entre copia superficial y profunda, en dos párrafos.
- [Estructuras de datos — tutorial oficial de Python](https://docs.python.org/es/3/tutorial/datastructures.html) — listas y diccionarios, por si hace falta repasar.

**Bloque 5 — Leer errores**

- [Errores y excepciones — tutorial oficial de Python](https://docs.python.org/es/3/tutorial/errors.html) — cómo se lee un traceback y cómo se atrapan excepciones.
- [Excepciones: try, except, finally — El Libro de Python](https://ellibrodepython.com/excepciones-try-except-finally) — la misma idea con más ejemplos.

## Parte 1: Las consignas

### Bloque 1 — Funciones, namespaces y scope

Un *namespace* es un diccionario que asocia nombres con objetos. Cuando escribís `x`, Python lo busca en este orden: **L**ocal (la función actual) → **E**nclosing (la función que la contiene) → **G**lobal (el archivo) → **B**uilt-in (`print`, `len`, `list`…). Es la regla **LEGB**.

- **Ejercicio 1 (predecí):** ¿Qué imprime? Escribilo antes de correrlo.

  ```python
  x = "global"

  def mostrar():
      x = "local"
      print("dentro:", x)

  mostrar()
  print("fuera:", x)
  ```

- **Ejercicio 2 (predecí y arreglá):** Esto da error. Predecí **cuál** error y en **qué línea**, y después arreglalo de dos formas: con `global`, y sin `global`, pasando el valor por parámetro y devolviéndolo. ¿Cuál de las dos preferirías en un proyecto real, y por qué?

  ```python
  contador = 0

  def sumar_uno():
      contador = contador + 1
      return contador

  sumar_uno()
  ```

- **Ejercicio 3 (predecí):** ¿Qué imprime? Después borrá la línea `nonlocal total` y predecí qué pasa.

  ```python
  def crear_contador():
      total = 0
      def incrementar():
          nonlocal total
          total += 1
          return total
      return incrementar

  contar = crear_contador()
  contar()
  contar()
  print(contar())

  otro = crear_contador()
  print(otro())
  ```

- **Ejercicio 4 (pisar un builtin):** ¿Qué pasa en la segunda línea? Explicá el error usando la regla LEGB y arreglalo.

  ```python
  list = [3, 1, 2]
  letras = list("abc")
  ```

- **Ejercicio 5 (el argumento por defecto mutable):** Predecí las tres salidas. Después arreglá la función para que cada llamada sin lista arranque con una lista vacía nueva.

  ```python
  def agregar(item, lista=[]):
      lista.append(item)
      return lista

  print(agregar("a"))
  print(agregar("b"))
  print(agregar("c", []))
  ```

- **Ejercicio 6 (módulos y `__name__`):** Creá dos archivos en la misma carpeta:

  ```python
  # utilidades.py
  print("cargando utilidades")

  def saludar(nombre):
      return f"Hola, {nombre}"

  if __name__ == "__main__":
      print(saludar("desde utilidades"))
  ```

  ```python
  # principal.py
  import utilidades
  from utilidades import saludar

  print(utilidades.saludar("Ana"))
  print(saludar("Luis"))
  print(__name__)
  ```

  Predecí qué imprime `python utilidades.py` y qué imprime `python principal.py`. Dos preguntas: ¿cuántas veces aparece `cargando utilidades` si el módulo se importa dos veces? ¿Qué nombre queda definido en el namespace de `principal.py` con cada forma de `import`?

### Bloque 2 — Archivos

- **Ejercicio 7 (modos `w` y `a`):** Escribí un script que:
  1. cree `notas.txt` con tres líneas usando el modo `"w"`;
  2. le agregue una cuarta línea usando el modo `"a"`;
  3. lo lea e imprima cada línea numerada (`1: ...`).

  Corrélo **dos veces**. ¿Cuántas líneas tiene el archivo después de la segunda corrida? ¿Por qué no son ocho?

- **Ejercicio 8 (filtrar un log):** Guardá esto como `app.log`:

  ```text
  2026-09-01 10:00:01 INFO Servidor iniciado
  2026-09-01 10:00:05 INFO Usuario ana conectado
  2026-09-01 10:01:12 WARNING Respuesta lenta de la API (3.2s)
  2026-09-01 10:02:40 ERROR No se pudo conectar a la base de datos
  2026-09-01 10:02:41 INFO Reintentando conexión
  2026-09-01 10:02:45 ERROR Timeout al consultar la API de ofertas
  2026-09-01 10:03:00 INFO Usuario luis conectado
  ```

  Contá cuántas líneas hay de cada nivel (`INFO`, `WARNING`, `ERROR`) usando un diccionario, e imprimí el resultado. Después escribí solo las líneas de `ERROR` en `errores.txt`.

- **Ejercicio 9 (rutas relativas):** Armá esta estructura:

  ```text
  practica/
  └── scripts/
      ├── leer.py
      └── datos.txt
  ```

  `leer.py` hace `open("datos.txt")`. Corrélo desde `practica/scripts/` (funciona) y después desde `practica/`, con `python scripts/leer.py` (falla). Explicá por qué. Después arreglalo con `pathlib` para que funcione desde cualquier carpeta. Pista: `Path(__file__).parent`.

- **Ejercicio 10 (`FileNotFoundError` bien manejado):** Escribí `leer_config(ruta)`. Si el archivo existe, devuelve un diccionario con sus líneas `clave=valor`. Si no existe, avisa por pantalla y devuelve una configuración por defecto (`{"idioma": "es", "modo": "normal"}`). Solo tenés que atrapar `FileNotFoundError`, no cualquier excepción: ¿por qué un `except:` pelado sería peor acá?

- **Ejercicio 11 (JSON):** Guardá este diccionario en `perfil.json`, con sangría y con los acentos legibles (no `á`). Después volvé a leerlo, agregá `"nivel": 2` y guardalo de nuevo. Abrí el archivo con el editor y comprobá cómo quedó.

  ```python
  perfil = {"nombre": "Lucía", "ciudad": "Málaga", "cursos": ["Python", "n8n"]}
  ```

- **Ejercicio 12 (CSV con `DictReader` y `DictWriter`):** Guardá esto como `alumnos.csv`:

  ```text
  nombre,nota1,nota2,nota3
  Ana,7,8,9
  Luis,5,6,4
  Marta,9,9,10
  Pablo,6,5,7
  ```

  Leelo con `csv.DictReader`, calculá el promedio de cada alumno y escribí `promedios.csv` con las columnas `nombre,promedio,aprobado` (se aprueba con 6 o más). Ojo: `DictReader` te da todo como texto.

### Bloque 3 — Algoritmos básicos

- **Ejercicio 13 (máximo y promedio a mano):** Escribí `maximo(numeros)` y `promedio(numeros)` **sin** usar `max`, `sum` ni `sorted`. Las dos tienen que lanzar `ValueError` si la lista viene vacía. Probalas con `[4, -2, 17, 8]` y con `[-5, -1, -9]`. La segunda lista existe para romper una solución tentadora: ¿cuál?
- **Ejercicio 14 (frecuencias):** Dada la frase `"el perro y el gato y el loro"`, contá cuántas veces aparece cada palabra usando un diccionario (sin `Counter`), e imprimí las 3 más frecuentes de mayor a menor.
- **Ejercicio 15 (quitar duplicados sin perder el orden):** Escribí `sin_duplicados(items)`. Para `["python", "n8n", "python", "git", "n8n", "sql"]` tiene que devolver `["python", "n8n", "git", "sql"]`. Hacé una versión con una lista auxiliar y otra con un `set` de vistos. ¿Por qué `list(set(items))` no sirve acá?
- **Ejercicio 16 (búsqueda lineal vs. binaria):** Sobre `numeros = list(range(1, 1_000_001))`, escribí `busqueda_lineal` y `busqueda_binaria`. Cada una devuelve una tupla `(posición, comparaciones)`. Antes de correrlas, predecí cuántas comparaciones hace cada una para encontrar `765_432`. ¿Qué condición tiene que cumplir la lista para que la binaria funcione?
- **Ejercicio 17 (ordenar):** Con esta lista:

  ```python
  ofertas = [
      {"puesto": "Data Analyst", "salario": 32000},
      {"puesto": "AI Engineer", "salario": 45000},
      {"puesto": "Backend Dev", "salario": 38000},
      {"puesto": "ML Engineer", "salario": 45000},
  ]
  ```

  1. Ordenala por salario de mayor a menor y, si hay empate, por puesto alfabéticamente, usando `sorted` con `key`.
  2. Escribí un bubble sort a mano que ordene `[5, 2, 9, 1, 7]` y cuente cuántos intercambios hizo.

### Bloque 4 — Datos anidados y referencias

Todo lo que pasa entre nodos en n8n es exactamente esto: diccionarios con listas adentro y más diccionarios dentro de las listas. Si podés navegar esto en Python, podés leer `$json` en n8n.

Para los ejercicios 18 y 19, usá esta respuesta, que simula una API de ofertas de trabajo:

```python
respuesta = {
    "total": 3,
    "resultados": [
        {"titulo": "AI Engineer", "empresa": {"nombre": "Acme", "ciudad": "Madrid"},
         "salario": {"min": 40000, "max": 50000}, "etiquetas": ["python", "llm"]},
        {"titulo": "Data Analyst", "empresa": {"nombre": "Datos SL", "ciudad": "Valencia"},
         "salario": None, "etiquetas": []},
        {"titulo": "Backend Dev", "empresa": {"nombre": "WebCo"},
         "salario": {"min": 35000, "max": 42000}, "etiquetas": ["fastapi"]},
    ],
}
```

- **Ejercicio 18 (navegar):** Imprimí, para cada oferta, `titulo — empresa (ciudad)`. Antes de escribir código, escribí en una línea la "ruta" hasta la ciudad de la primera oferta, por ejemplo `respuesta → "resultados" → [0] → ...`. ¿Qué pasa con la tercera oferta?
- **Ejercicio 19 (`.get()` vs `[]`):** Imprimí la primera etiqueta y el salario mínimo de cada oferta sin que el programa se rompa. Cuando falte el dato, mostrá `"sin dato"`. Hay tres trampas: una ciudad que falta, un salario que es `None` y una lista de etiquetas vacía. Cada una necesita una protección distinta.
- **Ejercicio 20 (predecí — alias):** ¿Qué imprime? Después cambiá **una** línea para que `a` no se modifique.

  ```python
  a = [1, 2, 3]
  b = a
  b.append(4)
  print(a)
  print(a is b)
  ```

- **Ejercicio 21 (predecí — copia superficial vs. profunda):** ¿Qué imprime cada `print`?

  ```python
  import copy

  original = {"nombre": "Ana", "cursos": ["python"]}
  superficial = copy.copy(original)
  profunda = copy.deepcopy(original)

  superficial["nombre"] = "Eva"
  superficial["cursos"].append("n8n")
  profunda["cursos"].append("git")

  print(original)
  print(superficial)
  print(profunda)
  ```

### Bloque 5 — Leer errores

Un traceback se lee **de abajo hacia arriba**. La última línea dice *qué* pasó (tipo y mensaje). La línea de arriba dice *dónde* pasó. Las de más arriba cuentan *cómo se llegó* hasta ahí.

- **Ejercicio 22 (leer sin correr):** Para cada traceback, contestá sin ejecutar nada: 1) ¿qué tipo de error es?, 2) ¿en qué archivo y línea salta?, 3) ¿cuál es la causa más probable?, 4) ¿qué cambio mínimo probarías primero?

  **A.**

  ```text
  Traceback (most recent call last):
    File "ofertas.py", line 12, in <module>
      imprimir_resumen(datos)
    File "ofertas.py", line 7, in imprimir_resumen
      print(oferta["empresa"]["ciudad"])
            ~~~~~~~~~~~~~~~~~^^^^^^^^^^
  KeyError: 'ciudad'
  ```

  **B.**

  ```text
  Traceback (most recent call last):
    File "informe.py", line 4, in <module>
      print("Total de ofertas: " + total)
            ~~~~~~~~~~~~~~~~~~~~~^~~~~~~
  TypeError: can only concatenate str (not "int") to str
  ```

  **C.**

  ```text
  Traceback (most recent call last):
    File "limpiar.py", line 9, in <module>
      print(texto.upper())
            ^^^^^^^^^^^
  AttributeError: 'NoneType' object has no attribute 'upper'
  ```

  Y este es el código de C:

  ```python
  def limpiar(texto):
      texto = texto.strip()

  texto = limpiar("  hola  ")
  print(texto.upper())
  ```

- **Ejercicio 23 (pedir ayuda bien):** Elegí uno de los tres errores y escribí la consulta que le harías a un compañero o a un agente, en **tres líneas**:
  1. **Esperaba:** …
  2. **Pasó:** … (el error exacto y la línea)
  3. **Ya probé:** …

  Compará con lo que habrías escrito sin esta plantilla. ¿Qué información le ahorra al otro?

### Integrador

- **Ejercicio 24 (desafío):** Guardá esto como `ofertas.json`:

  ```json
  [
    {"id": 1, "titulo": "AI Engineer Junior", "empresa": "Acme", "salario": 32000, "descripcion": "Python, LLMs y RAG"},
    {"id": 2, "titulo": "Data Analyst", "empresa": "Datos SL", "salario": 28000, "descripcion": "SQL y Python"},
    {"id": 3, "titulo": "AI Engineer Junior", "empresa": "Acme", "salario": 32000, "descripcion": "Python, LLMs y RAG"},
    {"id": 4, "titulo": "Automation Specialist", "empresa": "FlowCo", "descripcion": "n8n y APIs"},
    {"id": 5, "titulo": "Backend Python", "empresa": "WebCo", "salario": 38000, "descripcion": "FastAPI y Python"},
    {"id": 6, "titulo": "Prompt Engineer", "empresa": "Acme", "salario": 41000, "descripcion": "LLMs y evaluación"}
  ]
  ```

  Escribí `seleccionar_ofertas.py` que:
  1. lea el archivo y, si no existe, avise y termine sin traceback;
  2. se quede con las ofertas cuya `descripcion` contenga una palabra clave (sin distinguir mayúsculas) y cuyo `salario` sea mayor o igual a un mínimo. Las que no tienen salario quedan afuera, sin romper el programa;
  3. quite los duplicados, que son ofertas con el mismo `titulo` y la misma `empresa`, quedándose con la primera;
  4. las ordene por salario de mayor a menor;
  5. escriba `seleccion.csv` con `titulo,empresa,salario`.

  Probalo con la palabra `python` y un mínimo de `30000`, y después con `llm` y `40000`. Antes de correrlo, anotá qué filas esperás en cada caso.

## Parte 2: Las soluciones

### Soluciones: Bloque 1

```python
# Ejercicio 1
# Salida:
# dentro: local
# fuera: global
# Asignar x dentro de la función crea un nombre NUEVO en el namespace local.
# No toca la x global: son dos variables distintas con el mismo nombre.
```

```python
# Ejercicio 2
# Error: UnboundLocalError en la línea `contador = contador + 1`.
# Como la función ASIGNA contador, Python decide (al compilarla) que contador es local.
# Cuando quiere leerla para sumarle 1, la local todavía no tiene valor.
# El texto del mensaje cambia con la versión: "local variable 'contador' referenced before
# assignment" (hasta 3.10) o "cannot access local variable 'contador'..." (3.11 en adelante).

# Forma 1: con global (funciona, pero cualquier función puede cambiar el estado sin avisar)
contador = 0

def sumar_uno():
    global contador
    contador = contador + 1
    return contador

sumar_uno()
print(contador)  # 1

# Forma 2: por parámetro y retorno (preferible: la función no depende de nada oculto
# y se puede testear sola)
def sumar_uno_puro(valor):
    return valor + 1

contador = sumar_uno_puro(contador)
print(contador)  # 2
```

```python
# Ejercicio 3
# Salida:
# 3
# 1
# Cada llamada a crear_contador() crea un namespace nuevo con su propio total.
# incrementar lo recuerda (es un "closure"). otro tiene un total distinto.
# Sin `nonlocal total`: UnboundLocalError, por el mismo motivo que el ejercicio 2,
# pero con el scope Enclosing en lugar del Global.
```

```python
# Ejercicio 4
# TypeError: 'list' object is not callable
# Al asignar `list = [3, 1, 2]`, el nombre list del namespace global tapa al builtin list.
# LEGB encuentra primero la G y nunca llega a la B.
numeros = [3, 1, 2]      # usá un nombre que no sea un builtin
letras = list("abc")
print(letras)            # ['a', 'b', 'c']
# Si ya lo pisaste en una sesión interactiva: `del list` borra el global y vuelve a aparecer el builtin.
```

```python
# Ejercicio 5
# Salida original:
# ['a']
# ['a', 'b']   <- ¡sorpresa! la lista por defecto se crea UNA sola vez, al definir la función
# ['c']
def agregar(item, lista=None):
    if lista is None:
        lista = []
    lista.append(item)
    return lista

print(agregar("a"))  # ['a']
print(agregar("b"))  # ['b']
```

```text
Ejercicio 6

$ python utilidades.py
cargando utilidades
Hola, desde utilidades

$ python principal.py
cargando utilidades
Hola, Ana
Hola, Luis
__main__

- "cargando utilidades" aparece UNA sola vez: Python ejecuta el módulo la primera vez que se importa y
  después lo reutiliza.
- Al importar, __name__ vale "utilidades" (no "__main__"), así que el bloque del if no se ejecuta.
- `import utilidades` agrega al namespace de principal.py el nombre `utilidades` (y se usa
  utilidades.saludar). `from utilidades import saludar` agrega directamente el nombre `saludar`.
```

### Soluciones: Bloque 2

```python
# Ejercicio 7
with open("notas.txt", "w", encoding="utf-8") as f:
    f.write("Primera\nSegunda\nTercera\n")

with open("notas.txt", "a", encoding="utf-8") as f:
    f.write("Cuarta\n")

with open("notas.txt", encoding="utf-8") as f:
    for numero, linea in enumerate(f, start=1):
        print(f"{numero}: {linea.rstrip()}")

# Después de dos corridas tiene 4 líneas, no 8: el modo "w" vacía el archivo
# cada vez, y recién después "a" agrega la cuarta.
```

```python
# Ejercicio 8
conteo = {}
errores = []

with open("app.log", encoding="utf-8") as f:
    for linea in f:
        partes = linea.split()
        if len(partes) < 3:
            continue            # salteamos líneas vacías o mal formadas
        nivel = partes[2]
        conteo[nivel] = conteo.get(nivel, 0) + 1
        if nivel == "ERROR":
            errores.append(linea)

print(conteo)  # {'INFO': 4, 'WARNING': 1, 'ERROR': 2}

with open("errores.txt", "w", encoding="utf-8") as f:
    f.writelines(errores)
```

```python
# Ejercicio 9
# open("datos.txt") busca el archivo en el DIRECTORIO ACTUAL (desde donde corrés python),
# no en la carpeta del script. Desde practica/ busca practica/datos.txt, que no existe.
from pathlib import Path

CARPETA = Path(__file__).parent          # la carpeta donde vive leer.py
ruta = CARPETA / "datos.txt"

with open(ruta, encoding="utf-8") as f:
    print(f.read())
```

```python
# Ejercicio 10
def leer_config(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            config = {}
            for linea in f:
                linea = linea.strip()
                if linea and "=" in linea:
                    clave, valor = linea.split("=", 1)
                    config[clave.strip()] = valor.strip()
            return config
    except FileNotFoundError:
        print(f"No encontré {ruta}, uso la configuración por defecto.")
        return {"idioma": "es", "modo": "normal"}

print(leer_config("no_existe.txt"))
# Un `except:` pelado también atraparía errores que NO querés esconder: un error de
# tipeo en tu código, un problema de permisos, un Ctrl+C. Atrapá solo lo que sabés manejar.
```

```python
# Ejercicio 11
import json

perfil = {"nombre": "Lucía", "ciudad": "Málaga", "cursos": ["Python", "n8n"]}

with open("perfil.json", "w", encoding="utf-8") as f:
    json.dump(perfil, f, ensure_ascii=False, indent=2)   # ensure_ascii=False deja "Lucía" legible

with open("perfil.json", encoding="utf-8") as f:
    datos = json.load(f)                                  # vuelve como dict

datos["nivel"] = 2

with open("perfil.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)
```

```python
# Ejercicio 12
import csv

with open("alumnos.csv", encoding="utf-8", newline="") as entrada:
    filas = list(csv.DictReader(entrada))

with open("promedios.csv", "w", encoding="utf-8", newline="") as salida:
    escritor = csv.DictWriter(salida, fieldnames=["nombre", "promedio", "aprobado"])
    escritor.writeheader()
    for fila in filas:
        notas = [int(fila["nota1"]), int(fila["nota2"]), int(fila["nota3"])]  # vienen como texto
        promedio = round(sum(notas) / len(notas), 2)
        escritor.writerow({
            "nombre": fila["nombre"],
            "promedio": promedio,
            "aprobado": "sí" if promedio >= 6 else "no",
        })
# Ana 8.0 sí · Luis 5.0 no · Marta 9.33 sí · Pablo 6.0 sí
```

### Soluciones: Bloque 3

```python
# Ejercicio 13
def maximo(numeros):
    if not numeros:
        raise ValueError("La lista está vacía")
    mayor = numeros[0]          # NO arrancar en 0: con [-5, -1, -9] devolvería 0, que ni está en la lista
    for n in numeros[1:]:
        if n > mayor:
            mayor = n
    return mayor

def promedio(numeros):
    if not numeros:
        raise ValueError("La lista está vacía")
    acumulado = 0
    cantidad = 0
    for n in numeros:
        acumulado += n
        cantidad += 1
    return acumulado / cantidad

print(maximo([4, -2, 17, 8]), promedio([4, -2, 17, 8]))   # 17 6.75
print(maximo([-5, -1, -9]), promedio([-5, -1, -9]))       # -1 -5.0
```

```python
# Ejercicio 14
frase = "el perro y el gato y el loro"
frecuencias = {}
for palabra in frase.split():
    frecuencias[palabra] = frecuencias.get(palabra, 0) + 1

top = sorted(frecuencias.items(), key=lambda par: par[1], reverse=True)[:3]
for palabra, veces in top:
    print(palabra, veces)
# el 3
# y 2
# perro 1   (entre los empates, sorted respeta el orden original: es "estable")
```

```python
# Ejercicio 15
def sin_duplicados(items):
    resultado = []
    for item in items:
        if item not in resultado:     # simple, pero revisa toda la lista cada vez
            resultado.append(item)
    return resultado

def sin_duplicados_rapido(items):
    vistos = set()
    resultado = []
    for item in items:
        if item not in vistos:        # buscar en un set es casi instantáneo
            vistos.add(item)
            resultado.append(item)
    return resultado

datos = ["python", "n8n", "python", "git", "n8n", "sql"]
print(sin_duplicados(datos))          # ['python', 'n8n', 'git', 'sql']
print(sin_duplicados_rapido(datos))   # ['python', 'n8n', 'git', 'sql']
# list(set(items)) quita duplicados pero NO garantiza el orden original.
```

```python
# Ejercicio 16
def busqueda_lineal(lista, objetivo):
    comparaciones = 0
    for i, valor in enumerate(lista):
        comparaciones += 1
        if valor == objetivo:
            return i, comparaciones
    return -1, comparaciones

def busqueda_binaria(lista, objetivo):
    inicio, fin = 0, len(lista) - 1
    comparaciones = 0
    while inicio <= fin:
        medio = (inicio + fin) // 2
        comparaciones += 1
        if lista[medio] == objetivo:
            return medio, comparaciones
        elif lista[medio] < objetivo:
            inicio = medio + 1
        else:
            fin = medio - 1
    return -1, comparaciones

numeros = list(range(1, 1_000_001))
print(busqueda_lineal(numeros, 765_432))   # (765431, 765432)
print(busqueda_binaria(numeros, 765_432))  # (765431, 20) — como mucho ~20 en un millón
# La binaria solo funciona si la lista está ORDENADA: descarta una mitad
# suponiendo que todo lo de esa mitad es menor (o mayor) que el objetivo.
```

```python
# Ejercicio 17
ofertas = [
    {"puesto": "Data Analyst", "salario": 32000},
    {"puesto": "AI Engineer", "salario": 45000},
    {"puesto": "Backend Dev", "salario": 38000},
    {"puesto": "ML Engineer", "salario": 45000},
]
# El signo menos invierte el salario (mayor primero) sin invertir el orden alfabético del puesto.
ordenadas = sorted(ofertas, key=lambda o: (-o["salario"], o["puesto"]))
for o in ordenadas:
    print(o["salario"], o["puesto"])
# 45000 AI Engineer
# 45000 ML Engineer
# 38000 Backend Dev
# 32000 Data Analyst

def bubble_sort(numeros):
    numeros = numeros[:]            # trabajamos sobre una copia
    intercambios = 0
    n = len(numeros)
    for vuelta in range(n - 1):
        for i in range(n - 1 - vuelta):
            if numeros[i] > numeros[i + 1]:
                numeros[i], numeros[i + 1] = numeros[i + 1], numeros[i]
                intercambios += 1
    return numeros, intercambios

print(bubble_sort([5, 2, 9, 1, 7]))   # ([1, 2, 5, 7, 9], 5)
```

### Soluciones: Bloque 4

```python
# Ejercicio 18
# Ruta: respuesta → "resultados" → [0] → "empresa" → "ciudad"
for oferta in respuesta["resultados"]:
    empresa = oferta["empresa"]
    print(f'{oferta["titulo"]} — {empresa["nombre"]} ({empresa.get("ciudad", "sin ciudad")})')
# La tercera oferta NO tiene "ciudad": con empresa["ciudad"] salta un KeyError.
# Por eso esa parte ya usa .get().
```

```python
# Ejercicio 19
for oferta in respuesta["resultados"]:
    etiquetas = oferta.get("etiquetas") or []           # si falta o viene vacía
    primera = etiquetas[0] if etiquetas else "sin dato"  # lista vacía: [0] daría IndexError

    salario = oferta.get("salario")                      # puede faltar o valer None
    minimo = salario.get("min", "sin dato") if salario else "sin dato"

    print(oferta["titulo"], "|", primera, "|", minimo)
# AI Engineer | python | 40000
# Data Analyst | sin dato | sin dato
# Backend Dev | fastapi | 35000
# Ojo: .get("salario", {}) NO alcanza, porque la clave existe y su valor es None.
```

```python
# Ejercicio 20
# Salida:
# [1, 2, 3, 4]
# True
# b = a no copia: los dos nombres apuntan a la MISMA lista.
a = [1, 2, 3]
b = a.copy()          # o list(a), o a[:]
b.append(4)
print(a)              # [1, 2, 3]
print(a is b)         # False
```

```python
# Ejercicio 21
# {'nombre': 'Ana', 'cursos': ['python', 'n8n']}
# {'nombre': 'Eva', 'cursos': ['python', 'n8n']}
# {'nombre': 'Ana', 'cursos': ['python', 'git']}
# La copia superficial crea un dict nuevo, así que cambiar "nombre" no afecta al original,
# pero la lista de cursos es LA MISMA en los dos. La profunda copia también la lista de adentro.
```

### Soluciones: Bloque 5

```text
Ejercicio 22

A. KeyError en ofertas.py, línea 7, dentro de imprimir_resumen (la llamó la línea 12).
   Causa: alguna oferta tiene "empresa" pero no "ciudad". El ^^^ marca justo la clave que falta.
   Primer cambio: imprimir oferta["empresa"] antes de esa línea para ver qué trae,
   y usar .get("ciudad", "sin ciudad").

B. TypeError en informe.py, línea 4.
   Causa: total es un int y se lo está sumando a un str.
   Primer cambio: f"Total de ofertas: {total}" o str(total).

C. AttributeError en limpiar.py, línea 9: texto vale None.
   Causa: limpiar() no tiene return, así que devuelve None, y texto = limpiar(...) guarda None.
   El error aparece en la línea 9, pero el bug está en la función. Casi siempre que ves
   'NoneType' object has no attribute, la pregunta es: ¿de dónde vino ese None?
   Primer cambio: return texto.strip() dentro de limpiar.
```

```text
Ejercicio 23 (ejemplo con el caso C)

Esperaba: que limpiar("  hola  ") me devolviera "hola" y poder pasarlo a mayúsculas.
Pasó: AttributeError: 'NoneType' object has no attribute 'upper', en limpiar.py línea 9.
Ya probé: imprimir texto antes de la línea 9, y vale None aunque la función hace strip().

Con estas tres líneas, el otro ya sabe qué querías, dónde falla y qué descartaste.
Sin la plantilla, lo típico es pegar el error solo, y la primera respuesta termina siendo
"¿qué querías hacer?".
```

### Solución: Integrador

```python
# Ejercicio 24 — seleccionar_ofertas.py
import csv
import json
import sys
from pathlib import Path

CARPETA = Path(__file__).parent


def cargar_ofertas(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No encontré {ruta}. ¿Está en la misma carpeta que el script?")
        sys.exit(1)


def filtrar(ofertas, palabra, salario_minimo):
    palabra = palabra.lower()
    seleccion = []
    for oferta in ofertas:
        salario = oferta.get("salario")
        if salario is None:
            continue                                  # sin salario: fuera, sin romper
        if palabra in oferta.get("descripcion", "").lower() and salario >= salario_minimo:
            seleccion.append(oferta)
    return seleccion


def quitar_duplicados(ofertas):
    vistas = set()
    unicas = []
    for oferta in ofertas:
        clave = (oferta["titulo"], oferta["empresa"])
        if clave not in vistas:
            vistas.add(clave)
            unicas.append(oferta)
    return unicas


def guardar_csv(ofertas, ruta):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["titulo", "empresa", "salario"])
        escritor.writeheader()
        for oferta in ofertas:
            escritor.writerow({c: oferta[c] for c in ["titulo", "empresa", "salario"]})


def main(palabra, salario_minimo):
    ofertas = cargar_ofertas(CARPETA / "ofertas.json")
    seleccion = quitar_duplicados(filtrar(ofertas, palabra, salario_minimo))
    seleccion.sort(key=lambda o: o["salario"], reverse=True)
    guardar_csv(seleccion, CARPETA / "seleccion.csv")
    for o in seleccion:
        print(o["salario"], o["titulo"], "—", o["empresa"])


if __name__ == "__main__":
    main("python", 30000)
    # 38000 Backend Python — WebCo
    # 32000 AI Engineer Junior — Acme      (el id 3 es duplicado; el 2 no llega al mínimo)
    # Con main("llm", 40000): solo 41000 Prompt Engineer — Acme
```

## Relacionado

- [[Tarea]]
- [[Tarea - Algoritmos]] — más práctica de contadores, acumuladores y ordenamiento.
- [[Tarea - Repaso 02 - Excepciones, testing y APIs]] — el paso siguiente: validar, testear y consumir APIs.
- [[Tarea - Repaso 05 - Depuración de flujos en n8n]] y [[Tarea - Repaso 04 - El recorrido del dato en n8n]] — el bloque 4, pero dentro de n8n.
- [[M02·S01 - Fundamentos de Programación]] — cursos base si un bloque entero cuesta.
