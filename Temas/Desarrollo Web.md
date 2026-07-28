---
tipo: tema
tags: [web, python]
---

# Desarrollo Web

## Servidor web simple

Python trae un servidor HTTP en la librería estándar: sirve los archivos del directorio actual sin instalar nada.

```bash
python3 -m http.server 9999 -b 192.168.1.7
```

- `9999` — puerto donde escucha.
- `-b 192.168.1.7` — dirección a la que se enlaza. Con la IP local de tu máquina, el servidor queda accesible desde otros equipos de la red; con `127.0.0.1` solo desde la tuya.

Referencia: [Simple HTTP Server in Python — NeuralNine](https://www.youtube.com/watch?v=DeFST8tvtuI)

## Red local

Para entender a qué IP enlazar y por qué otro equipo de la red puede o no llegar:

- [Diagrama de red local (Drive)](https://drive.google.com/file/d/11JBueCAuaORxk1cvj1lnwmhR17FM0RmX/view?usp=sharing)

> [!question] Pendiente
> Ampliar con HTML/CSS y algún framework (Flask o FastAPI) cuando se vea en clase.

## Relacionado

- [[2026-07-07 - Python Requests - Consumo de APIs]] — el otro lado: consumir HTTP en vez de servirlo.
