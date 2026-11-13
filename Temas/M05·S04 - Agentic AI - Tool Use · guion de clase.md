# Módulo 3 — Tool Use · guion de clase

Nov 13, 2026 · @Luciano · Agentic AI (DeepLearning.AI) → bootcamp Neoland

## Objetivos y mapa del módulo

Al terminar la clase el alumno entiende qué pasa realmente cuando "el LLM llama a una función", sabe exponer sus propias funciones como herramientas, y conoce las dos piezas que multiplican el alcance: ejecución de código y MCP.

Tres objetivos concretos:

1. Explicar el ciclo completo de tool use y quién ejecuta qué en cada paso.
2. Convertir una función Python en herramienta y exponerla al modelo.
3. Decidir cuándo conviene una herramienta específica, cuándo ejecución de código y cuándo un servidor MCP.

| Lección | Tipo | Duración |
| --- | --- | --- |
| What are tools? | Vídeo | 6 min |
| Creating a tool | Vídeo | 5 min |
| Tool syntax | Vídeo | 5 min |
| Ungraded Lab: Turning functions into tools | Lab | 15 min |
| Ungraded Lab: Email Assistant Workflow | Lab | 15 min |
| Code execution | Vídeo | 5 min |
| MCP | Vídeo | 5 min |
| Module 3 quiz + M3 Graded Lab | Evaluación | \~70 min |

Este resumen cubre los cinco vídeos; los labs quedan fuera.

**El cambio conceptual respecto del Módulo 2:** en reflexión el flujo estaba hardcodeado por el desarrollador. Acá el modelo empieza a decidir — qué herramienta usar, con qué argumentos, o ninguna. Es el primer paso real hacia lo agentic.

## Qué es tool use

Una herramienta es simplemente **una función que le damos al LLM para que pueda pedir que la ejecutemos**. Nada más que eso.

El ejemplo de arranque: si le preguntás a un modelo "¿qué hora es?", el modelo fue entrenado hace meses y no tiene forma de saberlo. Con una función `getCurrentTime` disponible, sí.

El ciclo, paso a paso:

1. Llega el prompt del usuario.
2. El LLM mira las herramientas disponibles y decide si usa alguna.
3. Si decide usarla, pide que se ejecute `getCurrentTime`.
4. La función devuelve un valor, que se agrega al historial de la conversación.
5. El LLM genera la respuesta final: "son las 3:20 PM".

**Lo importante es el paso 2: decide el modelo, no el desarrollador.** Si la pregunta fuera "¿cuánta cafeína tiene el té verde?", el mismo setup responde directo sin invocar nada. Ng usa en las diapositivas una caja punteada sobre el LLM para marcar justamente eso: hay herramientas ofrecidas, y es el modelo quien elige.

Ejemplos de cuándo ayuda:

| Pregunta | Herramienta |
| --- | --- |
| Restaurantes italianos cerca de Mountain View | Búsqueda web |
| Clientes que compraron anteojos blancos | Consulta a base de datos |
| $500 al 5% durante 10 años, ¿cuánto da? | Cálculo de interés (o ejecución de código) |

### Varias herramientas a la vez

El caso interesante es cuando hay más de una. Un agente de calendario con tres funciones — consultar agenda, crear cita, borrar cita — ante "buscá un hueco el jueves y agendá con Alice":

1. Llama a consultar agenda → devuelve los huecos del jueves.
2. Con esa información elige las 3 PM y llama a crear cita.
3. Recibe la confirmación y responde: "la cita con Alice quedó el jueves a las 3 PM".

Dos llamadas encadenadas, cada una informada por el resultado de la anterior. Eso ya es un agente.

## Cómo funciona por dentro

Este vídeo desarma el misterio, y vale la pena darlo tal cual: un LLM solo genera tokens de texto, así que **no ejecuta nada**. Lo que hace es emitir texto en un formato acordado, y es el código del desarrollador el que lo interpreta y ejecuta la función.

Ng lo muestra con la sintaxis artesanal que se usaba antes de que los modelos vinieran entrenados para esto:

1. En el system prompt: "tenés una herramienta `getCurrentTime`; para usarla, imprimí `FUNCTION: getCurrentTime`".
2. El usuario pregunta la hora; el modelo imprime exactamente ese texto.
3. **Código mío** busca ese patrón en la salida y extrae qué función se pide.
4. **Código mío** ejecuta la función y obtiene `8 AM`.
5. **Código mío** inyecta ese resultado en el historial de la conversación.
6. El modelo, viendo todo el historial, responde: "son las 8 AM".

Con argumentos es lo mismo con un nivel más: `getCurrentTime` que recibe zona horaria. Ante "¿qué hora es en Nueva Zelanda?", el modelo emite `FUNCTION: getCurrentTime Pacific/Auckland` — o sea, **también genera los argumentos**, y ahí entra en juego su conocimiento del mundo (sabe que Auckland es la zona que corresponde).

### Por qué enseñar la versión vieja

Porque deja claras tres cosas que la sintaxis moderna esconde:

- El modelo no tiene acceso a nada; solo pide.
- El loop lo maneja tu código, no el modelo.
- Todo pasa por el historial de conversación: es la única memoria que hay.

Y el ciclo no termina necesariamente ahí: después de recibir el resultado, el modelo puede decidir pedir otra herramienta, y otra. De ahí sale el parámetro `max_turns` del próximo vídeo.

## La sintaxis moderna

Hoy los modelos vienen entrenados para pedir herramientas con un formato propio, así que nada de `FUNCTION:` en mayúsculas ni regex. El curso usa **aisuite**, la librería open source del equipo de Ng para hablar con varios proveedores con la misma sintaxis, muy parecida a la de OpenAI:

```python
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=messages,
    tools=[get_current_time],
    max_turns=5,
)
```

Dos cosas que conviene aclarar en clase:

- **`tools`** recibe la función Python directamente. No hay que escribir ningún prompt describiendo la herramienta.
- **`max_turns`** es un tope de cuántas herramientas encadenadas permitís antes de cortar, para no quedar en un loop infinito. Ng usa 5 y dice que en la práctica casi nunca se toca.

Con aisuite, además, el cliente **ejecuta la función por vos** y devuelve el resultado al modelo. Hay APIs donde ese paso es manual.

### De dónde sale la descripción de la herramienta

Acá está el detalle que más le sirve a los alumnos para su propio código. Por detrás, aisuite genera un **JSON schema** y eso es lo que recibe el modelo:

| Campo del schema | De dónde sale |
| --- | --- |
| `name` | El nombre de la función |
| `description` | El **docstring** de la función |
| `parameters` | Los argumentos y su documentación |

O sea: **el docstring no es decoración, es el prompt de la herramienta.** Si está mal escrito, el modelo no sabe cuándo llamarla ni con qué valores. Buena consigna de laboratorio: hacerles escribir una herramienta con un docstring pobre, ver que el modelo no la usa, y arreglarla.

## Ejecución de código: la herramienta especial

El problema que la motiva se explica solo. Armás un resolvedor de problemas matemáticos con herramientas `sumar`, `restar`, `multiplicar`, `dividir`. Funciona. Entonces alguien pregunta por la raíz cuadrada de 2. ¿Agregás una herramienta? ¿Y después potenciación? ¿Vas a escribir una función por cada tecla de una calculadora científica?

La salida es dar **una sola herramienta que lo cubre todo: escribir y ejecutar código.**

El flujo, en la versión manual que muestra el vídeo:

1. Prompt: "escribí código para resolver la consulta, delimitado con tags `<execute_python>`".
2. El modelo responde con el código entre tags.
3. Un regex extrae el código.
4. Se ejecuta y se obtiene `1.4142...`.
5. El resultado vuelve al modelo, que redacta la respuesta final.

Y acá se conecta con el Módulo 2: si la ejecución falla, el mensaje de error vuelve al modelo para que reflexione y reescriba. Es exactamente el feedback externo de la clase anterior.

### Seguridad

Esta es la parte que no conviene saltear. Ejecutar código arbitrario generado por un modelo tiene riesgo real.

El caso que cuenta Ng: un compañero de equipo usó un agente de código muy autónomo y el agente decidió borrar `*.py` dentro del directorio del proyecto. Después se disculpó — "fue un error increíblemente estúpido" — pero los archivos ya no estaban. Había backup en GitHub, así que no pasó nada.

Las opciones de ejecución, de menos a más segura:

| Opción | Riesgo |
| --- | --- |
| `exec()` de Python | Alto: corre con tus permisos, sobre tus archivos |
| Sandbox Docker | Contenido: aislamiento del sistema |
| Sandbox liviano tipo E2B | Contenido, pensado para este caso de uso |

Ng es honesto: en la práctica muchos desarrolladores ejecutan sin demasiado control porque el riesgo de una línea suelta es bajo. Pero la buena práctica es sandbox, y en clase vale plantearlo como una decisión consciente, no como un descuido.

## MCP

Hasta acá, cada herramienta se construye y se expone de a una. MCP — Model Context Protocol, propuesto por Anthropic y hoy adoptado por el resto de la industria — ataca el problema de escala.

El argumento, que es el corazón del vídeo:

- **Antes:** cada equipo que quería integrar Slack, Google Drive, GitHub y Postgres escribía sus propios wrappers. Con M aplicaciones y N herramientas, el trabajo total de la comunidad era **M × N**.
- **Con MCP:** un estándar común. Cada aplicación lo implementa una vez, cada herramienta lo expone una vez. El trabajo total pasa a ser **M + N**.

Dos roles:

| Rol | Qué hace | Ejemplo |
| --- | --- | --- |
| Cliente MCP | La aplicación que consume herramientas y datos | Claude Desktop, tu agente |
| Servidor MCP | El wrapper que expone un servicio | Servidor de GitHub, de Slack |

Una distinción de vocabulario que conviene fijar: el diseño inicial de MCP se centró en darle más **contexto** al modelo, y a esas fuentes de datos la documentación las llama **resources**. Pero el protocolo cubre también **tools**, o sea funciones que ejecutan acciones.

La demo del vídeo: Claude Desktop conectado al servidor MCP de GitHub. "Resumí el README de este repo" → el cliente pide el archivo al servidor, el contenido vuelve al contexto, el modelo resume. "¿Cuáles son los últimos pull requests?" → otra herramienta del mismo servidor, mismo ciclo.

**Para el bootcamp:** vale señalar que es el mismo ciclo de tool use de toda la clase — lo único que cambia es que las herramientas ya no las escribís vos. Y que el camino natural para los alumnos es consumir servidores primero, y escribir uno propio después.

## Para dar la clase

### Secuencia sugerida (90 min)

| Bloque | Min | Contenido |
| --- | --- | --- |
| Apertura | 10 | "¿Qué hora es?" al modelo pelado. Que vean la respuesta y propongan la solución |
| El ciclo | 20 | El ciclo manual con `FUNCTION:`. Insistir en quién ejecuta qué |
| Sintaxis | 15 | aisuite, `tools=[]`, y el JSON schema generado desde el docstring |
| Práctica | 25 | Lab adaptado: convertir funciones propias en herramientas |
| Code exec | 15 | El problema de la calculadora, el flujo, y la sección de seguridad |
| MCP | 10 | M×N vs M+N y demo de un servidor MCP en vivo |

### Puntos de pizarra

- El ciclo de tool use dibujado con dos columnas: **lo que hace el LLM** (decidir, emitir texto) y **lo que hace tu código** (parsear, ejecutar, devolver).
- Función → docstring → JSON schema → contexto del modelo.
- El diagrama M×N contra el M+N.

### Errores típicos que conviene anticipar

- **Creer que el modelo ejecuta la función.** No: emite una petición y tu código ejecuta. Es el malentendido número uno.
- **Docstrings vacíos o vagos.** El modelo no ve el cuerpo de la función, solo el schema.
- **Una herramienta por cada cosa.** El caso de la calculadora: a veces la respuesta es ejecución de código, no otra función.
- **`exec()` sobre código generado, sin pensarlo.** Mostrar el caso del `rm` y hablar de sandboxes.
- **Confundir MCP con "otra forma de llamar al modelo".** Es un estándar de distribución de herramientas; el ciclo es el mismo.

### Preguntas para lanzar

1. ¿Qué tres herramientas necesitaría su proyecto para dejar de inventar respuestas?
2. Si el modelo no llama a su herramienta cuando debería, ¿dónde miran primero?
3. ¿Cuándo conviene una herramienta específica y cuándo ejecución de código?
4. ¿Qué le darían y qué no le darían a un agente que ejecuta código en su máquina?
5. ¿Qué servidor MCP les ahorraría más trabajo esta semana?

## Fuentes

- [Agentic AI — Module 3: Tool use](https://learn.deeplearning.ai/courses/agentic-ai/lesson/3s0czq/what-are-tools%3F), DeepLearning.AI. Transcripciones de los cinco vídeos, consultadas el 13 de noviembre de 2026.
- [aisuite](https://github.com/andrewyng/aisuite) — la librería que usa el curso para las llamadas con herramientas.
