# Módulo 2 — Reflection Design Pattern · guion de clase

Nov 13, 2026 · @Luciano · Agentic AI (DeepLearning.AI) → bootcamp Neoland

## Objetivos y mapa del módulo

Al terminar la clase el alumno sabe montar un bucle de reflexión, decidir con datos si le conviene mantenerlo, y reconocer que el feedback externo es lo que lo vuelve realmente potente.

Tres objetivos concretos:

1. Implementar el patrón: generar → criticar → reescribir, con uno o dos modelos.
2. Escribir un prompt de reflexión con criterios explícitos.
3. Medir el impacto con evals objetivas (código) o subjetivas (rúbrica binaria).

| Lección | Tipo | Duración |
| --- | --- | --- |
| Reflection to improve outputs of a task | Vídeo | 3 min |
| Why not just direct generation? | Vídeo | 5 min |
| Chart generation workflow | Vídeo | 3 min |
| Ungraded Lab: Chart Generation | Lab | 15 min |
| Evaluating the impact of reflection | Vídeo | 8 min |
| Using external feedback | Vídeo | 4 min |
| Ungraded Lab: Improving SQL Generation with Reflection | Lab | 15 min |
| Module 2 quiz + M2 Graded Lab | Evaluación | \~70 min |

Este resumen cubre los cinco vídeos; los labs quedan fuera.

## Qué es el patrón Reflection

Es el patrón más simple del curso: en vez de quedarte con la primera salida del modelo, se la devolvés con un prompt distinto que le pide revisarla y reescribirla.

La analogía que usa Andrew Ng: escribís un mail apurado, lo releés y detectás que "el mes que viene" no dice ninguna fecha concreta, que hay un typo y que te olvidaste de firmar. Lo reescribís. Eso mismo hace el modelo.

El bucle, en tres pasos:

1. **Generación**: prompt → borrador v1 (mail, código, consulta SQL, gráfico).
2. **Reflexión**: el mismo u otro modelo recibe v1 con un prompt que le pide criticarlo según criterios.
3. **Revisión**: con esa crítica, se produce v2, que es la salida final.

En esta versión básica el flujo está hardcodeado: son dos llamadas al LLM, una detrás de la otra. No hay agente que decida nada todavía.

**Punto para subrayar en clase:** los dos pasos no tienen por qué usar el mismo modelo. Los modelos de razonamiento son buenos encontrando bugs, así que una configuración habitual es generar código con un modelo rápido y reflexionar con uno de razonamiento.

## Por qué no generación directa

La alternativa es la **generación directa**: un prompt, una respuesta, listo. "Escribí un ensayo sobre agujeros negros", "escribí la función de interés compuesto".

Aprovechá para fijar vocabulario, porque el curso lo usa todo el tiempo:

- **Zero-shot**: el prompt no incluye ningún ejemplo de la salida deseada. Es lo que hace la generación directa.
- **One-shot / few-shot**: el prompt incluye uno o varios pares entrada–salida de ejemplo.

La evidencia que muestra el vídeo viene de [Madaan et al. (2023), *Self-Refine: Iterative Refinement with Self-Feedback*](https://arxiv.org/abs/2303.17651): en siete tareas distintas (sentiment reversal, dialogue response, code optimization, code readability, math reasoning, acronym generation, constrained generation) y con varios modelos, la barra con reflexión queda consistentemente por encima de la zero-shot.

Dónde conviene más, según los ejemplos del curso:

| Caso | Qué aporta la reflexión |
| --- | --- |
| Datos estructurados simples (HTML básico) | Poco: los LLM ya lo hacen bien |
| JSON anidado, estructuras complejas | Detecta errores de formato |
| Secuencias de instrucciones | Encuentra pasos faltantes o incoherentes |
| Generación de nombres de dominio | Filtra nombres impronunciables o con connotaciones malas |

**La advertencia honesta del vídeo:** la reflexión no es magia. No garantiza acertar siempre; muchas veces da una mejora modesta. Por eso la sección de evals existe.

## El caso de los gráficos (multimodal)

Este es el ejemplo más vistoso del módulo y el que anticipa el lab: reflexión sobre una **imagen**, no sobre texto.

El escenario: datos de ventas de una máquina de café (latte, chocolate caliente, cappuccino…) en un CSV, y el pedido de comparar las ventas del Q1 de 2024 contra las de 2025.

La secuencia:

1. El LLM escribe código Python para el gráfico → v1.
2. Se ejecuta y sale un **gráfico de barras apiladas**: técnicamente correcto, visualmente malo.
3. Se le pasan a un modelo **multimodal** las dos cosas — el código v1 y la imagen generada — pidiéndole que mire el gráfico, lo critique y reescriba el código.
4. v2 sale con barras agrupadas, mucho más legible.

La clave didáctica: el modelo multimodal **razona visualmente sobre su propia salida**. No está adivinando si el gráfico quedó bien, lo está mirando.

El prompt de reflexión del ejemplo le asigna un rol ("analista de datos experto que da feedback constructivo"), le pasa el código v1, y le pide criticarlo según criterios concretos: legibilidad, claridad y completitud. Después, reescribir el código.

Y otra vez la variable de configuración: qué modelo genera y qué modelo reflexiona. El curso sugiere probar un modelo de razonamiento en el paso de reflexión.

## Medir si la reflexión sirve (evals)

El vídeo más largo del módulo, y el más importante para el bootcamp. La premisa: la reflexión agrega un paso y por lo tanto latencia y costo, así que antes de dejarla fija hay que comprobar cuánto mejora de verdad.

### Evals objetivas: el caso SQL

Escenario de una tienda: preguntas en lenguaje natural ("¿qué color de producto tiene más ventas totales?") que el LLM traduce a una consulta SQL. Con reflexión, un segundo paso revisa la consulta antes de ejecutarla.

El método:

1. Juntar 10–15 preguntas con su respuesta correcta (ground truth).
2. Correr el flujo sin reflexión y anotar el % de aciertos.
3. Correr el flujo con reflexión y anotar el % de aciertos.

El resultado del ejemplo: **87% sin reflexión, 95% con reflexión**. Hay respuesta correcta, así que la eval se escribe en código y es barata de repetir cada vez que se toca un prompt.

### Evals subjetivas: LLM-as-a-judge

Con los gráficos no hay respuesta correcta: ¿cuál de los dos es "mejor"? Ahí entra el LLM como juez, pero con dos cuidados que conviene remarcar:

- **Comparar dos salidas funciona mal.** El resultado es sensible a cómo está redactado el prompt y el ranking no suele coincidir con el juicio de un experto humano.
- **Sesgo de posición.** La mayoría de los modelos elige la primera opción que se les presenta, sea cual sea.

La alternativa que recomienda el curso: **calificar una salida por vez contra una rúbrica**, y que la rúbrica sea de criterios binarios, no una escala del 1 al 5 (los modelos están mal calibrados en escalas).

Para un gráfico, cinco criterios binarios del estilo: ¿tiene título claro? ¿están las etiquetas de los ejes? ¿es el tipo de gráfico apropiado? Se suman los sí y sale un puntaje de 0 a 5.

### La regla general

| Tipo de tarea | Enfoque de eval | Costo de puesta a punto |
| --- | --- | --- |
| Criterio objetivo (hay respuesta correcta) | Eval por código sobre ground truth | Bajo |
| Criterio subjetivo (calidad, estilo) | LLM-as-a-judge con rúbrica binaria | Alto: hay que calibrar la rúbrica |

Una vez montada la eval, cambiar el prompt de generación o el de reflexión deja de ser una corazonada y pasa a ser una medición.

## Feedback externo: el multiplicador

Si hay una idea que los alumnos tienen que llevarse del módulo, es esta: **la reflexión sin información nueva tiene techo; con información externa, no.**

El argumento, contado como una curva de rendimiento en el tiempo:

1. Solo prompt engineering sobre generación directa: mejora un rato y después se aplana. Más iteraciones no mueven la aguja.
2. Agregar reflexión: salto de rendimiento (a veces chico, a veces grande) a cambio de más complejidad.
3. Agregar feedback externo: la curva vuelve a subir, bastante más alto.

La señal práctica para los alumnos: *si estás tuneando prompts hace rato y ya no mejora nada, no sigas tuneando — buscá de dónde traer información nueva.*

Cuatro ejemplos concretos del curso, todos resueltos con código común, no con LLM:

| Tarea | Herramienta externa | Qué información nueva aporta |
| --- | --- | --- |
| Generar código | Ejecutarlo | Salida real y mensajes de error |
| Escribir emails | Regex sobre nombres de competidores | Si se coló una mención prohibida |
| Redactar con datos | Búsqueda web / fuente confiable | Verificación factual |
| Copy con límite de palabras | Contador de palabras | El número exacto, que el LLM no sabe |

El ejemplo del Taj Mahal es bueno para clase: el modelo escribe que se construyó en 1648. No es exactamente falso — se terminó ese año — pero se encargó en 1631, así que la frase pierde la historia real. Una búsqueda web que devuelva el período completo le da al paso de reflexión algo que por sí solo nunca iba a tener.

Y el del contador de palabras ilustra lo mismo desde el ángulo opuesto: los LLM siguen siendo malos para respetar límites exactos de extensión. Diez líneas de código resuelven lo que ninguna cantidad de prompt engineering resuelve.

Este es además el puente al Módulo 3: el feedback externo ya es, de hecho, uso de herramientas.

## Cómo escribir un prompt de reflexión

Dos reglas, repetidas en varios vídeos:

1. Decí explícitamente que querés que **revise o reflexione** sobre el primer borrador.
2. Dale **criterios concretos**. Un "mejoralo" genérico rinde mucho menos que una lista de qué mirar.

Los dos ejemplos del curso, útiles para mostrar en pantalla:

**Nombres de dominio** — Revisá los nombres que sugeriste. Verificá si cada uno es fácil de pronunciar. Verificá si puede significar algo negativo en inglés u otros idiomas. Devolvé una lista corta solo con los que cumplen estos criterios.

**Email** — Revisá el primer borrador del email. Controlá el tono. Verificá que todos los hechos y compromisos mencionados sean exactos. Según los problemas que encuentres, escribí el siguiente borrador.

Un detalle de método que vale contar a los alumnos: Ng dice que una de las formas en que aprendió a escribir mejores prompts fue **leer prompts ajenos** — bajarse software open source y leer los prompts que escribieron sus autores. Es una buena consigna de trabajo para el bootcamp.

## Para dar la clase

### Secuencia sugerida (90 min)

| Bloque | Min | Contenido |
| --- | --- | --- |
| Apertura | 10 | La analogía del email. Que escriban un borrador malo a propósito y lo critiquen a mano |
| Concepto | 15 | El bucle generar → criticar → reescribir. Zero-shot vs reflexión. Gráfico de Madaan |
| Demo | 15 | El caso de los gráficos: apilado → agrupado, con el modelo mirando la imagen |
| Práctica | 25 | Lab adaptado: que corran el bucle y prueben combinaciones de modelos |
| Evals | 15 | SQL 87% vs 95%. Rúbrica binaria para lo subjetivo |
| Cierre | 10 | Feedback externo y puente al Módulo 3 |

### Puntos de pizarra

- El bucle de tres pasos, dibujado con las dos llamadas al LLM separadas.
- La curva que se aplana: prompt engineering → reflexión → feedback externo.
- La tabla objetivo / subjetivo de evals.

### Errores típicos que conviene anticipar

- **Creer que reflexionar siempre mejora.** No: a veces el salto es despreciable. Por eso se mide.
- **Prompts de reflexión vagos.** "Mejorá esto" devuelve cambios cosméticos. Sin criterios no hay crítica.
- **Confundir reflexión con feedback externo.** Releer lo mismo no agrega información; ejecutar el código sí.
- **Comparar dos salidas con un LLM juez.** Sesgo de posición. Una por vez, contra rúbrica.
- **Olvidar el costo.** Cada reflexión es una llamada más: más latencia y más tokens.

### Preguntas para lanzar

1. ¿En qué tarea de las que ya hicieron habrían ganado más con reflexión? ¿Y en cuál nada?
2. ¿Qué información externa pueden conseguir con código para su proyecto?
3. Si el feedback externo es tan potente, ¿para qué sirve todavía la reflexión sola?
4. ¿Cómo arman la rúbrica binaria para evaluar la salida de su propio agente?
5. ¿Cuándo deja de valer la pena el paso extra de reflexión?

## Fuentes

- [Agentic AI — Module 2: Reflection Design Pattern](https://learn.deeplearning.ai/courses/agentic-ai/lesson/shknq1/reflection-to-improve-outputs-of-a-task), DeepLearning.AI. Transcripciones de los cinco vídeos, consultadas el 13 de noviembre de 2026.
- [Madaan et al. (2023), *Self-Refine: Iterative Refinement with Self-Feedback*](https://arxiv.org/abs/2303.17651) — fuente del gráfico comparativo citado en clase.
