# Parte 4 — Qué hay que tocar para agregar un feature

Oct 8, 2026 · @Luciano

Son seis features sobre TaskFlow s12, ordenados del que toca un archivo al que toca diez. La idea que tienen que llevarse los alumnos es que, antes de escribir, se puede predecir qué capas toca un cambio.

Implementé cada feature y lo ejecuté contra PostgreSQL y un navegador. También probé qué pasa cuando se olvida una capa: los errores que figuran acá son los que salieron. Cada feature va como parche en `taskflow-features.zip`.

## La matriz

&#91;embedded content: Seis features contra ocho capas · cada cuadro es una capa que hubo que tocar\]

Los huecos importan tanto como los cuadros. Un estado nuevo no toca la base, una regla nueva no toca el frontend y una búsqueda no toca las reglas. Solo un campo nuevo atraviesa todo.

## Las ocho capas

Las columnas de la matriz son estas. Las tres primeras son el frontend; las otras cinco, el backend y la base.

| Capa | Qué decide | Dónde está en TaskFlow |
| --- | --- | --- |
| HTML | Qué cajas hay en la página | `frontend/index.html` |
| CSS | Cómo se ven | El `<style>` de `frontend/index.html` |
| JavaScript | Qué hace la página y qué le pide a la API | `frontend/app.js` |
| Contrato | Qué se le puede pedir a la API y qué responde | `app/routers/v1/`, los handlers de `app/main.py` y `docs/api-v1.yaml` |
| Reglas | Qué está permitido | `app/services/` |
| Consultas | Cómo se busca y cómo se guarda | `app/repositories/` |
| Dominio | Qué es una tarea | `app/models/` |
| Base | Qué columnas existen | `app/db/models.py` y las tablas de PostgreSQL |

## Cinco preguntas para predecir qué se toca

| Pregunta | Si la respuesta es sí, se toca |
| --- | --- |
| ¿Cambia lo que se ve? | HTML si aparece una caja nueva; CSS si cambia el aspecto |
| ¿Cambia lo que la página hace? | JavaScript |
| ¿Cambia lo que se le pide a la API o lo que responde? | Contrato |
| ¿Hay una regla nueva sobre lo que está permitido? | Reglas |
| ¿Hay un dato nuevo para guardar o una forma nueva de buscar? | Dominio, base y consultas |

Hay una sexta que se hace antes de tocar nada: ¿en cuántos lugares está escrito hoy lo que voy a cambiar? Se contesta buscando, no pensando. El feature E muestra por qué.

## Los seis features

### A · Tachar las tarjetas de «hecho»

**Qué pide:** que el título de las tarjetas terminadas se vea tachado.

**Qué se toca:** una línea de CSS en `frontend/index.html`.

```css
#col-hecho .tarjeta .titulo { text-decoration: line-through; }
```

**Qué no se toca:** JavaScript, la API y la base. El dato ya existe: la tarjeta está dentro de la columna «hecho», y el CSS puede elegir por ubicación.

**Para preguntar:** «¿Hay que guardar en algún lado que la tarea está tachada?» No. Es otra forma de mostrar un estado que ya está guardado.

### B · Borrar una tarea desde el tablero

**Qué pide:** un botón «×» en cada tarjeta que la elimine.

**Qué se toca:** dos archivos y 21 líneas, todo en el frontend.

- `frontend/app.js`: el botón dentro de `crearTarjeta` y una función `eliminar` que hace `fetch` con el método `DELETE`.
- `frontend/index.html`: una regla de CSS para el botón.

**Qué no se toca:** el backend. `DELETE /v1/tareas/{id}` existe desde s10 y nadie lo usaba desde la página.

**Comprobado:** el click manda `DELETE /v1/tareas/3`, la API responde 204, la tarjeta desaparece y al recargar no vuelve.

**El detalle fino:** el botón vive dentro de la tarjeta, y la tarjeta ya escucha clicks para moverse. Por eso el botón llama a `evento.stopPropagation()`, para que su click no le llegue también a la tarjeta.

**Para preguntar:** «Antes de pedirle un cambio al backend, ¿dónde miro si la API ya lo ofrece?» En `/docs`.

### C · Una regla: sin responsable no se pasa a «hecho»

**Qué pide:** que la API rechace mover a «hecho» una tarea que no tiene responsable.

**Qué se toca:** cuatro archivos, todos del backend.

- `app/services/tarea_service.py`: la regla, dos líneas dentro de `mover_tarea`.
- `app/services/errores.py`: una excepción nueva, `TareaSinResponsable`.
- `app/main.py`: el handler que traduce esa excepción a un 409.
- `docs/api-v1.yaml`: la respuesta 409 en el contrato.

```python
if nuevo_estado == Estado.HECHO and tarea.responsable_id is None:
    raise TareaSinResponsable(tarea_id)
```

**Qué no se toca:** el frontend, las consultas y la base. El frontend viejo respeta la regla sin saber que existe: la API responde 409, `mover` ve que la respuesta no es buena y la tarjeta no se mueve.

**Comprobado:** mover la tarea 3 a «hecho» responde 409 con `La tarea 3 no tiene responsable: no se puede pasar a hecho`. La tarea 2, que tiene responsable, pasa con 200.

**Si se olvida el handler de `main.py`:** la API responde 500, pero en el navegador no se ve un 500. La consola dice `blocked by CORS policy`. La causa real está en la terminal de la API: `app.services.errores.TareaSinResponsable: 3`.

**Para preguntar:** «El usuario hace click y la tarjeta no se mueve. ¿Se entera de por qué?» No, el mensaje queda en la consola. Mostrarlo en pantalla sería otro feature, y ese sí toca el frontend.

### D · Buscar tareas por título

**Qué pide:** un campo de búsqueda que filtre el tablero.

**Qué se toca:** cinco archivos.

- `frontend/index.html`: el `<input>` de búsqueda.
- `frontend/app.js`: volver a pedir el tablero con `&q=` cada vez que cambia el texto.
- `app/routers/v1/tareas.py`: aceptar el parámetro `q` y pasarlo.
- `app/repositories/tarea_repository.py`: el filtro en la consulta.
- `docs/api-v1.yaml`: el parámetro nuevo.

```python
if q:
    consulta = consulta.where(TareaORM.titulo.ilike(f"%{q}%"))
```

**Qué no se toca:** el service y la base. El service recibe los filtros y los pasa tal cual con `**filtros`, y no hay ningún dato nuevo que guardar.

**Comprobado:** con `q=orden` la API devuelve una sola tarea. Escribir «doc» en el buscador deja una sola tarjeta y manda `GET /v1/tareas?proyecto_id=1&limit=100&q=doc`.

**Si se olvida el router:** la API ignora `q` sin avisar. Responde 200 con todas las tareas, el buscador no filtra y no aparece un error en ningún lado.

**Si se olvida el repository:** 500 en todos los listados, también sin buscar, y el tablero queda vacío. La terminal dice `TypeError: RepositorioTareasSQL.listar() got an unexpected keyword argument 'q'`.

**Para preguntar:** «¿Cuál de los dos olvidos es peor?» El del router, porque no hay ningún error que avise.

### E · Un estado nuevo: «bloqueado»

**Qué pide:** una cuarta columna entre «en progreso» y «hecho».

**Qué se toca:** ocho archivos, doce líneas en total. Es poco código en muchos lugares.

| Archivo | Capa | Qué cambia |
| --- | --- | --- |
| `app/models/estado.py` | Dominio | Una línea en el Enum |
| `app/routers/v1/schemas.py` | Contrato | Una columna más en `ColumnasTablero` |
| `app/routers/v1/proyectos.py` | Contrato | Una entrada más en el dict que reparte las tareas por columna |
| `app/models/tablero.py` | Dominio | Una columna más en la vista para agentes |
| `app/repositories/tablero_repository.py` | Consultas | El dict de reparto y el resumen por estado |
| `docs/api-v1.yaml` | Contrato | El enum y el schema del tablero |
| `frontend/app.js` | JavaScript | La lista `ESTADOS` |
| `frontend/index.html` | HTML | Una `<section>` más |

**Qué no se toca:** la base, las reglas y el CSS. El estado se guarda como texto (`String(20)` en `app/db/models.py`), así que la tabla acepta el valor nuevo sin cambios.

**Comprobado:** una tarjeta recorre las cuatro columnas a clicks, y los dos endpoints de tablero devuelven la columna `bloqueado`.

Las tres formas de dejarlo a medias dan tres resultados distintos:

- **Solo el frontend.** La columna aparece, pero al mover una tarjeta ahí la API responde 422: `Input should be 'backlog', 'en progreso' or 'hecho'`. La tarjeta no se mueve.
- **El Enum y el frontend, que parece suficiente.** El tablero funciona. Pero en cuanto hay una tarea bloqueada, `GET /v1/proyectos/1/tablero` y `GET /agent/proyectos/1/tablero` responden 500 con `KeyError`, y `scripts/client.py` deja de andar.
- **El backend completo y el frontend viejo.** Si otro cliente deja una tarea en «bloqueado», la página muestra una sola tarjeta de tres y la consola dice `Cannot read properties of null (reading 'appendChild')`. Es el error del caso 09 del detective.

**Para preguntar:** «¿Cómo me entero de que son ocho archivos y no dos?» Buscando antes de tocar. Los estados están escritos a mano en ocho archivos. Este comando devuelve exactamente esos ocho:

```bash
grep -rnE "en_progreso|EN_PROGRESO|en progreso" app frontend docs/api-v1.yaml
```

### F · Un campo nuevo: «prioridad»

**Qué pide:** que cada tarea tenga prioridad baja, media o alta, que se elija al crearla y que se vea en la tarjeta.

**Qué se toca:** diez archivos y además la base. Es el único de los seis que atraviesa las ocho capas.

| Archivos | Capa | Qué cambia |
| --- | --- | --- |
| `app/models/prioridad.py` (nuevo) y `app/models/tarea.py` | Dominio | El Enum y el campo, con `media` por defecto |
| `app/db/models.py` | Base | La columna en la tabla `tareas` |
| `app/repositories/tarea_repository.py` | Consultas | Tres lugares: al leer, al crear y al guardar |
| `app/routers/v1/schemas.py`, `app/routers/v1/tareas.py` y `docs/api-v1.yaml` | Contrato | Aceptar el campo al crear y al actualizar, y pasarlo |
| `app/services/tarea_service.py` | Reglas | Aplicarlo en la actualización parcial |
| `frontend/index.html` y `frontend/app.js` | HTML, CSS y JavaScript | El selector en el formulario, el color en la tarjeta y el envío |

**Comprobado:** crear con `"prioridad": "alta"` devuelve y guarda `alta`, un valor inválido responde 422 y la tarjeta creada desde el formulario sale con el borde rojo.

Dos formas de dejarlo a medias:

- **El código nuevo sobre una base ya creada.** Todos los pedidos responden 500 y el tablero queda vacío. La terminal dice `column tareas.prioridad does not exist`; el navegador, otra vez, muestra un error de CORS. El proyecto crea las tablas al arrancar, pero no modifica las que ya existen.
- **El router sin pasar el campo.** La API acepta `"alta"`, responde `"media"` y guarda `media`. No hay error en ningún lado: la prioridad se pierde en silencio.

Para el primer caso, el arreglo que probé es agregar la columna a mano. La alternativa es borrar la base y volver a correr `seed.py`.

```sql
ALTER TABLE tareas ADD COLUMN prioridad VARCHAR(10) NOT NULL DEFAULT 'media';
```

**Qué quedó sin tocar a propósito:** el tablero para agentes de s08 no muestra la prioridad. No es un olvido, es una decisión pendiente, y sirve para discutir en clase si un agente la necesita.

**Para preguntar:** «Si el campo es nuevo, ¿qué prioridad tienen las tareas que ya existían?» La que diga el valor por defecto. Por eso el default se decide antes de escribir código.

## Tres cosas que se repiten

**1. Olvidar una capa no siempre hace ruido.** Los mismos seis features muestran tres desenlaces.

| Qué se olvidó | Qué pasa | Avisa |
| --- | --- | --- |
| E, solo el frontend | 422 con un mensaje que dice qué valores acepta | Sí, y dice qué está mal |
| D sin el repository; F sin migrar la base | 500 y tablero vacío | Sí, pero hay que leer la terminal de la API |
| D sin el router; F sin pasar el campo | 200, y el dato se ignora | No |

La tercera fila es la que importa. Probar un feature es mirar el resultado, no comprobar que no haya errores.

**2. Un 500 del backend se ve como error de CORS en el navegador.** Pasó en C y en F. Cuando la API falla sin manejar el error, la respuesta sale sin el permiso de CORS y el navegador informa eso. Si un frontend que funcionaba empieza a hablar de CORS, lo primero es mirar la terminal de la API.

**3. Lo que no hubo que tocar es el beneficio de las capas.** C no tocó el frontend, D no tocó el service y E no tocó la base. Con todo en un solo archivo, como el `main.py` del principio de s05, cada feature tocaría «el archivo» y no habría nada que predecir.

## Cómo usarlo en clase

Cada feature se trabaja en cuatro movimientos, y los alumnos no escriben código.

1. Leés el pedido, en una frase.
2. Apuestan por chat qué capas toca, usando las cinco preguntas.
3. Mostrás la lista real de archivos. Este comando la imprime sin aplicar nada: `git apply --stat E-estado-bloqueado.patch`.
4. Apuestan qué pasa si se olvida una capa, y lo mostrás.

La matriz conviene mostrarla recién al final, como resumen.

Para mostrar un olvido en vivo, se aplica el parche completo y se deshace un archivo:

```bash
git apply C-regla-responsable.patch
git checkout -- app/main.py        # el feature C, sin su handler
```

| Olvido | Qué deshacer después de aplicar el parche |
| --- | --- |
| C sin el handler | `git checkout -- app/main.py` |
| D sin el router | `git checkout -- app/routers/v1/tareas.py` |
| D sin el repository | `git checkout -- app/repositories/tarea_repository.py` |
| E, solo el frontend | `git checkout -- app` |
| E, el Enum y el frontend | `git checkout -- app/routers app/models/tablero.py app/repositories` |
| E, con el frontend viejo | `git checkout -- frontend`, y mover una tarea a «bloqueado» desde `/docs` |
| F sin pasar el campo | `git checkout -- app/routers/v1/tareas.py` |
| F sin migrar la base | Nada: alcanza con aplicar el parche sobre la base que ya existía |

Para volver al original entre un feature y otro: `git checkout -- .` y, después del F, borrar `app/models/prioridad.py`.

Tiempos, como estimación mía: A y B 5 minutos cada uno, C y D 10, E y F 15. Una hora en total. Si hay que partirlo, A a D van en una clase y E y F en otra.

## Qué no pude probar

- **El servidor levantado desde un repo parcheado.** Ejecuté cada feature y cada olvido desde copias del proyecto. Los parches aplican limpio sobre `main`, y para C, E y F comprobé que aplicar y deshacer un archivo da el mismo código que ejecuté.
- **`docker compose`.** Usé un PostgreSQL 16 instalado directo.
- **Los tiempos con alumnos.**
