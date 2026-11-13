# Módulo 4 — Evals y error analysis · guion de clase

Nov 13, 2026 · @Luciano · Agentic AI (DeepLearning.AI) → bootcamp Neoland

## Objetivos y mapa del módulo

Ng abre el módulo diciendo que estos tips son lo que separa a un equipo eficiente de uno que pierde meses, y lo cierra diciendo que es el módulo más importante del curso. Vale tratarlo así en el bootcamp: acá está el método de trabajo, no una técnica más.

Tres objetivos concretos:

1. Construir un prototipo rápido y mirar sus salidas para decidir qué evaluar.
2. Hacer error analysis sobre traces y priorizar con datos, no por intuición.
3. Distinguir evals end-to-end de evals por componente y saber cuándo usar cada una.

| Lección | Tipo | Duración |
| --- | --- | --- |
| Evaluations (evals) | Vídeo | 15 min |
| Error analysis and prioritizing next steps | Vídeo | 9 min |
| More error analysis examples | Vídeo | 5 min |
| Component-level evaluations | Vídeo | 3 min |
| Ungraded Lab: Adding a component-level eval to the research workflow | Lab | 15 min |
| How to address problems you identify | Vídeo | 9 min |
| Latency, cost optimization | Vídeo | 4 min |
| Development process summary | Vídeo | 3 min |
| Module 4 quiz | Evaluación | 10 min |

Este resumen cubre los siete vídeos; el lab queda fuera. Es el módulo más largo del curso: casi 50 minutos de video, probablemente dos clases.

## Empezar rápido y sucio

La primera recomendación es casi de actitud: **construí un sistema rápido y sucio y mirá cómo falla**, en vez de pasar semanas teorizando dónde va a fallar. Con el prototipo delante, el esfuerzo se dirige solo.

Ng lo dice con cuidado: rápido no quiere decir irresponsable — el prototipo igual tiene que ser razonable y no filtrar datos.

El ejemplo es el flujo de procesamiento de facturas (extraer cuatro campos y guardarlos en la base). Con el prototipo andando, agarrás 10 o 20 facturas, mirás las salidas una por una y anotás en una planilla qué salió mal:

| Factura | Resultado |
| --- | --- |
| 1 | OK |
| 2 | Confundió fecha de emisión con fecha de vencimiento |
| 3 | OK |
| 4 | OK |

Después de 20, aparece el patrón: se equivoca con las fechas. Y ahí está el punto del vídeo — **mirar las salidas no sirve solo para detectar errores, sirve para decidir qué vale la pena evaluar.** Si el patrón hubiera sido otro (nombres de proveedores internacionales, por ejemplo), el eval sería otro.

El ciclo completo queda así: construí → mirá las salidas → si sabés cómo arreglarlo, arreglalo; si no, poné un eval y usálo para guiar el trabajo.

## Evals end-to-end

Son las que miden el sistema entero: de la consulta del usuario a la salida final. El vídeo construye tres, y cada una ilustra una forma distinta de evaluar.

**1. Fecha de vencimiento de la factura.** Se anotan a mano las fechas correctas de 10–20 facturas en formato `YYYY-MM-DD`, se le pide al modelo que use ese mismo formato, se extrae con un regex y se compara con código. Hay una respuesta correcta distinta para cada factura.

**2. Largo del copy de marketing.** El asistente genera captions para Instagram con un límite de 10 palabras y se pasa: 17, 14, 11. El eval es contar palabras con Python y comparar contra 10. Acá el objetivo es el mismo para todos los ejemplos: no hay ground truth por caso.

**3. Talking points del research agent.** Para cada tema se definen tres a cinco puntos gold standard que un experto humano habría cubierto, y un LLM juez cuenta cuántos aparecen en el ensayo, devolviendo un JSON con el puntaje y una explicación. Se usa un juez porque hay demasiadas formas de mencionar un mismo punto como para hacerlo con regex.

De esos tres salen los dos ejes que organizan todo el tema: **cómo evaluás** (código o LLM juez) y **si tenés ground truth por ejemplo**.

&#91;embedded content: tipos de eval · 2×2 con los cuatro ejemplos del curso\]

El cuadrante de abajo a la derecha es el de la rúbrica de gráficos del Módulo 2: juez sin ground truth, misma rúbrica para todas las imágenes.

## Error analysis: dónde poner el esfuerzo

Un eval end-to-end te dice que el sistema falla. No te dice **qué componente** arreglar. Y eso importa: Ng dice que uno de los mayores predictores de qué tan bueno es un equipo es si sabe hacer error analysis disciplinado, porque sin eso se eligen componentes por intuición y se pierden meses mejorando algo que no movía la aguja.

### Vocabulario

- **Trace**: el conjunto de salidas intermedias de una corrida completa del agente.
- **Span**: la salida de un paso individual. Viene del mundo de observabilidad; en el curso se usa poco, pero aparece en la literatura.

### El método

1. Juntá **solo los casos donde la salida final fue mala**. Los que salieron bien se dejan de lado; por eso se llama *error* analysis.
2. Leé el trace completo de cada uno: qué devolvió cada paso.
3. Para cada paso, preguntá si ese resultado es **sensiblemente peor que el de un experto humano con la misma entrada**.
4. Anotá en una planilla qué componente falló en cada caso y contá.

El criterio del paso 3 es el más fino y conviene detenerse ahí: si el paso que elige las cinco mejores fuentes recibió solo artículos malos, no se le anota el error — hizo lo mejor que podía con lo que tenía. El error es del paso anterior.

### Los tres ejemplos del curso

| Sistema | Componentes sospechosos | Qué mostró el conteo |
| --- | --- | --- |
| Research agent | Términos de búsqueda, motor de búsqueda, selección de fuentes, fetch, redacción | Términos 5%, resultados de búsqueda 45% → cambiar el motor |
| Facturas | PDF a texto, extracción con LLM | La extracción con LLM concentraba casi todos los errores — tunear el OCR habría sido semanas perdidas |
| Emails de clientes | Consulta SQL, datos de la base, redacción del mail | 75% consulta SQL, algo de datos corruptos, 30% redacción |

Detalle para aclarar en clase: **los porcentajes no suman 100%**, porque un mismo caso puede tener errores en varios componentes.

Y la priorización final combina dos cosas: qué componente falla más **y** en cuál tenés ideas de cómo mejorarlo. Un componente problemático sin ideas para arreglarlo baja de prioridad.

## Evals por componente

Una vez que el error analysis dice qué componente arreglar, evaluar end-to-end cada vez que lo tocás es mal negocio por dos razones:

- **Es caro**: cada corrida ejecuta el flujo entero.
- **Es ruidoso**: la aleatoriedad del resto del sistema tapa una mejora chica en el componente que estás tocando.

La alternativa es un eval que mida solo ese componente. Para la búsqueda web del research agent:

1. Para un puñado de consultas, un experto define las fuentes **gold standard** — las páginas que cualquiera debería encontrar.
2. Se mide cuánto se superponen los resultados del buscador con esa lista, con métricas estándar de recuperación de información como **F1**.
3. Con esa métrica se barren hiperparámetros rápido: cambiar de motor (Google, Bing, DuckDuckGo, Tavily, You.com), variar la cantidad de resultados, acotar el rango de fechas.

Ventaja adicional en equipos: si hay gente distinta trabajando en componentes distintos, cada uno tiene una métrica clara para optimizar sin depender del resto.

**La advertencia:** antes de dar el trabajo por terminado, hay que correr igual el eval end-to-end. Mejorar un componente no garantiza mejorar el sistema.

## Cómo mejorar un componente

Ya sabés cuál arreglar. ¿Cómo? Depende de si es un componente con LLM o no.

### Componentes sin LLM

Buscador web, retrieval de RAG, ejecución de código, un modelo entrenado aparte. Dos caminos: **tunear sus hiperparámetros** o **reemplazarlo** por otro proveedor.

| Componente | Qué se tunea |
| --- | --- |
| Búsqueda web | Cantidad de resultados, rango de fechas |
| Retrieval de RAG | Umbral de similitud, tamaño del chunk |
| Detección de personas | Umbral de detección (falsos positivos vs negativos) |

### Componentes con LLM

Cuatro opciones, de la más barata a la más cara:

1. **Mejorar el prompt**: instrucciones más explícitas, o few-shot (agregar ejemplos de entrada y salida deseada).
2. **Probar otro modelo**: con aisuite es cuestión de cambiar un string, y el eval decide cuál queda.
3. **Descomponer el paso**: si un solo prompt tiene instrucciones demasiado complejas, partirlo en dos o tres llamadas — o en generación + reflexión, que es el Módulo 2.
4. **Fine-tuning**: lo último. Ng dice que no lo toca hasta haber agotado el resto, porque es caro en tiempo de desarrollo. Sirve cuando ya estás en 90–95% y necesitás exprimir los últimos puntos.

### Afinar la intuición sobre modelos

Una parte del vídeo que vale como consejo de carrera para los alumnos. El ejemplo: pedirle a un modelo que redacte información personal identificable (PII) de un resumen de llamada. Un modelo chico (Llama 3.1 8B) no sigue bien las instrucciones — devuelve la lista, el texto redactado y otra lista que no correspondía, y encima se le escapa el nombre. Un modelo frontier lo hace bien.

La moraleja: los modelos grandes son mejores siguiendo instrucciones; los chicos responden bien preguntas fácticas simples. Y cada proveedor se especializa en cosas distintas.

Tres hábitos que recomienda:

- Probar cada modelo nuevo que sale, abiertos y cerrados.
- Tener un set personal de evals para calibrar modelos entre sí.
- **Leer prompts ajenos**: publicados, de colegas, o buscados dentro de paquetes open source de gente que respetás. Lo repite en varios módulos.

## Latencia y costo

El orden importa: **primero calidad, después costo y latencia.** No es que no importen, es que lograr buena calidad suele ser lo más difícil, y optimizar lo que todavía no funciona es trabajo perdido.

Ng cuenta que a su equipo le pasó varias veces lanzar un workflow, tener tantos usuarios que el costo se volvió un problema, y tener que correr a bajarlo. Su comentario: es un buen problema para tener.

El método es el mismo en los dos casos — **medir por paso y recortar donde está el bulto**. Para el research agent:

| Paso | Latencia | Costo |
| --- | --- | --- |
| Generar términos de búsqueda | 7 s | 0,04 ¢ |
| Búsqueda web | 5 s | 1,6 ¢ por llamada |
| Elegir fuentes | 3 s | tokens |
| Fetch de páginas | 11 s | por llamada a la API |
| Redactar el ensayo | 18 s | tokens |

Con la tabla delante las decisiones son obvias: el fetch de páginas pide **paralelización**; la redacción, que es el paso más lento, pide probar un modelo más chico o un proveedor más rápido (hay empresas con hardware especializado para servir modelos). Y el ejercicio también sirve al revés: suele dejar claro que varios componentes no vale la pena tocarlos porque no mueven ni el costo ni el tiempo.

## El proceso: construir ↔ analizar

El cierre del módulo es el que más vale repetir en clase. Desarrollar un sistema agentic son dos actividades alternadas:

- **Construir**: escribir código, cambiar prompts, mejorar el sistema.
- **Analizar**: mirar traces, hacer error analysis, armar evals. No se siente como progreso, y es igual de importante.

Cómo madura, según el sistema avanza:

1. Sistema rápido y sucio end-to-end → mirar salidas y traces, intuición a ojo.
2. Primeros evals end-to-end con 10–20 ejemplos → métricas, no solo impresiones.
3. Error analysis sistemático → conteo por componente, prioridades con datos.
4. Evals por componente → iteración rápida sobre la pieza elegida.

No es lineal: se va y se vuelve entre las dos actividades todo el tiempo.

**El diagnóstico de Ng sobre equipos con menos experiencia:** construyen mucho y analizan poco. Y sobre herramientas: existen plataformas de observabilidad para traces, logs y costos, pero él termina escribiendo evals a medida igual, porque cada workflow agentic es bastante particular y los evals tienen que capturar los problemas específicos de ese sistema.

## Para dar la clase

Son casi 50 minutos de video: conviene partirlo en dos clases, con el corte natural después de error analysis.

### Clase 1 — Evals y error analysis (90 min)

| Bloque | Min | Contenido |
| --- | --- | --- |
| Apertura | 10 | Mostrar 20 salidas de un sistema del bootcamp y que anoten qué está mal |
| Evals end-to-end | 20 | Los tres ejemplos y la 2×2 |
| Práctica | 25 | Que escriban un eval de 10 ejemplos para su propio proyecto |
| Error analysis | 25 | Traces, spans, la planilla y los tres casos |
| Cierre | 10 | Que armen la lista de componentes de su sistema |

### Clase 2 — Componentes, costo y proceso (90 min)

| Bloque | Min | Contenido |
| --- | --- | --- |
| Repaso | 10 | Resultados del error analysis que hicieron |
| Evals por componente | 20 | Gold standard, F1, barrido de hiperparámetros |
| Práctica | 25 | Lab: agregar un eval de componente al research workflow |
| Mejorar componentes | 20 | No-LLM vs LLM, el caso PII, fine-tuning al final |
| Costo y proceso | 15 | Benchmark por paso y el vaivén construir ↔ analizar |

### Puntos de pizarra

- La 2×2 de evals, dibujada en vivo con los cuatro ejemplos.
- El flujo del research agent con un porcentaje de error anotado sobre cada paso.
- El timón del proceso: construir ↔ analizar, con las cuatro etapas de madurez.

### Errores típicos que conviene anticipar

- **Querer el eval perfecto antes de empezar.** 10 o 20 ejemplos alcanzan; el eval también se itera.
- **Elegir qué arreglar por intuición.** Es exactamente lo que el módulo viene a corregir.
- **Culpar al componente equivocado.** Si la entrada ya era mala, el error es del paso anterior.
- **Mirar solo los casos que salieron bien.** El análisis vive en los que fallaron.
- **Optimizar costo antes que calidad.**
- **Confiar ciegamente en la métrica.** Si el eval no refleja tu juicio sobre qué versión es mejor, el que hay que arreglar es el eval.

### Preguntas para lanzar

1. ¿En qué cuadrante de la 2×2 cae el eval que necesita su proyecto?
2. ¿Cuáles son los componentes de su sistema y cuál creen que falla más? ¿En qué se basan?
3. ¿Cómo distinguen un error del componente de un error heredado de la entrada?
4. Si su eval dice que la versión nueva es peor pero a ustedes les parece mejor, ¿qué hacen?
5. ¿Cuánto tiempo de la semana pasada pasaron construyendo y cuánto analizando?

## Fuentes

- [Agentic AI — Module 4: Practical Tips for Building Agentic AI](<https://learn.deeplearning.ai/courses/agentic-ai/lesson/pu5xbl/evaluations-(evals)>), DeepLearning.AI. Transcripciones de los siete vídeos, consultadas el 13 de noviembre de 2026.
