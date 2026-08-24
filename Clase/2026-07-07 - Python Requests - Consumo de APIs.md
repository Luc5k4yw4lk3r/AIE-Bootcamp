---
tipo: clase
fecha: 2026-07-07
modulo: 3
tags: [python, apis]
---

# Python Requests — Consumo de APIs

## Resumen

- `requests.get()` y lectura de la respuesta: el objeto en sí, `.text`, `.status_code` y `.json()`.
- `requests.post()` para enviar datos con `json=`.
- Tres niveles de manejo de errores: comprobar `status_code` con un `if`, `raise_for_status()` dentro de `try`/`except`, y capturar `requests.exceptions.Timeout`.
- `timeout=5` para no quedarse colgado, y cabeceras de autenticación con `Authorization: Bearer`.

## Tutorial

- [Python Requests Tutorial: HTTP Requests and Web Scraping — pixegami](https://www.youtube.com/watch?v=XqIfWkVI3UA)

APIs que usamos para las pruebas:

- [httpbin.org](https://httpbin.org/) — devuelve lo que le mandás, así que sirve para comprobar qué está saliendo de tu código (`/post`, `/headers`, `/delay/10`).
- [PokéAPI](https://pokeapi.co/) — API pública de solo lectura, sin autenticación.

## Ejercicios

```bash
# Get normal - solicitar 
import requests
response = requests.get("https://pokeapi.co/api/v2/pokemon/ditto")
# response = requests.get("https://www.google.com")
# Objeto
print(response)
# Toda la info
print(response.text)
# status code
print(response.status_code)

# POST - Enviar informacion a un server
import requests
data = {"name": "Jack", "message": "Hello!"}
url = "https://httpbin.org/post"
response = requests.post(url, json=data)
print(response.text)
response_data = response.json()
print(response_data)

# Manejo de errores simple con if
response = requests.get("https://pokeapi.co/api/v2/pokemon/ditto333")
if response.status_code != 200:
    print(f"Hubo un problema con el request Codigo de Error: {response.status_code}") 

# Manejo de errores con try except
import requests
try:
    response = requests.get("https://pokeapi.co/api/v2/pokemon/ditto333")
    response.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
except Exception:
    print("Exception all")
import requests
url = "https://www.httpbin.org/delay/10"
try:
    response = requests.get(url, timeout=5)
    print(response)
    print(response.text)
except requests.exceptions.Timeout as err:
    print(err)
    

# Headers
import requests

auth_token = "XXXXXXXX"
headers = {"Authorization": f"Bearer {auth_token}"}

url = "https://httpbin.org/headers"
response = requests.get(url, headers=headers)
print(response.json())

```

## Relacionado

- [[2026-06-18 - Revisión Python - LLMs y chat con historial]]
- [[Tarea - Excepciones, testing y APIs]] — ejercicios de repaso sobre esta sesión.
- [[Fundamentos de Programación]]
