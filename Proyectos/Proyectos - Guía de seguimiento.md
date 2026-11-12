# Cuatro mapas para no perderse en el proyecto

Nov 11, 2026 · @Luciano

Esta guía sirve para dirigir el trabajo de Claude sin saber programar. Sesión anotada muestra una fase completa paso a paso y Hoja de una página resume todo para tenerlo al lado.

## Cuatro mapas, cuatro preguntas

Hay cuatro mapas distintos, y cada uno responde una pregunta que el alumno se hace mientras el proyecto avanza. Tres salen de los diagramas del curso; el cuarto lo dibuja cada proyecto.

| Pregunta del alumno | Mapa | Dónde está |
| --- | --- | --- |
| ¿En qué momento del proceso estoy? | Ciclo de vida (Iniciativa → Mantenimiento) | Franja de abajo del mapa mental |
| ¿En qué parte del sistema estoy? | Cliente-servidor | El diagrama de arquitectura |
| ¿Qué está haciendo Claude Code, el agente que construye? | Agentic Loop + Memoria | Bloque naranja de Agentes del mapa mental |
| ¿Qué están haciendo los agentes que construimos? | Flujo de agentes del proyecto | Un diagrama propio de cada proyecto, más la ficha de cada agente |

El tercero es el que menos se usa, y es justo donde más se pierde el hilo. Lo que ven pasar en la terminal es el loop que ya vieron en clase: objetivo, plan, ejecución con herramientas, evaluación.

Si aprenden a leer la salida de Claude como "ahora está planificando", "ahora usa una herramienta", "ahora evalúa", dejan de ver ruido.

## Ficha de fase

Todas las fases se describen con los mismos seis campos, para que el alumno sepa siempre qué esperar y cuándo terminó.

| Campo | Qué se escribe | Ejemplo: Fase 1, persistencia |
| --- | --- | --- |
| Objetivo | Una frase de negocio | Cargar un dato en un formulario y volver a verlo después de recargar la página |
| Cajas del mapa | Qué partes del cliente-servidor se tocan | Navegador, puerto 8000, servidor FastAPI, base de datos |
| Pedido a Claude | Qué se le pide, acotado a la fase | Un formulario mínimo, un endpoint que guarda y otro que lista. Sin diseño ni login. |
| Validación | Qué hago, dónde miro, qué veo | Cargo el dato. Veo la llamada en DevTools. Veo la fila nueva en la base de datos. Recargo y el dato sigue ahí. |
| Señales de alarma | Qué indicaría que algo está mal | El dato aparece en pantalla pero no en la base de datos: quedó en la memoria del programa. Se confirma reiniciando el servidor; si el dato desaparece, no se guardó. |
| Punto de guardado | El commit que cierra la fase | Commit "Fase 1: persistencia", con la bitácora actualizada |

Conviene que la Fase 1 sea este recorrido fino de punta a punta. Se ve todo el mapa funcionando desde temprano, aunque sea feo.

### La Fase 0 con la misma ficha

La Fase 0 es la fundación: no construye ninguna funcionalidad, deja el proyecto listo para construir.

| Campo | Fase 0, fundación |
| --- | --- |
| Objetivo | Tener el entorno creado, las reglas y las specs revisadas y la base conectada |
| Cajas del mapa | Estructura de proyectos (CLAUDE.md o AGENTS.md, specs, versionado) y base de datos |
| Pedido a Claude | Pegar el template de inicialización, después el PRD, después los datos de conexión a la base de datos para que los guarde en .env |
| Validación | Leo CLAUDE.md entero en un par de minutos y no encuentro contradicciones ni estado del proyecto. Cada spec tiene criterios de aceptación que puedo verificar. Veo la base de datos creada. Hay un primer commit. |
| Señales de alarma | CLAUDE.md con párrafos copiados del PRD. Specs que dicen cómo programar en vez de qué debe pasar. Claude ya empezó a construir funcionalidades. Credenciales en un archivo que se sube al repositorio. |
| Punto de guardado | Commit "Fase 0: fundación" |

CLAUDE.md y las specs se validan contra lo visto en MA·S04, Spec-driven development.

Si la Fase 0 queda mal, todas las fases siguientes heredan el problema. Vale más repetirla que arrastrarla.

## Dónde mirar

Cada hexágono amarillo del diagrama cliente-servidor es una ventana al sistema real. Acá no se le pregunta a Claude: se mira directamente el navegador, el servidor, la base de datos o el código.

Hay dos formas de saber algo del proyecto. Preguntarle a Claude da una interpretación; mirar el sistema da el hecho. Cuando no coinciden, gana el sistema, y esa diferencia es justo lo que hay que llevarle a Claude.

| Quiero saber | Dónde miro | Qué debería ver |
| --- | --- | --- |
| ¿El servidor está corriendo? | La terminal donde se lanzó | Un mensaje de que escucha en el puerto 8000, sin errores debajo |
| ¿Qué sabe hacer el servidor? | localhost:8000/docs en el navegador (si es FastAPI) | La lista de endpoints, cada uno con un botón para probarlo sin tocar código |
| ¿El navegador le habló al servidor? | DevTools de Chrome, pestaña Network | La llamada a la API con un código que empieza en 2 |
| ¿Qué respondió el servidor? | La misma llamada en DevTools, o Postman | Los datos esperados |
| ¿Hay errores que la pantalla no muestra? | DevTools de Chrome, pestaña Console | Ninguna línea en rojo |
| ¿Se guardó el dato? | Las tablas de la base de datos | Una fila nueva con lo que cargué |
| ¿Qué pasó adentro del servidor? | Los logs | Una línea por pedido; si falló, el error |
| ¿Qué archivos cambió Claude? | El panel Source Control de VS Code | Los archivos modificados desde el último commit, con el antes y el después |
| ¿Qué debería hacer el sistema? | Las specs | El criterio de aceptación de esa funcionalidad |
| ¿Por qué no arranca el servidor? | Los puertos ocupados del sistema operativo | Si otro proceso ya usa el 8000 |
| ¿Se instaló la librería? | pip freeze | La librería en la lista |
| ¿La máquina da abasto? | El administrador de tareas | Procesos, memoria y disco con margen |
| ¿Qué hizo un agente propio? | El registro de esa ejecución: la conversación de Claude Code, la consola y los logs, o las trazas, según cómo esté escrito | Qué recibió, qué herramientas usó y qué devolvió |

### Cómo se ve cada ventana

Cuatro esquemas de las ventanas que más se usan, con lo que hay que mirar marcado. Son dibujos simplificados: las pantallas reales tienen más botones, pero lo marcado está en el mismo lugar.

&#91;embedded content: terminal del servidor · 2 líneas clave\]

La terminal responde dos preguntas: si el servidor arrancó y si le llegó cada pedido.

&#91;embedded content: DevTools, pestaña Network · una fila por pedido\]

DevTools se abre con F12 o clic derecho, Inspeccionar. Si la lista está vacía, hay que repetir la acción con la pestaña ya abierta.

&#91;embedded content: tabla de la base de datos · la fila nueva\]

Las tablas se ven en la consola web de la base de datos. Después de cargar un dato hay que refrescar la vista.

&#91;embedded content: página /docs del servidor · 3 direcciones\]

Esta página existe sola cuando el servidor es FastAPI: alcanza con abrir localhost:8000/docs con el servidor encendido.

## Técnicas sin código, paso a paso

Son cinco ejercicios para entender el sistema mirándolo, sin leer ni escribir código. Los tres primeros usan las ventanas de "Dónde mirar"; los dos últimos son archivos que Claude mantiene.

### 1. Seguir un dato

Consiste en cargar un dato reconocible y verlo pasar, en orden, por cada parte del sistema.

1. Abrir las cuatro ventanas antes de empezar: la aplicación en el navegador, DevTools en la pestaña Network, la terminal del servidor y la tabla de la base de datos.
2. Cargar un dato imposible de confundir, por ejemplo "PRUEBA-JUEVES-01".
3. Pantalla: ¿aparece en la lista?
4. Network: ¿salió una llamada nueva? Al abrirla, Payload muestra lo que se envió y Response lo que contestó el servidor.
5. Terminal: ¿hay una línea nueva para ese pedido?
6. Base de datos: ¿hay una fila con "PRUEBA-JUEVES-01"?
7. Recargar la página: ¿el dato sigue ahí?

**Para qué sirve.** Si el dato se pierde, se sabe entre qué dos ventanas se perdió. Eso es exactamente lo que se le dice a Claude: "llega al servidor pero no aparece en la base de datos".

### 2. Predecir antes de probar

Consiste en escribir qué va a pasar antes de ejecutar cada paso del plan de pruebas.

1. Leer el paso.
2. Escribir en una línea qué se va a ver y en qué ventana.
3. Ejecutar el paso.
4. Comparar lo escrito con lo que pasó.

**Ejemplo.** Predicción: "Si cargo una tarea sin título, espero un mensaje de error en pantalla y ninguna fila nueva en la base de datos". Resultado: apareció una fila vacía. La spec decide quién tiene razón; si dice que el título es obligatorio, es un error para llevarle a Claude.

**Para qué sirve.** Obliga a tener una idea de cómo funciona el sistema antes de mirar. Cuando la predicción falla, o hay un error en el sistema o hay un hueco en lo que el alumno entendió, y las dos cosas conviene encontrarlas.

### 3. Romper algo a propósito

Consiste en provocar una falla conocida para aprender cómo se ve, cuando todavía no asusta.

1. Confirmar que el commit está hecho.
2. Elegir una falla de la tabla.
3. Predecir en qué ventana se va a ver.
4. Provocarla y recorrer las ventanas.
5. Anotar el síntoma junto a su causa.
6. Dejar todo como estaba.

| Qué rompo | Qué se ve | Dónde |
| --- | --- | --- |
| Apago el servidor con Ctrl+C en su terminal | La pantalla no carga datos y la llamada aparece en rojo, sin código | Navegador y Network |
| Corto internet con el servidor encendido | El servidor sigue vivo pero no llega a la base de datos: error de conexión en la terminal y, normalmente, un código 500 | Terminal y Network |
| Envío el formulario con un dato inválido | Un código 422 con el detalle del campo rechazado, si el servidor es FastAPI | Network |
| Pido una dirección que no existe, como localhost:8000/nada | Un código 404 | Navegador |

**Para qué sirve.** Queda una tabla propia de síntoma y causa. Cuando aparezca un error real, la mayoría ya se reconoce.

### 4. MAPA.md

Es un archivo que traduce las carpetas del proyecto a las cajas del diagrama cliente-servidor.

Se le pide a Claude: "Quiero que crees MAPA.md con una tabla: cada carpeta o archivo principal, qué hace en una línea sin jerga y a qué caja del diagrama cliente-servidor pertenece. Quiero que lo actualices al cerrar cada fase".

Ejemplo ilustrativo de lo que devuelve:

| Carpeta o archivo | Qué hace | Caja del mapa |
| --- | --- | --- |
| app/main.py | Arranca el servidor | Servidor web |
| app/routers/ | Una función por cada cosa que el navegador puede pedir | Servidor web, la API |
| app/models/ | La forma de cada tabla | Base de datos |
| frontend/ | Lo que se ve en pantalla | Frontend |
| specs/ | Qué debe hacer el sistema | Documentación |
| .env | Los datos de conexión; no se sube al repositorio | Infraestructura |

**Para qué sirve.** Cuando Claude dice "modifiqué app/routers/tareas.py", el alumno sabe en qué parte del sistema está parado.

### 5. GLOSARIO.md

Es el diccionario propio del proyecto, en lenguaje de negocio.

Se agrega esta regla a CLAUDE.md, porque vale en todas las fases: "Cada término técnico que no esté en GLOSARIO.md se agrega con una definición de una línea en lenguaje de negocio y un ejemplo de este proyecto".

Ejemplo ilustrativo:

| Término | Qué es | En este proyecto |
| --- | --- | --- |
| Endpoint | Una dirección del servidor que hace una sola cosa | /tareas guarda y lista tareas |
| Migración | Un cambio en la forma de las tablas | Agregar la columna de vencimiento |
| 422 | El servidor rechazó los datos por incompletos o inválidos | Enviar una tarea sin título |

**Para qué sirve.** Las explicaciones de Claude dejan de tener palabras desconocidas, y el glosario muestra cuánto se aprendió.

## Cómo leer a Claude: el agentic loop

Lo que pasa por la terminal es siempre el mismo ciclo de cuatro etapas. Reconocer en cuál está alcanza para dejar de ser espectador.

| Etapa | Qué se ve en la terminal | Qué hace el alumno |
| --- | --- | --- |
| Objetivo | Claude repite con sus palabras lo que entendió del pedido | Comparar con lo que quiso pedir. Si no coincide, corregir ahora, que todavía no cuesta nada. |
| Plan | Una lista de pasos o tareas, a veces con los archivos que va a crear | Leerlo entero. Preguntar qué cajas del mapa toca y cómo se va a probar. Dar el OK recién ahí. |
| Ejecución | Lectura y edición de archivos, comandos, instalaciones, pedidos de permiso | No hace falta entender cada línea. Mirar qué archivos toca y si coinciden con el plan. Leer cada permiso antes de aceptarlo. |
| Evaluación | Corre pruebas, lee errores, se corrige y vuelve a intentar | Es donde aparece más texto rojo, y es normal. Contar cuántas vueltas lleva sobre lo mismo. |

El loop vuelve de Evaluación a Plan todas las veces que haga falta. Que Claude se corrija solo es parte del diseño, no una falla.

### Señales de que el loop se trabó

- Tres vueltas seguidas sobre el mismo error.
- Empieza a tocar archivos que no tienen que ver con la fase.
- Cambia la prueba o la spec para que "pase", en vez de arreglar el código.
- Dice "listo" sin haber corrido ni probado nada.

Ante cualquiera de las cuatro: frenarlo y pedirle un diagnóstico antes de que siga arreglando.

## Memoria: qué recuerda Claude y qué no

Claude arranca cada sesión nueva sin recordar la conversación anterior. Lo que sabe del proyecto sale de lo que quedó escrito en archivos, así que cuidar esos archivos es cuidar su memoria.

| Pieza | Qué guarda | Cuánto dura | Quién la cuida |
| --- | --- | --- | --- |
| CLAUDE.md / AGENTS.md | Reglas fijas del proyecto: stack, convenciones, cómo correr y cómo probar | Se lee al empezar cada sesión | El alumno la revisa al cerrar cada fase |
| Rules | Reglas de negocio que no cambian | Permanente | El alumno, que es quien conoce el negocio |
| Specs | Qué debe hacer el sistema, con criterios de aceptación | Permanente; cambia cuando cambia el comportamiento | El alumno lee cada cambio |
| Contexto | Todo lo dicho y leído en la sesión actual | Solo esta sesión, y se llena | Se gestiona con clear y compact |
| Bitácora (ESTADO.md, propuesta) | Qué está hecho, qué sigue, qué quedó pendiente | Permanente | Claude la actualiza al cerrar la sesión; el alumno la lee al abrir la siguiente |

### Dónde va cada cosa

- Vale siempre, en cualquier fase → CLAUDE.md.
- Describe qué hace el sistema → spec.
- Describe por dónde vamos → bitácora.

La mayoría de los CLAUDE.md sucios nacen de mezclar la tercera con la primera.

### Cuándo usar cada comando

| Situación | Comando | Qué pasa |
| --- | --- | --- |
| Termina una fase y empieza otra | clear | Contexto limpio. Pedirle que lea la bitácora para ubicarse. |
| La sesión viene larga y la tarea no terminó | compact | Resume la conversación y libera espacio. |
| Se cerró la terminal o se retoma al otro día | resume | Vuelve a la sesión anterior. |

### Señales de un CLAUDE.md sucio

- Instrucciones que se contradicen.
- Estado del proyecto mezclado con reglas ("ya hicimos el login").
- Párrafos copiados de las specs.
- No se puede leer de corrido en un par de minutos.
- Reglas que nadie recuerda por qué están.

### Una spec sana tiene

- Criterios de aceptación que un no técnico puede verificar.
- Ejemplos concretos, con datos.
- Un "fuera de alcance" explícito.

Regla de oro: si cambia el comportamiento, primero cambia la spec, y el alumno lee ese cambio.

## Pasos mentales: preguntas para hacerse

El alumno no necesita saber programar para dirigir el trabajo; necesita hacerse las preguntas correctas en cuatro momentos.

### Antes de dar el OK a un plan

- ¿Puedo decir en una frase qué va a existir al terminar que hoy no existe?
- ¿Qué cajas del mapa cliente-servidor toca?
- ¿Está dentro de la fase actual o Claude se adelantó?
- ¿Cómo lo voy a probar yo, a mano?

Si alguna queda sin respuesta, se le pregunta a Claude antes de avanzar.

### Mientras Claude trabaja

- ¿En qué etapa del loop está?
- ¿Está tocando lo que dijo el plan?
- ¿Cuántas vueltas lleva sobre el mismo error?

### Cuando Claude dice "listo"

- ¿Lo vi funcionar yo, o solo me lo contó?
- ¿En qué ventana lo verifiqué: navegador, DevTools, base de datos, logs?
- ¿Coincide con lo que dice la spec?
- ¿Puedo explicárselo a un compañero en dos minutos?

"Listo" significa que el alumno lo vio funcionar, no que Claude lo afirmó.

### Antes de cerrar la sesión

- ¿Quedó el commit hecho?
- ¿Está actualizada la bitácora?
- ¿Sé cuál es el próximo paso?

## Frases para decirle a Claude

Once frases para copiar y pegar cubren casi todos los momentos en que un alumno no sabe qué escribir.

| Momento | Frase |
| --- | --- |
| Al abrir una sesión nueva | "Quiero que leas la bitácora y las specs de la fase actual y me digas dónde estamos antes de hacer nada." |
| Antes de empezar una tarea | "Antes de escribir código, quiero que me expliques el plan en lenguaje no técnico, qué partes de la arquitectura cliente-servidor vas a tocar y cómo lo voy a probar yo. No avances hasta que te dé el OK." |
| Para mantener el alcance | "Quiero que trabajes solo en la fase actual. Si ves algo para mejorar fuera de ella, quiero que lo anotes en la bitácora y no lo toques." |
| Al terminar una tarea | "Quiero que me expliques qué hiciste, qué archivos tocaste y por qué, como si yo no fuera técnico." |
| Para probar | "Necesito un plan de pruebas manuales paso a paso: qué hago, dónde miro y qué debería ver en cada paso." |
| Para comprobar que entendí | "Quiero que me hagas tres preguntas para verificar que entendí lo que construiste." |
| Cuando aparece un error | "No arregles nada todavía. Primero quiero el diagnóstico: en qué parte del sistema está el problema y por qué pasa." |
| Al cerrar la sesión | "Quiero que actualices la bitácora con lo hecho, lo que sigue y lo pendiente, y que hagas el commit." |
| Para ver el flujo de agentes propios | "Quiero un diagrama del flujo de agentes: quién le pasa qué a quién y qué herramientas usa cada uno." |
| Para probar un agente propio solo | "Quiero que corras solo este agente con esta entrada y me muestres qué recibió, qué herramientas usó y qué devolvió." |
| Cuando un agente propio se equivoca | "No cambies nada todavía. Quiero saber si el problema está en las instrucciones del agente, en sus herramientas o en los datos que recibió." |

## Skills, herramientas y técnicas para entender lo que se construye

Conviene sumar pocas cosas. La mayoría de lo que ayuda ya viene en Claude Code o en Archify, y el resto son ejercicios que no requieren programar.

### Ya incluido en Claude Code

| Herramienta | Qué hace | Cuándo usarla |
| --- | --- | --- |
| Estilo Explanatory | Claude agrega bloques "Insight" que explican por qué eligió cada cosa. Se activa con `/output-style explanatory` o desde `/config`. | Toda la cursada |
| Estilo propio del curso | Un archivo en `.claude/output-styles/` que le dice a Claude cómo explicar (ejemplo abajo) | Incluirlo en el template de inicialización |
| Plan mode | Claude investiga y propone sin tocar archivos. Se activa empezando el pedido con `/plan`. | Al empezar cada tarea |
| `/diff` | Muestra qué cambió en los archivos | Antes de cada commit |
| `/rewind` | Vuelve el código, la conversación o ambos a un punto anterior de la sesión | Cuando un intento salió mal |
| `/context` | Muestra cuánto contexto lleva usado la sesión | Para decidir entre compact y clear |

- El estilo Learning también existe, pero le pide al alumno que escriba partes del código. Sirve solo para perfiles técnicos.
- `/rewind` no deshace lo que hicieron comandos de terminal. El commit sigue siendo el punto de guardado real.

Fuentes: [output styles](https://code.claude.com/docs/en/output-styles), [permission modes](https://code.claude.com/docs/en/permission-modes), [checkpointing](https://code.claude.com/docs/en/checkpointing), [commands](https://code.claude.com/docs/en/commands).

### El estilo Explanatory en detalle

Con Explanatory, Claude hace la tarea igual que siempre y además explica por qué eligió cada cosa. La explicación aparece en la conversación, en un bloque llamado Insight, y no se escribe en los archivos.

Ejemplo ilustrativo de un Insight, después de crear la parte del servidor que guarda tareas:

```text
★ Insight ─────────────────────────────────────
- El servidor revisa los datos antes de guardarlos, así que una tarea sin título nunca llega a la base.
- La conexión a la base de datos se lee del archivo .env; por eso no aparece ninguna contraseña en el código.
─────────────────────────────────────────────────
```

**Cómo activarlo**

1. En Claude Code, escribir `/output-style explanatory`.
2. Si ese comando no existe en la versión instalada, escribir `/config` y elegir Output style.
3. En la extensión de VS Code, escribir `/` y elegir Output styles.

La elección queda guardada para ese proyecto. Para volver atrás: `/output-style default`.

**Qué hacer con cada Insight**

- ¿De qué caja del mapa está hablando?
- ¿Hay un término que no conozco? Va al glosario.
- ¿Lo puedo comprobar en alguna ventana de "Dónde mirar"?

**Qué tener en cuenta**

- Las respuestas son más largas, así que cada sesión consume más.
- Los Insights explican decisiones de código y pueden resultar técnicos para quien no programa.
- Solo hay un estilo activo a la vez. Conviene empezar con Explanatory y, si los Insights quedan lejos del negocio, pasar al estilo propio del curso que sigue.

### Un estilo propio para el curso

Este archivo hace que Claude cumpla solo buena parte de las frases y los pasos mentales de este documento, sin que el alumno tenga que pegarlos cada vez.

```text
---
name: Modo alumno
description: Explica cada cambio en lenguaje de negocio y lo ubica en el mapa cliente-servidor
keep-coding-instructions: true
---

Quien dirige este proyecto conoce el negocio pero no programa.

Antes de cada tarea, decir en una frase qué va a existir al terminar, qué partes del sistema se tocan (navegador, API, servidor, base de datos) y cómo se prueba a mano.

Después de cada tarea, explicar qué cambió sin jerga. Cada término técnico nuevo se define en una línea.

Cerrar siempre indicando dónde mirar para comprobarlo directamente en el sistema: pantalla, pestaña Network, tablas de la base de datos o logs.

No dar nada por terminado sin haberlo ejecutado.
```

Se guarda como `.claude/output-styles/modo-alumno.md`, se reinicia Claude Code y se elige desde `/config`, en Output style.

### Archify, más allá del diagrama de arquitectura

- **Secuencia de una sola acción.** "Qué pasa cuando aprieto Guardar", paso a paso entre navegador, servidor y base.
- **Flujo de datos.** Por dónde viaja un dato desde que entra hasta que queda guardado.
- **Ciclo de vida.** Los estados por los que pasa una entidad del negocio: borrador, enviada, aprobada.
- **Antes y después.** Regenerar el diagrama de arquitectura al cerrar cada fase y compararlo con el anterior. Lo nuevo es lo que se construyó.

Las skills de Playwright y Chrome DevTools, que ya están en el mapa del curso, sirven para pedirle a Claude que ejecute el plan de pruebas en el navegador con una captura por paso. Después el alumno repite esos pasos a mano.

Fuente: [Archify](https://github.com/tt-a1i/archify).

## Los agentes que construimos

En estos proyectos hay agentes en dos lugares. Claude Code construye el sistema; los agentes propios son parte del sistema y hacen el trabajo del negocio. En el resto de la guía, "Claude" es siempre Claude Code.

### El que construye y los que construimos

|  | Claude Code, el que construye | Los agentes propios |
| --- | --- | --- |
| Qué hace | Escribe y modifica el proyecto | El trabajo del negocio: buscar, analizar, redactar, decidir |
| Cuándo corre | Mientras se desarrolla | Cada vez que alguien usa el sistema, o cuando se lo prueba |
| Quién le da instrucciones | El alumno, en la conversación | Las instrucciones escritas dentro del propio agente |
| Dónde se lo ve | En la terminal de Claude Code | En el registro de cada ejecución |
| Si algo sale mal | Se corrige el pedido, el plan o la spec | Se corrige el agente: sus instrucciones, sus herramientas o los datos que recibe |

Claude puede aparecer dos veces en un mismo proyecto: como Claude Code, que construye, y como el modelo que piensa adentro de un agente propio. Son dos usos distintos y dejan registros distintos.

### Formas de escribir un agente

Hay más de tres formas, pero todas caen en pocas familias. Lo que cambia de una a otra es quién pone el loop: una herramienta que ya lo trae, una librería, código propio o una plataforma.

| Familia | Qué es | Ejemplos | En estos proyectos |
| --- | --- | --- | --- |
| En prosa | El agente es un texto con instrucciones, y lo ejecuta una herramienta que ya trae el loop. También se los llama declarativos o definidos en Markdown; en Claude Code son los subagentes. | Subagentes de Claude Code | Sí |
| Framework nativo del modelo | Código que usa la librería de agentes del mismo proveedor que hace el modelo | Claude Agent SDK, OpenAI Agents SDK, Google ADK | Sí, Claude Agent SDK |
| Framework independiente | Código con una librería que funciona con modelos de distintos proveedores | LangChain y LangGraph, CrewAI, Pydantic AI | Sí, LangChain y LangGraph |
| A mano | Código que llama directo a la API del modelo y escribe su propio loop, sin framework | Un script propio | No |
| Visual, sin código | El agente se arma conectando bloques en una pantalla | n8n | No |
| Alojado por el proveedor | El proveedor del modelo ejecuta el agente en su propia infraestructura | Claude Managed Agents | No |

Las tres primeras son las de estos proyectos. En la práctica se diferencian así:

| Forma | Dónde vive | Cómo se prueba solo | Dónde se ve qué hizo |
| --- | --- | --- | --- |
| En prosa | Un archivo de texto con instrucciones, en `.claude/agents/` | Se le pide a Claude Code que use ese agente con una entrada de prueba | En la conversación de Claude Code y en los archivos que el agente deja |
| Framework nativo del modelo (Claude Agent SDK) | Código dentro del proyecto | Con un comando de consola que lo ejecuta con una entrada de prueba | En la salida de la consola y en los logs del servidor. También en LangSmith, si se lo conecta |
| Framework independiente (LangChain y LangGraph) | Código: un grafo de pasos conectados | Igual, por consola. Studio además dibuja el grafo y permite correrlo | En las trazas de LangSmith: cada paso con su entrada y su salida |

- En prosa, cambiar el agente es editar un texto. Quien lo ejecuta es el mismo Claude Code, así que conviene abrir una sesión para construir y otra para ejecutar.
- En las otras dos formas el agente es código. Lo escribe Claude Code y corre sin él.
- Regla para CLAUDE.md, porque vale para todos: cada agente deja registro de qué recibió, qué herramientas usó y qué devolvió. Sin ese registro no hay dónde mirar.

Fuentes: [subagentes de Claude Code](https://code.claude.com/docs/en/subagents), [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview), [Studio de LangSmith](https://docs.langchain.com/langsmith/observability-studio).

### LangSmith: la ventana para ver un agente por dentro

LangSmith es la plataforma de LangChain para observar agentes. Guarda cada ejecución como una traza: la lista ordenada de pasos que dio el agente desde la entrada hasta la salida. Se verá con más detalle más adelante en la cursada.

| Qué muestra una traza | Para qué le sirve al alumno |
| --- | --- |
| La entrada que recibió el agente | Responder "¿recibió lo que necesitaba?" |
| Cada llamada al modelo, con lo que se le envió y lo que contestó | Ver qué decidió y con qué información |
| Cada herramienta usada, con sus datos y su resultado | Responder "¿tenía la herramienta y la usó?" |
| La salida final | Compararla con la ficha del agente |
| Cuánto tardó y cuánto consumió cada paso | Encontrar el paso lento o caro |

- **Sirve para las dos formas con código.** Los agentes en LangChain o LangGraph se trazan con solo activarlo, y el Claude Agent SDK tiene una integración propia.
- **Se activa con dos variables en el archivo .env:** `LANGSMITH_TRACING=true` y `LANGSMITH_API_KEY`, con la clave que da la cuenta de LangSmith. Es un paso de la Fase 0 y lo hace Claude Code.
- **Studio,** dentro de LangSmith, dibuja el grafo de un agente en LangGraph y permite correrlo desde ahí.
- **Para los agentes en prosa,** el registro principal sigue siendo la conversación de Claude Code.

Fuentes: [trazas con LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph), [trazas con Claude Agent SDK](https://docs.langchain.com/langsmith/trace-claude-agent-sdk), [Studio](https://docs.langchain.com/langsmith/observability-studio).

### El mismo loop, otra vez

Cada agente propio recorre las mismas cuatro etapas que Claude Code. Lo que se aprendió a leer en la terminal sirve para leer el registro de un agente.

| Etapa | Qué se busca en el registro del agente |
| --- | --- |
| Objetivo | Qué recibió: la entrada y sus instrucciones |
| Plan | Qué decidió hacer primero, si lo dice |
| Ejecución | Qué herramientas llamó y con qué datos |
| Evaluación | Cómo decidió que había terminado y qué devolvió |

### El cuarto mapa: el flujo de agentes

Cada proyecto necesita su propio dibujo de quién le pasa qué a quién. Se le pide a Claude Code, con Archify, un diagrama de workflow del flujo de agentes, y se regenera cada vez que se suma o cambia un agente.

En el mapa cliente-servidor, los agentes escritos en código viven dentro de la caja del servidor: el navegador pide, el servidor pone a trabajar a los agentes y ellos llaman al modelo por internet. Los agentes en prosa corren dentro de Claude Code, sin servidor.

### Ficha de agente

Una ficha por agente, con los mismos seis campos, escrita antes de construirlo.

| Campo | Qué se escribe | Ejemplo: investigador de tendencias |
| --- | --- | --- |
| Rol | Qué hace, en una frase de negocio | Busca qué temas están creciendo en el rubro del cliente |
| Entrada | Qué recibe y de quién | El perfil del cliente, que carga el usuario |
| Herramientas | Qué puede usar | Búsqueda web |
| Salida | Qué entrega y a quién | Cinco tendencias con su fuente, para el agente redactor |
| Bien hecho es | Un criterio que un no técnico puede verificar | Cada tendencia trae un enlace que abre y es del último mes |
| Forma | Prosa, framework nativo o framework independiente | Prosa |

La ficha cumple para un agente el papel que la spec cumple para una funcionalidad: dice qué debe pasar, y contra ella se juzga lo que pasó.

### Cómo probar agentes propios

1. **Uno solo, antes que el flujo.** Correr cada agente con una entrada conocida y comparar la salida con su ficha.
2. **Después, los traspasos.** La salida de un agente es la entrada del siguiente; hay que mirar qué llegó de verdad, no qué debería haber llegado.
3. **Varias veces.** Un agente no responde siempre igual. Con la misma entrada se lo corre tres veces y se juzga con el criterio de la ficha, sin esperar el mismo texto.
4. **Recién entonces, el flujo completo.**

### Cuando un agente propio se equivoca

Tres preguntas, en este orden, ubican el problema antes de pedir un arreglo.

| Pregunta | Si la respuesta es no | Qué se corrige |
| --- | --- | --- |
| ¿Recibió lo que necesitaba? | El problema viene de antes | El agente anterior o el traspaso |
| ¿Tenía la herramienta y la usó? | No pudo o no quiso hacer el trabajo | Sus herramientas, o la instrucción de usarlas |
| ¿Sus instrucciones decían qué hacer en este caso? | Improvisó | Sus instrucciones |

Con la respuesta se le dice a Claude Code qué corregir, por ejemplo: "el investigador recibe bien el perfil, pero no usa la búsqueda". Es el mismo principio del protocolo de error: ubicar primero, arreglar después.

## Red de seguridad y qué hacer cuando algo se rompe

Con un commit por fase, nada de lo que se rompa es grave: siempre se puede volver al último punto que funcionaba.

### Red de seguridad

- Un commit al cerrar cada fase validada. Es el punto de guardado.
- Una fase por sesión, y sesión nueva para la siguiente.
- La bitácora al día al cerrar cada sesión.
- Las credenciales de la base de datos en el archivo .env, nunca en CLAUDE.md ni en un commit.

### Protocolo de error

1. Copiar el error exacto, sin resumirlo.
2. Ubicarlo en el mapa: cliente, servidor, base de datos o la conexión entre ellos.
3. Pedir el diagnóstico antes de que Claude arregle.
4. Si en dos o tres intentos no sale, frenar, volver al último commit y abrir una sesión nueva.
5. Si después de volver atrás sigue sin salir, escribirle al profesor con el error, la fase y lo que se intentó.

### Sustos normales

- Texto rojo durante la Evaluación: es Claude leyendo sus propios errores.
- Warnings: son avisos, no fallas.
- Instalaciones de librerías que tardan.
- Pedidos de permiso repetidos.
- Respuestas largas con archivos que no se entienden: alcanza con saber qué caja del mapa tocan.
