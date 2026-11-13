# Módulo 5 — Planning y multi-agente · guion de clase

Nov 13, 2026 · @Luciano · Agentic AI (DeepLearning.AI) → bootcamp Neoland

## Objetivos y mapa del módulo

Es el módulo de cierre y el más experimental: hasta acá el desarrollador decidía la secuencia de pasos; de acá en más la decide el sistema. Dos patrones: **planning** (un agente arma su propio plan) y **multi-agente** (varios agentes con roles se reparten el trabajo).

Tres objetivos concretos:

1. Implementar un agente que genere un plan y lo ejecute paso a paso.
2. Decidir cuándo el plan conviene expresarlo en JSON y cuándo directamente en código.
3. Descomponer una tarea compleja en agentes con rol y elegir un patrón de comunicación.

| Lección | Tipo | Duración |
| --- | --- | --- |
| Planning workflows | Vídeo | 7 min |
| Creating and executing LLM plans | Vídeo | 2 min |
| Planning with code execution | Vídeo | 7 min |
| Ungraded Lab: Customer Service Agent | Lab | 15 min |
| Multi-agentic workflows | Vídeo | 9 min |
| Ungraded Lab: Market Research Team | Lab | 15 min |
| Communication patterns for multi-agent systems | Vídeo | 4 min |
| Module 5 quiz + M5 Graded Assignment | Evaluación | \~70 min |
| Conclusion | Vídeo | 2 min |

Este resumen cubre los cinco vídeos del módulo; los labs quedan fuera.

**El hilo del curso completo**, útil para abrir la clase: M2 reflexión (el modelo revisa lo suyo) → M3 herramientas (el modelo actúa sobre el mundo) → M4 evals (cómo saber si funciona) → M5 planning y multi-agente (el modelo decide la secuencia).

## El patrón Planning

En el Módulo 3 el modelo elegía qué herramienta llamar, una por vez. En planning **escribe primero la secuencia completa de pasos y después la ejecuta**.

El ejemplo central es un agente de atención al cliente de una tienda de anteojos de sol, con herramientas para obtener descripciones de productos, consultar stock, procesar devoluciones, obtener precios, ver transacciones pasadas y registrar ventas.

Llega la consulta: *"¿tienen anteojos redondos en stock por menos de $100?"*. El prompt le describe las herramientas y le pide un plan paso a paso, y el modelo devuelve algo como:

1. Usar `get_item_descriptions` para encontrar cuáles son redondos.
2. Usar `check_inventory` sobre esos para ver cuáles hay en stock.
3. Usar `get_item_price` para filtrar los que están bajo $100.

Después el sistema ejecuta cada paso en una llamada aparte: el texto del paso 1 va al modelo con el contexto y las herramientas, su salida se pasa junto con el texto del paso 2, y así. Al final, una última llamada redacta la respuesta al cliente.

**Lo que se gana:** nadie decidió de antemano el orden de las herramientas. Si el cliente hubiera pedido *"quiero devolver los de marco dorado, no los de metal"*, el modelo arma otro plan con otras herramientas. Ese es todo el punto del patrón.

El segundo ejemplo, el asistente de email, muestra lo mismo con otras herramientas (buscar, mover, borrar, enviar): *"respondele a Bob que voy a la cena y archivá el mail"* → buscar el mail → redactar y enviar la confirmación → mover a archivados.

**La advertencia, y conviene darla sin suavizar:** planning funciona muy bien en asistentes de código altamente agénticos, que arman un checklist de componentes y lo van tachando. Fuera de ahí la adopción todavía está creciendo, porque el sistema se vuelve más difícil de controlar: en tiempo de desarrollo no sabés qué plan va a salir en runtime.

## El formato del plan

Un plan en prosa queda lindo en la diapositiva, pero el código que lo ejecuta tiene que parsearlo. Por eso la práctica habitual es **pedirle el plan en JSON**, y los modelos actuales lo generan bien.

Cada paso lleva tres claves: la descripción de la tarea, la herramienta a usar y los argumentos:

```json
[
  {
    "step": 1,
    "description": "Encontrar los anteojos redondos",
    "tool": "get_item_descriptions",
    "args": {"shape": "round"}
  },
  {
    "step": 2,
    "description": "Chequear stock de esos modelos",
    "tool": "check_inventory",
    "args": {"items": "<salida del paso 1>"}
  }
]
```

Las cuatro opciones, en orden de confiabilidad según el curso:

| Formato | Comentario |
| --- | --- |
| JSON | La opción recomendada: parseo limpio, los modelos lo generan bien |
| XML | Igual de válida; delimitadores por tag |
| Markdown | Más ambiguo de parsear, se usa menos |
| Texto plano | La menos confiable |

Es un vídeo de dos minutos, pero da para un ejercicio corto: que pidan el mismo plan en los cuatro formatos y vean cuánto código cuesta parsear cada uno.

## Planning con ejecución de código

La idea: en vez de un plan en JSON que se ejecuta paso a paso, **que el modelo escriba código** y que el código sea el plan.

El ejemplo vuelve al CSV de ventas de la máquina de café, con herramientas tipo `get_column_max`, `get_column_mean`, `filter_rows`, `get_column_median`, `sum_rows`.

Y ahí aparece el problema, que es el mismo del Módulo 3 pero más grave:

- *"¿qué mes tuvo más ventas de chocolate caliente?"* → se puede, pero hay que filtrar enero, calcular, repetir para febrero, marzo… los doce meses, y después tomar el máximo. Horrible.
- *"¿cuántas transacciones únicas hubo la semana pasada?"* → no se puede: falta una herramienta.
- *"¿qué montos tuvieron las últimas cinco transacciones?"* → tampoco: falta otra.

Ng dice que vio equipos agregando herramientas sin parar para cubrir cada caso nuevo. **El enfoque es frágil e ineficiente.**

La alternativa: pedirle que escriba Python. Con pandas importado, el modelo tiene cientos o miles de funciones disponibles — y, sobre todo, funciones sobre las que vio muchísimos ejemplos de cuándo usarlas. El plan queda expresado en el código mismo: cargar el CSV, parsear la columna de fecha, ordenar, tomar las últimas cinco, mostrar el precio.

**La evidencia:** el vídeo cita el paper de Xingyao Wang y otros sobre *CodeAct*, con un orden claro de rendimiento: código > JSON > texto plano.

Dos salvedades:

- Vale la advertencia del Módulo 3 sobre **sandbox**, que Ng repite acá (y vuelve a admitir que muchos no lo usan).
- No aplica a todo: hay aplicaciones donde lo que necesitás es darle tus herramientas propias, no un intérprete.

## Sistemas multi-agente

La pregunta que siempre aparece en clase es la que Ng anticipa: *si es el mismo LLM al que le hablo varias veces, ¿para qué necesito varios agentes?*

Su respuesta es la analogía del software: también hay una sola CPU, y sin embargo descomponemos el trabajo en procesos y threads porque **nos resulta más fácil razonar y escribir así**. Multi-agente es lo mismo: no es una capacidad nueva del modelo, es una forma de descomponer el problema.

Y la segunda analogía, más práctica: en vez de preguntarte *¿a qué persona contrataría para esto?*, preguntáte *¿qué equipo de tres o cuatro roles contrataría?*. Las tareas complejas ya vienen descompuestas en el mundo humano:

| Tarea | Roles |
| --- | --- |
| Material de marketing | Investigador, diseñador gráfico, redactor |
| Artículo de investigación | Investigador, estadístico, redactor principal, editor |
| Preparar un caso legal | Asociados, paralegals, investigador |

### Cómo se construye cada agente

Un agente es **un LLM con un prompt de rol más las herramientas que ese rol necesita**. Para el equipo de marketing de anteojos de sol:

| Agente | Tarea | Herramientas |
| --- | --- | --- |
| Investigador | Analizar tendencias y competidores | Búsqueda web |
| Diseñador gráfico | Crear visualizaciones y arte | APIs de generación de imágenes, ejecución de código para gráficos |
| Redactor | Convertir todo en el folleto final | Ninguna: alcanza con generar texto |

La pregunta de diseño para cada uno es siempre la misma: **¿qué herramientas necesitaría un humano en ese rol?**

### Dos formas de coordinarlos

La primera es un **flujo lineal**: el investigador produce el informe, el diseñador lo usa para generar las piezas, el redactor junta todo y escribe el folleto.

La segunda es **planning con agentes**, y es el cierre elegante del módulo: es el mismo patrón de planning, pero donde antes había herramientas ahora hay agentes. El prompt dice "sos un gerente de marketing, tenés este equipo" y pide un plan paso a paso. El modelo responde: pedirle al investigador que investigue, después al diseñador las imágenes, después al redactor el informe, y quizás una reflexión final sobre el resultado.

Visto así, ese coordinador es **un cuarto agente**: el gerente de marketing.

**Ventaja práctica para el bootcamp:** cada agente se construye y se mejora por separado — encaja perfecto con las evals por componente del Módulo 4 — y después se reutiliza. Un diseñador gráfico hecho para folletos puede servir para posts de redes o para ilustrar páginas.

## Patrones de comunicación

Una vez que tenés varios agentes, la decisión de diseño es **quién le habla a quién**. Ng lo compara con armar un organigrama: es más difícil de lo que parece, y es un área de investigación activa. El curso muestra cuatro patrones, dos comunes y dos de frontera.

&#91;embedded content: patrones de comunicación · lineal y jerárquico\]

En el jerárquico conviene que cada agente le devuelva el resultado al manager en vez de pasárselo directo al siguiente: la implementación queda más simple.

### Los otros dos

**Jerarquía profunda.** Igual que el jerárquico, pero algunos agentes tienen sub-agentes propios: el investigador delega en un buscador web y un verificador de datos; el redactor, en un estilista y un chequeador de citas; el diseñador trabaja solo. Se usa, pero bastante menos: la complejidad sube rápido.

**Todos con todos.** Cualquier agente puede hablarle a cualquiera cuando quiera. Se implementa diciendo a cada agente quiénes son los otros; cada mensaje entra al contexto del que lo recibe, que decide cuándo responder, y el proceso sigue hasta que todos se declaran listos (o hasta que el redactor da el resultado por bueno).

El comentario honesto de Ng sobre este último: **los resultados son difíciles de predecir**. Sirve donde no necesitás mucho control — si el folleto sale mal, lo corés de nuevo — y hay desarrolladores que lo usan, con esa tolerancia al caos.

Cierre del módulo: hoy hay bastantes frameworks que facilitan armar sistemas multi-agente e implementar estos patrones.

## Para dar la clase

### Secuencia sugerida (90 min)

| Bloque | Min | Contenido |
| --- | --- | --- |
| Apertura | 10 | Repaso del hilo M2→M5. Qué decide el desarrollador y qué decide el modelo en cada patrón |
| Planning | 20 | El agente de atención al cliente, el plan en JSON, y la advertencia sobre control |
| Planning con código | 15 | El CSV de la máquina de café y el espiral de herramientas. CodeAct |
| Práctica | 25 | Lab del Customer Service Agent, o el propio proyecto con un plan en JSON |
| Multi-agente | 15 | El equipo de marketing: roles, herramientas por rol, coordinación |
| Cierre | 5 | Los patrones de comunicación y el cierre del curso |

### Puntos de pizarra

- La misma figura de planning dos veces: primero con herramientas (M3), después con agentes. Es literalmente el mismo dibujo con las cajas cambiadas.
- El espiral de herramientas: una consulta nueva → una herramienta nueva → otra consulta → otra herramienta.
- Los cuatro patrones de comunicación, de más controlado a más caótico.

### Errores típicos que conviene anticipar

- **Creer que multi-agente da una capacidad nueva.** Es el mismo modelo: lo que cambia es cómo descomponés el problema.
- **Arrancar con todos-con-todos.** Lineal o jerárquico cubren casi todo y son depurables.
- **Pedir el plan en texto libre.** Después hay que parsearlo: JSON desde el principio.
- **Usar planning donde alcanza tool use.** Si la secuencia es siempre la misma, hardcodearla es más barato y más controlable.
- **Olvidar el sandbox** cuando el plan se ejecuta como código.
- **Agentes sin eval.** Con varios agentes, las evals por componente del Módulo 4 dejan de ser opcionales.

### Preguntas para lanzar

1. ¿Su proyecto necesita planning, o la secuencia de pasos es siempre la misma?
2. ¿Qué equipo de tres roles contratarían para la tarea de su proyecto? ¿Qué herramienta necesita cada uno?
3. ¿Cuándo conviene que el plan sea código y cuándo JSON con herramientas propias?
4. Si el agente arma un plan malo, ¿cómo se dan cuenta? ¿Qué miden?
5. ¿Cuánta impredecibilidad tolera su aplicación?

## Fuentes

- [Agentic AI — Module 5: Patterns for Highly Autonomous Agents](https://learn.deeplearning.ai/courses/agentic-ai/lesson/jcl177/planning-workflows), DeepLearning.AI. Transcripciones de los cinco vídeos, consultadas el 13 de noviembre de 2026.
- [Wang et al. (2024), *Executable Code Actions Elicit Better LLM Agents* (CodeAct)](https://arxiv.org/abs/2402.01030) — fuente del gráfico que compara código, JSON y texto.
