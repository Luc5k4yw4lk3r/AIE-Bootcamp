---
tipo: tema
tags: [prompting, llm]
---

# Prompting — Curso de Andrew Ng

Curso completo de Andrew Ng sobre cómo pasar de usar la IA como buscador a usarla como herramienta de trabajo. Los apuntes de abajo siguen el orden del vídeo y cada punto enlaza al minuto exacto.

- [Full AI Prompting Course with Andrew Ng — DeepLearningAI](https://www.youtube.com/watch?v=8ib4Qnh2HFE)

## Ideas principales

### 1. El cambio de mentalidad: Novato vs. Usuario Avanzado

- **De búsquedas simples a problemas complejos:** Los novatos usan la IA como si fuera un buscador de Google (preguntas cortas de una sola línea). Los usuarios avanzados le plantean problemas difíciles y le dan tiempo para "pensar" [[00:39](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=39)].
- **Empatía con la IA (Contexto):** Se propone pensar en la IA como un graduado universitario muy inteligente pero que no sabe nada de ti. Si le pides *"escribe mi evaluación anual"*, el resultado será genérico. Un usuario avanzado le sube notas de voz, capturas de pantalla y documentos para darle el contexto necesario [[01:47](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=107)].

### 2. Cómo se origina el conocimiento de la IA

- **Conocimiento preentrenado (Pre-trained knowledge):** La IA aprende patrones leyendo billones de palabras en internet (Reddit, Wikipedia, noticias, libros). Su fiabilidad depende de qué tan común sea el tema en la web (sabe mucho de cocina, pero menos de conceptos astronómicos específicos como los cuásares) [[10:08](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=608)].
- **Tolerancia a errores tipográficos:** Al estar entrenada con textos reales de internet, la IA entiende perfectamente comandos con faltas de ortografía o errores de tipeo; no hace falta perder tiempo corrigiendo cada letra al escribirle [[14:06](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=846)].

### 3. Búsqueda web (Web Search) y el problema del "corte de conocimiento"

- **Knowledge Cutoff:** El entrenamiento de un modelo se congela en una fecha exacta. Para eventos posteriores o información en tiempo real, necesita activar la búsqueda web [[15:55](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=955)].
- **Cómo funciona bajo el capó:** El modelo principal con el que chateas no lee las páginas web completas. Tiene un "asistente" que busca en Google/Bing, filtra y le pasa **resúmenes** al modelo principal. Esto puede provocar que la IA a veces malinterprete una fuente citada [[25:05](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=1505)].
- **Filtro de fuentes:** Por defecto, la IA prioriza los sitios más populares (como Reddit o Wikipedia). Si buscas información científica o médica, debes ordenarle explícitamente en el prompt que utilice fuentes oficiales (como la OMS o la FDA) [[21:43](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=1303)].

### 4. Investigación Profunda (Deep Research)

- **Modo Deep Research:** A diferencia de la búsqueda web común (que tarda segundos y usa pocas fuentes), este modo formula un plan de investigación, realiza múltiples búsquedas en paralelo, evalúa de forma autónoma qué sirve y qué no, y redacta un reporte completo. Puede tardar minutos en responder [[29:31](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=1771)].
- **Comportamiento Agéntico (Agentic AI):** Capacidad de la IA para tomar decisiones por sí misma sobre cuál debe ser el siguiente paso o qué términos nuevos buscar para profundizar [[31:54](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=1914)].

### 5. La IA como compañero de pensamiento (Thought Partner)

- **Brainstorming iterativo:** En lugar de pedirle una lista simple de ideas (que suele dar respuestas genéricas y de "sentido común"), la técnica correcta es darle mucho contexto, pedirle de 3 a 5 opciones, darle feedback sobre qué te gustó y qué no de esas opciones, y repetir el ciclo varias veces [[43:11](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=2591)].
- **Gestión del contexto (Context Window):** Los modelos actuales pueden procesar cientos de miles de palabras a la vez en su memoria de trabajo. Sin embargo, si vas a cambiar drásticamente de tema, es fundamental **abrir un chat nuevo** para limpiar la memoria y evitar que el contexto anterior distorsione o empeore la nueva respuesta [[52:56](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=3176)].

### 6. Modelos de Razonamiento y el sesgo de adulación

- **Ya no hace falta el "piensa paso a paso":** Con los modelos de razonamiento modernos, esa clásica instrucción de 2023 ya quedó obsoleta. Ahora basta con incluir palabras clave como *"piensa en profundidad"* u *"ultra think"* para que el modelo active su razonamiento lógico avanzado [[01:09:20](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=4160)].
- **Sicofancia (Sycophancy / Adulación):** Las IA están entrenadas con feedback humano (refuerzo basado en lo que nos gusta), por lo que tienden a darnos la razón de forma exagerada para complacernos. Si le dices *"tengo una gran idea de negocio, critícala"*, te elogiará. Para evitarlo, se debe usar un **enfoque neutral** (*"Analiza de forma objetiva los pros y contras de..."*) [[01:14:34](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=4474)].

### 7. Escritura, edición y el concepto de "AI Slop"

- **AI Slop (Basura de IA):** Textos que a primera vista parecen bien escritos pero que carecen de sustancia, abusan de listas de tres elementos, guiones largos (em-dashes) y palabras cliché como *"delve"* (ahondar) o *"nuanced"* (matizado) [[01:20:01](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=4801)].
- **Esquema progresivo (Progressive Outlining):** La mejor técnica para escribir con IA. Primero pídele un esquema (outline), edítalo y pídele cambios; luego expande cada punto en viñetas (bullet points) y, solo cuando estés conforme con la estructura, ordénale redactar el texto final [[01:22:52](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=4972)].
- **Uso de rúbricas objetivas para co-evaluar:** Si le pides opinión sobre tu texto, te dirá que es excelente debido a la adulación. Debes proporcionarle una **rúbrica de evaluación matemática y objetiva** (ej: *Puntaje de 0 a 25 si cumple X condición de SÍ o NO*). Incluso puedes usar un modelo (como ChatGPT) para escribir un texto y otro modelo distinto (como Gemini) para que lo evalúe con la rúbrica [[01:29:35](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=5375)].

### 8. Uso de Imágenes en los Prompts (Visión)

- Añadir imágenes a un prompt es una forma excelente de darle un contexto rico y rápido a la IA [[01:55:41](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=6941)].
- **Fortalezas:** La IA es muy buena para interpretar pizarras (incluso con texto tapado o matemáticas), transcribir notas manuscritas o calcular la división de una cuenta a partir de la foto de un recibo [[01:51:44](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=6704)], [[01:53:42](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=6822)], [[01:54:08](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=6848)].
- **Debilidades:** Tiende a ver las imágenes de forma general y suele fallar en detalles muy finos (por ejemplo, diferenciar máquinas de gimnasio muy parecidas entre sí) [[01:52:36](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=6756)].

### 9. Generación y Edición de Imágenes

- **Modelos de Difusión:** Tecnologías como *Imagen* o *Nano Banana* de Google generan imágenes reduciendo "ruido aleatorio" de forma secuencial hasta revelar una imagen nítida en base a la descripción dada [[01:59:39](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7179)].
- **El lenguaje del arte:** Conocer términos técnicos y artísticos (como *cinematic, cyberpunk, anime, watercolor*) ayuda a obtener mejores resultados. Si no conoces estos términos, puedes pedirle a un modelo de texto que te redacte el prompt ideal para la imagen que imaginas [[01:57:24](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7044)], [[01:58:02](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7082)].
- **Evolución:** Los modelos modernos han corregido errores virales del pasado (como deformaciones en las manos o texto mal escrito) y ahora permiten crear elementos complejos como infografías o personajes consistentes en diferentes cuadros [[01:59:17](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7157)], [[02:01:45](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7305)].

### 10. Creación de Apps y Mini-Juegos sin Saber Programar

- La IA democratiza la creación de software simple mediante instrucciones en lenguaje natural.
- Un prompt efectivo para este fin debe incluir tres pilares [[02:06:09](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7569)]:
    1. **El objetivo:** Qué se quiere construir (ej. un simulador de fuegos artificiales).
    2. **Las entradas (*Inputs*):** Qué hará el usuario (ej. hacer clic en la pantalla).
    3. **Las salidas (*Outputs*):** Qué mostrará la aplicación (ej. destellos de colores).
- Se recomienda empezar con proyectos sencillos e independientes (como contadores de tiempo Pomodoro, juegos de plataformas básicos o calculadoras de propinas) antes de intentar plataformas más complejas o multijugador [[02:07:08](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7628)], [[02:08:18](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7698)].

### 11. Análisis de Datos Automatizado

- Al subir archivos de datos (como hojas de cálculo de ventas o registros de salud de un reloj inteligente), la IA tiene la capacidad de escribir y ejecutar código en segundo plano de manera autónoma (*agéntica*) para procesarlos [[02:10:05](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7805)], [[02:11:44](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7904)].
- Esto le permite realizar cálculos exactos, crear gráficos personalizados con paletas visualmente atractivas e identificar las tendencias más importantes de forma eficiente sin que el usuario tenga que usar Excel directamente [[02:12:51](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=7971)], [[02:13:32](https://www.youtube.com/watch?v=8ib4Qnh2HFE&t=8012)].

## Relacionado

- [[M02·S02 - Prompting - Crear una app en 30 minutos]]
- [[M03·S03 - Claude y MCPs]]
