---
tipo: tarea
modulo: 3
estado: pendiente
tags: [n8n, apis]
---

# Tarea — El recorrido del dato en n8n

## Resumen

- Un flujo de n8n se puede contar de dos formas. **Por nodos:** "acá conecto la API con el filtro y el filtro con Telegram". **Por datos:** "acá entra un JSON con estos campos, este nodo lo convierte en tres items y el siguiente espera `salario_min` como número". La segunda es la que te permite arreglarlo cuando se rompe.
- Cuatro semanas para pasar de la primera a la segunda: predecir, documentar, romper a propósito y explicar.
- Se hace **sin agente**. Esta tarea mide qué tenés en la cabeza, no qué puede generar el agente.

## Material para hacer los ejercicios

- [Understand n8n's data structure — documentación de n8n](https://docs.n8n.io/build/work-with-data/understand-n8ns-data-structure/) — la base de todo: los datos viajan como una **lista de items** y cada item tiene su `json`. Leela antes de la semana 1.
- [Reference previous nodes — documentación de n8n](https://docs.n8n.io/build/work-with-data/reference-data/reference-previous-nodes/) — `$json`, `$input.all()` y `$('Nodo')`.
- [Expressions for data transformation — documentación de n8n](https://docs.n8n.io/build/work-with-data/transform-data/expressions-for-data-transformation/) — cómo se navega un JSON anidado dentro de `{{ }}`.
- [Pin and mock data — documentación de n8n](https://docs.n8n.io/build/work-with-data/pin-and-mock-data/) — fijar la salida de un nodo para probar el resto sin volver a llamar a la API. Muy útil en la semana 3.
- [Edit Fields (Set) — documentación de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.set/) — qué campos deja pasar y cuáles no.
- [If — documentación de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/) — para las guardas de la semana 3.
- El bloque 4 de [[Tarea - Repaso 01 - Python esencial - namespaces, archivos y algoritmos]]: es el mismo ejercicio mental, pero en Python. Si te cuesta la semana 1, hacé ese bloque antes.
- [[M03·S04 - Proyectos de n8n con Claude Code]], sección "Documentar el proyecto con OKF": el formato para la semana 4.

## Parte 1: Las consignas

### Semana 1 — Predecir antes de ejecutar

Importá este flujo pegándolo en un workflow vacío con `Ctrl+V`, pero **no lo ejecutes todavía**.

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
        "jsCode": "return [{ json: {\n  total: 3,\n  results: [\n    { id: 1, title: 'AI Engineer Junior', company: { name: 'Acme', city: 'Madrid' }, salary: { min: 32000, max: 38000 }, remote: true },\n    { id: 2, title: 'Data Analyst', company: { name: 'Datos SL', city: 'Valencia' }, salary: { min: 26000, max: 30000 }, remote: false },\n    { id: 3, title: 'Automation Specialist', company: { name: 'FlowCo', city: 'Barcelona' }, salary: { min: 35000, max: 42000 }, remote: true }\n  ]\n} }];"
      },
      "name": "API simulada",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [220, 0]
    },
    {
      "parameters": {
        "jsCode": "const respuesta = $input.first().json;\nreturn respuesta.results.map(oferta => ({ json: oferta }));"
      },
      "name": "Separar ofertas",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [440, 0]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            { "id": "e1", "name": "titulo", "value": "={{ $json.title }}", "type": "string" },
            { "id": "e2", "name": "empresa", "value": "={{ $json.company.name }}", "type": "string" },
            { "id": "e3", "name": "salario_min", "value": "={{ $json.salary.min }}", "type": "number" },
            { "id": "e4", "name": "remoto", "value": "={{ $json.remote }}", "type": "boolean" }
          ]
        },
        "options": {}
      },
      "name": "Aplanar",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [660, 0]
    },
    {
      "parameters": {
        "jsCode": "return $input.all().filter(item => item.json.salario_min >= 30000);"
      },
      "name": "Filtrar por salario",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [880, 0]
    }
  ],
  "connections": {
    "Ejecutar a mano": { "main": [[{ "node": "API simulada", "type": "main", "index": 0 }]] },
    "API simulada": { "main": [[{ "node": "Separar ofertas", "type": "main", "index": 0 }]] },
    "Separar ofertas": { "main": [[{ "node": "Aplanar", "type": "main", "index": 0 }]] },
    "Aplanar": { "main": [[{ "node": "Filtrar por salario", "type": "main", "index": 0 }]] }
  }
}
```

Leé el código y la configuración de cada nodo y escribí, en papel o en un archivo:

1. **Cuántos items** sale de cada uno de los cuatro nodos.
2. **El JSON del primer item** que sale de cada nodo, completo, con todos sus campos.
3. Qué campos que **existían** en `Separar ofertas` ya **no existen** después de `Aplanar`, y por qué.

Recién entonces ejecutalo y compará nodo por nodo. Anotá cada diferencia entre lo que predijiste y lo que salió. **Cada diferencia es algo que aprendiste.**

### Semana 2 — El contrato de datos de un flujo propio

Elegí **uno de tus flujos reales** (si tenés varios, el que más miedo te da que se rompa). Para cada nodo, completá una fila de esta tabla:

| Nodo | Recibe (campos y tipos) | Devuelve (campos y tipos) | Items que entran → salen | ¿Qué pasa si recibe vacío? |
|---|---|---|---|---|
| … | … | … | … | … |

Reglas:

- Los campos se escriben con su nombre **exacto**: mayúsculas, espacios y tildes incluidos.
- Si un campo viene anidado, escribí la ruta completa: `company.name`, no "la empresa".
- Si no sabés qué devuelve un nodo, **ejecutalo y mirá**. No lo supongas y no se lo preguntes al agente.
- La última columna podés dejarla con "no sé". Es la que se trabaja en la semana 3.

### Semana 3 — ¿Qué pasa si…?

Con el flujo de la semana 1, y después con el tuyo, probá estos tres casos. Para cada uno, **primero predecí** qué va a pasar, después probalo y por último agregá una guarda (un **If**, un valor por defecto o un aviso) para que el flujo no falle en silencio.

1. **Falta un campo:** en `API simulada`, borrale `salary` a una de las ofertas.
2. **La lista viene vacía:** dejá `results: []`.
3. **Un tipo distinto:** poné `min: '32.000'`, como texto y con punto de miles, en una oferta.

Truco: con **pin data** (el ícono del alfiler en la salida de un nodo) podés fijar la salida de `API simulada` y editarla a mano para cada caso, sin tocar el código. Ver la documentación de *Pin and mock data* en el material.

### Semana 4 — Explicarlo en 10 minutos

Prepará una explicación de **tu** flujo para contarla en la pizarra en 10 minutos, **sin mirar n8n**. Tiene que tener:

1. **Un diagrama** hecho a mano o con cualquier herramienta de diagramas. En cada flecha va **qué dato viaja**, no solo la conexión. Por ejemplo: `3 items {titulo, empresa, salario_min}`.
2. **El recorrido de un caso concreto:** una oferta (o el dato que maneje tu flujo) desde que entra hasta que llega el mensaje. En cada paso: dónde vive, qué forma tiene y quién la transforma.
3. **Un punto débil que conozcas:** dónde se rompería primero y qué harías.
4. **Una decisión que tomaste y por qué.** Por ejemplo: "separé la ingesta del filtrado en dos flujos porque…".

Para practicar, contáselo a alguien que no esté en el curso. Si esa persona te sigue, ya está listo para la pizarra.

## Parte 2: Las soluciones

### Solución: Semana 1

| Nodo | Items que salen | Primer item |
|---|---|---|
| `API simulada` | **1** | `{ "total": 3, "results": [ …las tres ofertas… ] }` |
| `Separar ofertas` | **3** | `{ "id": 1, "title": "AI Engineer Junior", "company": { "name": "Acme", "city": "Madrid" }, "salary": { "min": 32000, "max": 38000 }, "remote": true }` |
| `Aplanar` | **3** | `{ "titulo": "AI Engineer Junior", "empresa": "Acme", "salario_min": 32000, "remoto": true }` |
| `Filtrar por salario` | **2** | igual que el anterior. Quedan AI Engineer Junior (32000) y Automation Specialist (35000); Data Analyst (26000) queda afuera |

Lo que más suele fallar en la predicción:

- **`API simulada` devuelve 1 item, no 3.** La lista de ofertas está *dentro* de un solo item. Casi todas las APIs reales responden así: un objeto con la lista adentro. Por eso existe `Separar ofertas`, que convierte una lista de adentro en items de verdad. En n8n también se puede hacer sin código, con el nodo **Split Out**.
- **Después de `Aplanar` desaparecen `id`, `company.city`, `salary.max` y `total`.** *Edit Fields* deja pasar **solo los campos que definís**, salvo que actives la opción para incluir los demás campos de entrada. Si un nodo más adelante necesitara el `id`, fallaría en silencio.
- **`salario_min` es un número y no un texto,** porque el campo está configurado con tipo *Number*. Por eso la comparación `>= 30000` del filtro funciona como se espera.

### Solución: Semana 2

No hay una única respuesta: es tu flujo. Un contrato bien hecho se ve así:

| Nodo | Recibe | Devuelve | Items | Si recibe vacío |
|---|---|---|---|---|
| `Leer ofertas (HTTP)` | — (disparador) | `{ total: number, results: [ {title, company.name, salary.min, …} ] }` | 0 → 1 | Si la API responde `results: []`, sale 1 item con la lista vacía |
| `Separar ofertas` | el objeto de arriba | cada oferta como item: `{title, company, salary, remote}` | 1 → N | Con `results: []` salen **0 items** y todo lo que sigue deja de ejecutarse |
| `Aplanar` | `{title, company.name, salary.min, remote}` | `{titulo: string, empresa: string, salario_min: number, remoto: boolean}` | N → N | No se ejecuta |

Señales de que el contrato todavía está flojo: filas que dicen "los datos de la oferta" en lugar de los campos, rutas sin el nivel intermedio (`name` en vez de `company.name`) o ningún "no sé" en la última columna. Algún "no sé" tiene que haber, y es honesto que esté.

### Solución: Semana 3

1. **Falta `salary`:** la expresión `{{ $json.salary.min }}` intenta leer `min` de algo que no existe. Según la versión, `Aplanar` falla con un error sobre esa expresión, o deja el campo vacío. Cualquiera de los dos es un problema: en el primer caso se corta todo por una sola oferta, y en el segundo esa oferta pasa el filtro con un salario inventado o desaparece sin avisar. Guardas posibles:
   - un **If** antes de `Aplanar` con la condición *`salary` exists*, que manda las ofertas sin salario por otra rama (para registrarlas o avisar);
   - o un valor por defecto en la expresión: `{{ $json.salary?.min ?? 0 }}`. Si tu versión no acepta `?.`, usá el If.
2. **`results: []`:** `Separar ofertas` devuelve 0 items y el resto del flujo no corre. No hay error y no hay aviso. Es el mismo caso que la semana 4 de [[Tarea - Repaso 05 - Depuración de flujos en n8n]]: la guarda es devolver siempre un item con `total` y decidir con un If.
3. **`min: '32.000'`:** el campo es de tipo *Number*, así que `Aplanar` intenta convertir `'32.000'`. Según la configuración, falla o lo interpreta mal: `32.000` puede quedar como **32**, porque el punto se lee como separador decimal. Una oferta de 32 no pasa el filtro de 30000 y desaparece sin avisar. La guarda es limpiar el texto antes de convertirlo, por ejemplo `{{ Number(String($json.salary.min).replaceAll('.', '')) }}`, y **verificar la vista previa**.

La lección de las tres es la misma: los fallos más caros de un flujo **no dan error**. Dan un resultado plausible y equivocado.

### Solución: Semana 4

Checklist para autoevaluarte antes de salir a la pizarra:

- [ ] Cada flecha del diagrama dice qué dato viaja y cuántos items.
- [ ] Puedo decir el nombre exacto de al menos tres campos sin mirar.
- [ ] Sé en qué nodo una lista se convierte en items separados, y en cuál vuelven a juntarse si pasa.
- [ ] Sé qué hace mi flujo si la fuente viene vacía.
- [ ] Sé qué credenciales usa y qué nodo falla primero si una vence.
- [ ] Puedo contar una decisión de diseño con su *porque*.

Si alguna casilla queda sin marcar, esa es la próxima ventana sin copiloto.

## Relacionado

- [[Tarea]]
- [[Tarea - Repaso 05 - Depuración de flujos en n8n]] — la misma habilidad, pero partiendo del error.
- [[Tarea - Repaso 01 - Python esencial - namespaces, archivos y algoritmos]] — el bloque 4 es este mismo ejercicio en Python.
- [[M03·S01 - n8n]] · [[M03·S04 - Proyectos de n8n con Claude Code]]
