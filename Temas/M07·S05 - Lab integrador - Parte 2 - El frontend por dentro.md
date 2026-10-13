# Parte 2 — El frontend por dentro

Oct 1, 2026 · @Luciano

Esta parte abre los archivos del frontend y deja una distinción firme: HTML y CSS describen, JavaScript hace, y los datos que duran viven detrás de la API. Se trabaja sobre el tag `s11`, que funciona con doble click y sin ningún servidor, y recién en el último bloque se vuelve a s12.

A diferencia de la parte 1, acá los alumnos pueden tocar: todo lo que cambian es la copia de la página en su navegador, y al recargar vuelve a estar como antes. Ejecuté cada paso en Chromium contra los archivos de `s11` y contra s12 levantado.

## Las cuatro ideas que tienen que quedar

1. Una página es un archivo de texto. El navegador lo lee y arma con él un árbol de cajas, el DOM.
2. HTML y CSS no hacen nada por sí solos. Describen qué hay y cómo se ve.
3. JavaScript es un programa que corre en el navegador de cada persona y modifica ese árbol.
4. Lo que JavaScript tiene en memoria se pierde al recargar. Para que los datos duren y se compartan hace falta la API.

## Preparación

```bash
git worktree add ../taskflow-s11 s11   # una copia del proyecto en el tag s11, sin tocar la actual
```

- Abrir `../taskflow-s11/frontend/index.html` con doble click. Son dos archivos, `index.html` y `app.js`, y no hace falta Python, Docker ni internet.
- Abrir las DevTools. Se usan tres pestañas: Elements, Console y Network.
- Para el bloque D, tener s12 levantado como en la parte 1.

Si los alumnos tienen el repo, pueden hacer los bloques A, B y C en su propia máquina. No necesitan instalar nada.

## Bloque A — HTML: un texto que describe una estructura

### A1. Abrir el archivo con doble click

**Pregunta:** «¿Hace falta un servidor para ver una página?»

El tablero aparece y funciona. La barra de direcciones empieza con `file:///` y en Network hay dos filas, `index.html` y `app.js`, las dos leídas del disco. Una página es, antes que nada, un archivo.

### A2. Leer `index.html`

El archivo tiene 54 líneas. El `<head>` guarda lo que no se ve: el título de la pestaña y el CSS. El `<body>` es lo que se ve; acá va resumido, sin el párrafo de ayuda ni los comentarios.

```html
<body>
  <h1>TaskFlow — Tablero</h1>

  <form id="form-tarea">
    <input id="input-titulo" type="text" placeholder="Título de la tarea" required />
    <input id="input-desc" type="text" placeholder="Descripción (opcional)" />
    <button type="submit">Agregar tarea</button>
  </form>

  <div class="tablero">
    <section class="columna" id="col-backlog"><h2>backlog</h2></section>
    <section class="columna" id="col-en-progreso"><h2>en progreso</h2></section>
    <section class="columna" id="col-hecho"><h2>hecho</h2></section>
  </div>

  <script src="app.js"></script>
</body>
```

Tres cosas para nombrar mientras se lee:

- **Etiqueta.** Una caja con nombre que se abre y se cierra: `<h1>` y `</h1>`. Las cajas van unas dentro de otras.
- **Atributo.** Un dato pegado a la caja. `id` es un nombre único, `class` es el grupo al que pertenece.
- **`<script src="app.js">`.** La última línea le dice al navegador que vaya a buscar un programa.

**Pregunta:** «¿Dónde están las tareas en este archivo?»

No están. Las columnas vienen vacías y el texto «Diseñar el tablero» solo aparece en `app.js`. Tampoco hay condiciones ni repeticiones: HTML no es un lenguaje de programación, es una descripción.

### A3. El DOM: la copia viva de la página

**Pregunta:** «Si cambio el título desde las DevTools, ¿cambia el archivo?»

En Elements, doble click sobre el texto del `<h1>`, escribir «El tablero de mi equipo» y Enter. La pantalla cambia al instante. Al recargar vuelve «TaskFlow — Tablero».

El navegador leyó el archivo una vez y armó con él un árbol de cajas en memoria, el DOM. Lo que se edita en Elements es ese árbol; el archivo no se entera.

![[Pasted image 20261013135341.png]] El DOM del tablero en s11 · 15 cajas, 3 agregadas por JavaScript\]

Las cajas grises son las que alguien escribió en `index.html`. Las tres azules no figuran en ningún archivo HTML: aparecen cuando el navegador ejecuta `app.js`, y de eso trata el bloque C.

### A4. Lo único que el HTML sabe hacer solo

**Pregunta:** «Sin JavaScript, ¿qué hace el botón "Agregar tarea"?»

Desactivar JavaScript como en la parte 1, recargar, escribir un título y apretar el botón. La página se recarga, la dirección termina en `index.html?`, el campo queda vacío y no hay ninguna tarea nueva.

Por su cuenta, un formulario HTML solo sabe hacer una cosa: pedir una página de nuevo. Así funcionaba toda la web antes de JavaScript, y conviene que lo vean antes del bloque C. Volver a activar JavaScript.

## Bloque B — CSS: reglas sobre cómo se ve

### B1. Anatomía de una regla

El CSS de este proyecto son 20 líneas dentro del `<style>` de `index.html`. Todas tienen la misma forma.

```css
.tarjeta {                      /* a quién: toda caja con class="tarjeta" */
  background: #fff;             /* qué cambia: una propiedad y su valor   */
  border: 1px solid #dcdfe4;
  border-radius: 6px;
}
```

Una regla sirve para muchas cajas: las tres tarjetas la comparten. En este proyecto el CSS apunta por etiqueta o por clase (`.tablero`, `.columna`, `.tarjeta`) y JavaScript busca por `id` (`col-backlog`, `form-tarea`).

### B2. Cambiar el estilo en vivo

**Pregunta:** «Si cambio un valor acá, ¿a cuántas tarjetas afecta?»

En Elements, seleccionar una tarjeta. En el panel Styles, destildar `background` y cambiar `border-radius` de `6px` a `20px`. Cambian las tres al mismo tiempo. Al recargar, todo vuelve.

### B3. Una línea arma las columnas

**Pregunta:** «¿Qué hace que las tres columnas estén una al lado de la otra?»

Seleccionar el `<div class="tablero">` y destildar `display: flex`. Las columnas quedan apiladas.

&#91;image: El tablero sin display flex: las tres columnas apiladas una debajo de la otra, con el mismo contenido\]

El HTML dice que hay tres secciones. Que se vean como columnas lo decide el CSS.

### B4. El CSS cambia lo que se ve, no lo que hay

**Pregunta:** «En pantalla dice "Backlog" con mayúscula. ¿Qué dice el HTML?»

El HTML dice `<h2>backlog</h2>`, en minúscula. La mayúscula la pone la regla `text-transform: capitalize`. En la consola, `document.querySelector("h2").textContent` devuelve `"backlog"`.

Lo último es pasar el mouse por una tarjeta: el borde se oscurece por la regla `.tarjeta:hover`. Es toda la reacción que tiene el CSS. Puede responder al mouse, pero no puede recordar, contar ni pedir datos.

## Bloque C — JavaScript: un programa que corre en tu navegador

### C1. La consola: hablarle a la página

**Pregunta:** «¿De dónde salieron las tarjetas, si el HTML no las tiene?»

En Console, escribir `tareas`: devuelve un array con tres objetos, el mismo que está escrito en las líneas 11 a 15 de `app.js`. Después `document.querySelectorAll(".tarjeta").length`: devuelve `3`. Tres datos, tres cajas. Las une esta función, que se llama una sola vez, en la última línea del archivo.

```js
function renderInicial() {
  for (const tarea of tareas) {
    columnaDe(tarea.estado).appendChild(crearTarjeta(tarea));
  }
}
```

Se lee casi en castellano: por cada tarea, crear una tarjeta y colgarla de su columna.

### C2. Dibujar no es guardar

**Pregunta:** «Si dibujo una tarjeta a mano desde la consola, ¿cuántas tareas hay?»

```js
columnaDe("backlog").appendChild(crearTarjeta({ id: 99, titulo: "Tarjeta inventada", estado: "backlog" }))
```

En pantalla hay cuatro tarjetas. `tareas.length` sigue devolviendo `3`.

&#91;image: El tablero con una cuarta tarjeta, «Tarjeta inventada», agregada desde la consola en la columna backlog\]

La pantalla y los datos son dos cosas distintas. JavaScript puede cambiar una sin tocar la otra, y mantenerlas iguales es trabajo del programador.

### C3. Nada corre hasta que pasa algo

**Pregunta:** «Agrego una tarea con el formulario. ¿Se recarga la página, como en A4?»

Hacer click en una tarjeta: cambia de columna. Agregar una tarea con el formulario: aparece en backlog, la dirección no cambia y Network sigue vacía. JavaScript no está corriendo todo el tiempo. Deja funciones anotadas y espera.

```js
div.addEventListener("click", () => avanzarEstado(tarea, div));   // "cuando hagan click acá, llamá a esto"

form.addEventListener("submit", (evento) => {
  evento.preventDefault();   // "navegador, no hagas lo del paso A4: de esto me ocupo yo"
  ...
});
```

### C4. Recargar

**Pregunta:** «Moví una tarjeta y agregué una tarea. Recargo. ¿Qué queda?»

Nada. Vuelven las tres tarjetas originales en sus columnas originales. Al recargar, el navegador tira el DOM y la memoria de `app.js`, lee los dos archivos otra vez y arranca de cero.

Una tarea puede vivir en tres lugares, y cada uno tiene un alcance distinto.

| Lugar | Qué es | Sobrevive a recargar | Lo ven otras personas |
| --- | --- | --- | --- |
| La pantalla | Cajas en el DOM | No | No |
| La memoria de la pestaña | El array `tareas` de `app.js` | No | No |
| El servidor | Filas en PostgreSQL, detrás de la API | Sí | Sí |

En s11 solo existen las dos primeras filas. Ese es el problema que resuelve el bloque D.

## Bloque D — Del array a la API

Acá se cambia a s12, en `http://localhost:3000`, con la API levantada.

### D1. Qué cambia entre s11 y s12

**Pregunta:** «Para que las tareas duren, ¿qué parte del frontend hay que cambiar: el HTML, el CSS o el JavaScript?»

Solo el JavaScript. `index.html` es el mismo salvo el texto de ayuda, y el CSS no cambia. En `app.js` cambia de dónde salen los datos.

```js
// s11: los datos vienen escritos en el archivo
const tareas = [
  { id: 1, titulo: "Diseñar el tablero", descripcion: "Columnas y tarjetas", estado: "hecho" },
  { id: 2, titulo: "Mover tarjetas con click", descripcion: "", estado: "en progreso" },
  { id: 3, titulo: "Escribir el README", descripcion: "Breve", estado: "backlog" },
];
renderInicial();
```

```js
// s12 (resumido): el array arranca vacío y se llena con lo que responde la API
let tareas = [];

async function cargarTablero() {
  const resp = await fetch(`${API}/v1/tareas?proyecto_id=${PROYECTO_ID}&limit=100`);
  const pagina = await resp.json();
  tareas = pagina.items;
  pintarTablero();
}
cargarTablero();
```

Dos palabras nuevas alcanzan. `fetch` es «pedile esto a un servidor», el mismo pedido que en la parte 1 se hizo pegando la URL en la barra. `await` es «esperá la respuesta antes de seguir». La función que arma cada tarjeta, `crearTarjeta`, es la misma en los dos tags; solo cambia a qué función llama el click.

### D2. Un click, antes y después

**Pregunta:** «En s12, cuando hago click, ¿qué pasa primero: se mueve la tarjeta o se avisa al servidor?»

```js
// s11: cambia el dato en memoria y mueve la caja
function avanzarEstado(tarea, nodo) {
  const nuevoEstado = ESTADOS[(ESTADOS.indexOf(tarea.estado) + 1) % ESTADOS.length];
  tarea.estado = nuevoEstado;
  columnaDe(nuevoEstado).appendChild(nodo);
}
```

```js
// s12 (resumido): primero le pide el cambio a la API
async function mover(tarea, nodo) {
  const nuevoEstado = ESTADOS[(ESTADOS.indexOf(tarea.estado) + 1) % ESTADOS.length];
  const resp = await fetch(`${API}/v1/tareas/${tarea.id}/mover`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: nuevoEstado }),
  });
  if (!resp.ok) return;                        // si la API dice que no, no se mueve nada
  const actualizada = await resp.json();
  tarea.estado = actualizada.estado;           // recién acá cambia el dato en memoria
  columnaDe(tarea.estado).appendChild(nodo);   // y recién acá se mueve la caja
}
```

Las dos últimas líneas hacen lo mismo que en s11. Lo nuevo es todo lo que pasa antes.

&#91;embedded content: Un click en una tarjeta · 6 pasos en s12, 3 en s11\]

La tarjeta no se mueve hasta que la API responde. Si la API está apagada, el click no hace nada en pantalla, y eso se puede probar en el momento.

### D3. La prueba de la consola, ahora con API

**Pregunta:** «Repito la tarjeta inventada del paso C2. ¿Se guarda esta vez?»

Con Network abierta, pegar la misma línea de C2. La tarjeta aparece y Network no muestra ningún pedido: sigue siendo solo un dibujo. Después llamar a la función que usa el formulario.

```js
crear("Creada desde la consola", "")
```

Ahora Network muestra `POST /v1/tareas` con respuesta 201. Al recargar, «Tarjeta inventada» desaparece y «Creada desde la consola» sigue ahí. `crear` hace las dos cosas: le pide a la API que guarde y después dibuja.

### D4. Dos ventanas

**Pregunta:** «Muevo una tarjeta en esta ventana. ¿La otra ventana se entera sola?»

Abrir el tablero en dos ventanas, una al lado de la otra, y mover una tarjeta en la primera. La segunda no cambia. Recién al recargarla muestra la tarjeta en su columna nueva.

El dato ya estaba en el servidor, pero nadie le avisó a la segunda ventana. Un navegador solo se entera cuando pregunta.

## Cierre: qué es estático y qué es dinámico

«Estático» describe a los archivos, no a lo que pasa en pantalla. Las tres piezas del frontend llegan siempre iguales; lo que cambia viene de dos lugares.

| Cosa | Quién la produce | Cambia de un pedido a otro | Dónde hace su trabajo |
| --- | --- | --- | --- |
| `index.html` | Una persona lo escribió | No | En el navegador, como estructura |
| El CSS | Una persona lo escribió | No | En el navegador, como apariencia |
| `app.js` | Una persona lo escribió | No | En el navegador, como programa que corre |
| El JSON de `/v1/tareas` | La API lo arma en cada pedido | Sí, según lo que haya en la base | En el servidor |

La frase para el pizarrón: el HTML que llega es siempre el mismo, lo que cambia la pantalla es JavaScript y lo que cambia los datos es la API.

Esto deja preparado el cierre conceptual de s12. El paso A4 es el modelo multipágina y el bloque D es el de una SPA, que es como `docs/cierre-conceptual.md` describe a TaskFlow.

## Tropiezos previsibles

- **«Rompí la página».** Todo lo que se cambia en Elements, Styles o Console se va al recargar. Conviene decirlo antes de empezar, porque es lo que les da permiso para tocar.
- **En A4 el botón no hace nada.** Si el título queda vacío, el navegador no envía el formulario: es el atributo `required` del `<input>`. Hay que escribir algo para ver la recarga.
- **El tablero queda vacío después de A4.** JavaScript sigue desactivado. Hay que volver a activarlo antes del bloque B.
- **Chrome frena el pegado en la consola.** La primera vez que se pega código, las versiones recientes muestran una advertencia y piden escribir `allow pasting`.
- **s11 abre con doble click y s12 no.** En el bloque D hay que entrar por `http://localhost:3000`; con doble click aparece el error de CORS de la parte 1.
- **La copia de s11 queda en el disco.** Se borra con `git worktree remove ../taskflow-s11`.

## Tiempos y qué no probé

Tiempos, como estimación mía: bloque A 20 minutos, B 15, C 25 y D 20. Una hora y veinte en total. Si hay que recortar, B2 y D4 son los que menos se extrañan.

Lo que no pude probar:

- **Los clicks en las DevTools.** Editar texto en Elements y destildar propiedades en Styles los reproduje cambiando el DOM y los estilos por código. El efecto en la página es el real; la interfaz de tu Chrome no la vi.
- **La advertencia de pegado en la consola.** La menciono por cómo se comporta Chrome normalmente.
- **`git worktree`.** Saqué los archivos de `s11` del repo por otro camino; son los mismos dos archivos.
