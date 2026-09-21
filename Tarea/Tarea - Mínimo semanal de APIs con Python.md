---
tipo: tarea
modulo: 3
estado: pendiente
tags: [python, apis, git, csv]
---

# Tarea — Mínimo semanal de APIs con Python

## Resumen

- Cuatro entregas chicas, **una por semana y de 30 minutos como mucho** cada una. Cada entrega se apoya en la anterior y deja algo que funciona por sí solo.
- Cada una dice **"Está hecho cuando…"**: cuando se cumple eso, la semana está cumplida. No hace falta más.
- Si una semana no da el tiempo, no pasa nada: se retoma donde quedó. Es mejor una entrega chica terminada que una grande a medias.

## Material para hacer los ejercicios

- [APIs Explained in 6 Minutes — ByteByteGo](https://www.youtube.com/watch?v=hltLrjabkiY) — qué es una API, en 6 minutos. Para la semana 2.
- [Python Requests Tutorial: HTTP Requests and Web Scraping — pixegami](https://www.youtube.com/watch?v=XqIfWkVI3UA) — el vídeo de la clase de requests. Con la primera mitad alcanza.
- [PokéAPI](https://pokeapi.co/) — la API que usamos: pública, gratis y sin clave. En la portada podés probar una consulta sin escribir código.
- [How Git Works: Explained in 4 Minutes — ByteByteGo](https://www.youtube.com/watch?v=e9lnsKot_SQ) — el modelo mental de Git. Para la semana 1.
- [Trabajar con remotos — libro Pro Git, en castellano](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Trabajar-con-Remotos) — `clone`, `pull` y `remote`. Solo esa sección.
- [`csv` — documentación oficial de Python](https://docs.python.org/es/3/library/csv.html) — el ejemplo de `DictWriter`, para la semana 3.
- [Errores y excepciones — tutorial oficial de Python](https://docs.python.org/es/3/tutorial/errors.html) — `try` y `except`, para la semana 4.
- Los apuntes de clase: [[2026-07-07 - Python Requests - Consumo de APIs]] y [[2026-06-18 - Revisión Python - Archivos CSV]], y la guía [[M02·S05 - Subir repositorios a GitHub]].

## Parte 1: Las consignas

### Semana 1 — El entorno al día

El objetivo es que el material del curso esté actualizado en tu máquina y que Python y `requests` funcionen. Si se puede, esta semana se hace **en la tutoría**, con alguien al lado.

1. **Tener el repositorio del curso.**
   - Si todavía no lo tenés: `git clone <url-del-repo>`.
   - Si ya lo tenés: entrá a la carpeta y corré `git status`, y después `git pull`.
2. **Si `git pull` se queja** de que tenés cambios locales que se pisarían:
   - Si los cambios no te importan: `git stash` guarda tus cambios aparte, después `git pull`, y listo.
   - Si te importan, o no sabés qué son: **no borres nada**. Cloná el repo de nuevo en **otra** carpeta y seguí desde esa. Tu copia vieja queda intacta para mirarla después.
3. **Crear `chequeo.py`** en una carpeta tuya de prácticas:

   ```python
   import sys
   import requests

   print("Python", sys.version.split()[0])
   respuesta = requests.get("https://pokeapi.co/api/v2/pokemon/pikachu", timeout=10)
   print("PokéAPI respondió", respuesta.status_code)
   ```

4. Correlo con `python chequeo.py`.

**Está hecho cuando:** `git pull` dice *Already up to date* y `chequeo.py` imprime tu versión de Python y `PokéAPI respondió 200`.

Si falla, anotá el error exacto y traelo a la próxima tutoría: un error de entorno anotado ya es la mitad del arreglo.

### Semana 2 — Algo que sale

Es el Ejercicio 9 de [[Tarea - Excepciones, testing y APIs]], con una vuelta más. Si ya lo hiciste, arrancá directo por la variante.

- Hacé un `GET` a `https://pokeapi.co/api/v2/pokemon/ditto` e imprimí el nombre y el peso.
- **Variante:** pedile al usuario un nombre con `input()` y mostrá **nombre, altura, peso y tipos**. Los tipos vienen dentro de una lista de diccionarios anidados: imprimí primero `datos["types"]` para ver qué forma tienen antes de sacar el nombre.

**Está hecho cuando:** escribís `pikachu` y el programa muestra algo como `pikachu — altura 4, peso 60, tipos: electric`.

### Semana 3 — De la API a un archivo

- Con la lista `["bulbasaur", "charmander", "squirtle", "pikachu", "eevee"]`, pedí cada pokémon a la API y guardá un `pokemons.csv` con las columnas `nombre,altura,peso,tipos`.
- Si un pokémon tiene dos tipos, van juntos en la misma celda: `grass/poison`.

**Está hecho cuando:** abrís `pokemons.csv` con Excel, LibreOffice o el editor y ves 5 filas más el encabezado.

### Semana 4 — Que no se caiga

Tomá el script de la semana 3 y hacelo resistente:

1. Agregá a la lista un nombre que no existe (`pikachuuu`).
2. Cada pedido tiene que llevar `timeout=10` y `raise_for_status()`, dentro de un `try`.
3. Si un pokémon falla, el programa **avisa y sigue con el siguiente**: no se corta.
4. Al final imprime un resumen: `Guardados: 5 · Fallidos: 1 (pikachuuu)`.

**Está hecho cuando:** el script termina sin traceback, el CSV tiene los 5 que existen y el resumen nombra al que falló.

## Parte 2: Las soluciones

### Solución: Semana 1

`chequeo.py` es el de la consigna. Los problemas más comunes y qué hacer con cada uno:

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `ModuleNotFoundError: No module named 'requests'` | `requests` no está instalado en **ese** Python | `python -m pip install requests`. Usá el mismo `python` con el que corrés el script |
| `python: command not found` | En Mac y Linux el comando suele ser `python3` | Probá `python3 chequeo.py` |
| `requests.exceptions.ConnectionError` | No hay red, o una VPN o un antivirus bloquea la conexión | Probá abrir `https://pokeapi.co` en el navegador. Si tampoco carga, el problema no es tu código |
| `error: Your local changes ... would be overwritten by merge` | Tocaste archivos del repo del curso | El punto 2 de la consigna: `git stash`, o clonar en otra carpeta |
| `fatal: not a git repository` | Estás parado en otra carpeta | `cd` a la carpeta del repo. `ls` tiene que mostrar los archivos del curso |

### Solución: Semana 2

```python
import requests

nombre = input("¿Qué pokémon buscás? ").strip().lower()
respuesta = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre}", timeout=10)

if respuesta.status_code == 200:
    datos = respuesta.json()
    # datos["types"] es una lista de diccionarios: [{"slot": 1, "type": {"name": "electric", "url": ...}}]
    tipos = [t["type"]["name"] for t in datos["types"]]
    print(f'{datos["name"]} — altura {datos["height"]}, peso {datos["weight"]}, tipos: {", ".join(tipos)}')
else:
    print(f"No encontré '{nombre}' (código {respuesta.status_code})")
```

### Solución: Semana 3

```python
import csv
import requests

NOMBRES = ["bulbasaur", "charmander", "squirtle", "pikachu", "eevee"]

with open("pokemons.csv", "w", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=["nombre", "altura", "peso", "tipos"])
    escritor.writeheader()
    for nombre in NOMBRES:
        datos = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre}", timeout=10).json()
        escritor.writerow({
            "nombre": datos["name"],
            "altura": datos["height"],
            "peso": datos["weight"],
            "tipos": "/".join(t["type"]["name"] for t in datos["types"]),
        })

print("Listo: pokemons.csv")
```

### Solución: Semana 4

```python
import csv
import requests

NOMBRES = ["bulbasaur", "charmander", "squirtle", "pikachu", "eevee", "pikachuuu"]


def pedir_pokemon(nombre):
    respuesta = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre}", timeout=10)
    respuesta.raise_for_status()          # un 404 se convierte en excepción: no se puede ignorar
    datos = respuesta.json()
    return {
        "nombre": datos["name"],
        "altura": datos["height"],
        "peso": datos["weight"],
        "tipos": "/".join(t["type"]["name"] for t in datos["types"]),
    }


guardados = []
fallidos = []

for nombre in NOMBRES:
    try:
        guardados.append(pedir_pokemon(nombre))
    except requests.exceptions.HTTPError as error:
        print(f"{nombre}: la API respondió {error.response.status_code}")
        fallidos.append(nombre)
    except requests.exceptions.Timeout:
        print(f"{nombre}: la API tardó demasiado")
        fallidos.append(nombre)
    except requests.exceptions.ConnectionError:
        print(f"{nombre}: no hay conexión")
        fallidos.append(nombre)

with open("pokemons.csv", "w", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=["nombre", "altura", "peso", "tipos"])
    escritor.writeheader()
    escritor.writerows(guardados)

print(f"Guardados: {len(guardados)} · Fallidos: {len(fallidos)} ({', '.join(fallidos) or 'ninguno'})")
```

El `try` va **dentro** del `for`, no alrededor. Si envolviera todo el bucle, el primer fallo cortaría a todos los que vienen después. Es la misma idea del Ejercicio 4 de [[Tarea - Excepciones, testing y APIs]].

## Relacionado

- [[Tarea]]
- [[Tarea - Excepciones, testing y APIs]] — la versión completa de estos temas, con tests.
- [[Tarea - RAG con Telegram en n8n]] — el paso siguiente, una vez hechas estas cuatro semanas.
- [[2026-07-07 - Python Requests - Consumo de APIs]] · [[M02·S01 - Fundamentos de Programación]]
