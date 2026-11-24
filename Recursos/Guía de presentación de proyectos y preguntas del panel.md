# Demo Day — Guía de pitch y preguntas del panel

Nov 24, 2026 · @Luciano

## Formato

Cada equipo presenta su proyecto final como si fuera una startup ante un panel de inversores: 10 minutos de pitch y 5 de preguntas (tiempos sugeridos, ajustables según la cantidad de equipos).

La parte técnica no desaparece: es la respuesta a “¿por qué tendría que creerles?”. El panel puntúa decisiones y evidencia, no cantidad de features.

El documento tiene dos partes. La primera es la guía para los equipos. La segunda es para el panel: banco de preguntas, preguntas de inversión, roles y rúbrica.

## Guía para los equipos: estructura del pitch

El pitch tiene ocho bloques y empieza por una persona con un problema, no por el stack.

| # | Bloque | Tiempo | Qué contar |
| --- | --- | --- | --- |
| 1 | Problema | 1 min | Quién lo sufre, cómo lo resuelve hoy y qué le cuesta en tiempo o dinero. |
| 2 | Solución | 30 s | Una sola frase: “Ayudamos a X a hacer Y sin Z”. |
| 3 | Demo en vivo | 3 min | Un único recorrido guiado por una historia de usuario. Incluir un momento en que el sistema pide confirmación o se abstiene. |
| 4 | Cómo funciona | 2 min | El diagrama de punta a punta, sin nombrar frameworks: qué decide el modelo, qué decide el código, qué roles de agente hay y qué expone el server MCP. |
| 5 | Evidencia | 1 min 30 s | La “tracción” del proyecto: dataset de evaluación, resultado antes y después de una mejora, costo y latencia por tarea. |
| 6 | Riesgos y confianza | 1 min | Qué encontró el red team, qué guardrails hay, qué datos salen del perímetro y cómo se clasificó el riesgo (AI Act / GDPR). |
| 7 | Negocio | 1 min | Quién pagaría, cuánto cuesta atender a un usuario y por qué no alcanza con un chat genérico. |
| 8 | Roadmap y pedido | 30 s | Qué sigue y cuánto dinero piden para hacerlo. El panel va a preguntar qué harían con distintos montos: conviene traerlo pensado. |

## Consejos para preparar el pitch

- Un número por slide, y que sea medido, no declarado.
- Ensayar la demo con cronómetro y tener un video de respaldo por si falla la conexión o la API.
- Definir quién habla en cada bloque y quién responde cada tipo de pregunta.
- Nombrar una limitación antes de que la pregunte el panel: suma más de lo que resta.
- Preparar tres slides de anexo para las preguntas: una traza real, el ADR más discutido y la tabla de evaluación.
- Llevar calculado el costo por tarea y el costo mensual por usuario; casi todas las preguntas de negocio salen de esos dos números.

## Banco de preguntas del panel

Si solo hay tiempo para cinco por equipo, las imprescindibles son: explicar el sistema sin frameworks, agente vs workflow, cómo saben que funciona, lo peor que puede pasar sin confirmación y el costo por tarea.

### Producto y negocio

- ¿Qué hace hoy su usuario sin este producto?
- ¿Por qué esto no se resuelve con ChatGPT o Claude y un buen prompt?
- Si el proveedor del modelo saca esto como feature mañana, ¿qué les queda?
- ¿Lo probó alguien de fuera del equipo? ¿Qué dijo?
- ¿Quién es su competidor más cercano y en qué son mejores?

### Arquitectura y decisiones

- Expliquen su sistema sin nombrar ningún framework.
- ¿Por qué un agente y no un workflow? ¿Qué parte es determinista?
- ¿Por qué varios agentes y no uno con más tools? ¿Lo midieron?
- ¿Qué pasa si esta tool falla, tarda 30 segundos o devuelve basura?
- ¿Qué gana el proyecto con MCP frente a tools nativas?
- ¿Qué guardan en memoria y qué pasa cuando la conversación se alarga?

### Evaluación

- ¿Cómo saben que funciona? ¿Qué número mejoró y con qué cambio?
- Muestren un caso en el que hoy falla.
- ¿Cómo armaron el dataset y quién decidió cuál es la respuesta correcta?
- Si cambian de modelo mañana, ¿cómo se enteran de si empeoró?

### Seguridad y cumplimiento

- ¿Qué es lo peor que puede hacer el agente sin pedir confirmación?
- ¿Qué encontró el red team y qué quedó sin arreglar?
- ¿Qué datos personales salen del perímetro y hacia quién?
- ¿Cómo clasificaron el sistema según el AI Act y qué obligación les cuesta más cumplir?

### Costos y operación

- ¿Cuánto cuesta una tarea completa? ¿Y atender a un usuario durante un mes?
- ¿Cuánto le cobrarían a ese usuario y qué margen les queda?
- ¿Cuántos clientes de pago necesitan para cubrir los costos del mes?
- ¿Qué parte del costo son tokens y qué parte es infraestructura?
- ¿Qué pasa con el negocio si el proveedor del modelo duplica el precio? ¿Y si lo baja a la décima parte?
- ¿Qué modelo usan para cada paso y cuánto ahorrarían con uno más barato o uno abierto?
- ¿Cuánto cuesta un error del agente (una acción mal hecha, una respuesta inventada) y quién lo paga?
- Abran una traza real y cuenten qué pasó y cuánto costó cada paso.

### Reflexión

- ¿Qué decisión revertirían si empezaran de nuevo?
- ¿Qué recortaron del alcance y por qué eso y no otra cosa?
- ¿Qué parte del código podrían reescribir sin asistente y cuál no?

## Preguntas de inversión: la escalera de montos

La misma pregunta se repite con cuatro montos, y lo que se evalúa es si el plan cambia de naturaleza en cada escalón o si solo “hacen más de lo mismo”.

| Monto | Pregunta | Qué muestra una buena respuesta |
| --- | --- | --- |
| 10.000 € | ¿Qué harían con 10 mil euros? | Validar: un piloto con usuarios reales, presupuesto de API para unos meses y una métrica concreta que quieren demostrar. |
| 100.000 € | ¿Y con 100 mil? | Pasar de prototipo a producto: primera contratación, meses de autonomía financiera y primeros clientes de pago. |
| 500.000 € | ¿Y con 500 mil? | Equipo y canal de venta: qué perfiles suman, cómo consiguen clientes y qué parte de la arquitectura hay que rehacer para sostenerlos. |
| 1.000.000 € | ¿Y con un millón? | Escalar: nuevos mercados o segmentos, cumplimiento serio y qué se rompe primero al multiplicar los usuarios por cien. |

Repreguntas para cualquier escalón:

- ¿En qué gastarían el primer euro?
- ¿Cuánto de ese dinero se va en tokens y cuánto en personas?
- ¿Cuántos meses les dura?
- ¿Qué métrica mostrarían para pedir la ronda siguiente?
- ¿Cambia la arquitectura con más dinero (modelo propio, fine-tuning, infraestructura dedicada) o solo cambia el volumen?
- ¿Qué no harían aunque tuvieran el dinero?
- ¿Cuál es el monto mínimo con el que el proyecto sigue vivo seis meses?

## Roles del panel

Cada persona del jurado toma un rol, así las preguntas no se pisan y los compañeros participan con un foco claro.

| Rol | Qué pregunta | Secciones del banco |
| --- | --- | --- |
| Inversor | Negocio, costos y la escalera de montos | Producto y negocio · Costos y operación · Preguntas de inversión |
| CTO | Arquitectura, trade-offs y evidencia | Arquitectura y decisiones · Evaluación |
| Usuario escéptico | La demo y los casos en que falla | Producto y negocio · Evaluación |
| Legal y seguridad | Datos, riesgos y acciones irreversibles | Seguridad y cumplimiento |

Cada rol elige dos o tres preguntas del banco y puede sumar una propia.

## Rúbrica del panel

Cada criterio se puntúa de 1 a 5, con un máximo de 35 puntos por equipo.

| Criterio | Un 5 se ve así | Un 1 se ve así |
| --- | --- | --- |
| Problema y usuario | Una persona concreta, un dolor medible y la alternativa actual. | “Es una app con IA para…” sin usuario identificable. |
| Demo | Un recorrido completo en vivo, con un caso límite mostrado a propósito. | Capturas o video sin explicación, o la demo no arranca y no hay respaldo. |
| Arquitectura y trade-offs | Explican cada pieza sin frameworks y nombran la alternativa descartada. | Lista de herramientas usadas sin justificar ninguna. |
| Evidencia | Dataset, número antes y después, y un caso de falla reconocido. | “Funciona bien” sin ninguna medición. |
| Seguridad y cumplimiento | Hallazgos del red team, confirmación en acciones irreversibles y flujo de datos claro. | No saben qué datos salen ni qué puede hacer el agente por su cuenta. |
| Negocio y costos | Costo por tarea, precio, margen y un plan distinto para cada monto de inversión. | No conocen el costo por tarea o el plan es igual con 10 mil que con un millón. |
| Respuestas a preguntas | Responden con datos, reconocen lo que no saben y se reparten las respuestas. | Se defienden sin datos o responde siempre la misma persona. |
