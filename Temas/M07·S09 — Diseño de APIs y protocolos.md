# M07·S09 — Diseño de APIs y protocolos: cómo habla TaskFlow con sus clientes y cómo evoluciona sin romperlos

|                                  |                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sesión**                       | M07·S09 · Semana 2 — Gestión de datos y diseño de APIs                                                                                                                                                                                                                                                                                                            |
| **Fecha**                        | [Completar por el profesor: fecha de la sesión]                                                                                                                                                                                                                                                                                                                   |
| **Módulo**                       | 07 — Fundamentos de Software + System Design para AI Engineers                                                                                                                                                                                                                                                                                                    |
| **Tema**                         | Contrato primero (design-first) vs código primero (code-first), versionado `/v1` → `/v2` con deprecación legible por máquina, y los protocolos que TaskFlow necesita más allá del request/response: WebSocket para el tablero en vivo, una cola (Redis Streams) para las notificaciones por email, gRPC para un servicio interno, y TCP vs UDP por debajo de todo |
| **Duración estimada de estudio** | ≈ 10 h: ~3 h 30 min de lectura de recursos + ~3 h 30 min de lab + ~3 h de ejercicios                                                                                                                                                                                                                                                                              |

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Diseñar** un endpoint de TaskFlow en modo *design-first*: escribir el contrato OpenAPI a mano, validarlo con un linter, levantar un mock y **comparar** el contrato con el `openapi.json` que genera FastAPI (code-first).
2. **Clasificar** un cambio de API como compatible o incompatible, y **versionar** un breaking change real (`assignee` → `assignee_id`) con `/v1` y `/v2` conviviendo en FastAPI, `/v1` como adaptador y headers `Deprecation` / `Sunset` / `Link`.
3. **Construir** un tablero en vivo con WebSocket en FastAPI, alimentado por `task_events` vía `LISTEN/NOTIFY`, que funcione con varios workers de Uvicorn y re-sincronice por HTTP al reconectar. Y **explicar** cuándo SSE alcanza.
4. **Implementar** un worker de notificaciones sobre Redis Streams con consumer group, ack después de procesar, rescate de mensajes colgados e idempotencia, y **debuggearlo** con `XINFO` y `XPENDING`.
5. **Definir** un servicio interno con gRPC y Protocol Buffers (`.proto`, stubs generados, deadline) y **explicar** por qué en protobuf el contrato es el número de campo y no el nombre.
6. **Demostrar** con `socket` la diferencia entre TCP (byte-stream confiable, sin límites de mensaje) y UDP (datagramas sin garantía), y **registrar** la elección de protocolos de TaskFlow en TJ-008.

---

## 2. Resumen ejecutivo

Hasta M07·S08, TaskFlow habla un solo idioma: **HTTP request/response**. El cliente pide, el servidor contesta y la conexión se olvida. Para el CRUD de tareas de M07·S05 alcanza, pero el producto ya pide tres cosas que ese idioma resuelve mal, más un cambio de contrato que va a romper clientes:

- **Tablero en vivo.** Ana mueve la tarea #42 a *en progreso* y Beto tiene que verlo sin recargar. S08 dejó la fuente de esos eventos (`task_events` + `LISTEN/NOTIFY`). Hoy la conectamos a un **WebSocket**.
- **Email cuando te asignan una tarea.** Mandar un email es lento y falla, así que no puede frenar el `PATCH`. Se desacopla con una **cola** (Redis Streams, que está en el compose desde S06), y eso trae acks, reintentos e idempotencia.
- **Un servicio interno de notificaciones** (hipotético), que habla con el backend por **gRPC**.
- **`assignee` → `assignee_id`**, el cambio que S07 dejó en fase *expand* en la base. Hoy llega al contrato HTTP como `/v2`, con `/v1` deprecado.

Andrew Ng, en su *AI Engineering Skills Map* (2026), lista **la elección y el diseño de APIs** y **el procesamiento asíncrono** entre los componentes que maneja un desarrollador full-stack competente. Son exactamente los trade-offs que un agente de código decide mal si nadie se los especifica: le pedís "tablero en vivo" y te devuelve polling o una lista de sockets en memoria que se rompe con dos workers. REST, GraphQL y los códigos de estado quedan para S10. Hoy es **el transporte y la evolución del contrato**.

---

## 3. Conceptos clave (glosario)

Solo los términos nuevos.

| Término | Definición |
|---|---|
| **Design-first (top-down)** | Primero se escribe el contrato de la API (un documento OpenAPI) y después el código que lo implementa. *Analogía:* el plano antes de la obra. |
| **Code-first (bottom-up)** | Primero se escribe el código y el contrato se genera a partir de él. Es lo que FastAPI hace por defecto con `/openapi.json`. |
| **Breaking change** | Un cambio que hace fallar a un cliente que funcionaba sin tocar nada: quitar o renombrar un campo, cambiar su tipo, volver obligatorio algo que no lo era. |
| **Parallel change (expand / migrate / contract)** | Patrón para hacer un cambio incompatible sin cortar a nadie: se agrega lo nuevo al lado de lo viejo, los clientes migran y recién después se quita lo viejo. |
| **Tolerant reader** | Cliente que lee solo los campos que necesita e ignora el resto. Es lo que hace que agregar un campo no rompa a nadie. |
| **`Deprecation` / `Sunset`** | Headers HTTP de respuesta. `Deprecation` avisa desde cuándo algo está deprecado y `Sunset`, cuándo va a dejar de responder. |
| **Polling / long polling** | El cliente pregunta cada N segundos (polling), o pregunta y el servidor retiene la respuesta hasta que haya novedades o venza un timeout (long polling). |
| **WebSocket** | Canal bidireccional y persistente entre cliente y servidor. Arranca como un request HTTP con `Upgrade` y después deja de ser HTTP. |
| **SSE (Server-Sent Events)** | Respuesta HTTP que no termina y por la que el servidor va empujando eventos de texto. Es unidireccional: solo servidor → cliente. |
| **Backpressure** | Mecanismo para que un consumidor lento frene al productor, en vez de acumular mensajes hasta llenar la memoria. |
| **Dual write** | Escribir el mismo hecho en dos sistemas (Postgres y Redis) sin una transacción común. Si una escritura falla, quedan inconsistentes. |
| **Transactional outbox + relay** | Se guarda el evento en una tabla de la base **en la misma transacción** que el cambio (el outbox), y un proceso aparte (el relay) lo copia a la cola. En TaskFlow, `task_events` ya es ese outbox. |
| **Stream / consumer group** | Un stream de Redis es un log *append-only* de mensajes con id. Un consumer group es un grupo de consumidores que se reparten los mensajes y lleva la cuenta de qué se entregó a quién. |
| **PEL (Pending Entries List)** | La lista de mensajes que el grupo entregó y todavía nadie confirmó con `XACK`. |
| **At-most-once / at-least-once** | Semánticas de entrega. *At-most-once:* un mensaje llega una vez o se pierde. *At-least-once:* nunca se pierde, pero puede llegar más de una vez. |
| **Exactly-once efectivo** | Lo que se logra combinando at-least-once con un consumidor **idempotente**: el mensaje puede llegar dos veces, pero su efecto ocurre una sola. Es una propiedad de tu diseño, no algo que el broker te regala. |
| **Competing consumers** | Varios consumidores sobre una misma cola punto a punto que se reparten los mensajes para procesar más rápido. |
| **Poison message** | Un mensaje que falla siempre que se procesa y, si nadie lo saca, se reentrega para siempre. |
| **gRPC / Protocol Buffers** | gRPC es un framework de RPC entre servicios. El contrato se escribe en un archivo `.proto` (Protocol Buffers) y el cliente y el servidor se generan de ese archivo. |
| **Stub** | El objeto cliente generado desde el `.proto`. Llamar `stub.Send(...)` se ve como una función local, pero es una llamada por red. |
| **Deadline** | En gRPC, cuánto está dispuesto a esperar el cliente una respuesta. Si vence, la llamada falla en vez de colgarse. |
| **Byte-stream** | Lo que entrega TCP: bytes en orden, **sin límites entre mensajes**. Dos `send` pueden llegar en un solo `recv`. |
| **Framing** | Cómo marca la aplicación dónde termina cada mensaje sobre un byte-stream: un delimitador (`\n`) o un prefijo con el largo. |
| **Datagrama** | La unidad de UDP: un paquete independiente que conserva sus límites, pero que puede perderse, duplicarse o llegar desordenado. |
| **QUIC** | Transporte construido **sobre UDP** que agrega streams, control de flujo, cifrado y conexión rápida. HTTP/3 corre sobre QUIC. |

**Ya vistos, solo como refresco:** *OpenAPI, `/docs`, `/openapi.json`* (M07·S03), *`APIRouter`, `Depends`, `async def` vs `def`* (M07·S04), *`lifespan`, `TestClient`, UI estática* (M07·S05), *Redis en el compose* (M07·S06), *expand/contract en la base, Alembic* (M07·S07), *`task_events`, `LISTEN/NOTIFY` como "timbre, no cola", `operation_id`, `X-User-Id` provisorio, upsert idempotente* (M07·S08), *HTTP stateless, TCP/TLS en el recorrido de la petición* (M07·S02), *trade-off journal `TJ-NNN`* (M07·S01).

---

## 4. Notas de estudio por subtema

### Diagrama ancla: lo que TaskFlow suma hoy

Cada caja es algo que construís en el lab. La UI sigue hablando HTTP con la API, y además abre un WebSocket. El mismo `task_events` de S08 alimenta dos caminos con garantías distintas: el tablero (timbre, puede perderse) y la cola de emails (no puede perderse).

```mermaid
flowchart LR
    UI["UI estática S05<br/>fetch + WebSocket"] -->|"HTTP /v1 y /v2"| API["FastAPI TaskFlow"]
    UI <-->|"WS /v2/projects/id/board/ws"| API
    API -->|"UPDATE tasks"| PG[("PostgreSQL<br/>tasks + task_events")]
    PG -->|"trigger + pg_notify task_events"| LST["listener en lifespan<br/>AsyncConnection LISTEN"]
    LST --> HUB["BoardHub por proyecto"]
    HUB --> API
    PG -->|"SELECT id > last"| RLY["relay_events.py"]
    RLY -->|"XADD taskflow:events"| RS[("Redis Stream")]
    RS -->|"XREADGROUP notifier"| WRK["notify_worker.py"]
    WRK -.->|"stretch: gRPC Send"| GRPC["notifications_server.py"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class RS foco
```

El nodo resaltado es la cola. Es la única pieza nueva **con estado durable**, y la que obliga a pensar en acks, reintentos y duplicados.

---

### 4.1 Diseño de APIs: top-down (design-first) vs bottom-up (code-first)

Hay dos formas de llegar a un contrato OpenAPI:

- **Code-first (bottom-up):** escribís rutas y modelos Pydantic, y el contrato **sale** del código. Es lo que venís haciendo desde S03: FastAPI sirve el schema en `/openapi.json`, con `"openapi": "3.1.0"`, y de ahí salen Swagger UI y ReDoc. Es rápido y el contrato nunca queda desactualizado respecto del código. El problema: el contrato termina siendo **lo que salió**, no lo que se decidió. Un cambio en un modelo Pydantic cambia la API sin que nadie lo haya discutido.
- **Design-first (top-down):** el contrato se escribe **antes**, se revisa en un PR como cualquier otro archivo, y el código lo implementa después. La OpenAPI Initiative recomienda este enfoque, con un argumento concreto: *"The number of APIs that can be created in code is far superior to what can be described in OpenAPI"*. Diseñar primero garantiza que tu API sea describible, y que el frontend pueda arrancar contra un mock mientras el backend se escribe.

La OpenAPI Initiative pide además **una sola fuente de verdad** y tratar la descripción OpenAPI como archivo de código fuente: commiteado y dentro del pipeline. Acá está la tensión práctica con FastAPI, que es code-first por naturaleza. Si escribís `contracts/openapi-v2.yaml` a mano, ahora tenés **dos** fuentes: el YAML y el `openapi.json` generado. El flujo que resuelve eso tiene cuatro pasos:

```
openapi-v2.yaml  →  lint  →  mock  →  implementación en FastAPI  →  comparar con /openapi.json
```

El contrato de `/v2/tasks/{task_id}` (extracto):

```yaml
# contracts/openapi-v2.yaml
openapi: 3.1.0
info:
  title: TaskFlow API
  version: 2.0.0
paths:
  /v2/tasks/{task_id}:
    get:
      operationId: get_task_v2
      parameters:
        - name: task_id
          in: path
          required: true
          schema: { type: integer }
      responses:
        "200":
          description: La tarea
          content:
            application/json:
              schema: { $ref: "#/components/schemas/TaskV2" }
components:
  schemas:
    TaskV2:
      type: object
      required: [id, title, status, assignee_id]
      properties:
        id: { type: integer }
        title: { type: string }
        status: { type: string, enum: [backlog, in_progress, done] }
        assignee_id:
          type: [integer, "null"]
          description: ID del usuario responsable. Reemplaza al `assignee` (string) de v1.
```

Dos detalles de versión que te van a morder:

- El contrato se escribe en **3.1.0**, no en la última versión del estándar. A la fecha de consulta (23 de septiembre de 2026) la OpenAPI Specification va por la **3.2.1**, del 10 de septiembre de 2026, pero FastAPI genera `3.1.0`. Si escribís el YAML en 3.2.x, la primera línea ya difiere del generado.
- `type: [integer, "null"]` es la forma 3.1 de decir "puede ser null". La 3.0 usaba `nullable: true`. Si copiás un ejemplo viejo de internet, es probable que traiga la forma 3.0.

**Para qué sirve un contrato estable:** FastAPI documenta cómo generar un cliente tipado (SDK) desde el OpenAPI, por ejemplo con `npx @hey-api/openapi-ts -i http://localhost:8000/openapi.json -o src/client`. Si el contrato cambia de forma incompatible, **el cliente deja de compilar en desarrollo**, antes de llegar a producción. Ese es el argumento práctico para versionar.

**Los eventos también son contrato.** Los mensajes que viajan por el WebSocket y por la cola tienen un formato del que dependen el tablero y el worker. Si mañana cambia el payload de `task_events`, se rompen igual que un cliente HTTP. Para describir esos contratos existe AsyncAPI, que la AsyncAPI Initiative define como *"a communication contract between senders and receivers within an event-driven system"*. Hoy solo lo nombramos: en el lab el contrato de eventos es un modelo Pydantic, `BoardEvent`, versionado junto con `/v2`.

**Errores comunes**
- Escribir el YAML a mano y nunca compararlo con el generado. A los dos sprints divergen y el contrato "oficial" miente.
- Esperar igualdad textual entre el YAML y el generado. Pydantic puede expresar lo mismo con otra forma (por ejemplo, un nullable como `anyOf`). Lo que se compara es **la semántica**: campos, tipos, obligatorios, `operationId`.
- Olvidarse del `operationId`. Si no lo fijás en FastAPI (`operation_id="get_task_v2"`, visto en S08), el generado trae uno largo y opaco que no coincide con el contrato.

> 💡 Para profundizar: *Best Practices* de la OpenAPI Initiative (10 min) y la doc de Redocly y Prism para el lint y el mock (links en §10).

---

### 4.2 Versionado explícito `/v1` → `/v2`

#### Qué rompe y qué no

La vara para clasificar cambios es **AIP-180** de Google. Dentro de una versión mayor, son **compatibles** los cambios aditivos: agregar métodos, mensajes, campos o valores de enum, siempre que el código que no los conoce siga funcionando igual. Son **incompatibles**:

- **Quitar** un componente. Y **renombrar equivale a quitar + agregar**.
- **Cambiar el tipo** de un campo.
- Cambiar comportamiento visible o formatos, incluidos los valores por defecto.
- Agregar campos **obligatorios** a requests existentes (*"New required fields must not be added to existing request messages or resources"*).

Aplicado a TaskFlow:

| Cambio | ¿Rompe? | Dónde va |
|---|---|---|
| Agregar `due_date` opcional a la respuesta de la tarea | No (con clientes tolerantes) | Se queda en `/v1` |
| Hacer obligatorio `project_id` en el body del `POST` | **Sí** | Versión nueva |
| `assignee: str` → `assignee_id: int` | **Sí, dos veces** (nombre y tipo) | `/v2` |

Y **por qué vale la pena** el cambio de `assignee`: un nombre no identifica a una persona. Con dos usuarias "Ana" en el proyecto, `PATCH /v1/...` con `{"assignee": "Ana"}` no tiene respuesta correcta.

```python
# app/schemas_v1.py — el contrato viejo NO se toca (extracto)
class TaskOutV1(BaseModel):
    id: int
    title: str
    status: TaskStatus
    assignee: str | None = Field(default=None, description="Nombre del responsable. DEPRECADO: usá /v2 y assignee_id.")

# app/schemas_v2.py — el contrato nuevo
class TaskOutV2(BaseModel):
    id: int
    title: str
    status: TaskStatus
    assignee_id: int | None = Field(description="ID del usuario responsable.")
```

#### "Agregar no rompe"… si el cliente es tolerante

El patrón **Tolerant Reader** (Martin Fowler, 2011) dice: *"only take the elements you need, ignore anything you don't"*, y se apoya en la ley de Postel. "Agregar un campo no rompe" **solo es cierto si los clientes son tolerantes**. Un cliente que valida la respuesta con un schema estricto (`additionalProperties: false`) se rompe con un cambio aditivo. Del lado del servidor ya estás cubierto: Pydantic ignora por defecto los campos extra del body.

```python
# Cliente frágil: se rompe con cualquier campo nuevo
assert set(task.keys()) == {"id", "title", "status", "assignee"}
# Cliente tolerante: lee lo que necesita
title, status = task["title"], task["status"]
```

#### Dónde va la versión

**AIP-185**: todas las APIs de Google llevan la **versión mayor en el path** (`v1`) y **no exponen versiones menores ni de parche**, que llegan "en el lugar". Por eso es `/v1` y no `/v1.3`. Agrega una regla que ordena el diseño interno: *"A new major version of an API must not depend on a previous major version of the same API"*. Leída al revés: `/v2` no importa nada de `/v1`. Es `/v1` la que se apoya en el dominio nuevo, **como adaptador que traduce**, hasta que muera.

Hay alternativas serias al path:

| Estrategia | Visible en logs y `curl` | Granularidad | Ejemplo |
|---|---|---|---|
| Versión mayor en el path (`/v2/tasks`) | Sí, a simple vista | Toda la API de golpe | AIP-185, lo que hacemos hoy |
| Versión en un header | No, hay que mirar headers | Por request | Header propio o `Accept` |
| Versión por fecha, fijada por cuenta | No | Por cuenta y por request | Stripe |

Stripe versiona **por fecha** (`2017-05-24`). La cuenta queda fijada a la versión vigente en su primer request, y cada request puede sobrescribirla con el header `Stripe-Version`. Por dentro, cada cambio incompatible vive en un *version change module* que transforma la respuesta **hacia atrás**, versión por versión. Según Stripe (2017), mantenían compatibilidad con todas las versiones de su API desde 2011. El lab aplica la misma idea en chico: `/v1` traduce desde el modelo nuevo.

#### Parallel change: el mismo patrón de S07, ahora en el contrato

*Parallel change* (Danilo Sato, en el bliki de martinfowler.com, 2014) es *"a pattern to implement backward-incompatible changes to an interface in a safe manner"*, en tres fases. Aplica a APIs, firmas de métodos y esquemas de base:

1. **Expand:** la interfaz soporta la versión vieja y la nueva a la vez. En S07 fue agregar `assignee_id` a la tabla y hoy es publicar `/v2`.
2. **Migrate:** los clientes pasan a la nueva de a poco. Hoy migra la UI; los scripts de terceros pueden tardar meses.
3. **Contract:** se quita la vieja. Pasado el `Sunset`, se apaga `/v1` y se hace `DROP COLUMN assignee`.

Sato lo presenta además como **alternativa** a poner una versión explícita: podrías evolucionar `/v1` en el lugar, agregando `assignee_id` sin quitar `assignee`. Es válido mientras nadie necesite que desaparezca el campo viejo.

#### Deprecación legible por máquina

"Vamos a apagar `/v1`" en un mail no lo lee ningún cliente. En cada respuesta de `/v1`, sí:

```python
from fastapi import Response

def mark_v1_deprecated(response: Response) -> None:
    response.headers["Deprecation"] = "@1790812800"                  # 2026-10-01T00:00:00Z
    response.headers["Sunset"] = "Fri, 01 Jan 2027 00:00:00 GMT"
    response.headers["Link"] = '</v2/docs>; rel="deprecation"'
```

- `Deprecation` (RFC 9745, 2025) usa una fecha en formato `@<epoch>` y define `rel="deprecation"` para enlazar la guía de migración.
- `Sunset` (RFC 8594, 2019, Informational) usa **HTTP-date**. No son intercambiables.
- La RFC 9745 exige que el `Sunset` **no sea anterior** al `Deprecation`.

#### Dos formas de tener `/v1` y `/v2` en FastAPI

**Opción A, un app con dos routers** (la del lab). La doc de FastAPI dice explícitamente que se puede incluir el mismo router varias veces con prefijos distintos (*"e.g. `/api/v1` and `/api/latest`"*):

```python
app.include_router(tasks_v1.router, prefix="/v1", tags=["v1 (deprecada)"],
                   dependencies=[Depends(mark_v1_deprecated)], deprecated=True)
app.include_router(tasks_v2.router, prefix="/v2", tags=["v2"])
```

`dependencies=[...]` a nivel router aplica los headers a **todas** las rutas de v1 de una vez, y `deprecated=True` las muestra tachadas en Swagger UI.

**Opción B, dos sub-apps montadas.** `app.mount("/v1", v1)` monta una aplicación independiente con **su propio OpenAPI y su propia UI** en `/v1/docs`. Sirve para comparar cada versión contra su contrato, pero tiene una trampa que la doc dice textualmente: los eventos de lifespan *"will only be executed for the main application, not for Sub Applications - Mounts."* Si el listener del tablero (§4.4) se declara en el lifespan de la sub-app `v2`, **nunca arranca**.

**Errores comunes**
- Versionar **todo** porque cambió un recurso. Las rutas de S08 (`/v1/projects/{id}/search`, etc.) no exponen `assignee`, así que no cambian. Se versiona lo que cambia de forma incompatible.
- Copiar el service a `/v2` y tener dos dominios. En un mes divergen. Tiene que haber **un** dominio y un adaptador.
- Escribir el `Sunset` con `@epoch` o el `Deprecation` con HTTP-date.

> 💡 Para profundizar: AIP-180 (15 min) es la lectura imprescindible del subtema, y *Parallel Change* (8 min) es el puente con S07.

---

### 4.3 HTTP síncrono y sus límites

HTTP es **request/response**: el cliente abre, pide, el servidor contesta y ahí termina el intercambio. Además es **stateless**: cada request trae todo lo necesario (lo viste en S02). Ese modelo tiene tres virtudes que no hay que subestimar. Es simple de razonar, se cachea, se balancea y se reintenta con herramientas estándar, y cualquier cosa lo habla, desde `curl` hasta un navegador. Para el CRUD de TaskFlow es la respuesta correcta.

Se rompe en dos lugares.

**1. El servidor no puede hablar primero.** Si Ana mueve la #42, el servidor no tiene forma de avisarle a Beto: Beto no preguntó nada. Antes de WebSocket había dos parches:

```js
// Polling: preguntar cada 5 s
setInterval(async () => {
  const r = await fetch("/v2/tasks");
  renderBoard(await r.json());
}, 5000);
```

- **Polling:** la latencia de un cambio es, en el peor caso, el intervalo. Y la mayoría de los requests vuelven **vacíos**: con 50 personas mirando el tablero, son 50 requests cada 5 s para enterarse de que no pasó nada.
- **Long polling:** el cliente pregunta y el servidor **retiene** la respuesta hasta que haya novedades o venza un timeout. Después el cliente vuelve a preguntar. La latencia baja, pero cada cliente ocupa un request abierto todo el tiempo, y los proxies con timeout corto lo cortan.

**2. El trabajo lento bloquea el request.**

```python
@router.patch("/tasks/{task_id}/assignee")
def assign(task_id: int, body: TaskAssignV2, svc: TaskServiceDep):
    task = svc.assign(task_id, body.assignee_id)     # ya commiteado
    send_email_smtp(body.assignee_id, task_id)       # tarda lo que tarde el servidor de correo… o falla
    return task
```

El usuario espera el email para ver su asignación. Y si el correo falla, el `PATCH` devuelve error **aunque la asignación ya se guardó**. El cliente reintenta y ahora hay dos asignaciones y quizá dos emails. Proxies y clientes tienen además sus propios timeouts, que cortan el request aunque el servidor siga trabajando.

Las dos secciones que siguen resuelven cada problema: canal persistente para (1) y cola para (2).

**Errores comunes**
- Resolver "tiempo real" con polling de 1 s "porque es más simple". Es simple hasta que multiplicás por la cantidad de tableros abiertos.
- Poner `async def` y creer que eso hace el trabajo lento "en segundo plano". `async` libera el event loop mientras esperás I/O, pero **el request sigue esperando**. El cliente no recibe nada hasta que termine.

---

### 4.4 WebSockets: el tablero en vivo

#### Cómo arranca un WebSocket

La RFC 6455 describe un protocolo **bidireccional** en dos partes: un **handshake de apertura** y después **framing de mensajes**, *"layered over TCP"*. El handshake reutiliza el `Upgrade` de HTTP:

```http
GET /v2/projects/1/board/ws?user_id=1 HTTP/1.1
Host: localhost:8000
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Después del `101`, la misma conexión TCP deja de hablar HTTP y pasa a transportar frames en los dos sentidos. Por eso el WebSocket vive **en el mismo puerto y el mismo router** que tu API (`ws://` sobre 80, `wss://` sobre 443).

#### El endpoint en FastAPI

La doc de FastAPI muestra `@app.websocket`, `accept()`, `receive_text()` / `send_text()` y un `ConnectionManager` con `broadcast()`. Las dependencias (`Query`, `Path`, `Header`…) funcionan igual que en HTTP, pero para cortar se levanta **`WebSocketException`** en lugar de `HTTPException`. El endpoint del tablero:

```python
@router.websocket("/projects/{project_id}/board/ws")
async def board_ws(websocket: WebSocket, project_id: int, user_id: int = Query()):
    if not await run_in_threadpool(user_has_role, project_id, user_id):
        raise WebSocketException(code=1008)          # 1008 = policy violation, ANTES de accept()
    await websocket.accept()
    hub.join(project_id, websocket)
    try:
        async for _ in websocket.iter_text():        # el cliente no manda nada útil
            pass
    finally:
        hub.leave(project_id, websocket)
```

Tres decisiones que el agente no toma solo:

1. **Permiso antes de `accept()`.** Si levantás la excepción antes de aceptar, el handshake se rechaza y el socket nunca se abre. `1008` es, para el cliente, el equivalente del 403/404 de S08.
2. **`user_id` por query y no por header**, porque el constructor `WebSocket` del navegador no deja poner headers propios. Es tan provisorio e inseguro como el `X-User-Id` de S08 y se reemplaza en S14.
3. **Nada de `Depends(get_session)`**: la sesión de SQLAlchemy quedaría abierta toda la vida del socket (horas), ocupando una conexión del pool. `user_has_role` abre y cierra la suya.

#### El punto de diseño de la sesión: más de un proceso

La doc de FastAPI advierte que su `ConnectionManager` de ejemplo, *"as everything is handled in memory, in a single list, […] will only work while the process is running, and will only work with a single process."* Con `uvicorn --workers 2` (vas a escalar así en S12), la lista de un worker no conoce los sockets del otro. Ana está en el worker 1, Beto en el 2, y Beto nunca se entera.

La solución de TaskFlow usa lo que ya tenés: **`LISTEN/NOTIFY` entrega cada notificación a todas las sesiones que escuchan**. Cada worker abre su propio `LISTEN task_events`, recibe **todos** los eventos y los reparte a **sus** sockets.

```python
async def listen_task_events(dsn: str) -> None:
    while True:
        try:
            async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as conn:
                await conn.execute("LISTEN task_events")
                async for n in conn.notifies():
                    event = BoardEvent.model_validate_json(n.payload)
                    await hub.publish(event.project_id, event.model_dump(mode="json"))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("listener caído; reintento en 2 s")
            await asyncio.sleep(2)
```

Por qué cada línea está como está:

- **`autocommit=True`**: psycopg lo pide para recibir notificaciones a tiempo, y la doc de Postgres advierte que una sesión que hace `LISTEN` y queda dentro de una transacción larga impide limpiar la cola de notificaciones (8 GB en una instalación estándar; `pg_notification_queue_usage()` la mide).
- **`AsyncConnection`**: en S08 el worker de embeddings usó la versión sincrónica. Acá el listener vive **dentro** del proceso de FastAPI, en el event loop.
- **Payload chico.** `NOTIFY` exige un payload menor a 8000 bytes por defecto. El evento lleva ids y estados, **nunca** el cuerpo de un comentario.
- **Se entrega al commit.** Si el `PATCH` hace rollback, el tablero nunca ve el cambio. Detalle nuevo respecto de S08: notificaciones idénticas (mismo canal y payload) dentro de una transacción se pliegan en una sola.

Y existe una librería que hace esto, `encode/broadcaster`, con backends Redis, Kafka y Postgres `LISTEN/NOTIFY`. La doc de FastAPI todavía la recomienda, pero **el repo está archivado desde el 19 de agosto de 2025**. Es un buen recordatorio de que hay que mirar el estado de una dependencia antes de adoptarla (un agente no lo hace solo). El patrón son ~30 líneas y las escribimos a mano.

#### Re-sincronizar siempre

`NOTIFY` no es durable y un WebSocket se corta: wifi, laptop que se duerme, deploy. Todo evento emitido mientras el cliente estaba desconectado **se perdió**. Por eso el tablero **se reconstruye por HTTP en cada `open`**, y los eventos solo lo mantienen al día:

```js
ws.addEventListener("open", () => refreshBoardViaHttp(projectId));  // SIEMPRE al (re)conectar
ws.addEventListener("message", (e) => applyEvent(JSON.parse(e.data)));
ws.addEventListener("close", () => setTimeout(() => connectBoard(projectId, userId), 1000));
```

Es la regla "timbre, no cola" de S08, vista desde el cliente.

#### Backpressure

MDN lo dice sin vueltas: *"The WebSocket API has no way to apply backpressure"*. Si los mensajes llegan más rápido de lo que la página los procesa, se llena la memoria o la CPU se va al 100 %. Menciona `WebSocketStream` como alternativa que sí aplica backpressure. De ahí la decisión del lab: **eventos chicos** (qué tarea, qué cambió), nunca el tablero entero en cada cambio.

Del lado del servidor hay un problema simétrico. `hub.publish` hace `await ws.send_json(...)` socket por socket, así que un cliente lento frena la entrega a todos los demás. Hay dos mitigaciones canónicas: un **timeout por envío** (si no se pudo mandar en 1 s, se cierra ese socket) o **una cola acotada por socket** con una tarea que la vacía. Hoy la nombramos; implementarla es parte del desafío 🔴.

> ⚠️ **Seguridad, para S15:** el handshake de WebSocket no pasa por las mismas reglas que un `fetch`. CORS no lo protege de la misma forma, y cualquier página puede intentar abrir un socket contra tu servidor. En producción hay que validar el header `Origin` antes de aceptar.

#### SSE, la alternativa honesta

Mirá qué hace el tablero: **solo recibe**. Los movimientos de tareas viajan por `PATCH` HTTP. Para eso alcanza **SSE**, una respuesta HTTP de tipo `text/event-stream` que nunca termina. Es HTTP común (pasa por proxies y middlewares como cualquier request), y el `EventSource` del navegador **reconecta solo** y puede reanudar desde el último `id`. FastAPI lo soporta nativamente desde la **0.135.0**:

```python
from fastapi.sse import EventSourceResponse

@router.get("/projects/{project_id}/board/events", response_class=EventSourceResponse)
async def board_events(project_id: int, user_id: int = Query()):
    queue = hub.subscribe(project_id)          # un asyncio.Queue por cliente (lo implementás en el ejercicio 🟡1)
    try:
        while True:
            yield BoardEvent.model_validate(await queue.get())   # cada yield sale como `data:` en JSON
    finally:
        hub.unsubscribe(project_id, queue)
```

¿Cuándo se justifica WebSocket? Cuando el cliente **también** empuja por el mismo canal: presencia ("Beto está viendo esta tarea"), cursores, "está escribiendo…". SSE es además el transporte habitual con el que las APIs de modelos de lenguaje streamean su respuesta token a token.

**Errores comunes**
- Registrar el listener en el lifespan de una sub-app montada (opción B de §4.2). No corre nunca.
- Pasarle a psycopg la URL de SQLAlchemy (`postgresql+psycopg://…`). psycopg no entiende el dialecto: sacale el `+psycopg`.
- Confiar en el WebSocket como fuente de verdad. Es un aviso; la verdad está en `GET`.

> 💡 Para profundizar: la doc de WebSockets de FastAPI (20 min) y la de Starlette para `send_json` / `iter_text` / `close(code=…)`.

---

### 4.5 Colas y mensajería: notificaciones por email

#### Escalón 1: `BackgroundTasks`

FastAPI trae `BackgroundTasks`, que corre una función **después** de devolver la respuesta. El ejemplo de la doc es justamente un email:

```python
from fastapi import BackgroundTasks

@router.patch("/tasks/{task_id}/assignee", response_model=TaskOutV2)
def assign(task_id: int, body: TaskAssignV2, background_tasks: BackgroundTasks, svc: TaskServiceDep):
    task = svc.assign(task_id, body.assignee_id)
    if body.assignee_id is not None:
        background_tasks.add_task(send_email_fake, body.assignee_id, task_id)
    return task
```

Resuelve el problema 2 de §4.3 (el usuario ya no espera), pero la función corre **en el mismo proceso**, sin persistencia y sin reintentos. Si Uvicorn se reinicia entre la respuesta y el envío (un deploy, un OOM), **el email se pierde sin rastro**. La propia doc lo acota: para trabajo pesado o en varios procesos convienen herramientas como Celery, que *"require more complex configurations, a message/job queue manager, like RabbitMQ or Redis, but they allow you to run background tasks in multiple processes, and especially, in multiple servers."*

#### Escalón 2: una cola durable, sin dual write

La tentación es hacer `XADD` en Redis desde el handler, justo después del `commit`. Eso es un **dual write**: dos escrituras en dos sistemas sin transacción común. Si el proceso muere entre una y otra, la tarea quedó asignada y el mensaje nunca existió.

TaskFlow ya tiene la solución hecha: `task_events` se escribe **en la misma transacción** que el cambio (el trigger de S08). Es un **outbox**. Un proceso aparte, el **relay**, lo lee y lo copia a la cola. Si el relay se cae, al volver sigue desde su cursor.

```mermaid
sequenceDiagram
    participant API as FastAPI
    participant PG as PostgreSQL
    participant RLY as relay
    participant RS as Redis Stream
    participant WRK as worker
    API->>PG: UPDATE tasks + trigger INSERT task_events (una transacción)
    RLY->>PG: SELECT eventos con id mayor al cursor
    RLY->>RS: XADD taskflow:events
    RLY->>RS: SET cursor
    WRK->>RS: XREADGROUP notifier (el mensaje entra en la PEL)
    WRK->>WRK: enviar email si no se envió antes
    WRK->>PG: INSERT notifications_sent
    WRK->>RS: XACK (sale de la PEL)
```

Cada flecha es un punto donde algo puede morir. El diseño decide qué pasa en cada caso:

- **El relay muere entre `XADD` y `SET cursor`:** el evento se publica **dos veces**. Es at-least-once desde el productor.
- **El worker muere antes del `XACK`:** el mensaje queda en la **PEL** y otro consumidor lo rescata con `XAUTOCLAIM`. Es at-least-once desde el consumidor.

Conclusión: el worker **tiene** que ser idempotente. Una tabla `notifications_sent` con `event_id` como clave primaria alcanza.

#### Redis Streams, pieza por pieza

```bash
XADD taskflow:events MAXLEN ~ 100000 * kind assigned task_id 42 new 7   # agrega y recorta aprox.
XGROUP CREATE taskflow:events notifier 0 MKSTREAM                        # grupo que lee desde el principio
XREADGROUP GROUP notifier w1 COUNT 10 BLOCK 5000 STREAMS taskflow:events >   # ">" = nunca entregados
XACK taskflow:events notifier 1727100000000-0                            # confirmado: sale de la PEL
XPENDING taskflow:events notifier                                        # qué está entregado y sin ack
XAUTOCLAIM taskflow:events notifier w2 60000 0-0 COUNT 10                # rescata lo que lleva 60 s colgado
XINFO GROUPS taskflow:events                                             # observar grupos y pendientes
```

La doc de Redis describe la semántica como **at-least-once**, así que el procesamiento tiene que ser idempotente. Dentro de un grupo, los mensajes nuevos se reparten entre los consumidores activos.

El núcleo del worker es el orden de tres líneas:

```python
def handle(fields: dict) -> None:
    event_id, user_id = int(fields["event_id"]), int(fields["new"])
    if already_sent(event_id):
        return                                   # duplicado: no hago nada
    send_email_fake(user_id, task_id=int(fields["task_id"]))
    record_sent(event_id, user_id)               # INSERT … ON CONFLICT DO NOTHING

def process(msg_id: str, fields: dict) -> None:
    handle(fields)
    r.xack(STREAM, GROUP, msg_id)                # ack DESPUÉS de procesar, nunca antes
```

**Enviar → registrar → ack.** Si el worker muere entre enviar y registrar, el email sale **dos veces**. Para un aviso es aceptable. El orden inverso (registrar → enviar) puede **perder** el email: queda registrado como enviado sin haberse enviado. Es el trade-off central del subtema y va a TJ-008. Y el ack antes de procesar es el peor de todos: convierte tu cola durable en at-most-once.

#### Timbre vs cola: las garantías de cada pieza

Redis tiene también **Pub/Sub** (`PUBLISH` / `SUBSCRIBE`), con semántica **at-most-once**: si el suscriptor no puede manejar el mensaje, *"the message is forever lost."* La sesión tiene tres piezas de cada tipo, y la diferencia explica todo el diseño:

| Semántica | Piezas de TaskFlow | Por eso… |
|---|---|---|
| At-most-once (timbre) | Postgres `NOTIFY`, Redis Pub/Sub, `ConnectionManager` en memoria | …el tablero re-sincroniza por HTTP |
| At-least-once (cola) | Redis Streams con consumer group, RabbitMQ con ack manual | …el worker es idempotente |

#### Competing consumers y fan-out

El patrón *Competing Consumers* (Hohpe y Woolf, *Enterprise Integration Patterns*) resuelve el caso en que un consumidor *"cannot process messages as fast as they're being added to the channel"*: varios consumidores sobre un canal **punto a punto** se reparten los mensajes. Con publish-subscribe, en cambio, cada suscriptor recibiría una copia.

En Redis Streams tenés las dos cosas sobre el mismo stream:

- **Dos workers en el grupo `notifier`** se reparten los eventos (competing consumers).
- **Un segundo grupo, `board-metrics`,** recibe **todos** los eventos, independiente de `notifier`. Es un fan-out tipo pub/sub, pero persistente.

#### RabbitMQ, la alternativa de broker dedicado

El tutorial 2 de RabbitMQ (*Work Queues*) es la explicación más clara de acks y durabilidad. Lo esencial con pika:

```python
channel.queue_declare(queue="notifications", durable=True, arguments={"x-queue-type": "quorum"})
channel.basic_publish(exchange="", routing_key="notifications", body=payload,
                      properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
channel.basic_qos(prefetch_count=1)                       # fair dispatch: de a uno por worker
# en el callback, después de procesar:
ch.basic_ack(delivery_tag=method.delivery_tag)
```

Si un worker muere sin confirmar, el mensaje se reentrega a otro, y hay un **timeout de confirmación de 30 minutos**. El tutorial advierte que cola durable + mensaje persistente **no garantiza** cero pérdidas. RabbitMQ también reentrega, así que la idempotencia sigue siendo necesaria.

**Errores comunes**
- Olvidar `decode_responses=True` en redis-py y comparar `b"assigned"` con `"assigned"`: nunca matchea y el worker "no hace nada".
- Crear el grupo con `$` (el ejemplo típico de la doc) y no entender por qué no ve los eventos viejos. `$` significa "solo lo que llegue desde ahora"; `0`, "desde el principio".
- No pensar en el **poison message**: un evento que siempre falla vuelve a la PEL para siempre. El conteo de entregas de `XPENDING` permite mandarlo a un stream de "muertos" después de N intentos (ejercicio 🟡2).

> 💡 Para profundizar: la doc de Redis Streams (25 min) es la pieza central. Cada concepto de esa página tiene su línea en el worker del lab.

---

### 4.6 gRPC para un microservicio interno

Supongamos que el envío de emails crece y se separa en su propio servicio. El backend y ese servicio necesitan hablar entre sí con un contrato **tipado**, **binario** y con **timeouts explícitos**. Ese es el terreno de gRPC.

El contrato es un `.proto`:

```proto
// proto/notifications.proto
syntax = "proto3";
package taskflow.notifications.v1;      // versión mayor en el paquete, como en AIP-185

service Notifications {
  rpc Send (SendRequest) returns (SendReply);           // unario
  rpc Watch (WatchRequest) returns (stream Delivery);   // server streaming
}

message SendRequest {
  int64 event_id = 1;                   // clave de idempotencia: el id de task_events
  int64 user_id = 2;
  string template = 3;                  // "task_assigned"
  map<string, string> params = 4;
}
message SendReply { bool duplicate = 1; string delivery_id = 2; }
message WatchRequest { int64 user_id = 1; }
message Delivery { int64 event_id = 1; string template = 2; }
```

De ese archivo, `grpc_tools.protoc` genera las clases de mensajes (`_pb2.py`) y las de cliente y servidor (`_pb2_grpc.py`). Del lado cliente, la llamada parece local:

```python
with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.NotificationsStub(channel)
    reply = stub.Send(pb.SendRequest(event_id=311, user_id=7, template="task_assigned",
                                     params={"task_id": "42"}), timeout=2.0)   # deadline de 2 s
```

Conceptos que da la doc de gRPC:

- **Cuatro tipos de RPC:** unario, *server streaming*, *client streaming* y bidireccional. `Send` es unario y `Watch` es server streaming.
- **Deadline:** cuánto está dispuesto a esperar el cliente. `timeout=2.0` hace que, si el servicio no contesta en 2 s, recibas un error en vez de quedarte colgado. Cualquiera de los dos lados puede además **cancelar**.
- **Metadata** clave-valor (por ejemplo, para autenticación) y **channels** hacia un host y puerto.

**Números de campo: versionado otra vez, con otras reglas.** En JSON el contrato es el **nombre** del campo. En protobuf es el **número**: los números identifican el campo en el formato binario. La guía de proto3 lo dice así: *"Changing a field number is equivalent to deleting that field and creating a new field with the same type but a new number."* Consecuencias:

- Renombrar `assignee` a `assignee_name` en un `.proto` **no rompe el wire**, porque el número sigue siendo el mismo. En JSON rompería.
- **Reusar** el número de un campo borrado sí rompe: los clientes viejos decodifican basura. Al borrar un campo, se reservan su número y su nombre:

```proto
message SendRequest {
  reserved 5;                 // borramos `priority = 5`: nadie puede reusar el 5
  reserved "priority";
  int64 event_id = 1;
  // …
}
```

- Agregar campos o valores de enum es compatible, y los campos desconocidos se preservan al parsear.

"Breaking change" **depende del formato**. Es la idea que conecta AIP-180 con protobuf.

**Por qué gRPC no llega a la UI.** gRPC viaja sobre **HTTP/2**, con `Content-Type: application/grpc`. El navegador no habla gRPC directamente. El tutorial oficial de gRPC-Web usa el proxy Envoy para traducir las llamadas del navegador al servidor gRPC. Para TaskFlow la regla es simple: **gRPC entre servicios internos; hacia el navegador, HTTP/JSON y WebSocket**.

**Errores comunes**
- Llamar sin `timeout`. Un servicio lento te cuelga el worker indefinidamente.
- Usar `insecure_channel` entre máquinas. Alcanza para localhost; entre servidores va TLS (S15).
- Esperar ver `duplicate: false` al imprimir la respuesta. En proto3 los valores por defecto no se imprimen: un `false` no aparece.

---

### 4.7 TCP vs UDP

Todo lo que usa TaskFlow corre sobre uno de dos transportes:

- **TCP** (RFC 9293, 2022, que reemplaza a la RFC 793): *"TCP provides a reliable, in-order, byte-stream service to applications."* Es **orientado a conexión**: antes de mandar datos hay un *three-way handshake* (SYN, SYN-ACK, ACK). Numera los bytes para detectar pérdidas y retransmitir, usa checksum para detectar errores, y tiene **control de flujo** (no desbordar al receptor) y **control de congestión** (no desbordar la red).
- **UDP** (RFC 768, J. Postel, 1980): *"a procedure for application programs to send messages to other programs with a minimum of protocol mechanism"*, y *"delivery and duplicate protection are not guaranteed."* Sin conexión y sin retransmisión. Cada `sendto` es un datagrama independiente. Lo que necesites (orden, reintentos) lo construye tu aplicación.

La palabra clave de TCP es **byte-stream**: entrega bytes en orden, **no mensajes**. Si mandás cinco mensajes seguidos, el receptor puede recibirlos pegados en un solo `recv`, o partidos a la mitad. La doc de Python lo advierte: `send` y `recv` *"do not necessarily handle all the bytes you hand them"*, y un `recv` que devuelve 0 bytes significa que el otro lado cerró. Por eso cada protocolo sobre TCP define su **framing**: HTTP/1.1 usa headers y `Content-Length`, WebSocket y HTTP/2 tienen sus propios frames. Las opciones de framing son largo fijo, delimitador, prefijo de largo (que el HOWTO de Python llama *"much better"*) o cerrar la conexión.

```python
# Framing con prefijo de largo: 4 bytes big-endian + el mensaje
def send_msg(sock, msg: bytes) -> None:
    sock.sendall(len(msg).to_bytes(4, "big") + msg)

def recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("el otro lado cerró a mitad de mensaje")
        buf += chunk
    return buf

def recv_msg(sock) -> bytes:
    size = int.from_bytes(recv_exact(sock, 4), "big")
    return recv_exact(sock, size)
```

**Qué usa cada pieza de TaskFlow:**

| Pieza | Protocolo de aplicación | Transporte | Puerto típico |
|---|---|---|---|
| API y UI | HTTP/1.1 | TCP | 8000 en dev |
| Tablero | WebSocket | TCP | el mismo de la API |
| PostgreSQL | protocolo de Postgres | TCP | 5432 |
| Redis | RESP | TCP | 6379 |
| RabbitMQ (stretch) | AMQP | TCP | 5672 |
| gRPC (stretch) | gRPC sobre HTTP/2 | TCP | 50051 en el ejemplo oficial |
| Resolver el dominio | DNS | normalmente UDP | 53 |
| Detrás de un CDN con HTTP/3 | HTTP/3 sobre QUIC | **UDP** | 443 |

**QUIC rompe el binario "UDP = sin garantías".** La RFC 9000 define QUIC como un transporte **basado en UDP** que *"provides applications with flow-controlled streams for structured communication, low-latency connection establishment, and network path migration"*. Construye confiabilidad, streams y cifrado **encima** de UDP, en espacio de usuario. HTTP/3 (RFC 9114) corre sobre QUIC.

¿Por qué molestarse? Por el **head-of-line blocking**. HTTP/2 multiplexa muchos streams sobre **una** conexión TCP. Como TCP entrega bytes en orden estricto, si se pierde un paquete, **todos** los streams esperan su retransmisión, aunque el dato perdido fuera de uno solo. QUIC conoce los streams, así que una pérdida solo frena al stream afectado. La RFC 9114 advierte además que en algunas redes UDP está bloqueado y la conexión QUIC no se establece, por eso los clientes mantienen la vuelta a TCP.

Es el único lugar donde TaskFlow podría tocar UDP sin enterarse: detrás de un CDN con HTTP/3, el navegador habla QUIC con el borde, y el borde habla HTTP/1.1 o HTTP/2 con tu Uvicorn.

**Errores comunes**
- Usar `send` en vez de `sendall` y asumir que salió todo.
- Asumir que "un `recv` = un mensaje" porque en loopback siempre funcionó. Funciona hasta que no.
- Elegir UDP "porque es más rápido" para algo que no tolera pérdida. Vas a terminar reimplementando TCP, y peor.

---

### 4.8 Elegir protocolo y registrar la decisión

Las preguntas, en orden. El árbol es canónico; lo que cambia de un sistema a otro son las respuestas.

```mermaid
flowchart TD
    Q1{"¿El servidor necesita<br/>avisar primero?"} -->|"no"| Q3
    Q1 -->|"sí"| Q2{"¿El cliente también<br/>empuja por el canal?"}
    Q2 -->|"no"| SSE["SSE"]
    Q2 -->|"sí"| WS["WebSocket"]
    Q3{"¿Hay trabajo lento que<br/>no debe bloquear el request?"} -->|"no"| Q5
    Q3 -->|"sí"| Q4{"¿Se puede perder<br/>si el proceso muere?"}
    Q4 -->|"sí"| BG["BackgroundTasks"]
    Q4 -->|"no"| COLA["Cola durable<br/>+ worker idempotente"]
    Q5{"¿Es servicio a servicio,<br/>interno y tipado?"} -->|"sí"| GRPC["gRPC"]
    Q5 -->|"no"| HTTP["HTTP/JSON"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class COLA foco
```

Las preguntas no son excluyentes: TaskFlow recorre el árbol varias veces, una por necesidad. El CRUD cae en HTTP/JSON, el tablero en SSE o WebSocket, el email en cola durable y el servicio interno en gRPC.

Un agente al que le pedís "tablero en vivo" sin más contexto suele elegir polling o un connection manager en memoria. Y si le pedís "mandá un email al asignar", `BackgroundTasks`. Las tres respuestas son razonables en un prototipo y se rompen con dos workers o un reinicio. Por eso la decisión va al journal, con el formato `TJ-NNN` de S01:

```
TJ-008 · Tablero en vivo y notificaciones
Decisión: WebSocket (o SSE) para el tablero alimentado por LISTEN/NOTIFY; Redis Stream + worker para emails.
Alternativas descartadas: polling cada 5 s; BackgroundTasks; RabbitMQ; gRPC hacia la UI.
Por qué: …
Qué pierdo: …   (una conexión de Postgres por worker; at-least-once → idempotencia; email duplicado posible)
Qué me haría cambiar de opinión: …   (p. ej., muchos consumidores de eventos → CDC o un broker de eventos)
Versionado: /v1 deprecado el 2026-10-01, sunset 2027-01-01; assignee → assignee_id.
```

---

### Mapa de relaciones entre recursos

Cómo se apoyan entre sí los recursos de la sesión. La flecha se lee "se entiende mejor después de". El nodo resaltado es la lectura que ordena todo lo demás.

```mermaid
flowchart TD
    OAS["OpenAPI best practices<br/>design-first vs code-first"] --> PRISM["Redocly lint + Prism mock"]
    FFS["FastAPI First Steps<br/>openapi.json 3.1.0"] --> OAS
    AIP180["AIP-180<br/>qué rompe"] --> AIP185["AIP-185<br/>versión en el path"]
    AIP180 --> PC["Parallel Change<br/>expand-migrate-contract"]
    TR["Tolerant Reader"] --> AIP180
    AIP185 --> FBIG["FastAPI include_router<br/>opción A"]
    AIP185 --> FSUB["FastAPI mount<br/>opción B"]
    FSUB --> FLIFE["Lifespan: solo app principal"]
    DEP["RFC 9745 Deprecation"] --> SUN["RFC 8594 Sunset"]
    RFC6455["RFC 6455 WebSocket"] --> FWS["FastAPI WebSockets"]
    FWS --> STW["Starlette WebSocket API"]
    FWS --> TWS["Testing WebSockets"]
    NOTIFY["Postgres NOTIFY"] --> PSY["psycopg AsyncConnection"]
    PSY --> FWS
    FLIFE --> FWS
    MDN["MDN WebSocket (cliente)"] --> FWS
    BG["FastAPI BackgroundTasks<br/>caveat"] --> RS["Redis Streams"]
    PUBSUB["Redis Pub/Sub<br/>at-most-once"] --> RS
    RS --> RMQ["RabbitMQ work queues"]
    EIP["Competing Consumers"] --> RS
    GCORE["gRPC core concepts"] --> GQS["gRPC Python quickstart"]
    GQS --> GBAS["gRPC Python basics"]
    PROTO["proto3 guide<br/>field numbers"] --> GQS
    AIP180 --> PROTO
    TCP["RFC 9293 TCP"] --> HOWTO["Python Socket HOWTO"]
    UDP["RFC 768 UDP"] --> SOCK["socket module"]
    HOWTO --> SOCK
    UDP --> QUIC["RFC 9000 QUIC"]
    QUIC --> H3["RFC 9114 HTTP/3"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class AIP180 foco
```

Relaciones que el diagrama no muestra:

- **AIP-180 y la guía de proto3 dicen lo mismo con distinto identificador**: en JSON el contrato es el nombre del campo y en protobuf, el número.
- **Parallel Change une S07 con S09**: S07 hizo el *expand* en la base y hoy se hace en el contrato HTTP. El *contract* llega después del `Sunset`.
- **`task_events` es a la vez fuente del tablero y outbox de la cola**: un solo trigger, dos consumidores con garantías distintas.
- **`encode/broadcaster` contradice a la doc de FastAPI**: la doc lo recomienda y el repo está archivado.

---

## 5. Guía práctica paso a paso (lab)

**Punto de partida:** el repo `taskflow` al día con S08. Eso incluye el `compose.yaml` de S06 con Postgres 16 (servicio `db`, con pgvector desde S08) y Redis 8 (servicio `cache`), SQLAlchemy + Alembic sobre la base `taskflow_app`, la tabla `task_events` con sus triggers, el `lifespan` de S05, la suite de pytest y la UI estática.

**Prerrequisitos:**

- Python con el venv del proyecto activo.
- Docker con el `compose.yaml` de S06 (`docker compose up -d`).
- Las variables de S07 en cada terminal donde corras la API, el relay o el worker: `export TASKFLOW_STORAGE=postgres` y `export TASKFLOW_DATABASE_URL="postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_app"`.
- **Node.js con `npx`**, solo para el paso 1 (lint y mock del contrato).
- Tres o cuatro terminales abiertas: vas a tener API, relay, worker y un cliente al mismo tiempo.

**Cómo se reparte la sesión (180 min):** concepto, 40 min (versionado + mapa de protocolos + TCP/UDP) → taller guiado, 60 min (pasos 1–4) → práctica autónoma, 45 min (pasos 5 y 7) → puesta en común, 20 min ("¿SSE o WebSocket para el tablero? ¿qué pasa si el worker muere?") → cierre, 15 min (paso 8 y entrega). El paso 6 (gRPC) es **stretch**, para después de clase.

**Estructura de archivos que vas a tocar:**

```
taskflow/
├── contracts/openapi-v2.yaml               (nuevo)
├── app/
│   ├── main.py                             (modificado: /v1 + /v2 + listener)
│   ├── schemas.py                          (TaskOut suma assignee_id)
│   ├── schemas_v1.py, schemas_v2.py        (nuevo: contratos por versión)
│   ├── routers/tasks.py                    (el de S05, ahora servido bajo /v1)
│   ├── routers/tasks_v2.py, board_ws.py    (nuevo)
│   ├── services/task_service.py            (+ get, assign, user_name…)
│   ├── repositories/sqlalchemy_repo.py     (+ set_assignee, user_name…)
│   ├── repositories/cached.py              (delegar los métodos nuevos)
│   ├── realtime/__init__.py, board.py      (nuevo: hub + listener)
│   └── db/models.py                        (+ NotificationSent)
├── static/board.js                         (nuevo; lo carga static/index.html)
├── migrations/versions/…                   (2 migraciones nuevas)
├── scripts/relay_events.py, notify_worker.py (nuevo)
├── proto/notifications.proto               (stretch)
└── labs/tcp_udp/                           (nuevo)
```

> 💡 Los nombres siguen la estructura de S05–S07: `app/schemas.py` (`TaskStatus`, `TaskOut`), `app/dependencies.py` (`TaskServiceDep`, `SessionLocal`, `DATABASE_URL`, `STORAGE`), `app/services/task_service.py` (`TaskService`, `TaskNotFound`, `InvalidTransition`), `app/repositories/sqlalchemy_repo.py` (`SqlAlchemyTaskRepository`, que devuelve `TaskOut` y nunca el objeto ORM) y los modelos `Task`, `User`, `ProjectMember` y `TaskEvent` de S07–S08. Los contratos por versión van en `app/schemas_v1.py` y `app/schemas_v2.py`, igual que `app/schemas_agent.py` en S08, para no convertir `schemas.py` en paquete. Si tu equipo usó otros nombres, adaptá los imports: la lógica no cambia.
>
> **Ids de ejemplo.** En esta guía, `42` es una tarea del proyecto 1 y `7` es `<ID_ANA>`, la usuaria "Ana (lab)" que el seed de S08 dejó como `viewer` del proyecto 1. Reemplazalos por los de tu base (`SELECT id FROM tasks WHERE project_id = 1 LIMIT 1;`).

---

### Paso 0 — Rama, dependencias y servicios

```bash
git switch -c s09-protocolos
pip install redis websockets              # websockets ya viene con fastapi[standard]; trae el cliente CLI
docker compose up -d
docker compose exec cache redis-cli PING
```

**Verificación:** el último comando responde `PONG`. `python -c "import redis, websockets; print('ok')"` imprime `ok`.

El cliente de Redis es `redis-py`. Lo vas a crear siempre con `decode_responses=True`, porque si no todas las respuestas llegan como `bytes`.

---

### Paso 1 — Contrato primero para `/v2/tasks/{task_id}`

**1a.** Creá `contracts/openapi-v2.yaml` con el contrato de §4.1 y agregale un ejemplo a la respuesta, para que el mock devuelva algo predecible:

```yaml
      responses:
        "200":
          description: La tarea
          content:
            application/json:
              schema: { $ref: "#/components/schemas/TaskV2" }
              example: { id: 42, title: "Login falla con mayúsculas", status: in_progress, assignee_id: 7 }
```

**1b.** Validalo y levantá el mock:

```bash
npx @redocly/cli@latest lint contracts/openapi-v2.yaml        # terminal 1
npx @stoplight/prism-cli mock contracts/openapi-v2.yaml        # terminal 2: queda escuchando
curl -s http://127.0.0.1:4010/v2/tasks/42                       # terminal 3
```

**Deberías ver algo como:**

- `lint`: un resumen sin errores. Pueden aparecer **warnings** de reglas recomendadas: no bloquean, pero leelos. Si hay errores, Redocly te da archivo, línea, columna y regla.
- `prism mock`: el servidor queda escuchando en el **puerto 4010**.
- `curl`: el JSON del `example`. Ya hay un `/v2` consumible **sin una línea de FastAPI**, y el que hace la UI puede empezar a trabajar contra el mock.

Probá también `curl -s http://127.0.0.1:4010/v2/tasks/abc` y fijate qué devuelve Prism cuando el request no respeta el contrato.

**1c.** Commiteá el contrato **antes** de implementar:

```bash
git add contracts/ && git commit -m "contrato v2 de tareas (design-first)"
```

La comparación contra el código la hacés al final del paso 3.

---

### Paso 2 — El cambio incompatible: esquemas y un solo dominio

**2a.** El modelo interno y los contratos por versión. Primero, en `app/schemas.py` de S05, `TaskOut` suma un campo **opcional** (un cambio aditivo: no rompe a nadie):

```python
class TaskOut(BaseModel):             # el de S05, ahora modelo interno del dominio
    id: int
    title: str
    description: str | None = None
    assignee: str | None = None       # legado S05: la columna de texto, ya no se escribe
    assignee_id: int | None = None    # S09: nuevo
    status: TaskStatus
    created_at: datetime
```

Y en `SqlAlchemyTaskRepository._to_out` de S07, pasale el valor: `assignee_id=t.assignee_id`.

`TaskOut` pasa a ser el modelo **interno**. Lo que ve cada cliente lo fija el contrato de su versión. `app/schemas_v1.py` congela la forma que tenía `TaskOut` en S05:

```python
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas import TaskStatus


class TaskOutV1(BaseModel):
    id: int
    title: str
    description: str | None = None
    assignee: str | None = Field(default=None, description="Nombre del responsable. DEPRECADO: usá /v2 y assignee_id.")
    status: TaskStatus
    created_at: datetime


class TaskAssignV1(BaseModel):
    assignee: str | None                     # por nombre: ambiguo si hay dos "Ana"
```

`app/schemas_v2.py`:

```python
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas import TaskStatus


class TaskOutV2(BaseModel):
    id: int
    title: str
    status: TaskStatus
    assignee_id: int | None = Field(description="ID del usuario responsable.")


class TaskAssignV2(BaseModel):
    assignee_id: int | None


class BoardEvent(BaseModel):
    """Contrato de los eventos del tablero (v2). Si cambia de forma incompatible, es otra versión."""
    event_id: int
    project_id: int
    task_id: int
    kind: str
    old_value: str | None = None
    new_value: str | None = None
    occurred_at: datetime
```

**2b.** Tres métodos nuevos en el repositorio de S07. Siguen su regla: **el objeto ORM nunca sale del repository** (devuelven `TaskOut`, ids o strings) y cada escritura hace su `commit`:

```python
# app/repositories/sqlalchemy_repo.py (agregar a SqlAlchemyTaskRepository)
from ..db.models import ProjectMember, Task, User     # sumá ProjectMember y User al import de S07

def user_name(self, user_id: int) -> str | None:
    return self.session.scalar(select(User.name).where(User.id == user_id))

def member_ids_named(self, task_id: int, name: str) -> list[int]:
    stmt = (select(User.id)
            .join(ProjectMember, ProjectMember.user_id == User.id)
            .join(Task, Task.project_id == ProjectMember.project_id)
            .where(Task.id == task_id, User.name == name))
    return list(self.session.scalars(stmt))

def set_assignee(self, task_id: int, user_id: int | None) -> TaskOut | None:
    task = self.session.get(Task, task_id)
    if task is None:
        return None                          # el service lo traduce a TaskNotFound
    task.assignee_id = user_id               # tasks.assignee (string) YA NO se escribe
    try:
        self.session.commit()                # sin commit, la sesión del request hace rollback al cerrarse
    except StaleDataError:                   # version_id_col de S07: alguien la tocó en el medio
        self.session.rollback()
        raise ConcurrentUpdate(task_id)
    return self._to_out(task)
```

El service los delega y traduce "no existe" a la excepción de dominio de S05:

```python
# app/services/task_service.py (agregar a TaskService)
def get(self, task_id: int) -> TaskOut:
    task = self.repo.get(task_id)
    if task is None:
        raise TaskNotFound(task_id)
    return task

def assign(self, task_id: int, user_id: int | None) -> TaskOut:
    task = self.repo.set_assignee(task_id, user_id)
    if task is None:
        raise TaskNotFound(task_id)
    return task

def user_name(self, user_id: int) -> str | None:
    return self.repo.user_name(user_id)

def member_ids_named(self, task_id: int, name: str) -> list[int]:
    return self.repo.member_ids_named(task_id, name)
```

Sumá los tres métodos al `Protocol` de `repositories/base.py`. Y si usás la caché de S06 (`TASKFLOW_CACHE=redis`), el `CachedTaskRepository` envuelve al repo y **no** los tiene: agregalos ahí delegando en `self.inner`, y en `set_assignee` llamá a `self._invalidate()` después de escribir, igual que en `update_status`. Sin eso, el `PATCH` de asignación falla con `AttributeError` o el tablero sigue mostrando el responsable viejo hasta que venza el TTL. El repo en memoria de S05 no hace falta tocarlo: los tests de hoy no asignan.

**2c.** El router `/v2`, que habla el dominio nuevo sin traducir nada. `app/routers/tasks_v2.py`:

```python
from fastapi import APIRouter, HTTPException

from ..dependencies import TaskServiceDep
from ..errors import ConcurrentUpdate          # S07: módulo neutro; el router no importa repositories/
from ..schemas import TaskStatus, TaskStatusUpdate
from ..schemas_v2 import TaskAssignV2, TaskOutV2
from ..services.task_service import InvalidTransition, TaskNotFound

router = APIRouter(prefix="/tasks", tags=["v2"])


@router.get("", response_model=list[TaskOutV2], operation_id="list_tasks_v2")
def list_tasks_v2(service: TaskServiceDep, status: TaskStatus | None = None):
    return service.list_tasks(status)                   # el mismo método de S05


@router.get("/{task_id}", response_model=TaskOutV2, operation_id="get_task_v2")
def get_task_v2(task_id: int, service: TaskServiceDep):
    try:
        return service.get(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@router.patch("/{task_id}/status", response_model=TaskOutV2, operation_id="move_task_v2")
def move_task_v2(task_id: int, body: TaskStatusUpdate, service: TaskServiceDep):
    try:
        return service.move(task_id, body.status)       # la regla de transiciones de S05
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")
    except (InvalidTransition, ConcurrentUpdate) as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.patch("/{task_id}/assignee", response_model=TaskOutV2, operation_id="assign_task_v2")
def assign_task_v2(task_id: int, body: TaskAssignV2, service: TaskServiceDep):
    try:
        return service.assign(task_id, body.assignee_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")
    except ConcurrentUpdate as exc:
        raise HTTPException(status_code=409, detail=str(exc))
```

`response_model=TaskOutV2` es el que filtra: el service devuelve un `TaskOut` completo y FastAPI saca `assignee`, `description` y `created_at` de la respuesta.

**2d.** El router `/v1` como **adaptador**. Es el `app/routers/tasks.py` de S05, con su `prefix="/tasks"`: no se mueve, se sirve bajo `/v1` en el paso 3. Todas sus rutas pasan a devolver `TaskOutV1`, traduciendo con `to_v1`, y se suman dos:

```python
# app/routers/tasks.py (lo nuevo y lo que cambia)
from ..schemas import TaskOut
from ..schemas_v1 import TaskAssignV1, TaskOutV1
from ..services.task_service import InvalidTransition, TaskNotFound, TaskService


def to_v1(task: TaskOut, service: TaskService) -> TaskOutV1:
    name = service.user_name(task.assignee_id) if task.assignee_id else None
    return TaskOutV1(**task.model_dump(exclude={"assignee", "assignee_id"}), assignee=name)


@router.get("/")
def list_tasks(service: TaskServiceDep, status: TaskStatus | None = None) -> list[TaskOutV1]:
    return [to_v1(t, service) for t in service.list_tasks(status)]


@router.get("/{task_id}")
def get_task(task_id: int, service: TaskServiceDep) -> TaskOutV1:
    try:
        return to_v1(service.get(task_id), service)     # el service ya trabaja con assignee_id
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@router.patch("/{task_id}/assignee")
def assign_task(task_id: int, body: TaskAssignV1, service: TaskServiceDep) -> TaskOutV1:
    user_id = None
    if body.assignee is not None:
        matches = service.member_ids_named(task_id, body.assignee)
        if len(matches) != 1:
            raise HTTPException(422, detail="Nombre inexistente o ambiguo: usá PATCH /v2 con assignee_id")
        user_id = matches[0]
    try:
        return to_v1(service.assign(task_id, user_id), service)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")
```

`create_task` y `move_task` de S05 quedan con su lógica: cambiá la anotación de retorno a `TaskOutV1` y devolvé `to_v1(...)`. Sin ese cambio, `/v1` empezaría a exponer `assignee_id`: un cambio aditivo, pero que nadie decidió.

---

### Paso 3 — `/v1` y `/v2` conviviendo (opción A)

`app/main.py` (solo lo nuevo; el `lifespan` se completa en el paso 4):

```python
from fastapi import Depends, FastAPI, Response
from fastapi.staticfiles import StaticFiles

from .routers import tasks as tasks_v1        # el router de S05, ahora adaptador de /v1
from .routers import tasks_v2


def mark_v1_deprecated(response: Response) -> None:
    response.headers["Deprecation"] = "@1790812800"                  # 2026-10-01T00:00:00Z
    response.headers["Sunset"] = "Fri, 01 Jan 2027 00:00:00 GMT"
    response.headers["Link"] = '</v2/docs>; rel="deprecation"'

app = FastAPI(title="TaskFlow API", version="2.0.0", lifespan=lifespan)
app.include_router(tasks_v1.router, prefix="/v1", tags=["v1 (deprecada)"],
                   dependencies=[Depends(mark_v1_deprecated)], deprecated=True)
app.include_router(tasks_v2.router, prefix="/v2")
app.mount("/static", StaticFiles(directory="static"), name="static")   # igual que en S05
# los routers de S08 (/v1/projects/...) siguen como estaban: no exponen assignee
```

Con el `prefix="/tasks"` de S05, las rutas quedan en `/v1/tasks/…` (listar y crear conservan la barra final de S05: `/v1/tasks/`) y en `/v2/tasks/…`.

Actualizá la UI estática (`static/index.html`) para que lea y mueva tareas con `/v2/...` en lugar de `/tasks/`. Crear tarea sigue en `POST /v1/tasks/`: `/v2` todavía no tiene alta, y diseñarla es parte del contrato completo de S10.

**Verificación:**

```bash
TASKFLOW_STORAGE=postgres uvicorn app.main:app --reload
curl -s -X PATCH http://localhost:8000/v2/tasks/42/assignee -H 'content-type: application/json' -d '{"assignee_id": 7}'
curl -i http://localhost:8000/v1/tasks/42
curl -s http://localhost:8000/v2/tasks/42
```

**Deberías ver algo como** esto en las dos últimas (Uvicorn escribe los nombres de header en minúsculas; ids, fechas y estado dependen de tu base):

```
HTTP/1.1 200 OK
date: …
server: uvicorn
content-length: …
content-type: application/json
deprecation: @1790812800
sunset: Fri, 01 Jan 2027 00:00:00 GMT
link: </v2/docs>; rel="deprecation"

{"id":42,"title":"Login falla con mayúsculas","description":null,"assignee":"Ana (lab)","status":"in_progress","created_at":"2026-09-23T11:55:34.648491Z"}

{"id":42,"title":"Login falla con mayúsculas","status":"in_progress","assignee_id":7}
```

Probá también el adaptador de escritura: `curl -s -X PATCH http://localhost:8000/v1/tasks/42/assignee -H 'content-type: application/json' -d '{"assignee": "Ana (lab)"}'` asigna por nombre, y con un nombre que no es miembro del proyecto (o que se repite) responde 422 con el mensaje que manda a `/v2`.

En `http://localhost:8000/docs`, las rutas `v1 (deprecada)` aparecen tachadas.

**Test** (en `tests/test_tasks.py`, con la fixture `client` de S05, que usa el repo en memoria):

```python
def test_v1_anuncia_deprecacion(client):
    task_id = client.post("/v1/tasks/", json={"title": "A"}).json()["id"]
    r = client.get(f"/v1/tasks/{task_id}")
    assert r.status_code == 200
    assert r.headers["deprecation"].startswith("@")
    assert "sunset" in r.headers and "assignee" in r.json()

def test_v2_expone_assignee_id(client):
    task_id = client.post("/v1/tasks/", json={"title": "A"}).json()["id"]
    body = client.get(f"/v2/tasks/{task_id}").json()
    assert "assignee_id" in body and "assignee" not in body
```

Los tests de S05 que llaman a `/tasks/` pasan a `/v1/tasks/`: las rutas sin versión ya no existen.

**Cerrar el ciclo design-first:** compará el contrato con lo que generó el código.

```bash
mkdir -p build
curl -s http://localhost:8000/openapi.json > build/openapi.generated.json
python -c "import json; d=json.load(open('build/openapi.generated.json')); print(json.dumps(d['paths']['/v2/tasks/{task_id}'], indent=2)); print(json.dumps(d['components']['schemas']['TaskOutV2'], indent=2))"
```

Revisá contra `contracts/openapi-v2.yaml`: mismo `operationId`, mismos campos obligatorios, mismo enum de `status`, `assignee_id` nullable. Podés hacerlo a ojo o pedírselo al agente ("listá las diferencias semánticas de schema entre estos dos archivos"). Si alguna diferencia es real (un campo que falta, otro nombre), corregí **el código o el contrato** y dejá constancia en el commit.

> 💡 **Opción B, si querés docs por versión:** creá `v1 = FastAPI(title="TaskFlow API v1")` y `v2 = FastAPI(title="TaskFlow API v2")`, incluí cada router (el de v1 con `include_router(..., dependencies=[Depends(mark_v1_deprecated)], deprecated=True)`) y montalas con `app.mount("/v1", v1)` y `app.mount("/v2", v2)`. Cada una tiene su `/v1/docs` y su `/v2/openapi.json`. El `lifespan` va **solo** en `app`.

---

### Paso 4 — WebSocket del tablero alimentado por `task_events`

**4a. Migración: un timbre por evento.** Se escribe a mano, porque *autogenerate* no ve triggers (igual que en S08).

```bash
alembic revision -m "notify task_events"
```

```python
def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION notify_task_event() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify('task_events', json_build_object(
                'event_id', NEW.id, 'project_id', NEW.project_id, 'task_id', NEW.task_id,
                'kind', NEW.kind, 'old_value', NEW.old_value, 'new_value', NEW.new_value,
                'occurred_at', NEW.occurred_at)::text);
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER task_events_notify AFTER INSERT ON task_events
            FOR EACH ROW EXECUTE FUNCTION notify_task_event();
    """)

def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS task_events_notify ON task_events;
        DROP FUNCTION IF EXISTS notify_task_event();
    """)
```

```bash
alembic upgrade head
```

**Verificación en psql:** abrí dos sesiones con `docker compose exec db psql -U taskflow -d taskflow_app`. En la primera, `LISTEN task_events;`. En la segunda, movés una tarea con un `UPDATE tasks SET status = 'done' WHERE id = 42;`. psql solo muestra las notificaciones **después de ejecutar un comando**, así que en la primera corré cualquier cosa (`SELECT 1;`). Deberías ver algo como:

```
Asynchronous notification "task_events" with payload "{"event_id" : 2, "project_id" : 1, "task_id" : 42, "kind" : "status_changed", "old_value" : "in_progress", "new_value" : "done", "occurred_at" : "2026-09-23T11:55:42.970497+00:00"}" received from server process with PID 91.
```

Aprovechá para mirar qué `kind` usa tu trigger de S08 para una asignación:

```sql
SELECT kind, old_value, new_value FROM task_events ORDER BY id DESC LIMIT 5;
```

Con la migración de S08 tal como está, son `status_changed` y `assigned`, con `new_value` = id del usuario como texto (el `CHECK` de `task_events` admite `created`, `status_changed`, `assigned` y `commented`). Si tu equipo la cambió, anotá el nombre exacto: lo vas a necesitar en el paso 5.

**4b. El hub y el listener.** `app/realtime/board.py` (creá también `app/realtime/__init__.py` vacío):

```python
import asyncio
import logging
from collections import defaultdict

import psycopg
from fastapi import WebSocket

from app.schemas.v2 import BoardEvent

log = logging.getLogger("taskflow.board")

class BoardHub:
    """Sockets abiertos por proyecto, EN ESTE PROCESO. Cada worker de Uvicorn tiene el suyo."""
    def __init__(self) -> None:
        self.rooms: dict[int, set[WebSocket]] = defaultdict(set)

    def join(self, project_id: int, ws: WebSocket) -> None:
        self.rooms[project_id].add(ws)

    def leave(self, project_id: int, ws: WebSocket) -> None:
        self.rooms[project_id].discard(ws)

    async def publish(self, project_id: int, event: dict) -> None:
        for ws in list(self.rooms.get(project_id, ())):
            try:
                await ws.send_json(event)
            except Exception:                  # socket muerto: lo sacamos
                self.leave(project_id, ws)

hub = BoardHub()

async def listen_task_events(dsn: str) -> None:
    """Un LISTEN por proceso. Postgres entrega cada NOTIFY a TODAS las sesiones que escuchan."""
    while True:
        try:
            async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as conn:
                await conn.execute("LISTEN task_events")
                async for n in conn.notifies():
                    event = BoardEvent.model_validate_json(n.payload)
                    await hub.publish(event.project_id, event.model_dump(mode="json"))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("listener caído; reintento en 2 s")
            await asyncio.sleep(2)
```

En `app/main.py`, sumalo a tu `lifespan` existente, **el del app principal**:

```python
import asyncio
from contextlib import asynccontextmanager, suppress

from .dependencies import DATABASE_URL, STORAGE
from .realtime.board import listen_task_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    # … lo que ya hacía tu lifespan de S05–S08 …
    listener = None
    if STORAGE == "postgres":            # en memoria o SQLite no hay a quién escuchar
        dsn = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")  # psycopg no entiende el dialecto de SQLAlchemy
        listener = asyncio.create_task(listen_task_events(dsn))
    yield
    if listener is not None:
        listener.cancel()
        with suppress(asyncio.CancelledError):
            await listener               # esperar a que cierre su conexión antes de apagar
```

`DATABASE_URL` y `STORAGE` son los de `app/dependencies.py` de S07: leen `TASKFLOW_DATABASE_URL` y `TASKFLOW_STORAGE`. La fixture de tests de S05 crea `TestClient(app)` **sin** `with`, así que en los tests el lifespan no corre y el listener no arranca.

**4c. El endpoint.** `app/routers/board_ws.py`:

```python
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from ..db.models import ProjectMember
from ..dependencies import SessionLocal          # el sessionmaker de S07
from ..realtime.board import hub

router = APIRouter()

def user_has_role(project_id: int, user_id: int) -> bool:
    """Sesión de BD corta y propia: NO un Depends que viva toda la conexión."""
    with SessionLocal() as s:
        return s.scalar(select(ProjectMember.user_id).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)) is not None

@router.websocket("/projects/{project_id}/board/ws")
async def board_ws(websocket: WebSocket, project_id: int,
                   user_id: int = Query(description="PROVISORIO hasta S14, como X-User-Id en S08")):
    if not await run_in_threadpool(user_has_role, project_id, user_id):
        raise WebSocketException(code=1008)            # policy violation, antes de accept()
    await websocket.accept()
    hub.join(project_id, websocket)
    try:
        async for _ in websocket.iter_text():          # solo mantenemos viva la conexión
            pass
    except WebSocketDisconnect:
        pass
    finally:
        hub.leave(project_id, websocket)
```

Y en `main.py`: `from .routers import board_ws` y `app.include_router(board_ws.router, prefix="/v2")`.

**4d. Cliente en la UI estática.** `static/board.js`, que cargás desde `static/index.html` con `<script src="/static/board.js"></script>`:

```js
async function refreshBoardViaHttp(projectId) {
  const r = await fetch(`/v2/tasks`);
  renderBoard(await r.json());               // la función de render que ya tenés desde S05
}

function applyEvent(ev) {
  if (ev.kind === "status_changed") {
    const card = document.querySelector(`[data-task-id="${ev.task_id}"]`);
    const column = document.querySelector(`[data-status="${ev.new_value}"]`);
    if (card && column) { column.appendChild(card); return; }
  }
  refreshBoardViaHttp(ev.project_id);        // cualquier otro evento: re-sincronizar
}

function connectBoard(projectId, userId) {
  const ws = new WebSocket(`ws://${location.host}/v2/projects/${projectId}/board/ws?user_id=${userId}`);
  ws.addEventListener("open", () => refreshBoardViaHttp(projectId));   // SIEMPRE al (re)conectar
  ws.addEventListener("message", (e) => applyEvent(JSON.parse(e.data)));
  ws.addEventListener("close", () => setTimeout(() => connectBoard(projectId, userId), 1000));
}

connectBoard(1, 7);                          // proyecto 1, usuario <ID_ANA>
```

**4e. Probar desde la terminal, sin navegador:**

```bash
# terminal 1 (la API ya corriendo en otra)
websockets "ws://localhost:8000/v2/projects/1/board/ws?user_id=7"
# terminal 2
curl -s -X PATCH localhost:8000/v2/tasks/42/status -H 'content-type: application/json' -d '{"status":"done"}'
```

**En la terminal 1 deberías ver algo como:**

```
Connected to ws://localhost:8000/v2/projects/1/board/ws?user_id=7.
< {"event_id":311,"project_id":1,"task_id":42,"kind":"status_changed","old_value":"in_progress","new_value":"done","occurred_at":"2026-09-23T15:02:11.482137Z"}
```

`send_json` manda el JSON compacto, sin espacios. Si la tarea ya estaba en `done`, el `PATCH` devuelve 409 (la regla de transiciones de S05) y no hay evento: movela a un estado permitido.

Probá también con un `user_id` sin rol en el proyecto (por ejemplo `999`): la conexión se rechaza antes de abrirse, y el cliente muestra algo como `Failed to connect to ws://…?user_id=999: server rejected WebSocket connection: HTTP 403.` (el `WebSocketException` antes de `accept()` llega al navegador como un handshake rechazado).

**4f. Varios workers.** Cortá el `--reload` (no convive con `--workers`):

```bash
uvicorn app.main:app --workers 2
```

Abrí tres clientes `websockets` y repetí el `PATCH`: **todos** reciben el evento, aunque caigan en procesos distintos, porque cada proceso tiene su propio `LISTEN`. Con el `ConnectionManager` en memoria de la doc, los que estuvieran en el otro worker no lo recibirían. El costo: **una conexión de Postgres dedicada por worker**. Anotalo para TJ-008.

**4g. Test.** `user_has_role` consulta Postgres directamente, sin pasar por `get_repository`, así que el override de la fixture de S05 no la alcanza. En el test se reemplaza con `monkeypatch`, y así no hace falta una base levantada:

```python
import pytest
from fastapi import WebSocketDisconnect

from app.routers import board_ws


def test_board_rechaza_sin_rol(client, monkeypatch):
    monkeypatch.setattr(board_ws, "user_has_role", lambda project_id, user_id: False)
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/v2/projects/1/board/ws?user_id=999"):
            pass
    assert exc.value.code == 1008


def test_board_acepta_con_rol(client, monkeypatch):
    monkeypatch.setattr(board_ws, "user_has_role", lambda project_id, user_id: True)
    with client.websocket_connect("/v2/projects/1/board/ws?user_id=7") as ws:
        ws.send_text("ping")                 # la conexión quedó abierta
```

Corré `pytest -q -k board`. `TestClient` expresa el handshake rechazado como `WebSocketDisconnect` con el código que mandó el servidor. Lo que importa es que **sin rol no se conecta**.

---

### Paso 5 — Worker de notificaciones sobre Redis Streams

**5a. Tabla de idempotencia.** En `app/db/models.py`:

```python
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

class NotificationSent(Base):
    __tablename__ = "notifications_sent"
    event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_events.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.clock_timestamp())
```

```bash
alembic revision --autogenerate -m "notifications_sent"
alembic upgrade head
```

Revisá la migración generada antes de aplicarla (el checklist de S07). Tiene que equivaler a:

```sql
CREATE TABLE notifications_sent (
    event_id bigint PRIMARY KEY REFERENCES task_events(id) ON DELETE CASCADE,
    user_id  integer NOT NULL REFERENCES users(id),
    sent_at  timestamptz NOT NULL DEFAULT clock_timestamp()
);
```

**5b. Relay: del outbox al stream.** `scripts/relay_events.py` (el `scripts/__init__.py` vacío ya lo creaste en S08; si no, creálo):

```python
import time
from datetime import timedelta

import redis
from sqlalchemy import func, select

from app.db.models import TaskEvent
from app.dependencies import SessionLocal

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
STREAM, CURSOR = "taskflow:events", "taskflow:relay:last_event_id"

while True:
    last = int(r.get(CURSOR) or 0)
    with SessionLocal() as s:
        events = s.scalars(
            select(TaskEvent)
            .where(TaskEvent.id > last,
                   TaskEvent.occurred_at < func.now() - timedelta(seconds=5))   # margen para transacciones lentas
            .order_by(TaskEvent.id).limit(500)
        ).all()
    for ev in events:
        r.xadd(STREAM, {"event_id": ev.id, "kind": ev.kind, "task_id": ev.task_id,
                        "project_id": ev.project_id, "old": ev.old_value or "", "new": ev.new_value or ""},
               maxlen=100_000, approximate=True)
        r.set(CURSOR, ev.id)            # si muere entre xadd y set → el evento se publica 2 veces
    time.sleep(1)
```

Dos limitaciones deliberadas:

1. **Duplicados desde el productor:** si el relay muere entre `xadd` y `set`, el evento sale dos veces. El worker lo tiene que tolerar.
2. **Ids fuera de orden de commit:** los ids `IDENTITY` se asignan al insertar, no al confirmar. Una transacción lenta puede confirmar un id **menor** que otro ya relevado, y el cursor lo saltearía. Es el mismo problema de la marca de agua de S08. El margen de 5 s lo mitiga, pero no lo elimina. La solución fuerte es CDC (nombrado en S08).

`maxlen=100_000, approximate=True` es el `MAXLEN ~` de la doc: recorta el stream para que no crezca sin límite.

**5c. Worker.** `scripts/notify_worker.py`:

```python
import logging
import os
import socket

import redis
from sqlalchemy.dialects.postgresql import insert

from app.db.models import NotificationSent
from app.dependencies import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("notify_worker")

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
STREAM, GROUP = "taskflow:events", "notifier"
CONSUMER = f"{socket.gethostname()}-{os.getpid()}"

try:
    r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)     # "0" = desde el principio
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e):                             # el grupo ya existe: está bien
        raise

def already_sent(event_id: int) -> bool:
    with SessionLocal() as s:
        return s.get(NotificationSent, event_id) is not None

def send_email_fake(user_id: int, task_id: int) -> None:
    line = f"email → user {user_id}: te asignaron la tarea {task_id}"
    log.info(line)
    with open("emails_enviados.log", "a") as f:
        f.write(line + "\n")

def handle(fields: dict) -> None:
    if fields["kind"] != "assigned" or not fields["new"]:
        return                                                # este consumidor solo mira asignaciones
    event_id, user_id = int(fields["event_id"]), int(fields["new"])
    if already_sent(event_id):
        log.info("evento %s ya notificado: se ignora", event_id)
        return
    send_email_fake(user_id, task_id=int(fields["task_id"]))
    with SessionLocal.begin() as s:
        s.execute(insert(NotificationSent).values(event_id=event_id, user_id=user_id)
                  .on_conflict_do_nothing())

def process(msg_id: str, fields: dict) -> None:
    handle(fields)
    r.xack(STREAM, GROUP, msg_id)                             # ack DESPUÉS de procesar

log.info("worker %s escuchando %s", CONSUMER, STREAM)
while True:
    # 1) rescatar lo que dejó colgado un worker muerto (más de 60 s sin ack)
    claimed = r.xautoclaim(STREAM, GROUP, CONSUMER, min_idle_time=60_000, start_id="0-0", count=10)[1]
    for msg_id, fields in claimed:
        process(msg_id, fields)
    # 2) mensajes nuevos, nunca entregados a nadie del grupo
    for _stream, messages in r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=10, block=5000) or []:
        for msg_id, fields in messages:
            process(msg_id, fields)
```

> ⚠️ Con Redis 8 y redis-py, `xautoclaim(...)` devuelve una lista de tres elementos: el cursor para la próxima llamada, **la lista de mensajes reclamados** (el `[1]`) y los ids que ya no existen en el stream. Por ejemplo: `['0-0', [('1790164690213-0', {'event_id': '6', 'kind': 'assigned', …})], []]`. Si tu versión devuelve otra forma, imprimí el resultado una vez y ajustá el índice.

Si en el paso 4a viste que tu trigger usa otro `kind` para las asignaciones, cambialo en `handle`.

**5d. Probar:**

```bash
python -m scripts.relay_events                     # terminal A (con -m, como el embed_worker de S08)
python -m scripts.notify_worker                    # terminal B
curl -s -X PATCH localhost:8000/v2/tasks/42/assignee -H 'content-type: application/json' -d '{"assignee_id": 7}'
docker compose exec cache redis-cli XINFO GROUPS taskflow:events
docker compose exec cache redis-cli XPENDING taskflow:events notifier
```

Se corren con `python -m` desde la raíz del repo: con `python scripts/relay_events.py`, Python pone `scripts/` en el path y el `import app` falla con `ModuleNotFoundError: No module named 'app'`. Si la tarea ya estaba asignada a ese usuario, el trigger no registra evento: asignala a otro o a `null` primero.

**Deberías ver algo como:**

- En el worker, unos 5–6 s después del `PATCH` (el margen del relay + su `sleep`): `email → user 7: te asignaron la tarea 42`. Si ya había asignaciones en `task_events`, la primera vez también salen sus emails: el grupo se creó con `0`, desde el principio.
- En `XINFO GROUPS`, el grupo `notifier` con `pending` en `0` una vez procesado:

  ```
  1)  1) "name"
      2) "notifier"
      3) "consumers"
      4) (integer) 1
      5) "pending"
      6) (integer) 0
      7) "last-delivered-id"
      8) "1790164662023-0"
      9) "entries-read"
     10) (integer) 5
     11) "lag"
     12) (integer) 0
  ```

- En `XPENDING`, cero pendientes: `1) (integer) 0` seguido de tres `(nil)`.
- En `emails_enviados.log`, una línea por asignación.

**5e. Experimentos** (práctica autónoma, uno por uno):

1. **Worker que muere.** Agregá `time.sleep(30)` al principio de `handle` (con `import time`), hacé el `PATCH` y matá el worker con `Ctrl+C` durante el sleep. `XPENDING` muestra **1 pendiente**, a nombre del consumidor muerto. Sacá el sleep, levantá el worker de nuevo y esperá: el nuevo tiene otro nombre (otro pid), y cuando el mensaje lleva 60 s sin ack, `XAUTOCLAIM` se lo pasa y el email sale.
2. **Competing consumers.** Levantá dos workers (terminales B y C) y hacé cinco asignaciones seguidas. Cada worker procesa una parte.
3. **Fan-out persistente.** `docker compose exec cache redis-cli XGROUP CREATE taskflow:events board-metrics 0` y leé con `docker compose exec cache redis-cli XREADGROUP GROUP board-metrics m1 STREAMS taskflow:events '>'`. Recibís **todos** los eventos, independientemente de `notifier`.
4. **Duplicado forzado.** `docker compose exec cache redis-cli DEL taskflow:relay:last_event_id`. En el próximo ciclo el relay republica todo desde el principio (no hace falta reiniciarlo: lee el cursor en cada vuelta), el worker loguea `evento N ya notificado: se ignora` por cada asignación y **ningún email sale dos veces** (`emails_enviados.log` no crece).

> 💡 **Stretch RabbitMQ:** agregá al compose un servicio con la imagen `rabbitmq:4-management` (AMQP en 5672, UI de management en 15672, credenciales por defecto `guest`/`guest`), instalá `pika` y reescribí el worker según el tutorial 2 con los parámetros de §4.5. La idempotencia no se toca: RabbitMQ también reentrega.

---

### Paso 6 — gRPC mínimo (stretch): `NotificationService`

```bash
pip install grpcio grpcio-tools
```

Creá `proto/notifications.proto` con el contrato de §4.6 y generá el código:

```bash
python -m grpc_tools.protoc -I proto --python_out=. --pyi_out=. --grpc_python_out=. proto/notifications.proto
ls notifications_pb2*
```

**Verificación:** existen `notifications_pb2.py`, `notifications_pb2.pyi` y `notifications_pb2_grpc.py`.

`notifications_server.py`:

```python
from concurrent import futures

import grpc

import notifications_pb2 as pb
import notifications_pb2_grpc as pb_grpc

class Notifications(pb_grpc.NotificationsServicer):
    def __init__(self) -> None:
        self.seen: set[int] = set()          # en memoria: alcanza para la demo

    def Send(self, request, context):
        if request.event_id in self.seen:
            return pb.SendReply(duplicate=True)
        self.seen.add(request.event_id)
        print(f"email → user {request.user_id}: {request.template} {dict(request.params)}")
        return pb.SendReply(duplicate=False, delivery_id=f"d-{request.event_id}")

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb_grpc.add_NotificationsServicer_to_server(Notifications(), server)
server.add_insecure_port("[::]:50051")
server.start()
server.wait_for_termination()
```

`grpc_client_demo.py`:

```python
import grpc

import notifications_pb2 as pb
import notifications_pb2_grpc as pb_grpc

with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.NotificationsStub(channel)
    for _ in range(2):
        reply = stub.Send(pb.SendRequest(event_id=311, user_id=7, template="task_assigned",
                                         params={"task_id": "42"}), timeout=2.0)
        print(reply)
```

```bash
python notifications_server.py        # terminal 1
python grpc_client_demo.py            # terminal 2
```

**Deberías ver algo como:** la primera respuesta imprime `delivery_id: "d-311"` (sin `duplicate`, porque `false` es el valor por defecto y proto3 no lo muestra), y la segunda, `duplicate: true`. El servidor imprime una sola vez `email → user 7: task_assigned {'task_id': '42'}`.

Apagá el servidor y volvé a correr el cliente: falla **enseguida** con `StatusCode.UNAVAILABLE` (`failed to connect to all addresses … Connection refused`). Por defecto gRPC no espera a que el servidor aparezca: si no hay a quién conectarse, corta. Para ver el deadline en acción, agregá `wait_for_ready=True` a la llamada (`stub.Send(..., timeout=2.0, wait_for_ready=True)`): ahora el cliente espera que el servidor vuelva, y a los 2 s falla con `StatusCode.DEADLINE_EXCEEDED`. En ningún caso se queda colgado.

El siguiente paso natural (el desafío 🔴1) es que `notify_worker.py` llame a `stub.Send` en lugar de `send_email_fake`.

---

### Paso 7 — TCP vs UDP con `socket`

En `labs/tcp_udp/`, cuatro archivos:

```python
# tcp_server.py
import socket

with socket.create_server(("127.0.0.1", 9000)) as srv:
    conn, addr = srv.accept()
    with conn:
        while chunk := conn.recv(1024):          # b"" = el otro lado cerró
            print(f"TCP recv {len(chunk)} bytes: {chunk!r}")
```

```python
# tcp_client.py
import socket

with socket.create_connection(("127.0.0.1", 9000)) as s:
    for i in range(5):
        s.sendall(f"move task {i}\n".encode())
```

```python
# udp_server.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 9001))
while True:
    data, addr = s.recvfrom(2048)
    print(f"UDP datagram de {addr}: {data!r}")
```

```python
# udp_client.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(5):
    s.sendto(f"cursor {i}".encode(), ("127.0.0.1", 9001))
```

**Corré los tres experimentos:**

```bash
cd labs/tcp_udp
python tcp_server.py & sleep 0.5; python tcp_client.py   # 1) TCP (el sleep le da tiempo al server a escuchar)
python udp_server.py & sleep 0.5; python udp_client.py   # 2) UDP (cortá el server con kill %1 al terminar)
python tcp_client.py                               # 3) con el server TCP apagado
python udp_client.py                               # 3) con el server UDP apagado
```

**Qué deberías observar** (la forma exacta depende del sistema operativo y del momento):

| Experimento | TCP | UDP |
|---|---|---|
| 5 envíos seguidos | Probablemente **menos de 5** `recv`, con mensajes pegados. En loopback suele ser uno solo: `TCP recv 60 bytes: b'move task 0\nmove task 1\n...move task 4\n'`. Es un *byte-stream* | **5 datagramas separados**: se respetan los límites |
| Servidor apagado | `ConnectionRefusedError: [Errno 111] Connection refused` inmediato (el número de error puede variar según el sistema operativo): hay conexión, y alguien avisa | Normalmente **ningún error**: `sendto` "sale" y nadie se entera de que se perdió |
| Orden y pérdida | Garantizados por el protocolo | Sin garantía. En loopback casi nunca se ve una pérdida: hace falta una red real |

El arreglo del framing TCP es el ejercicio 🟢2.

---

### Paso 8 — TJ-008 y entrega

Completá la entrada TJ-008 en `tradeoff-journal.md` con la plantilla de §4.8, **con tus números y tus decisiones**: ¿WebSocket o SSE? ¿Qué orden elegiste en el worker y qué pasa si muere en cada punto? ¿Cuántas conexiones de Postgres suma el tablero con N workers?

```bash
pytest -q
git add -A && git commit -m "S09: /v1-/v2, tablero WebSocket, worker de notificaciones, TJ-008"
git tag s09
git push -u origin s09-protocolos --tags
```

**Checklist de entrega:**

- [ ] `contracts/openapi-v2.yaml` commiteado **antes** que la implementación de `/v2`.
- [ ] `/v1` responde con `Deprecation`, `Sunset` y `Link`; `/v2` expone `assignee_id`.
- [ ] El tablero se actualiza en dos navegadores (o dos `websockets`) con `--workers 2`.
- [ ] El worker sobrevive a los experimentos 1 y 4 del paso 5 sin perder ni duplicar emails.
- [ ] `pytest -q` pasa, incluidos los tests nuevos.
- [ ] TJ-008 escrita.

> 📝 **Nota para el profesor:** todo el lab está escrito con defaults que conviene revisar antes de publicar. **Timing** 40/60/45/20/15, con gRPC como stretch fuera de clase (si hay que recortar, sale primero gRPC y después Prism; el lint queda). **Mismos equipos** de 3 de S05. **Entrega:** rama `s09-protocolos`, tag `s09`, TJ-008 y el contrato commiteado. **Fechas de `/v1`:** Deprecation 1-oct-2026 y Sunset 1-ene-2027, elegibles. **Backfill de S07:** confirmá que `assignee_id` quedó poblado; si no, el `/v1` devuelve `null` donde antes había nombre. **Rutas sin versión de S05:** se sirven bajo `/v1` sin alias, y la UI pasa a `/v2` para leer y mover (crear sigue en `/v1` hasta S10). **Opción A** de versionado por defecto, B como alternativa. **Broker:** Redis Streams (servicio `cache` del `compose.yaml` de S06), RabbitMQ como stretch. **Email fake** a log/archivo, sin servicio SMTP. **Identidad en el WebSocket:** `?user_id=`, inseguro a propósito hasta S14. **WebSocket** en el lab y SSE como alternativa: un equipo que entregue SSE justificado en TJ-008 también cumple. **Nombres de `kind`** del trigger de S08 (`status_changed`, `assigned`) y nombres de módulos/helpers tomados de S05–S08 (`app/schemas.py`, `app/dependencies.py` con `SessionLocal` y `DATABASE_URL`, `app/routers/`, `TaskService.move`, `SqlAlchemyTaskRepository`, `ProjectMember`): ajustalos a lo que haya quedado en el repo. **Ids de ejemplo:** tarea 42 y usuario 7 = `<ID_ANA>` del seed de S08. **Solape con S10:** conviene que S10 tome `/v1` y `/v2` como existentes y diseñe el contrato completo sobre `/v2`.

---

## 6. Ejercicios

Todos se hacen sobre el repo `taskflow` de la rama `s09-protocolos`.

### 🟢 Básico 1 — ¿Rompe o no rompe? Tres cambios en código

Implementá estos tres cambios **en ramas separadas** y decidí para cada uno si va en `/v1` (compatible) o necesita versión nueva:

1. Agregar `due_date: date | None` a la respuesta de la tarea.
2. Cambiar el valor del enum `in_progress` a `doing`.
3. Agregar un campo opcional `priority` al body de `PATCH /tasks/{id}/status`.

Para el que sea compatible, implementalo en `/v1` y `/v2`. Para los incompatibles, escribí en `docs/api/s09-cambios.md` qué regla de AIP-180 rompen y cómo los harías con parallel change.

**Sabés que lo lograste cuando…** el cambio compatible pasa **los tests existentes sin tocarlos**, aparece como opcional en `/openapi.json`, y tu documento nombra la regla exacta que rompe cada cambio incompatible.

<details>
<summary>Pistas</summary>

- Cambiar un valor de enum es cambiar un **formato de valor**, aunque el tipo siga siendo `string`.
- Para el campo del body, preguntate qué pasa con un cliente viejo que **no** lo manda.
- Un test existente que se rompe con tu cambio es la mejor señal de que es breaking.
</details>

### 🟢 Básico 2 — Framing sobre TCP

Modificá `labs/tcp_udp/tcp_server.py` para que imprima **exactamente un mensaje por línea**, sin importar cómo lleguen los bytes. Para probarlo, escribí `tcp_client_partido.py`, que mande `"move ta"`, espere 0,5 s, mande `"sk 0\nmove task 1\nmo"`, espere, y mande `"ve task 2\n"`.

**Sabés que lo lograste cuando…** con `tcp_client.py` y con `tcp_client_partido.py` el servidor imprime exactamente `move task 0`, `move task 1`, … una línea por mensaje, sin fragmentos ni mensajes pegados. Y si el cliente cierra a mitad de un mensaje, el servidor no imprime el fragmento como si fuera un mensaje completo.

<details>
<summary>Pistas</summary>

- Acumulá en un `bytearray` y buscá `b"\n"` en un bucle, no una sola vez por `recv`.
- Lo que queda después del último `\n` es el comienzo del próximo mensaje: no lo tires.
- Variante: pasá a prefijo de largo con las funciones de §4.7 y compará cuál te resultó más simple.
</details>

### 🟡 Intermedio 1 — El tablero con SSE

Implementá `GET /v2/projects/{project_id}/board/events` con `EventSourceResponse` (FastAPI ≥ 0.135.0), alimentado por el **mismo** listener de `LISTEN/NOTIFY`. Vas a tener que extender `BoardHub` con `subscribe(project_id) -> asyncio.Queue` y `unsubscribe(...)`, y hacer que `publish` también ponga el evento en esas colas. Aplicá el mismo chequeo de rol que en el WebSocket.

**Sabés que lo lograste cuando…** con `curl -N "http://localhost:8000/v2/projects/1/board/events?user_id=1"` en dos terminales, un `PATCH` de estado aparece en las dos como una línea `data: {...}` con el JSON de `BoardEvent`. El WebSocket sigue funcionando al mismo tiempo, y `user_id=999` no recibe nada. Cerrá con un párrafo en TJ-008: ¿con cuál te quedás para TaskFlow y por qué?

<details>
<summary>Pistas</summary>

- Usá `asyncio.Queue(maxsize=100)` y `put_nowait`. Pensá qué hacés si la cola de un cliente está llena: es backpressure otra vez.
- El `finally` del generador es donde desuscribís. Si no, cada cliente que se va deja una cola huérfana.
- El `EventSource` del navegador tampoco deja poner headers propios: la identidad va por query, igual que en el WebSocket.
</details>

### 🟡 Intermedio 2 — Poison messages y dead-letter stream

Hacé que el worker **no reintente para siempre**. Si un mensaje ya se entregó 3 veces o más, se copia a `taskflow:events:dead` (con el `msg_id` original y el motivo), se le hace `XACK` en el stream principal y se loguea como error.

Para probarlo, forzá un poison message:

```bash
docker compose exec cache redis-cli XADD taskflow:events '*' event_id 999999 kind assigned task_id 42 project_id 1 old '' new no-es-un-numero
```

Con el worker del paso 5 tal como está, ese mensaje lo tira abajo (`ValueError: invalid literal for int()`), queda en la PEL y, al relanzarlo, `XAUTOCLAIM` se lo vuelve a entregar: el loop infinito que este ejercicio corta.

**Sabés que lo lograste cuando…** ese mensaje termina en `taskflow:events:dead` (`XRANGE taskflow:events:dead - +` lo muestra), `XPENDING taskflow:events notifier` vuelve a 0, el worker sigue procesando asignaciones normales y en el log queda una línea de error por el mensaje muerto.

<details>
<summary>Pistas</summary>

- `XPENDING` en su forma extendida (con rango `- +` y un `COUNT`) devuelve, por mensaje, cuántas veces se entregó. Buscá en redis-py el método equivalente.
- Con `min_idle_time=60_000`, cada reintento tarda un minuto. Para probar, bajalo temporalmente.
- Envolvé `handle` en un `try/except`. Si falla, **no** hagas ack: dejá que vuelva por `XAUTOCLAIM` y sume una entrega.
</details>

### 🔴 Desafío 1 — Del worker al servicio gRPC, con idempotencia de punta a punta

Reemplazá `send_email_fake` en `notify_worker.py` por una llamada a `NotificationService.Send` (paso 6), con `event_id` como clave de idempotencia y un deadline de 2 s. Después hacé que el servicio **persista** los `event_id` vistos (en un archivo o en una tabla propia) en lugar del `set` en memoria. Por último, agregá el RPC `Watch` (server streaming) y un script `watch_user.py 7` que imprima en vivo las notificaciones del usuario 7.

**Sabés que lo lograste cuando…**

- Con el servicio gRPC **apagado**, el worker no se cuelga: la llamada falla (`UNAVAILABLE` enseguida, o `DEADLINE_EXCEEDED` a los 2 s si usás `wait_for_ready=True`), el mensaje **no** recibe ack y se procesa cuando el servicio vuelve.
- Reiniciar el servicio gRPC y repetir el experimento 4 del paso 5 (duplicado forzado) no genera ningún email duplicado.
- `watch_user.py 7` muestra cada asignación al usuario 7 mientras ocurre.
- En TJ-008 agregaste una línea: ¿quién es ahora el dueño de la idempotencia, el worker o el servicio? ¿Hace falta en los dos?

<details>
<summary>Pistas</summary>

- Capturá `grpc.RpcError` e imprimí `e.code()` para distinguir "no hay servicio" (`UNAVAILABLE`), "no llegó a tiempo" (`DEADLINE_EXCEEDED`) y "el servicio contestó con error".
- Con `Watch`, el servidor hace `yield pb.Delivery(...)` y el cliente itera con `for d in stub.Watch(...)`. Necesitás que `Send` le avise a los `Watch` abiertos: una cola por suscriptor, igual que en el ejercicio de SSE.
- Si cambiás el `.proto`, **no** reuses números de campo.
</details>

### 🔴 Desafío 2 — Comentarios en vivo, design-first de punta a punta

Agregá a `/v2` el endpoint `POST /v2/tasks/{task_id}/comments`, siguiendo el ciclo completo de la sesión:

1. **Contrato primero** en `contracts/openapi-v2.yaml` (request, respuesta 201 y `operationId`). Lint y mock con Prism **antes** de escribir el endpoint.
2. **Implementación** en FastAPI y comparación contra el `openapi.json` generado.
3. **Evento:** que el comentario produzca un `task_events` de `kind` `commented` (payload: solo ids, **nunca** el cuerpo), que el tablero lo reciba por WebSocket y que la UI marque la tarjeta con un contador.
4. **Segundo consumidor:** un consumer group nuevo, `mentions`, con su propio worker, que detecte `@nombre` en el comentario (leyéndolo de la base por id) y "notifique" al mencionado, con idempotencia propia.
5. **Backpressure:** agregá un timeout por envío en `BoardHub.publish`, para que un cliente lento no frene a los demás.

**Sabés que lo lograste cuando…** el contrato está en un commit anterior al del endpoint, un comentario con `@Ana` aparece en vivo en el tablero de otro usuario y genera exactamente una notificación aunque reinicies el relay, `notifier` y `mentions` procesan el mismo stream sin interferir, y un test cubre el endpoint nuevo.

<details>
<summary>Pistas</summary>

- ¿Por qué el payload del evento no lleva el cuerpo del comentario? Repasá el límite de `NOTIFY` y la regla de S08.
- El trigger del evento `commented` es una migración a mano, como en el paso 4a.
- Para el timeout por envío, pensá en `asyncio.wait_for` alrededor de `send_json`, y en qué hacés con ese socket si vence.
- Dos consumer groups sobre el mismo stream es el fan-out persistente del experimento 3.
</details>

---

## 7. Ruta de estudio sugerida

El orden tiene dependencias reales: el versionado motiva el lab, y el tiempo real y las colas se apoyan en `task_events` de S08. Los tiempos son de lectura de cada recurso.

```mermaid
flowchart TD
    V1["1. AIP-180 · 15 min"] --> V2["2. Parallel Change · 8 min"]
    V2 --> V3["3. AIP-185 · 10 min"]
    V3 --> V4["4. RFC 9745 + RFC 8594 · 15 min"]
    V1 --> V5["5. Tolerant Reader · 5 min"]
    V3 --> D1["6. OpenAPI best practices · 10 min"]
    D1 --> D2["7. FastAPI First Steps + Generating SDKs · 15 min"]
    D2 --> D3["8. Redocly + Prism · 10 min"]
    V3 --> F1["9. FastAPI Bigger Apps + Sub Apps + Lifespan · 25 min"]
    F1 --> W1["10. RFC 6455 handshake · 15 min"]
    W1 --> W2["11. FastAPI WebSockets + Starlette · 30 min"]
    W2 --> W3["12. NOTIFY + psycopg async · 20 min"]
    W3 --> W4["13. MDN WebSocket + Testing WS · 15 min"]
    W4 --> W5["14. FastAPI SSE · 10 min"]
    W3 --> Q1["15. BackgroundTasks + Redis Pub/Sub · 20 min"]
    Q1 --> Q2["16. Redis Streams · 25 min"]
    Q2 --> Q3["17. Competing Consumers · 10 min"]
    Q3 --> Q4["18. RabbitMQ tutorial 2 · 20 min"]
    V1 --> G1["19. gRPC core concepts + proto3 · 35 min"]
    G1 --> G2["20. gRPC Python quickstart + basics · 50 min"]
    T1["21. RFC 9293 + RFC 768 · 20 min"] --> T2["22. Socket HOWTO + socket · 30 min"]
    T2 --> T3["23. RFC 9000 + RFC 9114 · 10 min"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class Q2 foco
```

**Cómo usarla:**

- **Antes de la clase (≈ 1 h):** 1–5 (versionado) y 21–22 (TCP/UDP). Es lo que la clase da por leído para ir directo al código.
- **Durante o justo después del taller (≈ 1 h 30 min):** 6–14, en el orden en que armás los pasos 1–4 del lab.
- **Para la práctica autónoma (≈ 1 h):** 15–18, con el worker del paso 5 abierto al lado.
- **Stretch (≈ 1 h 30 min):** 19–20 si hacés gRPC, y 23 como cierre de TCP/UDP.
- Stripe (15 min) es lectura de contraste: cuando termines el bloque de versionado. AsyncAPI (10 min), cuando hayas escrito `BoardEvent`.

---

## 8. Checklist de autoevaluación

- [ ] Puedo explicar la diferencia entre design-first y code-first, y por qué con FastAPI el design-first necesita un paso de comparación contra `/openapi.json`.
- [ ] Puedo clasificar un cambio de API como compatible o incompatible citando la regla (renombrar = quitar + agregar, cambio de tipo, nuevo obligatorio en request) sin mirar los apuntes.
- [ ] Puedo explicar por qué `/v1` es un adaptador del dominio nuevo y no al revés, y escribir los headers `Deprecation` y `Sunset` con el formato correcto de cada uno.
- [ ] Puedo describir el handshake de WebSocket (`Upgrade` → `101`) y por qué vive en el mismo puerto que la API.
- [ ] Puedo explicar por qué el `ConnectionManager` en memoria falla con `--workers 2` y cómo lo resuelve `LISTEN/NOTIFY`.
- [ ] Puedo decir cuándo alcanza SSE y cuándo hace falta WebSocket para el tablero de TaskFlow.
- [ ] Puedo explicar qué es un dual write, por qué `task_events` funciona como outbox y qué hace el relay.
- [ ] Puedo recorrer el worker y decir qué pasa si muere en cada línea (antes de enviar, entre enviar y registrar, antes del ack), y por qué el orden es enviar → registrar → ack.
- [ ] Puedo explicar por qué en protobuf renombrar un campo no rompe el wire pero reusar su número sí.
- [ ] Puedo mostrar con `socket` que TCP no respeta los límites entre mensajes y que UDP no avisa si un datagrama se perdió.

---

## 9. Preguntas de repaso

1. Tu equipo quiere cambiar `assignee` (string) por `assignee_id` (int) en la API de TaskFlow, que ya consumen la UI y dos scripts de otros equipos. Contá las dos estrategias posibles (versión nueva vs evolucionar en el lugar con parallel change), qué hace cada una con los clientes existentes y cuál elegirías según cuántos clientes tenés y cuánto los controlás.
2. Un compañero implementó el tablero en vivo con una lista de WebSockets en memoria, y en local anda perfecto. En producción, con dos workers de Uvicorn, "a veces" no llegan las actualizaciones. Explicá por qué, cómo lo diagnosticarías y dos formas de resolverlo con sus costos.
3. ¿Por qué el worker de notificaciones de TaskFlow tiene que ser idempotente aunque uses una cola "confiable"? Recorré todos los puntos del camino (trigger, relay, stream, worker) donde un mensaje se puede duplicar, y explicá qué significa "exactly-once efectivo".
4. El tablero usa `LISTEN/NOTIFY`, que es at-most-once, y el email usa Redis Streams, que es at-least-once. ¿Por qué no usar la misma herramienta para los dos? ¿Qué hace el cliente del tablero para tolerar la pérdida de eventos?
5. Te proponen exponer el servicio de notificaciones por gRPC directamente al frontend "porque es más rápido que JSON". ¿Qué respondés? Incluí qué transporte usa gRPC, qué implica para el navegador, y cómo cambia la noción de "breaking change" entre JSON y protobuf.

---

## 10. Recursos adicionales

### Imprescindibles

- [AIP-180: Backwards compatibility — Google](https://google.aip.dev/180) · 15 min. Qué rompe y qué no.
- [AIP-185: API Versioning — Google](https://google.aip.dev/185) · 10 min. Versión mayor en el path.
- [Parallel Change — Danilo Sato (martinfowler.com)](https://martinfowler.com/bliki/ParallelChange.html) · 8 min. Expand, migrate, contract.
- [Best Practices — OpenAPI Initiative](https://learn.openapis.org/best-practices.html) · 10 min. Design-first vs code-first.
- [WebSockets — FastAPI](https://fastapi.tiangolo.com/advanced/websockets/) · 20 min + práctica.
- [NOTIFY — PostgreSQL 16](https://www.postgresql.org/docs/16/sql-notify.html) · 10 min.
- [Asynchronous operations / notifications — psycopg 3](https://www.psycopg.org/psycopg3/docs/advanced/async.html) · 10 min.
- [Redis Streams — Redis docs](https://redis.io/docs/latest/develop/data-types/streams/) · 25 min.
- [Background Tasks — FastAPI](https://fastapi.tiangolo.com/tutorial/background-tasks/) · 10 min.
- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html) · 20 min.

### Recomendados

- [Tolerant Reader — Martin Fowler](https://martinfowler.com/bliki/TolerantReader.html) · 5 min.
- [RFC 9745 — The Deprecation HTTP Response Header Field](https://www.rfc-editor.org/rfc/rfc9745) · 10 min (secciones 2–4).
- [RFC 8594 — The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594) · 5 min.
- [Bigger Applications - Multiple Files — FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/) · 15 min (solo `include_router`).
- [Sub Applications - Mounts — FastAPI](https://fastapi.tiangolo.com/advanced/sub-applications/) · 5 min.
- [Lifespan Events — FastAPI](https://fastapi.tiangolo.com/advanced/events/) · 5 min.
- [First Steps — FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/) · 5 min (la parte de OpenAPI).
- [Redocly CLI — Installation](https://redocly.com/docs/cli/installation) · [comando `lint`](https://redocly.com/docs/cli/commands/lint) · 5 min.
- [Prism — Stoplight](https://github.com/stoplightio/prism) · 5 min.
- [RFC 6455 — The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455) · 15 min (abstract + handshake).
- [WebSockets — Starlette](https://starlette.dev/websockets/) · 10 min.
- [Testing WebSockets — FastAPI](https://fastapi.tiangolo.com/advanced/testing-websockets/) · 5 min.
- [WebSocket — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) · 10 min.
- [Server-Sent Events (SSE) — FastAPI](https://fastapi.tiangolo.com/tutorial/server-sent-events/) · 10 min.
- [Redis Pub/Sub — Redis docs](https://redis.io/docs/latest/develop/pubsub/) · 10 min (sección *Delivery semantics*).
- [redis-py guide — Redis docs](https://redis.io/docs/latest/develop/clients/redis-py/) · 5 min.
- [Competing Consumers — Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CompetingConsumers.html) · 10 min.
- [Core concepts, architecture and lifecycle — gRPC](https://grpc.io/docs/what-is-grpc/core-concepts/) · 15 min.
- [Language Guide (proto 3) — Protocol Buffers](https://protobuf.dev/programming-guides/proto3/) · 20 min (field numbers, `reserved`, *Updating a message type*).
- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293) · 15 min (abstract + sección 2).
- [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768) · 5 min.
- [socket — Low-level networking interface (Python docs)](https://docs.python.org/3/library/socket.html) · consulta 10 min.
- Andrew Ng, *AI Engineering Skills Map: Software engineering fundamentals* (The Batch, 2026), sección *Building full-stack applications* · 5 min.

### Opcionales

- [APIs as infrastructure: future-proofing Stripe with versioning — Brandur Leach (Stripe)](https://stripe.com/blog/api-versioning) · 15 min. El contraejemplo del versionado en el path.
- [Generating SDKs — FastAPI](https://fastapi.tiangolo.com/advanced/generate-clients/) · 10 min.
- [OpenAPI Specification — latest](https://spec.openapis.org/oas/latest.html) · consulta puntual.
- [AsyncAPI Document — AsyncAPI Initiative](https://www.asyncapi.com/docs/concepts/asyncapi-document) · 10 min.
- [broadcaster — encode (GitHub, archivado)](https://github.com/encode/broadcaster) · 5 min.
- [websockets — documentación (Python)](https://websockets.readthedocs.io/en/stable/) · 5 min.
- [RabbitMQ tutorial 2 — Work Queues (Python)](https://www.rabbitmq.com/tutorials/tutorial-two-python) · 20 min + 30 min de práctica.
- [rabbitmq — imagen oficial (Docker Hub)](https://hub.docker.com/_/rabbitmq) · consulta 5 min.
- [Quick start — gRPC Python](https://grpc.io/docs/languages/python/quickstart/) · práctica 20 min.
- [Basics tutorial — gRPC Python](https://grpc.io/docs/languages/python/basics/) · 30 min.
- [gRPC over HTTP2 — especificación del protocolo](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md) · consulta 5 min.
- [Basics tutorial — gRPC-Web](https://grpc.io/docs/platforms/web/basics/) · 10 min (sección de proxy).
- [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000) · 5 min (abstract).
- [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114) · 5 min (abstract y §3.1).
