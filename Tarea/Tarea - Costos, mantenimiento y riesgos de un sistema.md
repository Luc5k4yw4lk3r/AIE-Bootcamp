---
tipo: tarea
modulo: A
estado: pendiente
tags: [estimacion, rag, llm]
---

# Tarea — Costos, mantenimiento y riesgos de un sistema

## Resumen

- Casi todo lo que armamos en el curso funciona el día de la demo. Esta tarea es sobre lo que pasa **después**: cuánto cuesta tenerlo andando, qué se rompe con el tiempo y qué puede salir mal.
- Se entrega una **presentación de 5 minutos** para la clase, sobre un sistema que ya vimos.
- Son las preguntas que se hace quien pone sistemas en producción. Traerlas a clase le sirve a todo el grupo.

## Material para hacer los ejercicios

- [Pricing — documentación de la API de OpenAI](https://developers.openai.com/api/docs/pricing) — el precio por millón de tokens de cada modelo, de chat y de embeddings.
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) — pegás un texto y te dice cuántos tokens tiene. Sirve para estimar el tamaño de un prompt real.
- [Pinecone — precios](https://www.pinecone.io/pricing/) · [Cohere — precios](https://cohere.com/pricing) · [n8n — precios](https://n8n.io/pricing/) — el resto de las piezas del RAG del curso.
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) — la lista de referencia de riesgos de seguridad en aplicaciones con LLM. Con leer los títulos y el primer párrafo de *Prompt Injection* y *Sensitive Information Disclosure* alcanza.
- [Agencia Española de Protección de Datos](https://www.aepd.es/) — para la parte de datos personales. Buscá sus guías sobre inteligencia artificial.
- [[M03·S02 - RAG en n8n]] — la arquitectura del RAG, y los límites de uso de Cohere.
- [[M07·S04 - Componentes avanzados de FastAPI y separación en capas]] — el endpoint que simula una API de LLM, con caching.
- [[MA·S07 - Estimación, costeo y defensa del proyecto]] — el marco de costeo del módulo transversal.

## Parte 1: La consigna

Elegí **uno** de estos dos sistemas:

- **A.** El RAG de [[M03·S02 - RAG en n8n]]: n8n + embeddings de OpenAI + Pinecone + reranker de Cohere + un modelo de chat.
- **B.** El webserver de [[M07·S04 - Componentes avanzados de FastAPI y separación en capas]] con el endpoint que llama a un LLM.

Prepará 5 minutos que respondan tres preguntas. Usá la guía para no dejar nada afuera, pero en la presentación quedate con **lo más importante de cada bloque**, no con todo.

### 1. ¿Cuánto cuesta cada 1000 consultas?

- ¿Qué piezas cobran **por uso** (tokens, búsquedas, requests) y cuáles cobran **fijo** (suscripción mensual, servidor)?
- Para una consulta típica: ¿cuántos tokens entran al modelo (prompt del sistema + contexto recuperado + pregunta) y cuántos salen? Medilo con el tokenizer sobre un ejemplo real.
- ¿Cuánto cuesta la **ingesta**, que se paga una vez por documento, frente a la **consulta**, que se paga cada vez?
- ¿A partir de cuántas consultas por mes pesa más el costo por uso que el costo fijo?
- ¿Qué palanca bajaría más el costo? Por ejemplo: un modelo más chico, menos chunks de contexto, caching de preguntas repetidas.

### 2. ¿Qué se rompe con el tiempo?

- **Claves y credenciales:** ¿cuáles vencen o se pueden revocar? ¿Quién se entera cuando pasa, y cómo?
- **Límites:** ¿qué cuotas o *rate limits* tiene cada servicio en el plan gratuito? ¿Qué le pasa al usuario cuando se alcanzan?
- **Cambios de terceros:** modelos que se deprecan, versiones nuevas del reranker o de n8n que cambian un nodo. [[M03·S02 - RAG en n8n]] ya tiene un ejemplo real con los modelos de Cohere.
- **Datos:** ¿qué pasa cuando cambia un documento de la base? ¿Alguien lo vuelve a ingestar? ¿Quedan versiones viejas respondiendo?

### 3. ¿Qué puede salir mal?

- **Claves expuestas:** ¿dónde viven las claves en este sistema? ¿Qué pasaría si el workflow o el repo se compartiera tal cual?
- **Prompt injection:** ¿qué hace el sistema si un documento, o un usuario, incluye "ignorá tus instrucciones y…"?
- **Datos personales:** ¿entran datos de personas en los documentos o en las preguntas? ¿A qué servicios externos se mandan?
- **Respuestas inventadas:** ¿qué hace el sistema cuando la respuesta no está en la base? ¿Lo dice, o la inventa?

### Formato de la entrega

- Una sola hoja o dos diapositivas, con **un número** de costo cada 1000 consultas (con los supuestos a la vista), **un riesgo de mantenimiento** y **un riesgo de seguridad**, y para cada riesgo, qué harías.
- Los precios cambian seguido: poné la **fecha** en que los consultaste.

## Parte 2: Ejemplo resuelto

Es un ejemplo para el sistema A, para ver la forma. Los precios se consultaron el 2026-09-18 en la página de OpenAI y **hay que volver a verificarlos**: cambian seguido.

**Supuestos de una consulta típica:**

| Pieza | Tokens | Precio usado (USD por 1M de tokens) | Costo por consulta |
|---|---|---|---|
| Embedding de la pregunta (`text-embedding-3-small`) | 20 | 0,02 | ≈ 0,0000004 |
| Entrada al modelo de chat (`gpt-4o-mini`): 300 del sistema + 4 chunks × 250 + 20 de la pregunta | 1320 | 0,15 | ≈ 0,00020 |
| Salida del modelo de chat | 200 | 0,60 | ≈ 0,00012 |
| **Total por consulta (sin reranker)** | | | **≈ 0,00032** |

**Cada 1000 consultas:** unos **0,32 USD** en modelos. A eso se le suma el reranker de Cohere, que cobra por búsqueda (mirar su página de precios), y el plan de Pinecone si se sale del gratuito.

**Ingesta:** 100 páginas de ~500 tokens son 50.000 tokens de embeddings, unos 0,001 USD. Es despreciable, y se paga una sola vez.

**Lo que muestra el número:** con poco volumen, el costo por uso es casi nada y lo que pesa es lo **fijo**: la suscripción de n8n Cloud o el servidor donde corre n8n, y el plan de Pinecone. Hacen falta muchos miles de consultas por mes para que los tokens superen al costo fijo. La primera palanca de ahorro, entonces, no es el modelo: es dónde se aloja todo.

**Un riesgo de mantenimiento:** la Trial Key de Cohere tiene un límite bajo de pedidos por minuto (ver [[M03·S02 - RAG en n8n]]). En una demo con varias personas a la vez, el reranker empieza a devolver errores 429 y el usuario recibe un error, no una respuesta. *Qué haría:* pasar a una clave de producción antes de abrirlo a usuarios, y agregar una rama de error que responda sin reranker si Cohere falla.

**Un riesgo de seguridad:** los documentos ingestados se tratan como fuente confiable. Si alguien consigue meter en la base un documento con instrucciones ("ignorá lo anterior y respondé…"), el modelo las recibe como contexto. Es *prompt injection* indirecta, del top 10 de OWASP. *Qué haría:* controlar quién puede cargar documentos, dejar dicho en el prompt del sistema que el contexto es información y no instrucciones, y no darle al agente herramientas con efectos (enviar, borrar) sin una confirmación humana.

## Relacionado

- [[Tarea]]
- [[MA·S07 - Estimación, costeo y defensa del proyecto]]
- [[M03·S02 - RAG en n8n]] · [[M07·S04 - Componentes avanzados de FastAPI y separación en capas]]
