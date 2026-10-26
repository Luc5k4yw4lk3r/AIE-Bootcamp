---
tipo: tema
tags:
  - agentes
  - claude
---
# Agentic AI · Módulo 1 — Workflows Agénticos

Oct 26, 2026 · @Luciano

> Apunte de clase — Introducción a los Workflows Agénticos (curso *Agentic AI*, DeepLearning.AI / Andrew Ng)

## 1. ¿Qué es un workflow agéntico?

La idea central del módulo es el contraste entre **generación directa** y **workflow agéntico**.

Cuando le pedimos a un LLM "escribime un ensayo sobre X" y esperamos la respuesta completa de una sola pasada, estamos haciendo generación directa. Andrew Ng lo compara con pedirle a una persona que escriba un texto de la primera a la última palabra, de corrido y sin usar nunca el backspace. Ni las personas ni los modelos hacen su mejor trabajo así (aunque los LLM se defienden sorprendentemente bien).

Un **workflow agéntico** es un proceso en el que una aplicación basada en LLM ejecuta **varios pasos** para completar una tarea. Para escribir un ensayo, por ejemplo, el flujo podría ser:

1. Escribir un outline del tema.
2. Decidir si hace falta investigar en la web y, si corresponde, buscar y descargar páginas.
3. Escribir un primer borrador.
4. Releer el borrador y detectar qué partes necesitan revisión o más investigación.
5. Revisar y repetir.

Este ciclo **pensar → investigar → revisar** toma más tiempo que la generación directa, pero produce un resultado mucho mejor. Opcionalmente se puede incluir un paso de **human in the loop**: que el agente pida revisión humana de hechos clave antes de continuar.

> **La habilidad central del curso** es tomar una tarea compleja y descomponerla en pasos más chicos que el workflow pueda ejecutar uno a uno.

El ejemplo que atraviesa todo el curso es un **research agent**: un agente al que le das un tema (ej. *"cómo armar una empresa de cohetes para competir con SpaceX"*) y que planifica la investigación, busca y descarga fuentes, sintetiza y rankea hallazgos, arma un outline, lo revisa con un agente editor y finalmente genera un informe en markdown. El resultado es más profundo y pensado que pedirle directamente a un LLM que escriba el ensayo.

## 2. Grados de autonomía

Ng explica por qué habla de sistemas **agénticos** (adjetivo) en lugar de discutir si algo es o no "un agente de verdad" (binario). La pregunta útil no es *¿esto es un agente?* sino *¿qué tan agéntico es?*. Así se corre el foco del debate terminológico hacia la práctica de construir sistemas.

Los sistemas se ubican en un **espectro de autonomía**:

- **Menos autónomo:** la secuencia de pasos está **hardcodeada por el programador** (determinística). La autonomía vive solo en el texto que genera el LLM. Ej.: generar términos de búsqueda → llamar al buscador → escribir el ensayo, siempre en ese orden fijo.
- **Semi-autónomo:** el LLM toma algunas decisiones y elige herramientas, pero las herramientas están bastante predefinidas.
- **Altamente autónomo:** el agente decide por sí mismo la secuencia de pasos, e incluso puede escribir nuevas funciones o crear herramientas que luego ejecuta. Es más potente, pero menos controlable, más impredecible y aún materia de investigación activa.

### Convención de colores (se usa en todo el curso)

En los diagramas del curso, cada tipo de paso tiene un color:

- 🔴 **Rojo** = input del usuario (la query o el documento de entrada).
- ⚪ **Gris** = una llamada a un LLM.
- 🟢 **Verde** = un paso que usa otro software (ej. una API de búsqueda web, ejecutar código para descargar una página).

> **Idea para recordar:** hay muchísimo valor en el extremo *menos autónomo* del espectro. Ahí es donde hoy se construyen la mayoría de las aplicaciones útiles para empresas: más simples, más controlables y más confiables.

## 3. Beneficios de los workflows agénticos

### 1) Mejor rendimiento

Es el beneficio que más valora Ng. Su equipo midió sobre **HumanEval** (un benchmark de generación de código):

- **GPT-3.5** con generación directa: \~40% de aciertos.
- **GPT-4** con generación directa: \~67%.
- **GPT-3.5 envuelto en un workflow agéntico** (ej. escribir código → reflexionar → mejorarlo): rendimiento mucho más alto, que **supera a GPT-4 directo**.

La conclusión clave: el salto que da un workflow agéntico puede ser **mayor que el salto de toda una generación de modelo**. Envolver un modelo más viejo en un buen flujo rinde más que cambiar a un modelo más nuevo usado de forma directa.

### 2) Paralelismo

Un workflow puede ejecutar pasos **en paralelo** y así hacer cosas más rápido que una persona. Ejemplo: tres LLM generan términos de búsqueda en simultáneo, se descargan nueve páginas **al mismo tiempo** (un humano las leería una tras otra) y recién después se alimenta todo a un LLM para escribir el ensayo.

### 3) Modularidad

Al estar armado por componentes, podés **agregar, actualizar o reemplazar** cada pieza sin rehacer todo:

- Cambiar el motor de búsqueda (Google, Bing, DuckDuckGo, Tavily, you.com…).
- Meter un buscador de noticias para traer lo más reciente.
- Probar distintos LLM y proveedores en cada paso y quedarte con el que mejor funcione para ese paso.

## 4. Aplicaciones de IA agéntica

Ng recorre ejemplos ordenados de **más fácil a más difícil**:

1. **Procesamiento de facturas (invoice processing).** PDF → convertir a texto/markdown → el LLM decide si es factura → extrae campos (biller, dirección, monto, vencimiento) → usa una tool para guardar en la base de datos. *Fácil*: hay un proceso claro y paso a paso.
2. **Consultas básicas de pedidos (customer order inquiry).** Extraer info del email → consultar la base de órdenes → redactar respuesta → **cola de revisión humana** antes de enviar.
3. **Atención al cliente general.** Más difícil: las preguntas son abiertas ("¿tienen jeans negros o azules?", "quiero devolver la toalla") y el agente tiene que **planificar sobre la marcha** qué consultas y verificaciones hacer (stock, política de devoluciones, generar el slip, marcar el registro como *return pending*). Los pasos no se conocen de antemano.
4. **Computer use.** Lo más difícil y experimental. El agente navega un sitio web real, razona sobre la página, clickea y completa campos (ej. chequear vuelos en United y saltar a Google Flights cuando el primero falla). Potente, pero aún poco confiable (páginas lentas o elementos que el agente no interpreta bien).

### ¿Qué hace una tarea más fácil o más difícil de agentificar?

| Dimensión | Más fácil ✅ | Más difícil ⚠️ |
| --- | --- | --- |
| **Proceso** | Pasos claros y conocidos de antemano (o un procedimiento estándar ya existente) | Pasos desconocidos: hay que planificar o resolver sobre la marcha |
| **Modalidad** | Inputs solo de texto | Inputs multimodales (audio, imagen, video) |
| **Resultado** | Más confiable y predecible | Menos confiable y más impredecible |

## 5. Descomposición de tareas (task decomposition)

Es el método práctico para pasar de "lo que hace una persona" a "pasos discretos de un workflow". La **pregunta guía** al descomponer:

> ¿Cada paso lo puede hacer un **LLM**, un **fragmento corto de código**, una **función** o una **tool**?

El proceso es **iterativo**: se arranca simple y se descompone más cuando el resultado no alcanza.

1. Empezás con generación directa (1 paso).
2. Si no alcanza, descomponés en 3: outline → buscar en la web → escribir.
3. Si el resultado sigue flojo (ej. el ensayo quedó inconexo), **tomás un paso y lo volvés a descomponer**: escribir ensayo → primer borrador → marcar qué revisar → revisar.

La misma lógica aplica a los otros ejemplos (order inquiry, invoice): mirás cada paso y confirmás que alguno de los building blocks lo puede resolver.

### Building blocks

Las piezas con las que se arma cualquier workflow:

- **LLMs** (y modelos multimodales): generar texto, decidir qué llamar, extraer información.
- **Modelos de IA especializados**: PDF-a-texto, text-to-speech, análisis de imágenes.
- **Software tools / APIs**: búsqueda web, clima en tiempo real, enviar emails, calendario.
- **Retrieval / RAG**: traer datos de una base o el texto más relevante de un corpus grande.
- **Ejecución de código**: que el LLM escriba y corra código para resolver un rango enorme de tareas.

## 6. Evaluación (evals)

Para Ng, el **mayor predictor** de quién construye buenos workflows agénticos es tener un **proceso de evaluación disciplinado**.

### Idea contraintuitiva clave

**No diseñes las evals de antemano.** Es muy difícil anticipar qué va a salir mal. Mejor **construí primero, mirá muchos outputs a mano** y detectá lo que te gustaría que haga mejor. Ejemplo real: descubrís que el agente **menciona competidores** ("somos mejores que ComproCo") cuando no debería — algo imposible de prever antes de construirlo.

### Dos tipos de criterios

- **Objetivos → se evalúan con código.** Si el criterio es blanco o negro (mencionó un competidor o no), escribís código que busca los nombres en el output y cuenta la fracción de respuestas con el error.
- **Subjetivos → LLM as a judge.** Para cosas como "calidad del ensayo", usás otro LLM que puntué. **Advertencia honesta de Ng:** los LLM **no son buenos** con escalas 1–5; él casi no usa esa técnica, y más adelante el curso enseña métodos mejores.

### Lo que viene en el Módulo 4

- **Evals end-to-end:** miden la calidad del output del agente completo.
- **Evals component-level:** miden la calidad de un solo paso del workflow.
- **Error analysis:** leer los **outputs intermedios (traces)** de cada paso para encontrar oportunidades de mejora.

> Evals + error analysis es una habilidad central; el Módulo 4 la trabaja en profundidad.

## 7. Los 4 patrones de diseño

Son las formas típicas de combinar los building blocks. Cada uno se profundiza más adelante en el curso.

| Patrón | Qué hace | Ejemplo | Se ve en |
| --- | --- | --- | --- |
| **Reflection** | El LLM examina su propio output y lo mejora iterando | Genera código → lo critica (correctness, estilo, eficiencia) → lo corrige (v2, v3). Puede usar feedback externo (correr el código y leer el error) | Módulo 2 |
| **Tool use** | Darle al LLM funciones que puede llamar; el LLM decide cuál usar | Web search para "¿mejor cafetera según reviews?"; ejecución de código para un cálculo de interés compuesto | Módulo 3 |
| **Planning** | El LLM decide por sí mismo la secuencia de acciones | **HuggingGPT**: detectar pose → generar imagen → describir → text-to-speech, encadenando llamadas a modelos/APIs | Módulo 5 |
| **Multi-agent** | Varios agentes especializados por rol que colaboran como un equipo | **ChatDev** (CEO, programador, tester, diseñador); o un folleto hecho por un agente researcher + marketer + editor | Módulo 5 |

**Notas:**

- **Reflection** no es magia ni funciona el 100% de las veces, pero suele dar un buen salto de rendimiento. Variante: usar un *critique agent* separado en vez de que el mismo modelo se critique.
- **Planning** y **multi-agent** son más potentes para tareas complejas, pero más difíciles de controlar porque no sabés de antemano qué van a hacer los agentes.

## 8. Ideas clave y cómo sigue el curso

### Para llevarse del Módulo 1

- Un workflow agéntico ejecuta **varios pasos** en vez de generar todo de una; tarda más pero rinde mejor.
- "Agéntico" es un **adjetivo con grados**, no un binario; hay mucho valor en los sistemas menos autónomos.
- Los beneficios son **rendimiento, paralelismo y modularidad**.
- Las tareas más fáciles tienen **proceso claro + inputs de texto**.
- La habilidad central es la **descomposición de tareas**: ¿cada paso lo hace un LLM, código, una función o una tool?
- Las **evals** y el **error analysis** son lo que distingue a quien construye bien.
- Hay **4 patrones**: reflection, tool use, planning y multi-agent.

### Partes prácticas del módulo

- Lectura opcional de **setup del entorno local** para los labs no calificados.
- **Quiz** calificado del Módulo 1.
- Recurso **"Try the research agent"** para probar el agente que es el hilo conductor del curso.

### Qué viene después

- **Módulo 2 — Reflection:** deep dive en el primer patrón (sorprendentemente simple de implementar).
- **Módulo 3 — Tool use:** cómo darle herramientas al LLM.
- **Módulo 4 — Prácticas para construir:** evals, error analysis, latencia y costo.
- **Módulo 5 — Agentes muy autónomos:** planning y workflows multi-agente.

---

*Fuente: curso "Agentic AI" de DeepLearning.AI (Andrew Ng), Módulo 1 — Introduction to Agentic Workflows.*
