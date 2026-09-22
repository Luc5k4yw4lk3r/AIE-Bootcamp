---
tipo: tarea
modulo: 3
estado: pendiente
tags: [n8n, agentes]
---

# Tarea — Depuración de flujos en n8n

## Resumen

- Cuatro flujos rotos, uno por semana. Cada uno tiene **un fallo típico** de los que aparecen en clase: no dispara, una expresión quedó como texto literal, un dato que no está donde lo buscás, una fuente que devuelve vacío.
- Lo que se entrega no es el flujo arreglado. Se entregan **las cuatro respuestas del protocolo**, por escrito. El arreglo es la consecuencia.
- Cada semana es una **ventana sin copiloto** de 20 minutos. El objetivo no es sufrir: es leer un error entero al menos una vez por semana.

## El protocolo de las cuatro preguntas

> [!important] Pegalo al lado de la pantalla
> Cuando algo no funciona, antes de tocar nada:
>
> 1. **¿Llegó a ejecutarse?** ¿Hay una ejecución en la lista de *Executions*? ¿Qué nodos tienen el tilde verde y cuáles no?
> 2. **¿Cuál es el último punto donde había datos?** Abrí nodo por nodo, de izquierda a derecha, y mirá la pestaña *OUTPUT*. El fallo está entre el último nodo con datos correctos y el primero sin ellos.
> 3. **¿Qué esperaba yo que hubiera ahí?** Escribilo: qué campos, con qué nombres, con qué valores. Si no lo podés escribir, ese es el problema.
> 4. **¿Cuál es el cambio más chico que puedo probar?** Uno solo. Lo probás, mirás el resultado y volvés a la pregunta 1.

## Reglas de la ventana sin copiloto

- **20 minutos** con un temporizador. Si se termina, se termina: anotá hasta dónde llegaste.
- **Leé el error completo**, no solo el título en rojo. Casi siempre dice qué nodo, qué campo y qué esperaba.
- Nada de agente durante esos 20 minutos. **Después**, si hace falta, sí. Pero no pegues el error solo: escribí tres líneas.

> [!tip] Cómo pedirle ayuda al agente (o a un compañero)
> 1. **Esperaba:** qué tendría que salir y de qué nodo.
> 2. **Pasó:** qué salió en realidad, con el error exacto.
> 3. **Ya probé:** qué descartaste.
>
> Compará con "no me funciona, [error pegado]". La versión de tres líneas te obliga a hacer la mitad del diagnóstico antes de preguntar, y suele pasar que la respuesta aparece mientras la escribís.

## Cómo importar los flujos

Cada semana trae un bloque JSON. Copialo entero, abrí un workflow vacío en n8n y pegalo sobre el lienzo con `Ctrl+V` (o `Cmd+V`): aparecen los nodos ya conectados. Si tu versión de n8n no lo acepta, debajo de cada JSON está la descripción para armarlo a mano en dos minutos.

## Material para hacer los ejercicios

- [Understand n8n's data structure — documentación de n8n](https://docs.n8n.io/build/work-with-data/understand-n8ns-data-structure/) — qué es un *item* y por qué todo viaja como una lista de objetos `json`. Leela antes de la semana 1.
- [Types of executions — documentación de n8n](https://docs.n8n.io/build/understand-workflows/understand-executions/types-of-executions/) — la diferencia entre ejecutar a mano y un workflow publicado, y el error "not connected to any trigger". Para la semana 1.
- [Schedule Trigger — documentación de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/) — cuándo corre de verdad un disparador programado. Para la semana 1.
- [Expressions for data transformation — documentación de n8n](https://docs.n8n.io/build/work-with-data/transform-data/expressions-for-data-transformation/) — el modo *Expression* frente a *Fixed* y la sintaxis `{{ }}`. Para la semana 2.
- [Use the UI mapper — documentación de n8n](https://docs.n8n.io/build/work-with-data/reference-data/use-the-ui-mapper/) — arrastrar un campo desde *INPUT* para que n8n escriba la expresión por vos. Para la semana 2.
- [Reference previous nodes — documentación de n8n](https://docs.n8n.io/build/work-with-data/reference-data/reference-previous-nodes/) — `$json` frente a `$('Nodo').item.json`. Para la semana 3.
- [If — documentación de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/) — para la guarda de la semana 4.
- [Create and edit credentials — documentación de n8n](https://docs.n8n.io/build/understand-workflows/create-and-edit-credentials/) — para la parte de credenciales de la semana 4.
- [Debug executions — documentación de n8n](https://docs.n8n.io/build/understand-workflows/understand-executions/debug-executions/) — cómo traer los datos de una ejecución vieja al editor para reproducir un fallo.
- [Curso de N8N desde CERO (completo) — Soy Dalto](https://www.youtube.com/watch?v=4eRPQmzO_Nw) — si hace falta repasar cómo se mueve la interfaz.
- Los apuntes de [[M03·S01 - n8n]], sobre todo la parte de credenciales de Google.

## Parte 1: Las consignas

### Semana 1 — El flujo que no dispara

**Caso A.** Importá esto y tratá de ejecutarlo:

```json
{
  "nodes": [
    {
      "parameters": {
        "jsCode": "return [\n  { json: { cliente: 'Ana', pedido: 101 } },\n  { json: { cliente: 'Luis', pedido: 102 } }\n];"
      },
      "name": "Crear pedidos",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 0]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            { "id": "a1", "name": "aviso", "value": "={{ $json.cliente }}: tu pedido {{ $json.pedido }} salió", "type": "string" }
          ]
        },
        "options": {}
      },
      "name": "Armar aviso",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [440, 0]
    }
  ],
  "connections": {
    "Crear pedidos": { "main": [[{ "node": "Armar aviso", "type": "main", "index": 0 }]] }
  }
}
```

*A mano:* un nodo **Code** llamado `Crear pedidos` que devuelve dos pedidos, conectado a un **Edit Fields (Set)** llamado `Armar aviso`.

**Caso B.** Este flujo "debería correr cada 5 minutos". Importalo, esperá 10 minutos y mirá la pestaña *Executions*.

```json
{
  "nodes": [
    {
      "parameters": { "rule": { "interval": [{ "field": "minutes", "minutesInterval": 5 }] } },
      "name": "Cada 5 minutos",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [0, 0]
    },
    {
      "parameters": {
        "jsCode": "return [{ json: { chequeo: 'ok', hora: new Date().toISOString() } }];"
      },
      "name": "Registrar chequeo",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 0]
    }
  ],
  "connections": {
    "Cada 5 minutos": { "main": [[{ "node": "Registrar chequeo", "type": "main", "index": 0 }]] }
  }
}
```

*A mano:* **Schedule Trigger** cada 5 minutos → **Code** que devuelve la hora.

**Entrega:** las cuatro respuestas del protocolo para cada caso. Pista para la pregunta 1: en un caso la respuesta es "no se puede ni intentar" y en el otro "nunca se intentó". No son lo mismo.

### Semana 2 — La expresión que quedó como texto

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Ejecutar a mano",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [0, 0]
    },
    {
      "parameters": {
        "jsCode": "return [\n  { json: { nombre: 'Ana', email: 'ana@ejemplo.com', pedido: 101 } },\n  { json: { nombre: 'Luis', email: 'luis@ejemplo.com', pedido: 102 } },\n  { json: { nombre: 'Marta', email: 'marta@ejemplo.com', pedido: 103 } }\n];"
      },
      "name": "Cargar contactos",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 0]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            { "id": "b1", "name": "mensaje", "value": "Hola {{ $json.nombre }}, tu pedido {{ $json.pedido }} está listo", "type": "string" },
            { "id": "b2", "name": "destinatario", "value": "$json.email", "type": "string" }
          ]
        },
        "options": {}
      },
      "name": "Armar mensaje",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [440, 0]
    }
  ],
  "connections": {
    "Ejecutar a mano": { "main": [[{ "node": "Cargar contactos", "type": "main", "index": 0 }]] },
    "Cargar contactos": { "main": [[{ "node": "Armar mensaje", "type": "main", "index": 0 }]] }
  }
}
```

*A mano:* **Manual Trigger** → **Code** con tres contactos (`nombre`, `email`, `pedido`) → **Edit Fields (Set)** con dos campos: `mensaje`, con el valor `Hola {{ $json.nombre }}, tu pedido {{ $json.pedido }} está listo`, y `destinatario`, con el valor `$json.email`. Los dos se escriben con el campo en modo **Fixed**.

Ejecutalo. El flujo sale "en verde", sin ningún error. **Entrega:** las cuatro respuestas del protocolo, y además esto: ¿por qué un fallo que no da error es más peligroso que uno que sí da?

### Semana 3 — El dato que no está donde lo buscás

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Ejecutar a mano",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [0, 0]
    },
    {
      "parameters": {
        "jsCode": "// Simula filas leídas de una hoja de cálculo: los encabezados empiezan con mayúscula\nreturn [\n  { json: { Nombre: 'Ana', Email: 'ana@ejemplo.com' } },\n  { json: { Nombre: 'Luis', Email: 'luis@ejemplo.com' } }\n];"
      },
      "name": "Leer hoja",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 0]
    },
    {
      "parameters": {
        "jsCode": "return [{ json: { asunto: 'Tu resumen semanal' } }];"
      },
      "name": "Cargar plantilla",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 200]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            { "id": "c1", "name": "para", "value": "={{ $json.email }}", "type": "string" },
            { "id": "c2", "name": "saludo", "value": "=Hola {{ $json.nombre }}", "type": "string" },
            { "id": "c3", "name": "asunto", "value": "={{ $('Cargar plantilla').item.json.asunto }}", "type": "string" }
          ]
        },
        "options": {}
      },
      "name": "Preparar envío",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [440, 0]
    }
  ],
  "connections": {
    "Ejecutar a mano": { "main": [[{ "node": "Leer hoja", "type": "main", "index": 0 }]] },
    "Leer hoja": { "main": [[{ "node": "Preparar envío", "type": "main", "index": 0 }]] }
  }
}
```

*A mano:* **Manual Trigger** → **Code** `Leer hoja`, que devuelve filas con `Nombre` y `Email` (con mayúscula) → **Edit Fields (Set)** `Preparar envío`, con `para = {{ $json.email }}`, `saludo = Hola {{ $json.nombre }}` y `asunto = {{ $('Cargar plantilla').item.json.asunto }}`. Aparte, **sin conectar a nada**, un **Code** `Cargar plantilla` que devuelve `{ asunto: 'Tu resumen semanal' }`.

Este flujo tiene **dos** fallos, y el segundo solo aparece cuando arreglás el primero. **Entrega:** el protocolo completo para cada uno. En la pregunta 3, escribí literalmente el JSON que esperabas ver a la salida de `Preparar envío`.

### Semana 4 — Cuando llega vacío, y la credencial rota

**Parte A — la fuente vacía.**

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Ejecutar a mano",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [0, 0]
    },
    {
      "parameters": {
        "jsCode": "// Simula una API de ofertas que hoy no tiene resultados para tu búsqueda\nconst resultados = [];\nreturn resultados.map(r => ({ json: r }));"
      },
      "name": "Buscar ofertas",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 0]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            { "id": "d1", "name": "texto", "value": "=Nueva oferta: {{ $json.titulo }}", "type": "string" }
          ]
        },
        "options": {}
      },
      "name": "Formatear aviso",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [440, 0]
    },
    {
      "parameters": {
        "jsCode": "// En el flujo real esto sería Telegram o email\nreturn $input.all().map(i => ({ json: { enviado: true, texto: i.json.texto } }));"
      },
      "name": "Enviar aviso (simulado)",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [660, 0]
    }
  ],
  "connections": {
    "Ejecutar a mano": { "main": [[{ "node": "Buscar ofertas", "type": "main", "index": 0 }]] },
    "Buscar ofertas": { "main": [[{ "node": "Formatear aviso", "type": "main", "index": 0 }]] },
    "Formatear aviso": { "main": [[{ "node": "Enviar aviso (simulado)", "type": "main", "index": 0 }]] }
  }
}
```

*A mano:* **Manual Trigger** → **Code** `Buscar ofertas`, que devuelve una lista vacía → **Edit Fields (Set)** → **Code** que simula el envío.

Ejecutalo. "No pasa nada" y tampoco hay error. **Entrega:** el protocolo, y después modificá el flujo para que, cuando no haya ofertas, igual llegue un aviso que diga "Hoy no hay ofertas nuevas". Necesitás un nodo **If**.

**Parte B — la credencial rota.** Hacelo con una credencial tuya que ya funcione, en un flujo de prueba y no en el real:

1. En *Credentials*, duplicá la credencial (o creá una nueva del mismo tipo) y pegale una clave **con un carácter cambiado**.
2. Usala en un nodo que la necesite y ejecutalo.
3. **Entrega:** copiá el mensaje de error **completo**, incluido lo que aparece al desplegar los detalles. Marcá qué parte del mensaje te dice que es un problema de autenticación, y qué código HTTP devolvió el servicio (`401`, `403`…). ¿En qué se diferencia de un error de datos como los de las semanas 2 y 3?
4. Al final, borrá la credencial rota.

## Parte 2: Las soluciones

### Solución: Semana 1

**Caso A:** no hay ningún disparador. n8n no tiene cuándo arrancar el flujo, así que no se puede ejecutar: al intentar *Execute step* sobre un nodo aparece *"The destination node is not connected to any trigger"*.

1. ¿Se ejecutó? No, y ni siquiera se puede intentar.
2. Último punto con datos: ninguno.
3. Esperaba que al ejecutar salieran dos avisos.
4. Cambio mínimo: agregar un **Manual Trigger** y conectarlo a `Crear pedidos`.

**Caso B:** el Schedule Trigger solo corre solo cuando el workflow está **publicado** (en versiones anteriores de n8n, el interruptor se llamaba *Active*). Un flujo importado queda sin publicar. Mientras estás editando, solo corre cuando apretás *Execute workflow*.

1. ¿Se ejecutó? No: la lista de *Executions* está vacía. Nunca se intentó.
2. Último punto con datos: ninguno.
3. Esperaba una ejecución cada 5 minutos.
4. Cambio mínimo: publicarlo (o activarlo), esperar 5 minutos y volver a mirar *Executions*.

La diferencia importa: en A el problema es de diseño, porque falta una pieza. En B el flujo está bien y el problema es de estado: está apagado.

### Solución: Semana 2

La salida de `Armar mensaje` es literalmente:

```json
{ "mensaje": "Hola {{ $json.nombre }}, tu pedido {{ $json.pedido }} está listo", "destinatario": "$json.email" }
```

Los dos campos están en modo **Fixed**, así que n8n los trata como texto y no evalúa nada. En el JSON del workflow se nota porque al valor le falta el `=` inicial: una expresión se guarda como `"={{ $json.nombre }}"`.

1. ¿Se ejecutó? Sí, todo en verde.
2. Último punto con datos correctos: la salida de `Cargar contactos` tiene `nombre`, `email` y `pedido` bien.
3. Esperaba `"Hola Ana, tu pedido 101 está listo"` y `"ana@ejemplo.com"`.
4. Cambio mínimo: pasar `mensaje` a modo **Expression**. En el editor, el texto dentro de `{{ }}` se pone de color y aparece la vista previa del resultado. En `destinatario` no alcanza con cambiar el modo: `$json.email` sin llaves sigue siendo texto. Tiene que quedar `{{ $json.email }}`. Lo más seguro es **arrastrar el campo desde el panel INPUT**, y así n8n escribe la expresión por vos.

**¿Por qué es más peligroso?** Porque nadie se entera. El flujo "funciona", y el día que el paso siguiente sea enviar un email de verdad, lo que se envía es `{{ $json.nombre }}` a 300 personas. La costumbre que protege es mirar la vista previa de cada expresión antes de dar un nodo por terminado.

### Solución: Semana 3

**Fallo 1 — el nodo que no se ejecutó.** El campo `asunto` pide datos de `Cargar plantilla`, pero ese nodo no está conectado, así que en esta ejecución nunca corrió y no tiene datos para dar. n8n corta con un error que nombra al nodo referenciado y dice que no se ejecutó.

1. ¿Se ejecutó? Sí, hasta `Preparar envío`, que falla.
2. Último punto con datos: la salida de `Leer hoja`.
3. Esperaba que `asunto` valiera `"Tu resumen semanal"`.
4. Cambio mínimo: conectar `Cargar plantilla` en el camino (por ejemplo, `Ejecutar a mano` → `Cargar plantilla` → `Leer hoja` → `Preparar envío`), o, si el asunto es fijo, escribirlo directo en el campo. Regla general: **`$('Nodo')` solo funciona con nodos que ya corrieron antes en la misma ejecución.**

**Fallo 2 — el nombre que no coincide.** Ya sin error, la salida es:

```json
{ "para": "", "saludo": "Hola ", "asunto": "Tu resumen semanal" }
```

Los campos se llaman `Email` y `Nombre`, con mayúscula, y la expresión pide `email` y `nombre`. Para n8n son claves distintas, y una clave que no existe vale vacío, **sin error**.

1. ¿Se ejecutó? Sí, todo verde.
2. Último punto con datos correctos: `Leer hoja`. Ahí mismo se ve que las claves tienen mayúscula.
3. Esperaba `{ "para": "ana@ejemplo.com", "saludo": "Hola Ana", "asunto": "Tu resumen semanal" }`.
4. Cambio mínimo: `{{ $json.Email }}` y `{{ $json.Nombre }}`. De nuevo: arrastrar el campo desde *INPUT* evita este error por completo.

Esto pasa todo el tiempo con Google Sheets: los encabezados de la hoja se convierten en las claves del JSON, tal cual están escritos, con mayúsculas, espacios y tildes.

### Solución: Semana 4

**Parte A.** `Buscar ofertas` devuelve **cero items**, y en n8n cada nodo se ejecuta una vez por item que recibe. Con cero items, los nodos siguientes no tienen nada que procesar y el flujo termina "bien" sin haber hecho nada.

1. ¿Se ejecutó? Sí, sin error.
2. Último punto con datos: ninguno. `Buscar ofertas` muestra que no devolvió items, y los nodos siguientes no llegaron a correr.
3. Esperaba una lista de ofertas, o al menos un aviso de que no había.
4. Cambio mínimo: que la búsqueda **siempre** devuelva un item que diga cuántos resultados hubo, y decidir con un **If**.

Una forma de hacerlo:

- En `Buscar ofertas`, devolver un solo item con el total:

  ```js
  const resultados = [];
  return [{ json: { total: resultados.length, ofertas: resultados } }];
  ```

- Agregar un **If** con la condición `{{ $json.total }}` *is greater than* `0`.
  - La rama **true** va a un nodo que separa las ofertas (Split Out sobre `ofertas`) y de ahí a `Formatear aviso`.
  - La rama **false** va a un **Edit Fields** con `texto = Hoy no hay ofertas nuevas` y de ahí al envío.

Otra opción es activar *Always Output Data* en la configuración (*Settings*) de `Buscar ofertas`: así devuelve un item vacío en lugar de ninguno. Funciona, pero el If con `total` deja más claro qué está pasando para quien lea el flujo después.

**Parte B.** El error de credencial se reconoce porque:

- trae un código **401** (no autenticado) o **403** (autenticado pero sin permiso) y palabras como *Unauthorized*, *invalid API key*, *authentication*, *Forbidden*;
- falla **siempre igual, con cualquier dato de entrada**. Un error de datos cambia según lo que entra; uno de credencial no;
- falla en el primer nodo que usa esa credencial, aunque todo lo anterior esté perfecto.

Cuando lo veas, no toques el flujo: revisá la credencial. Fijate si la clave está completa (se cortó al copiar, tiene un espacio al final), si es del proyecto correcto, si venció, y en OAuth de Google, si la app está publicada (ver [[M03·S01 - n8n]]).

## Relacionado

- [[Tarea]]
- [[Tarea - Repaso 04 - El recorrido del dato en n8n]] — la otra mitad: entender qué forma tiene el dato en cada paso.
- [[Tarea - Repaso 01 - Python esencial - namespaces, archivos y algoritmos]] — los bloques 4 y 5 son lo mismo, pero en Python.
- [[M03·S01 - n8n]] · [[M03·S04 - Proyectos de n8n con Claude Code]]
