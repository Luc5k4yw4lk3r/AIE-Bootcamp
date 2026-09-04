---
tipo: clase
fecha: 2026-06-18
modulo: 2
tags: [python, llm, apis]
---

# Revisión Python — LLMs y chat con historial

## Resumen

- Primera llamada a la API de OpenAI, con la clave cargada desde un `.env` mediante `dotenv`.
- El problema del modelo sin memoria: dos llamadas seguidas no guardan relación entre sí.
- Solución: acumular preguntas y respuestas en una lista `historial` y mandarla unida en cada llamada.
- Ejercicio final: bucle `while` que sigue preguntando hasta que el usuario escribe `salir`.

## Ejercicio - Solictar por consola al usuario una pregunta para resolver con el LLM

Nota: Recordar tener el api_token activo

```jsx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

pregunta = input("Inserta tu pregunta al LLM: ")

response = client.responses.create(
    model="gpt-4o-mini",
    tools=[],
    input=pregunta
)

print(response.output_text)
```

## Ejercicio - Ayudar a recordar al LLM.

- Se hacen 2 llamadas al llm pero no guardan relacion

```jsx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

historial = []

pregunta = input("Inserta tu pregunta al LLM: ")

historial.append(pregunta)

response = client.responses.create(
    model="gpt-4o-mini",
    tools=[],
    input=pregunta
)

historial.append(response)

print(response.output_text)

pregunta_2 = input("Inserta tu 2da pregunta al LLM: ")

historial.append(pregunta_2)

response = client.responses.create(
    model="gpt-4o-mini",
    tools=[],
    input=historial
)

print(response.output_text)

```

Solucion

```jsx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

historial = []

pregunta = input("Inserta tu pregunta al LLM: ")

historial.append(pregunta)

response = client.responses.create(
    model="gpt-4o-mini",
    tools=[],
    input=pregunta
)

historial.append(response.output_text)

print(response.output_text)

pregunta_2 = input("Inserta tu 2da pregunta al LLM: ")

historial.append(pregunta_2)

print("--------")
print(" ".join(historial))

response = client.responses.create(
    model="gpt-4o-mini",
    tools=[],
    input=" ".join(historial)
)
# "Donde esta la Toscana? Respuesta de la toscana llm Tiene mar?"
# ["Donde esta la Toscana?", "Respuesta de la toscana llm", "Tiene mar?"]

print(response.output_text)
```

## Ejercicio - Chat con el llm

Para pensar hacer el codigo que solicite preguntas al usuario hasta que el mismo escriba la palabra “salir”

Pistas:

- Condicion de fin: while pregunta != "salir":

```jsx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

historial = []
pregunta = input("Inserta tu pregunta al LLM: ")

while pregunta != "salir":

    historial.append(pregunta)

    response = client.responses.create(
        model="gpt-4o-mini",
        tools=[],
        input="\n".join(historial)
    )

    historial.append(response.output_text)
    
    print(response.output_text)
    
    pregunta = input("Inserta tu pregunta al LLM: ")
```

[chat_llm_simple.drawio](https://drive.google.com/file/d/1nJ4VPHHJN36mRk7aJhw1v-xh1Btpy9gW/view?usp=sharing)

## Relacionado

- [[2026-07-07 - Python Requests - Consumo de APIs]]
- [[M03·S03 - Claude y MCPs]]
