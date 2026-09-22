---
tipo: tarea
modulo: 3
estado: pendiente
tags: [rag, n8n, agentes, llm]
---

# Tarea — RAG con Telegram en n8n

## Resumen

- Un repaso de [[M03·S02 - RAG en n8n]] armando algo que se puede usar desde el celular: un **bot de Telegram que responde preguntas sobre un documento**.
- Cinco pasos chicos (el último es opcional), **de 40 minutos como mucho** cada uno. Cada paso deja algo funcionando por sí solo: si una semana se complica, lo hecho no se pierde.
- Para ahorrar fricción, se arranca con el **Simple Vector Store** de n8n, que guarda todo en memoria y no pide crear cuentas nuevas. Pinecone y Cohere, los de la clase, quedan para el paso opcional.

## Antes de empezar: dónde corre n8n

> [!warning] Telegram necesita una dirección pública con HTTPS
> Telegram le avisa a n8n de cada mensaje llamando a una URL, y esa URL tiene que ser **pública y con HTTPS**. Un n8n que corre en tu computadora (`localhost`) no la tiene, así que el Telegram Trigger falla al activarse.
>
> - **Lo más simple:** usar **n8n Cloud**, que tiene prueba gratuita. Ya tiene una URL pública.
> - **Si usás n8n local:** hace falta un túnel. La documentación de n8n explica cómo, pero pide Docker y más configuración. Si no lo tenés resuelto, no gastes la semana en esto: pedilo en la tutoría o usá n8n Cloud.

Vas a necesitar también:

- la app de **Telegram**, en el celular o en la computadora;
- una **clave de OpenAI**, la misma de la clase de RAG.

## Material para hacer los ejercicios

**Telegram**

- [How to Create a Telegram Bot with BotFather + Connect to n8n — Mike Murphy](https://www.youtube.com/watch?v=PGB4qj_ZEUY) — en inglés, crear el bot y conectarlo a n8n paso a paso. Para el paso 1.
- [Tutorial oficial de bots de Telegram](https://core.telegram.org/bots/tutorial) — la sección *Obtain Your Bot Token* explica BotFather.
- [Telegram credentials — documentación de n8n](https://docs.n8n.io/integrations/builtin/credentials/telegram/) — dónde pegar el token.
- [Telegram Trigger — documentación de n8n](https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.telegramtrigger/) y sus [problemas comunes](https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.telegramtrigger/common-issues/) — **leé los problemas comunes antes del paso 1**: explica lo del HTTPS y por qué el modo de prueba y el publicado se pisan.
- [Telegram: operaciones de mensaje — documentación de n8n](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.telegram/message-operations/) — *Send Message*.

**RAG**

- [Step-by-Step Tutorial: Create a RAG Chatbot with n8n AI Agents — Leon van Zyl](https://www.youtube.com/watch?v=UeFi5oV9UpY) — en inglés, un RAG completo en n8n. Es la referencia para los pasos 2 y 3.
- [Build an AI Assistant with n8n and Telegram — Leon van Zyl](https://www.youtube.com/watch?v=m8gj7q_HRo0) — en inglés, un agente conectado a Telegram. Es la referencia para el paso 4.
- [Simple Vector Store — documentación de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.vectorstoreinmemory/) — cómo se inserta y cómo se consulta, y el *Memory Key*.
- [Default Data Loader](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.documentdefaultdataloader/) y [Embeddings OpenAI — documentación de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.embeddingsopenai/) — los sub-nodos de la ingesta.
- [AI Agent — documentación de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/) — y en *Common issues*, el error *No prompt specified*.
- [Simple Memory — documentación de n8n](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.memorybufferwindow/) — la memoria de la conversación y el *Session Key*.
- [[M03·S02 - RAG en n8n]] — los conceptos (chunking, embeddings, retrieval) y los vídeos de Ryan & Matt, si querés repasar algo en particular.

## El documento de prueba

Es la base de conocimiento del bot: las preguntas frecuentes de un curso inventado. Copiala entera en el nodo Code del paso 2.

```js
const faq = [
  { pregunta: "¿Cuándo empiezan las clases?", respuesta: "Las clases empiezan el lunes 5 de octubre y terminan el viernes 18 de diciembre." },
  { pregunta: "¿Qué horario tienen las clases?", respuesta: "Las clases en vivo son de lunes a jueves de 18:30 a 21:30, hora de Madrid. Los viernes no hay clase." },
  { pregunta: "¿Las clases quedan grabadas?", respuesta: "Sí. Todas las clases quedan grabadas y se suben al campus virtual dentro de las 24 horas." },
  { pregunta: "¿Cuánto cuesta el curso?", respuesta: "El curso cuesta 1.200 euros. Se puede pagar en un solo pago o en tres cuotas de 400 euros sin interés." },
  { pregunta: "¿Qué necesito saber antes de empezar?", respuesta: "No hace falta experiencia previa en programación. Sí conviene saber usar una computadora con soltura y tener unas 10 horas por semana." },
  { pregunta: "¿Qué computadora necesito?", respuesta: "Cualquier computadora con 8 GB de RAM y Windows, macOS o Linux. No se puede hacer el curso desde una tablet." },
  { pregunta: "¿Hay certificado?", respuesta: "Sí. Se entrega un certificado a quien apruebe el proyecto final y asista al menos al 80% de las clases." },
  { pregunta: "¿Qué pasa si falto a una clase?", respuesta: "Podés ver la grabación. Si faltás a más del 20% de las clases, no se entrega el certificado, pero podés seguir cursando." }
];
return faq.map(f => ({ json: { texto: `Pregunta: ${f.pregunta}\nRespuesta: ${f.respuesta}`, pregunta: f.pregunta } }));
```

## Parte 1: Las consignas

### Paso 1 — Un bot que repite lo que le escribís

1. En Telegram, abrí un chat con **@BotFather**, mandale `/newbot` y seguí los pasos. El nombre de usuario tiene que terminar en `bot`. Al final te da un **token**: guardalo como si fuera una contraseña.
2. En n8n, creá una credencial de **Telegram** con ese token.
3. Armá un workflow con dos nodos:
   - **Telegram Trigger**, con *Trigger On* en `Message`;
   - **Telegram → Send Message**, con *Chat ID* `{{ $json.message.chat.id }}` y *Text* `Me dijiste: {{ $json.message.text }}`.
4. Ejecutalo en modo prueba (*Execute workflow*), mandale un mensaje al bot y mirá la **salida del Telegram Trigger**: ¿dónde está el texto? ¿Y el id del chat?

**Está hecho cuando:** le escribís `hola` al bot y te contesta `Me dijiste: hola`.

### Paso 2 — Cargar el documento (ingesta)

Armá un **segundo workflow**, separado del bot:

1. **Manual Trigger** → **Code** con el documento de prueba de arriba. Salen 8 items, uno por pregunta.
2. → **Simple Vector Store** en modo *Insert Documents*, con *Memory Key* `faq_curso`.
3. Colgale los sub-nodos:
   - **Default Data Loader**: tipo JSON, con el texto a cargar en `{{ $json.texto }}`;
   - **Embeddings OpenAI**: modelo `text-embedding-3-small`.
4. Ejecutalo.

Antes de ejecutar, predecí cuántos documentos van a quedar guardados. Después fijate en la salida del Vector Store si acertaste.

**Está hecho cuando:** el Simple Vector Store termina en verde y la salida muestra los documentos insertados.

> [!note] El Simple Vector Store vive en memoria
> Si n8n se reinicia, se borra todo y hay que volver a correr este workflow. Para practicar está bien. Para algo que tiene que durar, se usa Pinecone (paso 5).

### Paso 3 — Preguntarle al documento

Todavía sin Telegram, en un **tercer workflow**:

1. **Chat Trigger** (*When chat message received*) → **AI Agent**.
2. Colgale al agente:
   - un **OpenAI Chat Model** (un modelo chico alcanza, por ejemplo `gpt-4o-mini`);
   - un **Simple Vector Store** en modo *Retrieve Documents (As Tool for AI Agent)*, con **el mismo** *Memory Key* `faq_curso` y **el mismo** modelo de embeddings que en la ingesta. En la descripción de la tool, poné algo concreto: `Preguntas frecuentes del curso: fechas, horarios, precio, requisitos y certificado`.
3. En el *System Message* del agente: `Respondé solo con la información de la herramienta de preguntas frecuentes. Si la respuesta no está ahí, decí que no lo sabés y sugerí escribir a secretaría.`
4. Probalo desde el chat de n8n con estas tres preguntas:
   - `¿Cuánto sale el curso?` (está en el documento, pero con otras palabras);
   - `¿Hay clases los sábados?` (no está explícito);
   - `¿Quién es el profesor?` (no está en el documento).

**Está hecho cuando:** la primera responde 1.200 euros con las cuotas y la tercera dice que no lo sabe, sin inventar un nombre. Anotá qué hizo con la segunda.

### Paso 4 — Juntar todo: el bot que responde con el documento

Volvé al workflow del paso 1 y reemplazá el eco por el agente:

1. **Telegram Trigger** → **AI Agent** (configurado como en el paso 3) → **Telegram → Send Message**.
2. El agente **no** recibe el texto solo, porque el Telegram Trigger no lo entrega en el formato del chat de n8n. En el AI Agent, cambiá la fuente del prompt a *Define below* y poné `{{ $json.message.text }}`.
3. Agregale una **Simple Memory** al agente, con *Session Key* `{{ $('Telegram Trigger').item.json.message.chat.id }}`. Así cada persona que le escribe al bot tiene su propia conversación.
4. En el Send Message: *Chat ID* `{{ $('Telegram Trigger').item.json.message.chat.id }}` y *Text* `{{ $json.output }}`.
5. Probalo en modo prueba y, cuando funcione, **publicá** el workflow para que responda siempre.

**Está hecho cuando:** le preguntás al bot `¿cuándo empiezan las clases?` y te contesta con la fecha, y si después le preguntás `¿y cuándo terminan?`, entiende que seguís hablando de las clases.

### Paso 5 (opcional) — Hacerlo más robusto

Elegí uno o más:

- **Mensajes que no son texto:** mandale al bot un sticker o un audio. ¿Qué pasa? Agregá un **If** después del Telegram Trigger que revise que `message.text` exista, y si no, que responda `Por ahora solo entiendo mensajes de texto`.
- **Pasar a Pinecone:** reemplazá el Simple Vector Store por Pinecone siguiendo los pasos 2 a 4 de la guía de [[M03·S02 - RAG en n8n]]. El índice tiene que tener **1536 dimensiones** para `text-embedding-3-small`, y el mismo modelo en la ingesta y en la consulta.
- **Reranker:** activá *Rerank Results* con Cohere, como en el paso 5 de esa misma guía.

## Parte 2: Errores típicos y cómo resolverlos

Antes de mirar esta tabla, pasá por el protocolo de cuatro preguntas de [[Tarea - Repaso 05 - Depuración de flujos en n8n]]: ¿se ejecutó?, ¿dónde hay datos por última vez?, ¿qué esperaba?, ¿cuál es el cambio más chico?

| Síntoma | Causa | Arreglo |
|---|---|---|
| El Telegram Trigger falla al activarse con un error que habla de HTTPS o de *webhook* | n8n corre en `localhost`, sin URL pública | Usar n8n Cloud o configurar un túnel (ver el recuadro de arriba) |
| Error *Unauthorized* al guardar o usar la credencial | El token está mal copiado (le falta un carácter o tiene un espacio) | Volver a copiarlo de BotFather. Si se filtró, `/revoke` en BotFather genera uno nuevo |
| En modo prueba anda, pero publicado no responde (o al revés) | Telegram admite **un solo** webhook por bot, y el de prueba y el de producción se pisan | Despublicar mientras probás, o crear un segundo bot solo para pruebas |
| El agente dice *No prompt specified* | Le llega el mensaje de Telegram, no un mensaje de chat de n8n | Prompt en *Define below* con `{{ $json.message.text }}` (paso 4.2) |
| Error en el sub-nodo Simple Memory que menciona `sessionId` | Sin el Chat Trigger, nadie le da un id de sesión | *Session Key* con el `chat.id` (paso 4.3) |
| El bot contesta "no lo sé" a todo | El vector store está vacío (n8n se reinició), el *Memory Key* es distinto, o el modelo de embeddings no es el mismo | Volver a correr la ingesta y revisar que la clave y el modelo coincidan en los dos workflows |
| Al mandar un sticker, el agente falla | `message.text` no existe en ese mensaje | El If del paso 5 |
| *dimension mismatch* (con Pinecone) | La dimensión del índice no coincide con el modelo | 1536 para `text-embedding-3-small`. La dimensión de un índice no se puede cambiar: hay que crear otro |
| Error 429 (con Cohere) | Límite de pedidos por minuto de la clave de prueba | Esperar un minuto y no probar todos a la vez (ver [[M03·S02 - RAG en n8n]]) |
| Al final de cada respuesta aparece un texto que dice que se envió con n8n | Es la atribución que el nodo de Telegram agrega por defecto | Desactivar la opción de atribución en *Additional Fields* del Send Message |

### Qué se espera en el paso 3

- **Precio:** encuentra la respuesta aunque la pregunta diga "cuánto sale" y el documento diga "cuánto cuesta". Esa es la gracia de los embeddings: buscan por **significado**, no por palabras exactas.
- **Sábados:** depende del modelo. Lo ideal es que diga que las clases son de lunes a jueves, sin afirmar nada que el documento no dice. Si inventa ("sí, hay clases los sábados"), reforzá el *System Message*.
- **Profesor:** tiene que decir que no lo sabe. Si inventa un nombre, el *System Message* no alcanza. Revisá que la herramienta tenga una descripción clara y probá con un modelo un poco más grande.

## Relacionado

- [[Tarea]]
- [[M03·S02 - RAG en n8n]] — la clase que repasa esta tarea.
- [[Tarea - Repaso 03 - Mínimo semanal de APIs con Python]] — la tarea anterior de este mismo recorrido.
- [[Tarea - Repaso 05 - Depuración de flujos en n8n]] — el protocolo para cuando algo no dispara.
- [[Proyectos]] — la idea "Chatbot con RAG por Telegram o Whatsapp" parte exactamente de acá.
