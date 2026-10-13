# TaskFlow — Clase puente: qué es una API, vista desde el navegador

Oct 1, 2026 · @Luciano

La clase desarma el TaskFlow terminado con las DevTools del navegador para llegar a una sola idea: una API es una URL que devuelve datos en vez de una página. Los alumnos no escriben código; miran, apuestan qué va a pasar y comprueban.

Ejecuté los nueve pasos de la demo contra el código de s12, con la API en el puerto 8000, el front en el 3000 y PostgreSQL 16. Las capturas son de esa corrida. Lo que no pude probar está listado al final.

## El mapa

![[Pasted image 20261013135207.png]]

Los pasos 1 a 3 son pedidos que salen del navegador; el 4 pasa adentro. La base de datos nunca habla con el navegador: solo la API llega a ella.

Este dibujo cierra el paso 6 de la demo y conviene dejarlo proyectado hasta el final.

## Preparación

El tag `s12` todavía no existe en el repo. El código de s12 es el último commit de `main`.

```bash
git checkout main
pip install -r requirements.txt
cp .env.example .env
docker compose up -d                            # PostgreSQL
python scripts/seed.py                          # datos de ejemplo
uvicorn app.main:app --reload --env-file .env   # API en el puerto 8000
cd frontend && python -m http.server 3000       # front en el 3000, en otra terminal
```

Antes de que lleguen los alumnos:

- Abrir `http://localhost:3000` y confirmar que hay una tarjeta en cada columna.
- Dejar las DevTools abiertas en la pestaña Network, con «Disable cache» marcado y la letra agrandada para el proyector.
- Dejar a la vista las dos terminales, la de la API y la del front. Cada servidor imprime los pedidos que recibe, y eso refuerza que son dos programas.

## Antes de la demo: API humana

Diez minutos sin computadoras. Deja instalada la idea de pedido y respuesta antes de mostrar una sola pantalla.

1. Un alumno es el servidor. Tiene una hoja con tres tareas que nadie más puede ver ni tocar.
2. El resto son clientes. Solo pueden pasarle papelitos con este formato: `GET /tareas`, `POST /tareas` con un título, `POST /tareas/2/mover` con un estado.
3. El servidor responde cada papelito con un número y datos: `200` y la lista, `201` y la tarea creada, `404` si la tarea no existe, `422` si el papelito está mal escrito.
4. Probar a propósito un papelito mal formado y un pedido hecho de palabra. El servidor no responde a lo que no llega por papelito.

Después del juego, la tabla de equivalencias queda en el pizarrón durante toda la demo.

| En el juego | En TaskFlow |
| --- | --- |
| La hoja de tareas | La base de datos, PostgreSQL |
| El alumno servidor | La API, hecha con FastAPI |
| El formato del papelito | El contrato de la API: qué URL, qué método, qué datos |
| El número de la respuesta | El código de estado HTTP |
| Los que pasan papelitos | Los clientes: la página, un script, Swagger |

## La demo

Cada paso tiene el mismo ritmo: pregunta, apuesta de los alumnos, acción, lo que se ve. La apuesta es lo que hace que se acuerden.

### 1. Cargar la página con Network abierta

**Pregunta:** «¿Cuántas cosas tiene que pedir el navegador para mostrar esta página?»

Abrir `http://localhost:3000`. Aparecen tres pedidos.

| Pedido | Quién responde | Qué vuelve | Tamaño |
| --- | --- | --- | --- |
| `localhost:3000/` | Servidor de archivos | HTML | 2.320 bytes |
| `localhost:3000/app.js` | Servidor de archivos | JavaScript | 3.774 bytes |
| `localhost:8000/v1/tareas?proyecto_id=1&limit=100` | API | JSON | 733 bytes |

Abrir la respuesta de cada uno. Los dos primeros son archivos de texto que alguien escribió. El tercero va a otro puerto y trae datos.

&#91;image: El tablero de TaskFlow cargado, con una tarjeta en cada columna\]

### 2. Código fuente contra Inspeccionar

**Pregunta:** «El HTML que llegó, ¿tenía las tarjetas?»

«Ver código fuente» (`Ctrl+U`) muestra lo que mandó el servidor: tres columnas vacías y cero tarjetas. «Inspeccionar» muestra la página como está ahora: tres tarjetas. La diferencia la puso `app.js` después de que el HTML llegó.

### 3. Desactivar JavaScript

**Pregunta:** «Si JavaScript no corre, ¿qué queda?»

En las DevTools, `Ctrl+Shift+P`, escribir «Disable JavaScript» y recargar. En Network queda un solo pedido: no se pide `app.js` ni se llama a la API. El tablero aparece vacío. Eso es todo lo que sabe hacer el servidor de archivos. Volver a activarlo antes de seguir.

&#91;image: El mismo tablero sin JavaScript: las tres columnas vacías\]

### 4. Borrar el CSS

**Pregunta:** «Si saco los estilos, ¿se pierde contenido o se pierde forma?»

En la pestaña Elements, seleccionar el `<style>` dentro de `<head>` y borrarlo con `Delete`. El contenido sigue entero, tarjetas incluidas. Se van las columnas, los fondos y los bordes.

&#91;image: El tablero sin CSS: los mismos títulos y tareas, uno debajo del otro, sin columnas ni bordes\]

En este proyecto el CSS viaja dentro de `index.html`, por eso no tiene un pedido propio en Network. Recargar para recuperarlo.

La frase que cierra los primeros cuatro pasos: el HTML es lo que hay, el CSS es cómo se ve y JavaScript es lo que pasa después de que la página llegó.

### 5. Apagar la API

**Pregunta:** «Apago la API y recargo. ¿Se ve la página?»

`Ctrl+C` en la terminal de uvicorn y recargar. La página llega igual: los pedidos de HTML y de `app.js` responden 200. El tercero queda en rojo con `net::ERR_CONNECTION_REFUSED`, la consola muestra `Failed to fetch` y el tablero se ve como en el paso 3, con las columnas vacías.

Son dos programas distintos en dos puertos distintos. Volver a levantar la API.

### 6. La URL de la API en la barra de direcciones

**Pregunta:** «¿Qué pasa si pego esa tercera URL en la barra, como si fuera una página?»

Pegar `http://localhost:8000/v1/tareas?proyecto_id=1&limit=100`. El navegador muestra JSON crudo.

&#91;image: La respuesta de la API vista en el navegador: texto JSON con las tres tareas\]

Acá se dice la definición: una API es una URL que devuelve datos en vez de una página. El navegador pidió las dos cosas de la misma manera. Cambia lo que vuelve y para quién es: el HTML es para una persona, el JSON es para un programa, en este caso `app.js`.

### 7. Hacer click en una tarjeta

**Pregunta:** «Muevo una tarjeta. ¿El navegador le avisa a alguien?»

Limpiar Network y hacer click en «Escribir documentación de la API». Aparece un pedido nuevo.

```
POST http://localhost:8000/v1/tareas/3/mover
se envía:   {"estado":"en progreso"}
vuelve:     200, con la tarea completa y su estado nuevo
```

No todos los pedidos son para leer. Este lleva datos de ida y pide un cambio.

### 8. Abrir otra ventana

**Pregunta:** «Abro la página en otra ventana. ¿La tarjeta está donde la dejé o donde estaba al principio?»

Abrir `http://localhost:3000` en una ventana de incógnito. La tarjeta está en «en progreso». El cambio no quedó en la pestaña: quedó en el servidor, y cualquiera que pregunte recibe lo mismo.

### 9. Otro cliente para la misma API

**Pregunta:** «¿Hace falta una página web para usar la API?»

En una terminal, `python scripts/client.py`. El script crea dos tareas, «Diseñar el tablero» y «Escribir el README», y mueve la primera. Recargar el tablero: las tareas del script están ahí.

Después abrir `http://localhost:8000/docs`. Swagger es un tercer cliente de la misma API, y ese ya lo conocen.

### El cierre de la demo, en un dibujo

![[Pasted image 20261013135242.png]]

La página, el script y Swagger mandan los mismos pedidos y reciben las mismas respuestas. Por eso se puede construir y probar la API antes de que exista una sola pantalla, que es lo que vienen haciendo desde s05.

## Volver a Python

El cierre conecta lo que vieron con lo que están construyendo. Abrir `http://localhost:8000/health` en la barra: se ve `{"status":"ok"}`. Al lado, mostrar la función que lo produce, que es la del paso 1 de s05.

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

La función devuelve un dict y el navegador recibe ese JSON. Todo lo que escriben en Python desde s05 es esto mismo con más reglas adentro: funciones que reciben un pedido y devuelven datos.

## Tropiezos previsibles

- **Abrir `index.html` con doble click.** Es la costumbre que queda de s11. El tablero aparece vacío y la consola dice `Access to fetch at 'http://localhost:8000/v1/tareas?proyecto_id=1&limit=100' from origin 'null' has been blocked by CORS policy`. Hay que entrar por `http://localhost:3000`.
- **Servir el front en otro puerto.** `app/main.py` solo autoriza los orígenes `http://localhost:3000` y `http://127.0.0.1:3000`. Con Live Server u otro puerto debería aparecer el mismo error de CORS.
- **Tablero vacío y sin errores.** Falta `python scripts/seed.py`. Sin los datos de ejemplo existe el proyecto «General», pero no tiene tareas.
- **Un pedido de más en cada POST.** Antes de `POST .../mover` el navegador manda un `OPTIONS` a la misma URL; el log de la API muestra los dos. Es la consulta previa de CORS. Para esta clase alcanza con «el navegador pregunta si puede»; el tema completo es de s12.
- **`/docs` en blanco.** Swagger carga su interfaz desde `cdn.jsdelivr.net`. Sin internet en el aula no se dibuja.
- **Un `favicon.ico` en rojo.** Chrome suele pedirlo por su cuenta y el servidor de archivos no lo tiene. Se puede ignorar.

## Tiempos y qué no probé

Tiempos, como estimación mía: API humana 10 minutos, demo 40, volver a Python 10. Una hora en total.

Lo que no pude probar:

- **Los clicks en las DevTools.** Hice lo equivalente por automatización en Chromium: sin JavaScript, sin `<style>`, con registro de pedidos y de consola. Los resultados son los reales; los atajos de teclado no los verifiqué en tu Chrome.
- **`/docs` dibujado.** El entorno donde corrí todo no tiene salida al CDN de Swagger.
- **El front en un puerto distinto de 3000 y el pedido de `favicon.ico`.** Salen de leer el código y de cómo se comporta Chrome normalmente.
- **`docker compose`.** Usé un PostgreSQL 16 instalado directo, con las mismas credenciales de `.env.example`.

La clase sigue en Parte 2 — El frontend por dentro, que abre los archivos del frontend: HTML, CSS y JavaScript por dentro.
