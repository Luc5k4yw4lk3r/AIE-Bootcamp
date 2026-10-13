# Parte 3 — Actividades de comprensión

Oct 5, 2026 · @Luciano

Son cuatro actividades para después de las partes 1 y 2, ordenadas de menor a mayor exigencia: una entrada en calor de preguntas, el detective de capas, ejercicios de modificar y tres de transferir para fuera de clase. Los alumnos no necesitan entorno para ninguna: todo lo que tocan abre con doble click.

Los 16 casos del detective y las 7 soluciones de modificar los ejecuté en Chromium. Los síntomas y los mensajes de error que figuran acá son los que salieron.

Los archivos van en `taskflow-detective.zip`. La carpeta `alumnos` es para compartir; la carpeta `docente` trae los casos con API y las soluciones.

## 1. Entrada en calor: preguntas sin código

Son 16 preguntas en cuatro rondas, para unos 18 minutos. Todos responden a la vez por el chat, con una palabra o una letra, antes de que digas la respuesta. Así queda registrado qué contestó cada uno, incluidos los que no hablan.

### Ronda 1 — ¿Qué es esto? (4 minutos)

Mostrás el fragmento y responden: HTML, CSS, JavaScript o respuesta de la API.

| N.º | Fragmento | Respuesta | Por qué |
| --- | --- | --- | --- |
| 1 | `<section class="columna" id="col-backlog">` | HTML | Una caja con nombre y atributos |
| 2 | `.tarjeta { border-radius: 6px; }` | CSS | A quién se aplica y qué propiedad cambia |
| 3 | `form.addEventListener("submit", ...)` | JavaScript | Deja anotado qué hacer cuando pase algo |
| 4 | `{"id": 3, "titulo": "Escribir el README", "estado": "backlog"}` | Respuesta de la API | Son datos en JSON, no instrucciones |
| 5 | `fetch("http://localhost:8000/v1/tareas")` | JavaScript | Es el pedido a la API, escrito en el frontend. La API es quien responde |
|  |  |  |  |

La 4 y la 5 son las que separan: quien confunde el pedido con la respuesta todavía no tiene claro quién es quién.

### Ronda 2 — ¿Verdadero o falso? (6 minutos)

| N.º | Afirmación | Respuesta | Por qué |
| --- | --- | --- | --- |
| 6 | Si desactivo JavaScript, el tablero de s12 muestra las tarjetas igual | Falso | Las tarjetas las crea `app.js`; sin JavaScript quedan las columnas vacías |
| 7 | Si borro el CSS, el contenido sigue ahí | Verdadero | Cambia la forma, no lo que hay |
| 8 | Si apago la API, la página llega igual | Verdadero | El HTML y `app.js` vienen de otro servidor; lo que falta son los datos |
| 9 | Lo que cambio en la pestaña Elements queda guardado en el archivo | Falso | Se edita la copia en memoria; al recargar vuelve |
| 10 | Un script de Python puede crear una tarea y aparece en el tablero al recargar | Verdadero | La API no distingue quién la llama |
| 11 | Si muevo una tarjeta en una ventana, la otra ventana abierta se actualiza sola | Falso | Un navegador solo se entera cuando pregunta |

### Ronda 3 — ¿Dónde vive y qué pasa si recargo? (5 minutos)

Para cada situación responden dónde quedó la tarea (pantalla, memoria de la pestaña, servidor) y si sobrevive a recargar.

| N.º | Situación | Dónde vive | Al recargar |
| --- | --- | --- | --- |
| 12 | Dibujo una tarjeta inventada desde la consola | Solo en la pantalla | Se va |
| 13 | En s11 agrego una tarea con el formulario | Pantalla y memoria | Se va |
| 14 | En s12 agrego una tarea con el formulario | Pantalla, memoria y servidor | Sigue |
| 15 | Otra persona abre el tablero de s12 desde su computadora. ¿Cuál de las tres tareas ve? | Solo la 14 | La ve recién cuando su navegador pregunta |

### Ronda 4 — Ordenar (4 minutos)

**16.** Estos son los seis pasos de un click sobre una tarjeta en s12, desordenados. Responden con las letras en orden.

- A. `app.js` mueve la tarjeta a la otra columna
- B. La API guarda el cambio en la base
- C. Hacés click en la tarjeta
- D. `app.js` manda un `POST` a la API
- E. El navegador llama a la función `mover`
- F. La API responde 200 con la tarea

Respuesta: C, E, D, B, F, A. Repregunta: ¿cuáles de esos pasos existen también en s11? Solo C, E y A.

## 2. Detective de capas

Son 16 casos, cada uno con una sola falla. Por cada caso los alumnos dicen dos cosas: en qué capa está el problema y con qué evidencia lo saben. «Me parece que es el JavaScript» no vale. «En Elements hay tres tarjetas pero no se ven» sí.

Cómo se juega:

1. Compartís la carpeta `alumnos`. Cada caso es una carpeta con su `index.html` y su `app.js`, y se abre con doble click.
2. Trabajan de a dos. Uno maneja el navegador y el otro anota.
3. Primero el navegador, después el código. No se abre `app.js` hasta haber mirado Network, Console y Elements.
4. Responden por chat con el formato «caso 05: CSS, porque…».
5. Al terminar cada nivel, puesta en común.

Los casos 11 a 16 necesitan la API. Esos los mostrás vos desde tu pantalla y ellos diagnostican mirando tu Network y tu Console.

| Nivel | Casos | Qué entrena | Minutos |
| --- | --- | --- | --- |
| 1 | 01 a 03 | De qué archivo sale cada cosa que se ve | 6 |
| 2 | 04 a 06 | Un mismo síntoma con tres causas distintas | 12 |
| 3 | 07 a 10 | Se ve bien pero no se comporta bien | 16 |
| 4 | 11 a 16 | Qué respondió la API, si es que respondió | 20 |

En total son unos 54 minutos. Para acortar a 45, salen el 03, el 10 y el 13.

### La rutina

Esta rutina es lo que se llevan para sus propios proyectos. Conviene mostrarla sin los números de caso al empezar y completa al cerrar.

&#91;embedded content: La rutina del detective · 5 preguntas y a qué caso lleva cada una\]

Cada pregunta se contesta mirando una pestaña de las DevTools. Si la respuesta es no, ahí está la falla; si es sí, se pasa a la siguiente. En los casos con API el rojo aparece ya en Network y en Console, y el mensaje manda directo a la pregunta 5.

### Casos 01 a 10: sin API, con doble click

Esta tabla es la hoja de respuestas. A los alumnos les llega solo la carpeta.

| Caso | Qué se ve | Dónde está la falla | La evidencia |
| --- | --- | --- | --- |
| 01 | La segunda columna se titula «En Progeso» | HTML: el texto del `<h2>` en `index.html` | Elements muestra `<h2>en progeso</h2>` |
| 02 | Las tres columnas quedan apiladas | CSS: a `.tablero` le falta `display: flex` | En Styles, la regla de `.tablero` no lo tiene |
| 03 | Una tarjeta dice «Mover tarjetas con clik» | Los datos, en el array de `app.js` | Ese texto no está en `index.html`; `tareas[1].titulo` lo muestra |
| 04 | Tablero vacío; el formulario recarga la página | HTML: el `<script>` apunta a `app.jss` | Network: `app.jss` en rojo. Console: `net::ERR_FILE_NOT_FOUND` |
| 05 | Tablero vacío, sin errores | CSS: `.tarjeta` tiene `display: none` | Elements muestra las tres tarjetas; `document.querySelectorAll(".tarjeta").length` da 3 |
| 06 | Tablero vacío, sin errores | JavaScript: falta la llamada a `renderInicial()` | Elements no tiene tarjetas, `tareas.length` da 3 y el formulario sí agrega |
| 07 | Todo se ve bien, pero el click no mueve las tarjetas | JavaScript: el evento está escrito `"clic"` | Console sin errores; el formulario sí funciona |
| 08 | Al agregar una tarea la página se recarga y la tarea no queda | JavaScript: falta `evento.preventDefault()` | Después de enviar, la dirección termina en `index.html?` |
| 09 | Solo aparece una tarjeta, en «Hecho» | El HTML dice `id="col-en_progreso"` y JavaScript busca `col-en-progreso` | Console: `Cannot read properties of null (reading 'appendChild')` |
| 10 | Las tarjetas aparecen sin título | JavaScript: lee `tarea.title` y el dato se llama `titulo` | Elements muestra `<div class="titulo"></div>` vacío; `tareas[0].titulo` sí tiene texto |

Qué dejar dicho en cada puesta en común:

- **Nivel 1.** Los títulos de las columnas salen del HTML, el texto de las tarjetas sale de los datos y la disposición sale del CSS. Tres cosas que se ven juntas vienen de tres lugares.
- **Nivel 2.** Los casos 04, 05 y 06 se ven iguales. En el 04 hay rojo en Network, en el 05 las tarjetas están en Elements y en el 06 no están. «Tablero vacío» es un síntoma, no un diagnóstico.
- **Nivel 3.** El 09 es el único con mensaje de error, y sirve para aprender a leerlo. El 09 y el 10 son la misma idea: dos partes que tenían que ponerse de acuerdo en un nombre. Eso prepara los casos 14 y 15.

### Casos 11 a 16: con API, desde tu pantalla

Para cada uno servís la carpeta del caso en el puerto 3000 (`cd caso-13 && python -m http.server 3000`) con la API en el 8000. El archivo `LEEME.txt` de la carpeta `docente` dice cómo armar cada uno.

| Caso | Cómo se arma | El pedido a la API en Network | Console | Diagnóstico |
| --- | --- | --- | --- | --- |
| 11 | Apagar la API | `GET localhost:8000/v1/tareas` falla con `ERR_CONNECTION_REFUSED` | `Failed to fetch` | Nadie atiende en el 8000: la API está apagada |
| 12 | Abrir `index.html` con doble click | El mismo pedido falla con `ERR_FAILED` | `blocked by CORS policy`, con `origin 'null'` | La API está viva pero no autoriza ese origen |
| 13 | Servir `caso-13` | `GET localhost:8001/v1/tareas` falla con `ERR_CONNECTION_REFUSED` | `Failed to fetch` | El frontend llama al puerto equivocado. Se distingue del 11 por el número de puerto |
| 14 | Servir `caso-14` | `GET localhost:8000/v1/tarea` responde 404 | `No se pudo cargar el tablero: 404` | La API respondió que esa URL no existe: a la ruta le falta una letra |
| 15 | Servir `caso-15` y crear una tarea | El tablero carga con 200; `POST /v1/tareas` responde 422 | `No se pudo crear la tarea: 422` | La API respondió que falta el campo `titulo`: el frontend manda `title` |
| 16 | API contra una base sin `seed.py` | `GET /v1/tareas` responde 200 | Nada | Todo funciona y no hay datos: la respuesta trae `"items": []` |

En el caso 15 conviene abrir la respuesta del `POST` en Network. La API explica el error con todas las letras: `"loc": ["body", "titulo"], "msg": "Field required"`.

Lo que deja el nivel 4 son tres resultados distintos de un pedido, que conviene escribir uno debajo del otro:

- **No hubo respuesta** (11, 12 y 13). El pedido no llegó o el navegador no dejó leerlo.
- **Respondió que no** (14 y 15). La API está bien; el pedido estaba mal armado. El número dice por qué.
- **Respondió que sí, sin datos** (16). No hay ningún error que buscar.

Para cerrar la actividad: el tablero vacío apareció en ocho casos (04, 05, 06, 11, 12, 13, 14 y 16) por ocho causas distintas.

## 3. Modificar

Son siete cambios sobre `alumnos/para-modificar`, una copia limpia de s11, para unos 45 minutos. Editan con cualquier editor de texto, guardan y recargan la página.

La regla que la convierte en actividad de comprensión: antes de tocar, cada pareja escribe por chat en qué capa va el cambio y en qué archivo. Recién después lo hacen.

| N.º | Consigna | Capa | Cómo saber que quedó |
| --- | --- | --- | --- |
| 1 | Que el botón diga «Sumar al tablero» | HTML | El botón muestra el texto nuevo |
| 2 | Que la columna «hecho» tenga fondo verde claro | CSS | Solo esa columna cambia de color |
| 3 | Que el tablero arranque con una cuarta tarea, «Probar el tablero», en backlog | Los datos, en `app.js` | Aparece al abrir, sin usar el formulario |
| 4 | Agregar una columna «bloqueado» entre «en progreso» y «hecho» | HTML y JavaScript | Una tarjeta recorre las cuatro columnas a clicks |
| 5 | Que las tareas nuevas arranquen en «en progreso» | JavaScript | Al usar el formulario, la tarjeta aparece en la segunda columna |
| 6 | Que los títulos de las tarjetas en «hecho» se vean tachados | CSS | Al mover una tarjeta a «hecho», se tacha sola |
| 7 | Que el formulario no acepte títulos de menos de tres letras | JavaScript | Con «ab» no agrega nada; con «abc» sí |

Los tres primeros tocan una capa cada uno y son de calentamiento. El 4 es el central, porque obliga a tocar dos archivos. El 6 tiene trampa: parece que necesita JavaScript y se resuelve con una línea de CSS.

### Soluciones y qué hacerles notar

**1.** En `index.html`:

```html
<button type="submit">Sumar al tablero</button>
```

**2.** Dentro del `<style>`. Es la primera vez que usan un selector por `id`, que se escribe con `#`:

```css
#col-hecho { background: #e6f4ea; }
```

**3.** Una línea más en el array de `app.js`:

```js
{ id: 4, titulo: "Probar el tablero", descripcion: "", estado: "backlog" },
```

Repregunta: ¿hay que tocar alguna otra línea? Sí, `let siguienteId = 4;` tiene que pasar a 5. Si no, la próxima tarea creada con el formulario también recibe el id 4 y quedan dos tareas con el mismo id.

**4.** Una línea en cada archivo:

```html
<section class="columna" id="col-bloqueado"><h2>bloqueado</h2></section>
```

```js
const ESTADOS = ["backlog", "en progreso", "bloqueado", "hecho"];
```

Conviene dejar que algunos toquen una sola capa y vean qué pasa:

- **Solo el HTML.** La columna aparece, pero ninguna tarjeta entra nunca.
- **Solo el JavaScript.** Al llegar a «bloqueado» sale `Cannot read properties of null (reading 'appendChild')`, el mismo error del caso 09. La tarjeta queda en pantalla en «en progreso» mientras su dato ya dice «bloqueado».

**5.** En `agregarTarea`, cambiar una palabra:

```js
const tarea = { id: siguienteId++, titulo, descripcion, estado: "en progreso" };
```

**6.** Una regla de CSS, sin tocar `app.js`:

```css
#col-hecho .tarjeta .titulo { text-decoration: line-through; }
```

El CSS se aplica según dónde está la caja. Cuando JavaScript mueve la tarjeta a «hecho», el estilo cambia solo.

**7.** En el `submit` del formulario, debajo de la línea que ya rechaza el título vacío:

```js
if (!titulo) return;
if (titulo.length < 3) return;
```

Se resuelve copiando una línea que ya existe y adaptándola, que es la forma en que van a escribir código las primeras veces.

## 4. Transferir

Son tres actividades cortas para fuera de clase. Ninguna usa TaskFlow: sirven para comprobar que el modelo funciona en otro lado.

1. **Caza de APIs** (unos 15 minutos). En un sitio que usen todos los días, abrir las DevTools, ir a Network, elegir el filtro «Fetch/XHR» y recargar. Tienen que encontrar un pedido cuya respuesta sea JSON y traer tres cosas: la URL, el método y un dato de la respuesta que reconozcan en la pantalla.
2. **Los pedidos de mi pantalla** (unos 30 minutos). Elegir una pantalla de su propio proyecto y completar la tabla de abajo, con una fila por cada cosa que el usuario puede hacer. Es diseñar la API desde el front, y deja servida la sesión s09.
3. **Explicarlo sin jerga** (unos 10 minutos). Un audio de un minuto contando qué pasa cuando alguien hace click en una tarjeta de s12, para una persona que no programa. La restricción es no usar las palabras API, fetch ni JSON.

La tabla de la actividad 2, con una fila de TaskFlow como ejemplo:

| Lo que hace el usuario | Método | URL | Qué se envía | Qué vuelve |
| --- | --- | --- | --- | --- |
| Mueve una tarjeta | `POST` | `/v1/tareas/3/mover` | `{"estado": "en progreso"}` | La tarea completa, con su estado nuevo |

## Tiempos y qué no probé

Tiempos, como estimación mía: entrada en calor 18 minutos, detective 54 y modificar 45. Son tres bloques independientes y se pueden dar en clases distintas.

Lo que no pude probar:

- **Los tiempos con alumnos.** Salen de contar preguntas y casos, no de haberlos corrido con un grupo.
- **Cómo se ve cada caso en la interfaz de las DevTools.** Los corrí en Chromium automatizado. Lo que aparece en la página, los pedidos y los mensajes de consola son los reales.
- **El caso 16 con Docker.** Usé una base vacía creada a mano. Con `docker compose` equivale a una base recién creada a la que no se le corrió `seed.py`.

Lo escribí para responder por chat y trabajar de a dos, pensando en una videollamada. En forma presencial funciona igual.
