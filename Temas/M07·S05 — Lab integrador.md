# M07·S05 — Lab integrador + kickoff de TaskFlow

**Módulo:** 07 — Fundamentos de Software + System Design para AI Engineers **Fecha:** [Completar por el profesor: fecha] **Duración estimada de estudio:** ~7 horas en total: lectura de recursos (~2,5 h) y ejercicios sobre PostgreSQL en Docker (~4,5 h, preparación incluida). La guía práctica se hace en el lab en equipo, dentro de las 3 horas de la sesión en clase.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Construir**, dirigiendo al agente de código, el prototipo mínimo de TaskFlow: un webserver FastAPI en capas con tres endpoints (crear, listar con filtro, mover de estado) y **verificar** con tests que hace lo que pediste.
2. **Implementar** una regla de negocio —qué transiciones de estado son válidas— en la capa service, sin que el service importe nada de FastAPI, y **traducirla** a códigos HTTP (201, 404, 409, 422) en el router.
3. **Intercambiar** la persistencia de un `dict` en memoria a SQLite cambiando una variable de entorno, **sin tocar** ni el service ni el router, y explicar por qué eso justifica la capa repository.
4. **Servir** un cliente simple (HTML + `fetch`) desde el mismo FastAPI y explicar cuándo haría falta CORS y cuándo no.
5. **Diagramar** lo que construiste: diagrama de componentes del webserver y diagrama de secuencia del ciclo de request de "mover tarea", coherentes con el código.
6. **Registrar** tres decisiones del prototipo en el trade-off journal, cada una con la alternativa que descartaste y qué te haría cambiar de idea.

---

## 2. Resumen ejecutivo

Hasta ahora, cada sesión de la semana 1 te dio una pieza suelta. En **M07·S01** arrancaste el trade-off journal y viste que dirigir a un agente es explicitar decisiones; en **M07·S02** recorriste una petición de punta a punta; en **M07·S03** levantaste tu primer webserver con FastAPI, Pydantic y Uvicorn; y en **M07·S04** lo partiste en capas (router → service → repository) con `Depends`, `APIRouter` y un middleware, y lo conectaste a PostgreSQL levantado con Docker Compose. Hoy no aprendés componentes nuevos de FastAPI: **los integrás en un proyecto real que vive las próximas tres semanas**.

Ese proyecto es **TaskFlow**, una API de gestión de tareas para equipos, tipo mini-Trello. No tiene ningún componente de IA a propósito: así toda la atención queda en los fundamentos —datos, capas, contratos, verificación—, que son exactamente lo que un AI Engineer necesita dominar para que el agente de código no tome malas decisiones por él.

La idea fuerte de la sesión es una sola: **la capa repository se justifica cuando cambiás la persistencia sin tocar nada más**. Vas a arrancar con un `dict` en memoria, pasar a SQLite con una variable de entorno y comprobar con `git status` que el service y el router quedaron intactos. La segunda idea es de ubicación: **la regla de negocio vive en el service**, no en el router ni en el front.

El prototipo es deliberadamente chico. La arquitectura correcta cambia con la fase del proyecto, y por eso TaskFlow arranca **sin** el Postgres de S04: un `dict` y un archivo SQLite alcanzan para la fase 1 y no le suman Docker ni un servidor de base al arranque de nadie del equipo. Los cambios ya están agendados: PostgreSQL vuelve en S07 (ahora con el ORM de SQLAlchemy y migraciones), auth y roles en S14–S15, deploy en S16–S17.

---

## 3. Conceptos clave / glosario

Solo los términos **nuevos** de hoy. Lo ya visto se refresca en una línea al final.

**El proyecto y su arquitectura**

- **TaskFlow:** el proyecto del módulo: API de gestión de tareas para equipos (tareas que se mueven entre `backlog`, `in_progress` y `done`). Crece fase por fase hasta la defensa en S20. _Analogía:_ un Trello en miniatura que vas a ir reformando cada semana.
- **Prototipo mínimo (_walking skeleton_):** la versión más fina posible del sistema que ya atraviesa **todas** las capas —UI → API → service → repository → almacén— aunque cada una haga muy poco. Se engorda después; lo que no se hace es construir una capa entera antes de conectar la siguiente. _Analogía:_ un esqueleto que ya camina: le faltan músculos, pero todas las articulaciones están.
- **Puerto y adaptador:** el **puerto** es la interfaz de lo que el service necesita (`TaskRepository`); los **adaptadores** son las implementaciones concretas (`InMemoryTaskRepository`, `SqliteTaskRepository`). El service solo conoce el puerto. _Analogía:_ el enchufe de la pared: no le importa si enchufás una lámpara o un cargador.
- **`typing.Protocol`:** forma de declarar una interfaz en Python por estructura: cualquier clase que tenga esos métodos con esas firmas "cumple" el protocolo, sin heredar de nada. _Analogía:_ un contrato que se cumple por lo que hacés, no por cómo te llamás.

**Regla de negocio y contrato HTTP**

- **Tabla de transiciones:** un diccionario que dice, para cada estado, a qué estados se puede pasar. Es la máquina de estados de la tarea escrita como dato. _Analogía:_ el mapa de subte: desde cada estación, a cuáles podés ir directo.
- **409 Conflict:** código HTTP que indica que el request entra en conflicto con el **estado actual** del recurso. Distinto del 422, que dice que el request está mal formado. _Analogía:_ "Tu pedido está bien escrito, pero ahora mismo no se puede."

**Tests**

- **Fixture (pytest):** función marcada con `@pytest.fixture` que prepara algo que un test pide por nombre de parámetro; si usa `yield`, lo de después limpia. _Analogía:_ la mise en place de cada test.
- **`dependency_overrides`:** diccionario de la app de FastAPI donde decís "cuando alguien pida la dependencia X, dale Y". Se usa en tests para inyectar un repositorio limpio. _Analogía:_ cambiarle la pieza al motor sin desarmar el auto.

**Persistencia y cliente**

- **Placeholder SQL (`?`):** marcador en una consulta SQL que el driver reemplaza por un valor de forma segura. Evita SQL injection. _Analogía:_ un formulario con casilleros: el valor nunca se mezcla con el texto de la consulta.
- **Mismo origen:** dos URLs tienen el mismo origen si coinciden protocolo, dominio y puerto. Si tu HTML y tu API comparten origen, no hace falta CORS. _Analogía:_ vivir en el mismo edificio: no necesitás pasar por portería.

**Ya vistos, solo como refresco:** `Depends`, `Annotated` y dependencias con `yield` (M07·S04, `get_db`); `APIRouter` con `prefix` y `tags` (M07·S04, un router por recurso); capas router → service → repository y regla de dependencia de Clean Architecture (M07·S04); excepciones de dominio que el router traduce a HTTP, como `EmailAlreadyRegistered` → 409 (M07·S04); `lifespan` para preparar recursos al arrancar (M07·S04); rutas `def` en el threadpool vs `async def` (M07·S04); middleware (M07·S04); plan mode y explore → plan → implement → commit (M07·S01, y `CLAUDE.md` en MA·S04); trade-off journal y formato `TJ-NNN` (M07·S01); máquina de estados y diagrama de componentes C4 (MA·S05); tablero Kanban con columnas de estado (MA·S06); `/docs` como cliente (M07·S03).

---

## 4. Notas de estudio por subtema

### El mapa de lo que vas a construir

Este es el diagrama ancla de la sesión. Todo lo que sigue es una caja de este dibujo:

```mermaid
flowchart LR
    NAV["Navegador<br/>(index.html o /docs)"] --> UV["Uvicorn"]
    UV --> RT
    subgraph WS["Webserver FastAPI"]
        RT["routes/tasks.py"] --> SV["TaskService"]
        SV --> PR["TaskRepository (Protocol)"]
        DEPS["dependencies.py"] -.->|"elige según TASKFLOW_STORAGE"| PR
        PR -->|"implementa"| MEM["InMemoryTaskRepository"]
        PR -->|"implementa"| SQL["SqliteTaskRepository"]
    end
    MEM --> DICT["dict en el proceso"]
    SQL --> DB[("taskflow.db")]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class PR foco
```

El nodo resaltado es el **punto de intercambio**: el service habla con un `Protocol`, y `dependencies.py` decide qué adaptador enchufa. Si entendés por qué esa caja existe, entendiste la sesión.

---

### 4.1 Kickoff de TaskFlow: dominio, recorte y arquitectura como blanco móvil

**El dominio completo.** TaskFlow, tal como lo define el plan del módulo, tiene seis entidades (Usuario, Equipo, Proyecto, Tarea, Comentario, Etiqueta), roles por proyecto (owner, member, viewer) y una funcionalidad núcleo: registro/login, CRUD de proyectos y tareas, mover una tarea de estado, asignar responsable, comentar y listar el tablero con filtros, orden y paginación.

**El recorte de hoy.** Del dominio completo, el prototipo de hoy toma **una sola entidad**: la `Tarea`.

|Entra hoy|Queda para después|
|---|---|
|`Tarea` con `id`, `title`, `description`, `assignee` (string libre), `status`, `created_at`|Usuario, Equipo, Proyecto, Comentario, Etiqueta → modelo ER en S07|
|Crear, listar con filtro por estado, mover de estado|Paginación y orden → S10|
|Persistencia en memoria o SQLite|PostgreSQL → S07|
|Sin login|Auth y roles → S14–S15|

¿Por qué tan poco? Porque, como plantea Andrew Ng en su _AI Engineering Skills Map_ (2026), **la arquitectura correcta es un blanco móvil que depende de la fase del proyecto**: la de un prototipo rápido puede no servir para el primer sistema en producción, y eso está bien. Lo de hoy no es "hacerlo mal": es la arquitectura de la fase 1.

Pero ojo con la otra mitad de la misma idea: Ng también señala que **los datos son la base del software y son relativamente difíciles de cambiar**, aun con agentes ayudando en las migraciones. Por eso, aunque la persistencia de hoy sea descartable, el **modelo** de la tarea merece pensarse bien. Este es el contrato que vas a sostener por semanas:

```python
# app/schemas.py (extracto) — la Tarea que sale del servidor
class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    assignee: str | None = None      # string libre hoy; FK a Usuario en S07
    status: TaskStatus               # backlog | in_progress | done
    created_at: datetime
```

**Los estados.** Son los de un tablero Kanban (MA·S06): `backlog`, `in_progress`, `done`. En el código van en inglés; en la UI, en castellano. Cuáles transiciones valen lo vas a decidir en 4.7.

> ⚠️ **Error común:** "prototipo mínimo" no es "una sola capa". El error típico es meter todo en `main.py` porque "total es un prototipo". El prototipo es chico en **funcionalidad**, no en **estructura**: tiene que tener las capas desde el primer commit, porque es lo que vas a extender tres semanas.

> 📝 **Nota para el profesor:** el recorte (solo `Tarea`, sin `due_date` ni etiquetas, `assignee` como string) es la propuesta del material. Si preferís arrancar con Proyecto → Tarea, conviene avisarlo antes del lab porque cambia el prompt y los tests.

---

### 4.2 Dirigir al agente para levantar el prototipo

Ya conocés plan mode y `CLAUDE.md` (M07·S01, MA·S04). Hoy los aplicás a un repo de equipo, con tres reglas prácticas que salen de la guía oficial _Best practices for Claude Code_:

**1. Un `CLAUDE.md` corto, con lo que el agente no puede adivinar.** La guía advierte que un `CLAUDE.md` demasiado largo hace que el agente ignore instrucciones, y recomienda incluir comandos que no puede adivinar, decisiones de arquitectura propias del proyecto e instrucciones de testing. El de TaskFlow está completo en la guía práctica (paso 3): comandos, capas "no negociables" y alcance de la fase.

**2. Explore → plan → implement → commit.** Primero le pedís un plan en plan mode (`Shift+Tab`, o arrancando con `claude --permission-mode plan`; `Ctrl+G` abre el plan en tu editor para corregirlo). Recién cuando el plan tiene los archivos que esperás, lo dejás implementar.

**3. Darle una verificación que pueda correr.** Es la regla más importante. La guía lo dice sin vueltas: sin un chequeo que el agente pueda correr, _"you become the verification loop"_ — vos pasás a ser el que prueba todo a mano. Por eso el prompt de implementación termina siempre con "corré los tests y arreglá lo que falle". Y los tests son, literalmente, la especificación que le das:

```python
# tests/test_tasks.py (extracto) — esto es lo que el agente tiene que hacer pasar
def test_invalid_move_returns_409(client):
    task_id = client.post("/tasks/", json={"title": "A"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    assert r.status_code == 409          # backlog -> done directo no vale
```

Si el agente te dice "listo" y este test no pasa, no está listo.

**Organización del equipo.** Es la primera sesión en equipo del módulo. Un integrante crea el repo `taskflow` en GitHub y los demás lo clonan; cada uno trabaja en una rama y se integra por PR (Git y GitHub los viste en M01). Con un agente por integrante, lo que más rompe es que dos agentes toquen el mismo archivo a la vez: repartan por **capa** o por **paso** del lab, no "todos hacen todo".

> ⚠️ **Error común:** los checkpoints de Claude Code solo registran los cambios hechos con sus herramientas de edición, **no** los que hizo por Bash, y no reemplazan a git. Commiteá después de cada paso que funcione.

> ⚠️ **Error común — el _trust-then-verify gap_:** el agente genera algo que "parece andar" en `/docs` y lo aceptás. Síntomas típicos en este lab: el service importa `HTTPException`, la regla de transiciones quedó en el router, o aparece `@app.on_event("startup")` (deprecado). Revisá contra el `CLAUDE.md`, no contra tu intuición.

📎 Para profundizar: [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) — secciones "Give Claude a way to verify its work", "Explore first, then plan, then code" y "Write an effective CLAUDE.md".

---

### 4.3 Estructura del proyecto en capas

El árbol sigue el patrón de _Bigger Applications_ de la doc de FastAPI, extendido con las capas de S04:

```text
taskflow/
├── CLAUDE.md
├── requirements.txt            # dependencias, como en S04
├── app/
│   ├── __init__.py
│   ├── main.py                 # arma la app: routers, estáticos, lifespan
│   ├── schemas.py              # el contrato (Pydantic)
│   ├── dependencies.py         # quién arma el service y qué repository usa
│   ├── routes/tasks.py         # capa HTTP
│   ├── services/task_service.py# reglas de negocio
│   └── repositories/
│       ├── base.py             # el puerto (Protocol)
│       ├── memory.py           # adaptador: dict
│       └── sqlite.py           # adaptador: SQLite
├── static/index.html           # UI mínima
├── tests/test_tasks.py
└── docs/
    ├── diagramas/
    └── tradeoff-journal.md
```

**Qué cambia respecto de `webserver-fastapi/` (S04).** Las capas son las mismas; algunas formas cambian, y cada cambio tiene un motivo:

|En S04|En TaskFlow|Por qué|
|---|---|---|
|`routes/user.py`|`app/routes/tasks.py`|Igual: un router por recurso. Ahora todo vive dentro del paquete `app/`, así que los imports son relativos.|
|`schemas/user.py`|`app/schemas.py`|Hay una sola entidad; cuando haya más, se parte en un paquete como en S04.|
|`repositories/user_repository.py` (funciones)|`repositories/base.py` + un adaptador por almacén (clases)|Hoy hay **dos** almacenes intercambiables y hace falta un contrato común: el `Protocol`.|
|`get_db` en `repositories/db.py` (entrega una conexión)|`get_repository` + `get_task_service` en `app/dependencies.py`|Se inyecta el service ya armado, no la conexión: el router no sabe qué almacén hay abajo.|
|`config/db.py` + `models/user.py` (SQLAlchemy Core sobre Postgres)|`sqlite3` de la stdlib en `repositories/sqlite.py`|Fase 1: sin Docker ni servidor de base. SQLAlchemy y Postgres vuelven en S07.|
|Middleware `X-Process-Time`|—|Hoy no hace falta. Si lo querés, se copia tal cual a `app/main.py`.|

**La regla de dependencia (S04), aplicada:** `routes → services → repositories`. Las flechas van en un solo sentido:

- `routes/` conoce HTTP y conoce al service. No toca repositories.
- `services/` conoce el puerto (`TaskRepository`) y los schemas. **No importa nada de FastAPI.**
- `repositories/` conoce su almacén. No sabe que existe HTTP.

`main.py` es el único lugar que junta todo (la _composition root_): crea la app, monta el router y, más adelante, los estáticos y el lifespan.

```python
# app/main.py (versión final)
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .dependencies import DB_PATH, STORAGE
from .repositories.sqlite import init_db
from .routes import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    if STORAGE == "sqlite":
        init_db(DB_PATH)          # crea la tabla al arrancar
    yield                         # acá la app atiende requests; lo de abajo corre al apagar


app = FastAPI(title="TaskFlow", lifespan=lifespan)
app.include_router(tasks.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
```

Tres cosas para mirar en este archivo:

- **`lifespan`** es el lugar correcto para inicializar recursos al arrancar (en S04 lo usaste para `create_all` y `dispose`). Si el agente te genera `@app.on_event("startup")`, está usando una API deprecada: pedile que lo pase a `lifespan`.
- **Imports relativos** (`.dependencies`, `..schemas`): funcionan porque `app/` es un paquete (tiene `__init__.py`) y corrés desde la raíz con `app.main:app`.
- **`StaticFiles(directory="static")`** resuelve la ruta relativa al directorio desde donde corrés el servidor. Si la carpeta no existe ahí, la app no arranca.

> ⚠️ **Error común:** falta un `__init__.py` en `routes/`, `services/` o `repositories/` y los imports relativos fallan con errores confusos. Creálos todos en el paso 2 de la guía, aunque estén vacíos.

📎 Para profundizar: [Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/) · [Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

---

### 4.4 El contrato de datos: modelos Pydantic, el estado como Enum y los códigos

El contrato es lo que la API promete hacia afuera. En TaskFlow son **tres modelos para una entidad**, un patrón que la doc de FastAPI explica en _Extra Models_:

```python
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):          # en Python >= 3.11 equivale a: class TaskStatus(StrEnum)
    backlog = "backlog"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):          # lo que manda el cliente
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    assignee: str | None = None


class TaskStatusUpdate(BaseModel):    # body de "mover de estado"
    status: TaskStatus


class TaskOut(BaseModel):             # lo que devuelve el servidor
    id: int
    title: str
    description: str | None = None
    assignee: str | None = None
    status: TaskStatus
    created_at: datetime
```

**Por qué tres modelos y no uno.** `TaskCreate` no tiene `id`, `status` ni `created_at` porque **los decide el servidor**: toda tarea nace en `backlog`, el id lo asigna el almacén y la fecha la pone el servidor. Si usaras un solo modelo, el cliente podría mandar `"status": "done"` al crear y saltearse la regla de negocio. Separar entrada y salida es cerrar esa puerta en el contrato. (Es el mismo patrón de `UserCreate` / `UserRead` en S04: ahí evitaba devolver el hash de la contraseña, y en S14 va a cumplir ese rol con los usuarios de TaskFlow.)

**El estado como `Enum`.** Un `Enum` que hereda de `str` define un conjunto cerrado de valores. Te da tres cosas gratis: un estado inválido (`"archivada"`) se rechaza con **422** sin escribir validación, el JSON lo devuelve como string, y Swagger muestra un desplegable con los tres estados. `StrEnum` (agregado en Python 3.11) es equivalente; usamos `(str, Enum)` porque funciona en cualquier versión.

**`Field(min_length=1, max_length=200)`**: el título no puede ser vacío ni infinito, y eso queda en el contrato, no en un `if` perdido.

**Los cuatro códigos de hoy:**

|Código|Cuándo|Quién lo produce|
|---|---|---|
|**201 Created**|`POST /tasks/` creó la tarea|`status_code=201` en el decorador|
|**404 Not Found**|La tarea no existe|El router, al atrapar `TaskNotFound`|
|**409 Conflict**|La transición no es válida desde el estado actual|El router, al atrapar `InvalidTransition`|
|**422 Unprocessable**|Body mal formado o estado fuera del `Enum`|FastAPI, automáticamente|

**409 vs 422, la distinción que importa.** Mandar `{"status": "done"}` a una tarea en `backlog` es un request **válido**: el JSON está bien y `done` es un estado que existe. El problema es el **estado actual** de la tarea. Eso es exactamente lo que define el 409 (conflicto con el estado actual del recurso). El 422 queda para "no entiendo lo que me mandaste". Tenerlos separados le dice al cliente si tiene que corregir el request o esperar/cambiar el estado.

> ⚠️ **Error común:** si declarás el retorno como `-> TaskOut`, FastAPI **filtra** la salida a los campos de `TaskOut`. Es una feature (contrato explícito, OpenAPI correcto), pero si agregás un campo al repositorio y no al modelo, no va a aparecer en la respuesta y vas a pensar que no se guardó.

📎 Para profundizar: [Path Parameters — Predefined values](https://fastapi.tiangolo.com/tutorial/path-params/) · [Extra Models](https://fastapi.tiangolo.com/tutorial/extra-models/) · [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) · [Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/) · [409 Conflict — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/409) · [Fields — Pydantic](https://pydantic.dev/docs/validation/latest/concepts/fields/)

---

### 4.5 Persistencia intercambiable: memoria vs SQLite

**El puerto.** Primero se escribe lo que el service necesita, sin decir cómo se hace:

```python
# app/repositories/base.py
from typing import Protocol

from ..schemas import TaskCreate, TaskOut, TaskStatus


class TaskRepository(Protocol):
    def add(self, data: TaskCreate) -> TaskOut: ...
    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskOut]: ...
    def get(self, task_id: int) -> TaskOut | None: ...
    def update_status(self, task_id: int, status: TaskStatus) -> TaskOut: ...
```

Un `Protocol` no se hereda: cualquier clase con esos cuatro métodos lo cumple. Es el mismo principio de Clean Architecture que viste en S04 (el caso de uso depende de una abstracción), en su versión más liviana de Python.

**Adaptador 1: un `dict`.** Cero setup, ideal para arrancar:

```python
# app/repositories/memory.py (extracto)
class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskOut] = {}
        self._ids = count(1)
        self._lock = Lock()             # las rutas def corren en un threadpool (S04)

    def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
        with self._lock:
            task = self._tasks[task_id].model_copy(update={"status": status})
            self._tasks[task_id] = task
            return task
```

¿Por qué un `Lock`? Porque las rutas `def` de FastAPI corren en un threadpool (S04): dos requests pueden llegar al mismo tiempo en hilos distintos, y sin lock podrían pisarse al generar ids o al escribir.

**Adaptador 2: SQLite con `sqlite3` de la stdlib.** A propósito sin SQLAlchemy: en S04 las consultas las armaba SQLAlchemy Core (`select(users).where(...)`); acá escribís el SQL vos, para ver exactamente qué encapsula el repository. SQLAlchemy vuelve en S07, ya con el ORM y sobre PostgreSQL.

```python
# app/repositories/sqlite.py (extracto)
def get(self, task_id: int) -> TaskOut | None:
    row = self.con.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return TaskOut(**dict(row)) if row else None

def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
    with self.con:                                  # commit si sale bien, rollback si no
        self.con.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (status.value, task_id)
        )
    return self.get(task_id)
```

Cuatro detalles que la doc de `sqlite3` deja claros y que el agente suele equivocar:

- **Placeholders `?`, siempre.** La doc lo dice textual: _"Always use placeholders instead of string formatting to bind Python values to SQL statements, to avoid SQL injection attacks."_ Nunca `f"... WHERE id = {task_id}"`.
- **`with self.con:`** hace commit si el bloque sale bien y rollback si hay excepción (lo mismo que `engine.begin()` en el `get_db` de S04, pero por operación y no por request), pero **no cierra la conexión**. La cierra la dependencia (4.6).
- **`row_factory = sqlite3.Row`** te deja acceder por nombre de columna; `dict(row)` → `TaskOut(**...)` funciona porque las columnas se llaman igual que los campos. Pydantic convierte el `created_at` ISO a `datetime` y el string de `status` a `TaskStatus`.
- **`lastrowid`** te da el id que SQLite asignó en el `INSERT`. Es lo que la tabla "Qué cambia respecto de SQLite" de S04 contrastaba con el `INSERT ... RETURNING` de Postgres.

**Memoria vs SQLite: cuándo alcanza cada una.** La doc oficial de SQLite es muy honesta: SQLite no compite con las bases cliente/servidor sino con `fopen()`; un sitio con menos de 100K hits por día debería andar bien con SQLite; y admite **un solo escritor a la vez** por archivo. Para el prototipo sobra. TaskFlow la va a dejar no porque sea "de juguete", sino porque va a tener varios usuarios escribiendo a la vez y más de un proceso de servidor (S12–S13).

> ⚠️ **Error común — la trampa de `":memory:"`:** SQLite tiene bases en memoria (`sqlite3.connect(":memory:")`), pero **cada conexión a `":memory:"` crea una base distinta**, que desaparece al cerrarla. Como TaskFlow abre una conexión por request, cada request vería una base vacía. Por eso "memoria" en TaskFlow es un `dict`, y SQLite va siempre a archivo (`taskflow.db`).

📎 Para profundizar: [`sqlite3` — DB-API 2.0](https://docs.python.org/3/library/sqlite3.html) · [In-Memory Databases](https://www.sqlite.org/inmemorydb.html) · [Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html)

---

### 4.6 El punto de intercambio: `dependencies.py`

Este archivo es el nodo resaltado del diagrama ancla. Es donde se decide qué adaptador recibe el service, y por eso es lo único que cambia cuando cambiás de persistencia:

```python
# app/dependencies.py (versión final)
import os
import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends

from .repositories.base import TaskRepository
from .repositories.memory import InMemoryTaskRepository
from .repositories.sqlite import SqliteTaskRepository
from .services.task_service import TaskService

STORAGE = os.getenv("TASKFLOW_STORAGE", "memory")     # "memory" | "sqlite"
DB_PATH = os.getenv("TASKFLOW_DB", "taskflow.db")

_memory_repo = InMemoryTaskRepository()               # una sola instancia por proceso


def get_repository() -> Iterator[TaskRepository]:
    if STORAGE == "sqlite":
        con = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            yield SqliteTaskRepository(con)
        finally:
            con.close()
    else:
        yield _memory_repo


def get_task_service(
    repo: Annotated[TaskRepository, Depends(get_repository)],
) -> TaskService:
    return TaskService(repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
```

**La cadena de dependencias:** `get_repository` → `get_task_service` → endpoint. El endpoint pide un `TaskServiceDep`; FastAPI ve que para armarlo necesita un repository, llama a `get_repository`, y arma todo por request. Es la idea de `get_db` de S04 un nivel más arriba: allá la dependencia entregaba una conexión y el router se la pasaba a mano al service y al repository; acá la cadena de `Depends` entrega el service ya armado con su repository.

**Dependencia con `yield`:** lo de antes del `yield` corre antes del endpoint (abrir la conexión); lo de después, por defecto, corre después de enviar la respuesta (cerrarla). El `try/finally` garantiza que se cierre aunque el endpoint explote.

**`check_same_thread=False`:** por defecto, una conexión de `sqlite3` solo se puede usar desde el hilo que la creó. Es el parámetro que la tabla SQLite vs PostgreSQL de S04 marcaba como obligatorio en SQLite. La doc de FastAPI explica por qué hace falta relajarlo: un mismo request puede usar más de un hilo (por ejemplo, en las dependencias). No es peligroso acá porque la conexión sigue siendo **una por request**: no se comparte entre requests concurrentes.

**`_memory_repo` a nivel de módulo:** si lo crearas dentro de `get_repository`, cada request tendría un `dict` nuevo y vacío. Tiene que vivir lo que vive el proceso.

> ⚠️ **Error común:** `STORAGE` se lee **una vez, al importar el módulo**. Cambiar la variable de entorno con el servidor corriendo no hace nada: hay que reiniciarlo.

📎 Para profundizar: [Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/) · [SQL (Relational) Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) (solo "Create an Engine" y "Create a Session Dependency")

---

### 4.7 Los tres endpoints y la regla de negocio

**Primero se dibuja la regla.** El plan del módulo pide dibujar antes de codear. La máquina de estados de una tarea (el concepto lo viste en MA·S05) es esta:

```mermaid
stateDiagram-v2
    [*] --> backlog: crear
    backlog --> in_progress: empezar
    in_progress --> backlog: devolver
    in_progress --> done: terminar
    done --> in_progress: reabrir
```

Lo que **no** está dibujado está prohibido: `backlog → done` directo, `done → backlog`, y quedarse en el mismo estado.

**Después se traduce a código, en el service.** El diagrama se convierte en un diccionario, y la regla en un `if`:

```python
# app/services/task_service.py
from ..repositories.base import TaskRepository
from ..schemas import TaskCreate, TaskOut, TaskStatus

ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.backlog: {TaskStatus.in_progress},
    TaskStatus.in_progress: {TaskStatus.backlog, TaskStatus.done},
    TaskStatus.done: {TaskStatus.in_progress},        # reabrir
}


class TaskNotFound(Exception):
    pass


class InvalidTransition(Exception):
    pass


class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    def create(self, data: TaskCreate) -> TaskOut:
        return self.repo.add(data)

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskOut]:
        return self.repo.list_tasks(status)

    def move(self, task_id: int, new_status: TaskStatus) -> TaskOut:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        if new_status not in ALLOWED_TRANSITIONS[task.status]:
            raise InvalidTransition(f"{task.status.value} -> {new_status.value}")
        return self.repo.update_status(task_id, new_status)
```

Fijate que no hay ni un `import` de FastAPI. El service habla en términos del negocio: "esa tarea no existe", "esa transición no vale". Eso lo hace testeable sin levantar HTTP y reutilizable si mañana la misma regla la dispara una cola de mensajes o un CLI.

**El router traduce.** Su trabajo es HTTP: rutas, códigos, y convertir excepciones de dominio en respuestas:

```python
# app/routes/tasks.py
from fastapi import APIRouter, HTTPException

from ..dependencies import TaskServiceDep
from ..schemas import TaskCreate, TaskOut, TaskStatus, TaskStatusUpdate
from ..services.task_service import InvalidTransition, TaskNotFound

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", status_code=201)
def create_task(data: TaskCreate, service: TaskServiceDep) -> TaskOut:
    return service.create(data)


@router.get("/")
def list_tasks(service: TaskServiceDep, status: TaskStatus | None = None) -> list[TaskOut]:
    return service.list_tasks(status)


@router.patch("/{task_id}/status")
def move_task(task_id: int, body: TaskStatusUpdate, service: TaskServiceDep) -> TaskOut:
    try:
        return service.move(task_id, body.status)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail=f"Invalid transition: {exc}")
```

- **`?status=`** es un query parameter opcional tipado como `TaskStatus | None`: `GET /tasks/?status=in_progress` filtra el tablero por columna, y `?status=cualquiera` da 422 solo.
- **Rutas `def`, no `async def`:** `sqlite3` es bloqueante, así que FastAPI las corre en el threadpool. Es el mismo criterio que usaste en S04 para las rutas de `users` con `psycopg`.
- **`PATCH /tasks/{task_id}/status`**: mover es un update parcial de un solo campo. La doc de FastAPI (_Body - Updates_) aclara que PATCH es menos usado que PUT y que FastAPI no impone convención: es una **decisión de diseño**, y por eso es buen candidato para el trade-off journal (vs `POST /tasks/{id}/move`).

**El ciclo de un request de "mover tarea".** En S03 dibujaste cliente → Uvicorn → router → handler. Hoy la secuencia gana service y repository, y tiene tres salidas:

```mermaid
sequenceDiagram
    actor U as Navegador
    participant UV as Uvicorn
    participant R as Router tasks
    participant S as TaskService
    participant RP as Repository
    U->>UV: PATCH /tasks/7/status
    UV->>R: request
    Note over R: Pydantic valida el body (si falla, 422)
    R->>S: move(7, done)
    S->>RP: get(7)
    RP-->>S: TaskOut o None
    alt la tarea no existe
        S-->>R: raise TaskNotFound
        R-->>U: 404 Task not found
    else transición inválida
        S-->>R: raise InvalidTransition
        R-->>U: 409 Invalid transition
    else transición válida
        S->>RP: update_status(7, done)
        RP-->>S: TaskOut actualizada
        S-->>R: TaskOut
        R-->>U: 200 con TaskOut
    end
```

> ⚠️ **Error común — la regla en el lugar equivocado:** si la validación de transiciones queda en el router, funciona... hasta que alguien agrega otro endpoint que también mueve tareas (por ejemplo, "cerrar todas las de un proyecto") y se la saltea. Si queda solo en el front, cualquiera la saltea con `curl`. Un solo lugar: el service.

> ⚠️ **Error común — la barra final:** con `prefix="/tasks"` y `@router.post("/")`, la ruta es `/tasks/`. Si llamás a `/tasks` (sin barra), FastAPI te responde con un redirect 307 hacia `/tasks/`. Con `curl` sin `-L` vas a ver el redirect y no la tarea.

📎 Para profundizar: [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) · [Body - Updates](https://fastapi.tiangolo.com/tutorial/body-updates/) · [Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)

> 📝 **Nota para el profesor:** la tabla de transiciones (`backlog → in_progress`, `in_progress → backlog | done`, `done → in_progress`) y la forma del endpoint (`PATCH /tasks/{task_id}/status`) son la propuesta del material. Si querés otra regla, cambiala antes del lab: impacta el prompt, los tests y la UI.

---

### 4.8 Verificar lo que hizo el agente: tests mínimos

Testing como estrategia (unit vs integration, cobertura) es tema de S15. Hoy los tests son otra cosa: **la verificación que el agente puede correr** y la señal de pasa/no pasa para el equipo.

```python
# tests/test_tasks.py (fixture + dos tests)
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app
from app.repositories.memory import InMemoryTaskRepository


@pytest.fixture
def client():
    repo = InMemoryTaskRepository()                      # repo nuevo por test
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides = {}                        # limpiar overrides


def test_create_task_starts_in_backlog(client):
    r = client.post("/tasks/", json={"title": "Diseñar el tablero"})
    assert r.status_code == 201
    assert r.json()["status"] == "backlog"


def test_unknown_status_returns_422(client):
    task_id = client.post("/tasks/", json={"title": "A"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}/status", json={"status": "archivada"})
    assert r.status_code == 422
```

Las tres piezas y qué resuelve cada una:

- **`TestClient(app)`** te deja hacer requests a la app sin levantar Uvicorn. Los tests son funciones `def` normales, sin `async` ni `await`, así que `pytest` los corre directo. `TestClient` requiere `httpx`: si al correr los tests aparece un error de que falta, instalalo con `pip install httpx`.
- **`app.dependency_overrides`** es un diccionario: clave = la dependencia original (`get_repository`), valor = la que la reemplaza. Acá está el **para qué** de la inyección de dependencias de S04: cada test recibe un repositorio en memoria **nuevo**, sin tocar una línea del código de producción.
- **La fixture con `yield`** arma el override, entrega el cliente y, después del test, limpia con `app.dependency_overrides = {}`. El scope por defecto de una fixture es `function`: se crea y destruye por cada test, así que no hay estado compartido entre tests.

> ⚠️ **Error común:** si te olvidás de limpiar los overrides, el override de un test "se filtra" al siguiente. Y si no creás un repo nuevo por test (por ejemplo, usando `_memory_repo`), `test_filter_by_status` va a contar tareas creadas por otros tests y va a fallar según el orden de ejecución.

> ⚠️ **Error común:** corré `pytest` **desde la raíz** del repo. Con `tests/__init__.py` y el cwd en la raíz, `import app` resuelve; si no, probá `python -m pytest -q`.

📎 Para profundizar: [Testing](https://fastapi.tiangolo.com/tutorial/testing/) · [Testing Dependencies with Overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/) · [How to use fixtures — pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html)

---

### 4.9 Cliente/UI simple

Hay tres niveles de cliente, y el entregable acepta cualquiera:

1. **Piso: Swagger UI en `/docs`** (M07·S03). Costo cero, y gracias al `Enum` el estado aparece como desplegable. Si la UI no llega, alcanza para la demo.
2. **Default: una página HTML servida por el mismo FastAPI.** Se monta con `StaticFiles` y queda en `http://127.0.0.1:8000/static/index.html`.
3. **Alternativa de consola: un `client.py` con `httpx`.**

La pieza central de la UI es una función que envuelve `fetch` y **chequea `response.ok`**:

```javascript
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" }, ...options,
  });
  if (!res.ok) {                                  // fetch NO falla solo ante 404/409
    const body = await res.json();
    throw new Error(`${res.status}: ${JSON.stringify(body.detail)}`);
  }
  return res.json();
}
```

Es el detalle que más se olvida: `fetch` **no** rechaza la promesa ante un status de error como 404 o 409. Si no chequeás `res.ok`, el 409 de una transición inválida pasa en silencio y el usuario no se entera de por qué la tarjeta no se movió.

Y del lado de Python, el mismo flujo en consola:

```python
# client.py
import httpx

BASE = "http://127.0.0.1:8000"
task = httpx.post(f"{BASE}/tasks/", json={"title": "Escribir el README"}).raise_for_status().json()
httpx.patch(f"{BASE}/tasks/{task['id']}/status", json={"status": "in_progress"}).raise_for_status()
print(httpx.get(f"{BASE}/tasks/", params={"status": "in_progress"}).json())
```

**Validación en el front = UX; validación en el back = la regla.** La UI tiene su propia copia de las transiciones (`NEXT`) solo para decidir qué botones mostrar. No es la regla: si alguien llama a la API con `curl` y una transición inválida, el service igual devuelve 409.

**¿Y CORS?** Solo hace falta si el JavaScript del navegador llama a un backend de **otro origen** (protocolo + dominio + puerto). Con la UI servida por el mismo FastAPI, página y API comparten `127.0.0.1:8000`: mismo origen, **sin CORS**. Si tu equipo arma un front aparte (por ejemplo, en `localhost:5173`), sí necesitás `CORSMiddleware` (un middleware incluido en Starlette, como el `SessionMiddleware` de S04) con ese origen, y ojo: `allow_methods` por defecto es solo `['GET']`, así que el `POST` de crear y el `PATCH` de mover fallan hasta que los agregues.

> ⚠️ **Error común:** `localhost:8000` y `127.0.0.1:8000` son orígenes **distintos** para el navegador (el dominio no es el mismo string). Si abrís la página por uno y el JS llama al otro con URL absoluta, aparece un error de CORS "misterioso". Usá rutas relativas (`/tasks/`) como en el `index.html` del lab.

📎 Para profundizar: [Static Files](https://fastapi.tiangolo.com/tutorial/static-files/) · [Using the Fetch API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) · [CORS](https://fastapi.tiangolo.com/tutorial/cors/) · [QuickStart — HTTPX](https://www.python-httpx.org/quickstart/)

---

### 4.10 Correr el servidor

```bash
uvicorn app.main:app --reload                              # memoria (default)
TASKFLOW_STORAGE=sqlite uvicorn app.main:app --reload      # SQLite en taskflow.db
# alternativa: fastapi dev app/main.py
```

- `app.main:app` = módulo `app/main.py`, objeto `app`. Se corre **desde la raíz** `taskflow/`.
- Uvicorn escucha por defecto en `127.0.0.1:8000`.
- `--reload` reinicia el servidor al guardar un archivo. **Con el repo en memoria, cada reload borra las tareas**: el `dict` vive en el proceso y el proceso se reinicia. No es un bug, es el síntoma que justifica pasar a SQLite (y tu primer trade-off).
- `fastapi dev` corre con auto-reload en `127.0.0.1`; `fastapi run`, sin reload y en `0.0.0.0` (escucha en todas las interfaces). Por debajo, los dos usan Uvicorn. La diferencia `127.0.0.1` vs `0.0.0.0` es la misma que viste en el `Dockerfile` de S04 (`--host 0.0.0.0` para que la app sea alcanzable desde fuera del contenedor), y vuelve en S16.
- En Windows (PowerShell), la variable se setea aparte: `$env:TASKFLOW_STORAGE="sqlite"` y después el comando de `uvicorn`.

**Un experimento para pensar (no para hacer hoy):** `--reload` y `--workers` no se pueden combinar. Pero si corrieras `--workers 2` sin reload, tendrías **dos procesos, cada uno con su propio `dict`**: una tarea creada en uno no existiría en el otro. Es exactamente lo que S12 va a romper a propósito.

**Sobre la instalación:** en S03 instalaste con `pip` + venv y en S04 fijaste las dependencias en un `requirements.txt`; este material sigue así. La doc oficial de FastAPI hoy recomienda `uv` (`uv add "fastapi[standard]"`) y ofrece `pip install "fastapi[standard]"` como alternativa. Si el agente te genera un `pyproject.toml` con `uv`, no es un error: es la otra vía oficial. Elijan **una** y déjenla escrita en el `CLAUDE.md`.

```python
# Chequeo rápido de qué persistencia está activa (desde la raíz, con el venv activo)
from app.dependencies import STORAGE, DB_PATH
print(STORAGE, DB_PATH)   # "memory taskflow.db" salvo que hayas seteado TASKFLOW_STORAGE
```

📎 Para profundizar: [FastAPI CLI](https://fastapi.tiangolo.com/fastapi-cli/) · [Settings — Uvicorn](https://uvicorn.dev/settings/) · [Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/)

---

### 4.11 Entregables de diseño: diagramas y trade-offs

El entregable pide dos diagramas y tres entradas de bitácora. Van en `docs/`, en Mermaid, versionados junto al código.

**Diagrama de componentes.** Es el nivel "componente" de C4 (lo viste en MA·S05): descompone **un único container** —acá, el webserver FastAPI— en sus componentes. Su audiencia son arquitectos y desarrolladores, y la propia C4 lo marca como opcional; acá se pide porque dibujarlo te obliga a entender la estructura. Usá `flowchart` y no la sintaxis `C4Component` de Mermaid, que está marcada como experimental. El diagrama ancla de la sección 4 es un buen punto de partida, pero **tiene que reflejar tu código**: si tu equipo agregó un componente o cambió un nombre, el diagrama cambia.

**Diagrama de secuencia de "mover tarea".** Tiene que mostrar los tres caminos (404, 409, 200) con `alt` / `else`, como el de 4.7. Si tu equipo eligió `POST /tasks/{id}/move`, dibujá ese.

> ⚠️ **Error común con Mermaid:** en un `flowchart`, la palabra `end` en minúscula dentro de un nodo rompe el diagrama. Y si una etiqueta lleva `/`, `(` o `:`, ponela entre comillas: `RT["routes/tasks.py"]`.

**Un diagrama que dice la verdad se puede testear.** El diagrama de componentes afirma que el service no conoce HTTP y que el router no toca repositories. Podés convertir esa afirmación en un test:

```python
# tests/test_arquitectura.py
import ast
from pathlib import Path


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    return names


def test_services_no_importan_fastapi():
    for path in Path("app/services").glob("*.py"):
        assert not any(n.startswith("fastapi") for n in _imports(path)), path


def test_routes_no_tocan_repositories():
    for path in Path("app/routes").glob("*.py"):
        assert not any("repositories" in n for n in _imports(path)), path
```

Si el agente "resuelve" algo metiendo un `HTTPException` en el service, este test lo marca antes que vos.

**Trade-off journal: TJ-001 a TJ-003.** El formato `TJ-NNN` lo arrancaste en M07·S01. El lab hace aparecer varias decisiones solas; elegí tres:

|Candidato|Alternativas|Qué se gana / qué se paga|Qué lo haría cambiar|
|---|---|---|---|
|Persistencia del prototipo|`dict` en memoria vs SQLite en archivo|Memoria: cero setup, pero se pierde en cada `--reload` y no sirve con más de un proceso. SQLite: persiste, un escritor a la vez|Varios usuarios escribiendo a la vez / más de un proceso → PostgreSQL (S06–S07)|
|Dónde vive la regla de transiciones|service vs router vs base (constraint) vs front|Service: testeable sin HTTP, un solo lugar. Front solo: cualquiera la saltea con `curl`|Si otra app escribe en la misma base, la regla tiene que bajar a la base|
|Forma del endpoint "mover"|`PATCH /tasks/{id}/status` vs `POST /tasks/{id}/move` vs `PATCH /tasks/{id}` genérico|PATCH al subrecurso: semántica de update parcial. POST de acción: explícito, fácil de auditar|S10 (REST formal) puede reabrirlo|
|UI|Estático servido por FastAPI vs front aparte vs solo `/docs`|Estático: mismo origen, sin CORS, un proceso. Front aparte: más realista, suma CORS y otro proceso|Si el front necesita estado complejo o un equipo propio|
|Código de error de transición inválida|409 vs 422 vs 400|409 comunica "conflicto con el estado actual" y separa del 422 de validación|—|
|IDs|entero autoincremental vs UUID|Entero: legible y simple. UUID: no revela volumen y se genera sin la base|Varias bases o IDs expuestos públicamente|

Una entrada completa se ve así:

```markdown
## TJ-001 — Persistencia del prototipo: dict en memoria vs SQLite

- **Contexto:** prototipo de semana 1, una sola entidad (Tarea), un proceso de Uvicorn.
- **Alternativas:** (a) dict en memoria; (b) SQLite en archivo; (c) PostgreSQL ya,
  con el docker-compose.yml de S04.
- **Decisión:** las dos primeras detrás del mismo Protocol; memoria por defecto,
  SQLite con TASKFLOW_STORAGE=sqlite.
- **Por qué:** memoria arranca en cero minutos; SQLite nos da persistencia entre
  reinicios sin instalar nada; PostgreSQL ya sabemos levantarlo (S04), pero suma Docker
  y un servidor al arranque de cada integrante y hoy no compra nada: el Protocol deja la
  puerta abierta.
- **Qué pagamos:** con memoria, cada --reload borra todo; SQLite admite un solo
  escritor a la vez por archivo.
- **Qué nos haría cambiar:** varios usuarios escribiendo a la vez o más de un
  proceso de servidor → PostgreSQL (planificado para S07).
```

📎 Para profundizar: [Component diagram — C4 model](https://c4model.com/diagrams/component) · [Flowcharts — Mermaid](https://mermaid.js.org/syntax/flowchart.html) · [Sequence diagrams — Mermaid](https://mermaid.js.org/syntax/sequenceDiagram.html) · [State diagrams — Mermaid](https://mermaid.js.org/syntax/stateDiagram.html)

> 📝 **Nota para el profesor:** la plantilla de TJ de arriba (contexto / alternativas / decisión / por qué / qué pagamos / qué nos haría cambiar) es una propuesta coherente con lo de M07·S01; si en S01 fijaste otros campos, conviene alinearla.

---

### Mapa de relaciones entre recursos

```mermaid
flowchart TD
    CC["Claude Code: best practices"] --> BIG["FastAPI: Bigger Applications"]
    BIG --> SCH["Contrato: Enum, Extra Models,<br/>Response Model, Pydantic Fields"]
    SCH --> REPO["sqlite3 + SQLite in-memory y whentouse"]
    BIG --> DEP["Dependencies with yield + SQL Databases"]
    REPO --> DEP
    DEP --> EP["Endpoints: Query params, Body updates,<br/>Handling errors, Status code, MDN 409"]
    EP --> RUN["Correr: Tutorial, FastAPI CLI, Uvicorn, Lifespan"]
    EP --> TST["Testing + overrides + pytest fixtures"]
    RUN --> UI["UI: Static Files + MDN fetch<br/>(CORS o httpx como alternativas)"]
    EP --> DIA["Diagramas: C4 component + Mermaid<br/>flowchart, sequence, state"]
    TST --> DIA

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class DEP foco
```

El nodo resaltado es el que une todo: **Dependencies with yield** es donde el service recibe su repository y donde se hace el intercambio memoria ↔ SQLite. Relaciones que el diagrama no muestra:

- **Testing Dependencies with Overrides** solo tiene sentido después de **Dependencies with yield**: lo que overrideás es `get_repository`, la misma función que elige memoria o SQLite.
- **In-Memory Databases** corrige el error más probable al combinar `sqlite3` (`":memory:"`) con una conexión por request.
- **Uvicorn Settings** (`--workers` incompatible con `--reload`) y **Appropriate Uses For SQLite** (un escritor a la vez) son los dos argumentos del trade-off de persistencia, y los dos anticipan S12.
- **CORS** es condicional: solo si no seguís el default de **Static Files**.
- **Lifespan Events** reemplaza lo que el agente puede generar con `@app.on_event` (deprecado).

---

## 5. Guía práctica paso a paso: el prototipo de TaskFlow

Podés seguir esta guía escribiendo el código vos o dirigiendo al agente. En clase, **dirigís al agente** (paso 3) y usás los pasos 4 a 13 para **revisar** que lo que generó coincide. Cada paso termina con cómo verificar que funcionó.

**Prerrequisitos:**

- Python ≥ 3.10 (`python --version`). La sintaxis `str | None` lo necesita.
- Git y una cuenta de GitHub (M01).
- Claude Code instalado (o Cursor como alternativa).
- `curl` en la terminal (en Windows/PowerShell usá `curl.exe`, o probá todo desde `/docs`).
- Docker **no** hace falta para el lab, pero sí para los ejercicios (sección 6): Docker Desktop, el mismo de S04.

### Paso 0 — Equipo y repo

Un integrante crea el repo vacío `taskflow` en GitHub; los demás lo clonan:

```bash
git clone https://github.com/<USUARIO_O_ORG>/taskflow.git
cd taskflow
```

Reemplazá `<USUARIO_O_ORG>` por la cuenta donde se creó el repo. Si sos quien lo crea y preferís arrancar local: `mkdir taskflow && cd taskflow && git init` y después conectás el remoto.

✅ **Verificación:** `git status` responde sin error dentro de `taskflow/`.

### Paso 1 — Entorno e instalación

Creá `requirements.txt` en la raíz, con el mismo formato que en S04:

```text
fastapi[standard]>=0.115   # framework + uvicorn + httpx (lo usa TestClient)
pytest>=8                  # tests
```

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

- Lo que instala el equipo queda versionado en el repo; en S06 y S07 se le suman líneas.
- `TestClient` requiere `httpx`: si al correr los tests aparece un error de que falta, instalalo con `pip install httpx`.
- Alternativa oficial con `uv`: `uv add "fastapi[standard]" pytest` dentro de un proyecto `uv init --bare` (las comillas son obligatorias en zsh por los corchetes). Elijan **una** vía para todo el equipo.

Creá también un `.gitignore`:

```text
.venv/
__pycache__/
taskflow.db
.env
```

(`.env` todavía no existe, pero en S06 aparece con las credenciales de Docker Compose, igual que en S04.)

✅ **Verificación:** `python -c "import fastapi, pytest; print('ok')"` imprime `ok`.

### Paso 2 — Estructura de carpetas

```bash
mkdir -p app/routes app/services app/repositories static tests docs/diagramas
touch app/__init__.py app/routes/__init__.py app/services/__init__.py \
      app/repositories/__init__.py tests/__init__.py
```

(En Windows sin bash, creá las carpetas y los `__init__.py` vacíos desde el editor.)

✅ **Verificación:** tenés 5 archivos `__init__.py` (`find . -name "__init__.py" -not -path "./.venv/*"` lista 5).

### Paso 3 — `CLAUDE.md` y el prompt de dirección

Creá `CLAUDE.md` en la raíz:

```markdown
# TaskFlow — API de gestión de tareas (prototipo, semana 1)

## Comandos
- Instalar: `pip install -r requirements.txt`
- Correr: `uvicorn app.main:app --reload` (SQLite: `TASKFLOW_STORAGE=sqlite ...`)
- Tests: `pytest -q` — correlos después de cada cambio y arreglá lo que falle.

## Arquitectura (no negociable)
- Capas: routes/ → services/ → repositories/. Un router nunca toca un repository.
- services/ no importa nada de FastAPI: lanza TaskNotFound / InvalidTransition; el router las traduce a 404 / 409.
- Todo repository implementa el Protocol de repositories/base.py.
- SQL siempre con placeholders `?`. Nada de SQLAlchemy en esta fase.

## Alcance de esta fase
- Solo la entidad Tarea. Sin auth, sin usuarios, sin proyectos (llegan en semanas 2–3).
- Nada de LLM ni IA: TaskFlow no tiene componente de IA.
```

Abrí Claude Code en plan mode (`claude --permission-mode plan`, o `Shift+Tab` dentro de la sesión) y pasale:

```text
Leé CLAUDE.md. Quiero el prototipo de TaskFlow: los endpoints POST /tasks/, GET /tasks/?status=
y PATCH /tasks/{task_id}/status, con la estructura de carpetas de CLAUDE.md, repositorio en memoria
y SQLite intercambiables por TASKFLOW_STORAGE. Transiciones válidas: backlog→in_progress,
in_progress→backlog|done, done→in_progress; cualquier otra devuelve 409. Armá un plan con los
archivos a crear. No escribas código todavía.
```

Revisá el plan (`Ctrl+G` para editarlo): ¿lista `schemas.py`, `dependencies.py`, `routes/tasks.py`, `services/task_service.py` y los tres archivos de `repositories/`? ¿La regla de transiciones está en el service? Cuando esté bien:

```text
Implementá el plan. Escribí tests con TestClient para crear (201, status backlog), una transición
válida (200) y una inválida (409); corré pytest y arreglá lo que falle.
```

> 💡 Si preferís ir más lento y ver cómo emerge la capa repository, pedile al agente que implemente primero **solo memoria** (pasos 4–11) y después SQLite (paso 12). Es lo que hace esta guía.

✅ **Verificación:** el plan aprobado nombra los archivos del paso 2 y no propone `@app.on_event`, ORM ni código en `main.py` más allá de montar la app.

### Paso 4 — El contrato: `app/schemas.py`

El archivo completo es el de la sección 4.4. Copialo tal cual (o compará el del agente contra ese).

✅ **Verificación:**

```bash
python -c "from app.schemas import TaskCreate; print(TaskCreate(title='x'))"
# title='x' description=None assignee=None
python -c "from app.schemas import TaskCreate; TaskCreate(title='')"
# ... ValidationError ... String should have at least 1 character
```

### Paso 5 — El puerto y el repositorio en memoria

`app/repositories/base.py`: el `Protocol` completo de la sección 4.5.

`app/repositories/memory.py`, completo:

```python
from datetime import datetime, timezone
from itertools import count
from threading import Lock

from ..schemas import TaskCreate, TaskOut, TaskStatus


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskOut] = {}
        self._ids = count(1)
        self._lock = Lock()             # las rutas def corren en un threadpool (S04)

    def add(self, data: TaskCreate) -> TaskOut:
        with self._lock:
            task = TaskOut(
                id=next(self._ids),
                status=TaskStatus.backlog,
                created_at=datetime.now(timezone.utc),
                **data.model_dump(),
            )
            self._tasks[task.id] = task
            return task

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskOut]:
        return [t for t in self._tasks.values() if status is None or t.status == status]

    def get(self, task_id: int) -> TaskOut | None:
        return self._tasks.get(task_id)

    def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
        with self._lock:
            task = self._tasks[task_id].model_copy(update={"status": status})
            self._tasks[task_id] = task
            return task
```

✅ **Verificación:**

```bash
python -c "
from app.repositories.memory import InMemoryTaskRepository
from app.schemas import TaskCreate
r = InMemoryTaskRepository(); t = r.add(TaskCreate(title='A'))
print(t.id, t.status.value, len(r.list_tasks()))"
# 1 backlog 1
```

### Paso 6 — El service: `app/services/task_service.py`

El archivo completo es el de la sección 4.7 (con `ALLOWED_TRANSITIONS`, `TaskNotFound`, `InvalidTransition` y `TaskService`).

✅ **Verificación:** `grep -n "fastapi" app/services/task_service.py` no devuelve nada.

### Paso 7 — La inyección: `app/dependencies.py` (versión solo memoria)

Por ahora, sin SQLite:

```python
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends

from .repositories.base import TaskRepository
from .repositories.memory import InMemoryTaskRepository
from .services.task_service import TaskService

_memory_repo = InMemoryTaskRepository()               # una sola instancia por proceso


def get_repository() -> Iterator[TaskRepository]:
    yield _memory_repo


def get_task_service(
    repo: Annotated[TaskRepository, Depends(get_repository)],
) -> TaskService:
    return TaskService(repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
```

✅ **Verificación:** `python -c "import app.dependencies"` no tira error.

### Paso 8 — El router: `app/routes/tasks.py`

El archivo completo es el de la sección 4.7.

✅ **Verificación:** `python -c "from app.routes.tasks import router; print([r.path for r in router.routes])"` imprime las tres rutas (`/tasks/`, `/tasks/`, `/tasks/{task_id}/status`).

### Paso 9 — La app: `app/main.py` (versión inicial)

```python
from fastapi import FastAPI

from .routes import tasks

app = FastAPI(title="TaskFlow")
app.include_router(tasks.router)
```

### Paso 10 — Correr y probar a mano

```bash
uvicorn app.main:app --reload
```

Deberías ver una línea tipo `Uvicorn running on http://127.0.0.1:8000`. En **otra terminal**:

```bash
# 1. Crear → 201
curl -s -i -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" -d '{"title": "Diseñar el tablero"}'
# HTTP/1.1 201 Created
# {"id":1,"title":"Diseñar el tablero","description":null,"assignee":null,"status":"backlog","created_at":"..."}

# 2. Listar filtrando → 200
curl -s "http://127.0.0.1:8000/tasks/?status=backlog"
# [{"id":1, ... "status":"backlog", ...}]

# 3. Transición inválida backlog -> done → 409
curl -s -i -X PATCH http://127.0.0.1:8000/tasks/1/status \
  -H "Content-Type: application/json" -d '{"status": "done"}'
# HTTP/1.1 409 Conflict
# {"detail":"Invalid transition: backlog -> done"}

# 4. Transición válida → 200
curl -s -X PATCH http://127.0.0.1:8000/tasks/1/status \
  -H "Content-Type: application/json" -d '{"status": "in_progress"}'
# {"id":1, ... "status":"in_progress", ...}

# 5. Tarea inexistente → 404 ; estado inventado → 422
curl -s -i -X PATCH http://127.0.0.1:8000/tasks/999/status \
  -H "Content-Type: application/json" -d '{"status": "in_progress"}'
# HTTP/1.1 404 Not Found
curl -s -o /dev/null -w "%{http_code}\n" -X PATCH http://127.0.0.1:8000/tasks/1/status \
  -H "Content-Type: application/json" -d '{"status": "archivada"}'
# 422
```

Abrí también `http://127.0.0.1:8000/docs`: el campo `status` aparece como desplegable.

Ahora guardá cualquier archivo (por ejemplo, agregá un espacio en `main.py`) y volvé a listar: **la lista está vacía**. El reload reinició el proceso y el `dict` se fue con él. Anotalo: es la materia prima de TJ-001.

✅ **Verificación:** los cinco `curl` devuelven 201, 200, 409, 200 y 404/422 respectivamente.

### Paso 11 — Tests: `tests/test_tasks.py`

```python
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app
from app.repositories.memory import InMemoryTaskRepository


@pytest.fixture
def client():
    repo = InMemoryTaskRepository()                      # repo nuevo por test
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides = {}                        # limpiar overrides


def test_create_task_starts_in_backlog(client):
    r = client.post("/tasks/", json={"title": "Diseñar el tablero"})
    assert r.status_code == 201
    assert r.json()["status"] == "backlog"


def test_filter_by_status(client):
    client.post("/tasks/", json={"title": "A"})
    assert len(client.get("/tasks/", params={"status": "backlog"}).json()) == 1
    assert client.get("/tasks/", params={"status": "done"}).json() == []


def test_valid_move(client):
    task_id = client.post("/tasks/", json={"title": "A"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


def test_invalid_move_returns_409(client):
    task_id = client.post("/tasks/", json={"title": "A"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    assert r.status_code == 409


def test_unknown_status_returns_422(client):
    task_id = client.post("/tasks/", json={"title": "A"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}/status", json={"status": "archivada"})
    assert r.status_code == 422
```

Sumá también `tests/test_arquitectura.py` (sección 4.11).

```bash
pytest -q
# .......                                                   [100%]
# 7 passed in 0.xxs
```

Según la versión de Starlette instalada, el resumen puede decir `7 passed, 1 warning`: es un aviso de deprecación sobre cómo `TestClient` usa `httpx`, no un fallo de tus tests. Lo que importa es que no haya `failed` ni `error`.

Commiteá este punto: es tu prototipo en memoria, verde.

```bash
git add .
git commit -m "TaskFlow: prototipo en capas con repo en memoria y tests"
```

✅ **Verificación:** `7 passed` y `git status` limpio.

### Paso 12 — Cambiar a SQLite sin tocar service ni router

Este es el paso que justifica toda la arquitectura.

**12.a** Creá `app/repositories/sqlite.py`:

```python
import sqlite3
from datetime import datetime, timezone

from ..schemas import TaskCreate, TaskOut, TaskStatus

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    assignee    TEXT,
    status      TEXT    NOT NULL DEFAULT 'backlog',
    created_at  TEXT    NOT NULL
)
"""


def init_db(path: str) -> None:
    con = sqlite3.connect(path)
    with con:                            # commit al salir bien
        con.execute(SCHEMA)
    con.close()                          # el context manager NO cierra la conexión


class SqliteTaskRepository:
    def __init__(self, con: sqlite3.Connection) -> None:
        self.con = con
        self.con.row_factory = sqlite3.Row

    def _to_task(self, row: sqlite3.Row | None) -> TaskOut | None:
        return TaskOut(**dict(row)) if row else None

    def add(self, data: TaskCreate) -> TaskOut:
        with self.con:
            cur = self.con.execute(
                "INSERT INTO tasks (title, description, assignee, status, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (data.title, data.description, data.assignee,
                 TaskStatus.backlog.value, datetime.now(timezone.utc).isoformat()),
            )
        return self.get(cur.lastrowid)

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskOut]:
        if status is None:
            rows = self.con.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        else:
            rows = self.con.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY id", (status.value,)
            ).fetchall()
        return [self._to_task(r) for r in rows]

    def get(self, task_id: int) -> TaskOut | None:
        row = self.con.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._to_task(row)

    def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
        with self.con:
            self.con.execute(
                "UPDATE tasks SET status = ? WHERE id = ?", (status.value, task_id)
            )
        return self.get(task_id)
```

**12.b** Reemplazá `app/dependencies.py` por la versión final de la sección 4.6 (con `STORAGE`, `DB_PATH` y la rama SQLite).

**12.c** Agregá el `lifespan` a `app/main.py` (versión de la sección 4.3, **por ahora sin** la línea de `app.mount` ni el import de `StaticFiles`: los sumás en el paso 13).

**12.d** Corré con SQLite:

```bash
TASKFLOW_STORAGE=sqlite uvicorn app.main:app --reload
```

Creá una tarea con el `curl` del paso 10, frená el servidor con `Ctrl+C`, volvé a levantarlo y listá: **la tarea sigue ahí**. Mirala directo en la base:

```bash
python -c "import sqlite3; print(sqlite3.connect('taskflow.db').execute('SELECT id, title, status FROM tasks').fetchall())"
# [(1, 'Diseñar el tablero', 'backlog')]
```

✅ **Verificación — la prueba de la capa repository:**

```bash
git status --short
#  M app/dependencies.py
#  M app/main.py
# ?? app/repositories/sqlite.py
```

Ni `app/services/` ni `app/routes/` aparecen. Cambiaste la persistencia entera sin tocar la regla de negocio ni la capa HTTP. Y `pytest -q` sigue en `7 passed`. Commiteá.

### Paso 13 — La UI: `static/index.html`

Creá `static/index.html`:

```html
<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>TaskFlow</title>
<style>
  body { font-family: sans-serif; }
  #board { display: flex; gap: 1rem; }
  .col { flex: 1; border: 1px solid #ccc; padding: .5rem; min-height: 200px; }
  .task { border: 1px solid #999; margin: .3rem 0; padding: .3rem; }
</style></head>
<body>
  <h1>TaskFlow</h1>
  <form id="new-task">
    <input id="title" placeholder="Nueva tarea" required>
    <button>Crear</button>
  </form>
  <p id="error" style="color:#b00"></p>
  <div id="board">
    <div class="col" data-status="backlog"><h2>Backlog</h2></div>
    <div class="col" data-status="in_progress"><h2>En progreso</h2></div>
    <div class="col" data-status="done"><h2>Hecho</h2></div>
  </div>
<script>
const NEXT = { backlog: ["in_progress"], in_progress: ["backlog", "done"], done: ["in_progress"] };

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" }, ...options,
  });
  if (!res.ok) {                                  // fetch NO falla solo ante 404/409
    const body = await res.json();
    throw new Error(`${res.status}: ${JSON.stringify(body.detail)}`);
  }
  return res.json();
}

async function render() {
  document.querySelectorAll(".task").forEach(el => el.remove());
  for (const t of await api("/tasks/")) {
    const div = document.createElement("div");
    div.className = "task";
    div.textContent = `#${t.id} ${t.title} `;
    for (const s of NEXT[t.status]) {
      const b = document.createElement("button");
      b.textContent = `→ ${s}`;
      b.onclick = () => move(t.id, s);
      div.append(b);
    }
    document.querySelector(`.col[data-status="${t.status}"]`).append(div);
  }
}

async function move(id, status) {
  try {
    await api(`/tasks/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) });
    document.getElementById("error").textContent = "";
  } catch (e) { document.getElementById("error").textContent = e.message; }
  render();
}

document.getElementById("new-task").onsubmit = async (ev) => {
  ev.preventDefault();
  const title = document.getElementById("title").value;
  await api("/tasks/", { method: "POST", body: JSON.stringify({ title }) });
  ev.target.reset();
  render();
};

render();
</script>
</body>
</html>
```

Y montalo en `app/main.py` (queda igual a la versión final de la sección 4.3):

```python
from fastapi.staticfiles import StaticFiles
# ...
app.mount("/static", StaticFiles(directory="static"), name="static")
```

✅ **Verificación:** abrí `http://127.0.0.1:8000/static/index.html`, creá dos tareas y movelas entre columnas. Después provocá un 409 desde la terminal (`curl` con `backlog → done`) y confirmá que la UI no se rompió al recargar. Para ver el mensaje de error en la UI, abrí DevTools → Console y ejecutá `move(1, "done")` sobre una tarea en `backlog`: tiene que aparecer `409: "Invalid transition: backlog -> done"` en rojo.

### Paso 14 — Diagramas y bitácora

Creá en `docs/diagramas/`:

- `componentes.md` — `flowchart` del webserver (partí del diagrama ancla y ajustalo a tu código).
- `secuencia-mover-tarea.md` — `sequenceDiagram` con los tres caminos (404 / 409 / 200).
- `estados-tarea.md` (opcional, recomendado) — el `stateDiagram-v2` de 4.7.

Y `docs/tradeoff-journal.md` con TJ-001 a TJ-003 (sección 4.11).

✅ **Verificación:** abrí los `.md` en GitHub o en la vista previa de VS Code: los diagramas renderizan (sin cartel rojo de error) y los nombres de las cajas coinciden con archivos y clases que existen.

### Paso 15 — Entrega

Agregá un `README.md` con: cómo instalar, cómo correr (memoria y SQLite), cómo correr los tests y dónde está la UI. Después:

```bash
pytest -q                     # 7 passed
git add .
git commit -m "TaskFlow S05: SQLite, UI, diagramas y trade-offs"
git tag s05
git push origin main --tags
```

✅ **Verificación:** en GitHub se ve el tag `s05` y, clonando el repo en otra carpeta, siguiendo solo el README llegás a `7 passed` y a la UI funcionando.

> 📝 **Nota para el profesor:** los defaults de este lab son: equipos de 3 (de 2 si no cierra el número) que se mantienen todo el módulo; repo nuevo `taskflow` (no el `webserver-fastapi/` de S03–S04); Claude Code en plan mode; memoria y SQLite **ambos** esperables en clase; UI estática como default y `/docs` como piso; entrega con tag `s05` en GitHub. Docker no se usa en el lab; los ejercicios sí lo usan (Postgres en Docker, con una preparación de ~30–40 min al comienzo de la sección 6), así que conviene recordar que traigan Docker Desktop andando desde S04. Rúbrica propuesta, cuatro criterios de igual peso: funciona (tests en verde + demo del 409), capas respetadas (service sin FastAPI, intercambio memoria ↔ SQLite), diagramas coherentes con el código, 3 trade-offs con alternativa descartada. Timing propuesto de los 180 min: 40 presentación de TaskFlow + recorte + estados en pizarra → 60 taller guiado (pasos 3–11) → 45 práctica autónoma (pasos 12–14) → 20 puesta en común de trade-offs → 15 cierre y entrega. Ajustá lo que no coincida con cómo lo vas a dictar.

---

## 6. Ejercicios

Todos los ejercicios se hacen sobre tu repo de TaskFlow y corren contra **PostgreSQL en Docker**, como el webserver de S04. El lab te deja TaskFlow con memoria y SQLite. La preparación de abajo le suma un tercer adaptador sobre Postgres, y a partir de ahí cada ejercicio se verifica contra el contenedor.

Trabajá en una rama por ejercicio y no rompas los tests existentes: "lo lograste" siempre incluye `pytest -q` en verde, **con Postgres levantado**. Los tests de los ejercicios usan la fixture `pg_client`. Si el contenedor está apagado, esos tests fallan en vez de saltearse, así que un verde con Postgres apagado no es posible.

### Preparación — TaskFlow sobre Postgres en Docker

Se hace una sola vez, en una rama `s05-postgres`, antes del primer ejercicio. Tiempo estimado: 30–40 min.

Es también un anticipo de lo que viene. En S06, este mismo `docker-compose.yml` suma Redis. En S07, el adaptador pasa al ORM de SQLAlchemy con migraciones de Alembic.

**P1. `docker-compose.yml` y `.env.example`.** Es el de S04 con dos diferencias:

- **No hay servicio `api`.** La app sigue corriendo en tu venv, como la "alternativa sin Docker" de S04. Por eso se conecta por `localhost` y no por `db`.
- **El puerto se publica solo en `127.0.0.1`.** Así nadie fuera de tu máquina llega a la base.

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-taskflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-taskflow}   # solo para desarrollo local
      POSTGRES_DB: ${POSTGRES_DB:-taskflow}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 2s
      timeout: 3s
      retries: 15

volumes:
  pgdata:
```

```bash
# .env.example — copialo como .env (el .env no se sube a git)
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=taskflow
POSTGRES_DB=taskflow
```

Levantalo y creá dos bases propias de TaskFlow:

```bash
cp .env.example .env
docker compose up -d db
docker compose exec db psql -U taskflow -d taskflow -c "CREATE DATABASE taskflow_dev;"
docker compose exec db psql -U taskflow -d taskflow -c "CREATE DATABASE taskflow_test;"
```

Las tres bases tienen roles distintos:

- **`taskflow_dev`** es la de la app.
- **`taskflow_test`** es la de los tests, y se vacía antes de cada test.
- **`taskflow`**, la que crea la imagen, queda libre: en S06 la usás para el seed de 200.000 tareas.

> ⚠️ **Error común:** si el `db` de `webserver-fastapi/` (S04) sigue levantado, el puerto 5432 está ocupado y `docker compose up` falla con `address already in use`. Hacé `docker compose down` en esa carpeta: sin `-v`, sus datos quedan.

**P2. Dependencias.** Sumá dos líneas a `requirements.txt`, las mismas de S04, y reinstalá con `pip install -r requirements.txt`:

```text
sqlalchemy>=2.0,<2.1       # SQLAlchemy Core, como en S04
psycopg[binary]>=3.2       # driver de Postgres
```

**P3. El adaptador: `app/repositories/postgres.py`.** Cumple el mismo `Protocol` que memoria y SQLite. Las consultas se arman con SQLAlchemy Core, con el estilo de `user_repository.py` de S04. La diferencia es que la conexión llega en el constructor, como en `SqliteTaskRepository`.

```python
# app/repositories/postgres.py
from sqlalchemy import (
    Column, DateTime, Integer, MetaData, String, Table, Text, func, insert, select, update,
)
from sqlalchemy.engine import Connection, Engine

from ..schemas import TaskCreate, TaskOut, TaskStatus

meta = MetaData()

tasks = Table(
    "tasks",
    meta,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("description", Text),
    Column("assignee", String(100)),
    Column("status", String(20), nullable=False, server_default="backlog"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


def init_db(engine: Engine) -> None:
    meta.create_all(engine)          # como en S04: crea la tabla si no existe (no la modifica)


class PostgresTaskRepository:
    def __init__(self, con: Connection) -> None:
        self.con = con               # la conexión (y su transacción) la maneja dependencies.py

    def add(self, data: TaskCreate) -> TaskOut:
        stmt = insert(tasks).values(**data.model_dump()).returning(tasks)
        return TaskOut(**self.con.execute(stmt).one()._mapping)

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskOut]:
        stmt = select(tasks).order_by(tasks.c.id)
        if status is not None:
            stmt = stmt.where(tasks.c.status == status.value)
        return [TaskOut(**r._mapping) for r in self.con.execute(stmt)]

    def get(self, task_id: int) -> TaskOut | None:
        row = self.con.execute(select(tasks).where(tasks.c.id == task_id)).first()
        return TaskOut(**row._mapping) if row else None

    def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
        stmt = (
            update(tasks).where(tasks.c.id == task_id)
            .values(status=status.value).returning(tasks)
        )
        return TaskOut(**self.con.execute(stmt).one()._mapping)
```

Tres detalles del adaptador:

- **`INSERT ... RETURNING`** devuelve la fila recién creada en la misma consulta, igual que en S04. No hace falta el `lastrowid` de SQLite.
- **El estado y la fecha los pone la base** (`server_default`). Pydantic convierte el string de `status` a `TaskStatus` al armar el `TaskOut`.
- **`create_all` crea la tabla, pero no la modifica.** Lo vas a sentir en el Intermedio 2. En S07 lo reemplaza Alembic.

**P4. La rama `postgres` en `app/dependencies.py`.** Agregá el engine y la rama. Las ramas de memoria y SQLite quedan como en el lab:

```python
# app/dependencies.py (lo nuevo)
from sqlalchemy import create_engine

from .repositories.postgres import PostgresTaskRepository

STORAGE = os.getenv("TASKFLOW_STORAGE", "memory")     # "memory" | "sqlite" | "postgres"
DATABASE_URL = os.getenv(
    "TASKFLOW_DATABASE_URL",                           # el DATABASE_URL de S04
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_dev",
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)   # no conecta hasta el primer uso


def get_repository() -> Iterator[TaskRepository]:
    if STORAGE == "postgres":
        with engine.begin() as con:                    # como get_db en S04: commit o rollback al salir
            yield PostgresTaskRepository(con)
    elif STORAGE == "sqlite":
        ...                                            # igual que en el lab
    else:
        yield _memory_repo
```

**P5. El `lifespan` de `app/main.py`.** Crea la tabla al arrancar y cierra el pool al apagar, como en S04:

```python
# app/main.py (lifespan)
from .dependencies import DB_PATH, STORAGE, engine
from .repositories import postgres, sqlite


@asynccontextmanager
async def lifespan(app: FastAPI):
    if STORAGE == "sqlite":
        sqlite.init_db(DB_PATH)
    elif STORAGE == "postgres":
        postgres.init_db(engine)
    yield
    engine.dispose()
```

(Si tu `main.py` importaba `init_db` desde `.repositories.sqlite`, reemplazá ese import por el de arriba.)

**P6. La fixture de tests contra Postgres: `tests/conftest.py`.** Pytest carga este archivo solo, y sus fixtures quedan disponibles en todos los tests:

```python
# tests/conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.dependencies import get_repository
from app.main import app
from app.repositories.postgres import PostgresTaskRepository, init_db

TEST_URL = os.getenv(
    "TASKFLOW_TEST_DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_test",
)


@pytest.fixture(scope="session")
def pg_engine():
    engine = create_engine(TEST_URL, pool_pre_ping=True)
    try:
        init_db(engine)
    except OperationalError:
        pytest.fail("Postgres no responde: `docker compose up -d db` y creá taskflow_test (P1)")
    yield engine
    engine.dispose()


@pytest.fixture
def pg_client(pg_engine):
    with pg_engine.begin() as con:
        con.execute(text("TRUNCATE tasks RESTART IDENTITY"))   # tabla vacía e ids desde 1

    def override():
        with pg_engine.begin() as con:
            yield PostgresTaskRepository(con)

    app.dependency_overrides[get_repository] = override
    yield TestClient(app)
    app.dependency_overrides = {}
```

Y un primer test en `tests/test_tasks_pg.py`, que es donde van a ir los tests de los ejercicios:

```python
# tests/test_tasks_pg.py
def test_create_task_in_postgres(pg_client):
    r = pg_client.post("/tasks/", json={"title": "Primera en Postgres"})
    assert r.status_code == 201
    assert r.json()["id"] == 1                 # RESTART IDENTITY: cada test arranca en 1
    assert r.json()["status"] == "backlog"     # lo puso el server_default de la base
```

✅ **Verificación de la preparación:**

```bash
pytest -q                                              # 8 passed: los 7 del lab + el de Postgres
TASKFLOW_STORAGE=postgres uvicorn app.main:app --reload
# en otra terminal:
curl -s -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" -d '{"title": "Diseñar el tablero"}'
docker compose exec db psql -U taskflow -d taskflow_dev -c "SELECT id, title, status FROM tasks;"
git status --short                                     # ni app/services/ ni app/routes/
```

Dos cosas tienen que cumplirse. La tarea aparece en `taskflow_dev` y sobrevive a un reinicio del servidor. Y, como en el paso 12 del lab, el tercer adaptador entró sin tocar el service ni el router. Commiteá y mergeá `s05-postgres` antes de arrancar los ejercicios.

---

### 🟢 Básico 1 — Cubrir los huecos de la batería de tests

Los tests del lab no cubren dos casos del contrato. Agregá a `tests/test_tasks_pg.py`, con la fixture `pg_client`:

- un test que mueva una tarea **inexistente** (`/tasks/999/status`) y espere 404;
- un test que cree una tarea con `title` vacío y espere 422, y que además verifique que **no quedó ninguna fila** en Postgres (`GET /tasks/` vacío).

**Sabés que lo lograste cuando:**

- `pytest -q` pasa con 2 tests más que antes;
- si comentás temporalmente el `except TaskNotFound` del router, tu test de 404 falla y el resto no;
- con `docker compose stop db`, los dos tests fallan (y con `docker compose start db` vuelven a pasar): prueba de que corren contra el contenedor.

<details> <summary>Pistas</summary>

- El 404 no necesita crear nada antes: `pg_client` te da la tabla vacía (`TRUNCATE`).
- El 422 del título vacío lo produce `Field(min_length=1)`, no tu código: el service ni se entera. Si tu test da 201, revisá `schemas.py`.
- Sin el `except TaskNotFound`, la excepción sin manejar no se convierte en 404: por eso el test cae.

</details>

### 🟢 Básico 2 — El diagrama de estados como test

La tabla `ALLOWED_TRANSITIONS` tiene que coincidir exactamente con el diagrama de estados de 4.7. Escribí un test con `pg_client` que recorra **las 9 combinaciones** (3 estados de origen × 3 de destino) contra el endpoint y verifique que cada una devuelve 200 o 409 según el diagrama.

**Sabés que lo lograste cuando:**

- `pytest -q -v` muestra 9 casos (uno por combinación) y todos pasan contra Postgres;
- si agregás `TaskStatus.done` al set de `backlog` en el service, exactamente un caso falla;
- podés explicar por qué, al terminar `pytest`, `taskflow_test` solo conserva las tareas del **último** test que corrió: mirala con `docker compose exec db psql -U taskflow -d taskflow_test -c "SELECT * FROM tasks;"`.

<details> <summary>Pistas</summary>

- `@pytest.mark.parametrize("origen,destino,esperado", [...])` genera un test por fila.
- Para poner una tarea en `done` tenés que pasar por `in_progress`: armate un helper que lleve una tarea nueva al estado de origen usando solo transiciones válidas.
- Mover al mismo estado (por ejemplo, `backlog → backlog`) también es 409 según el diagrama.
- La respuesta a la última pregunta está en la primera línea de `pg_client`.

</details>

### 🟡 Intermedio 1 — `GET /tasks/{task_id}`

Agregá el endpoint para ver una tarea sola. Tiene que devolver 200 con `TaskOut` si existe y 404 si no. Respetá las capas: el router no llama al repository, y el service expone un método `get` que lanza `TaskNotFound`.

**Sabés que lo lograste cuando:**

- dos tests nuevos con `pg_client` pasan (existe → 200 con el `title` correcto; no existe → 404);
- `tests/test_arquitectura.py` sigue en verde;
- con `TASKFLOW_STORAGE=postgres uvicorn app.main:app --reload`, `curl -s -i http://127.0.0.1:8000/tasks/1` devuelve 200 con la misma tarea que ves en `docker compose exec db psql -U taskflow -d taskflow_dev -c "SELECT * FROM tasks WHERE id = 1;"`;
- no modificaste ningún adaptador.

<details> <summary>Pistas</summary>

- El `Protocol` ya tiene `get`: no hace falta tocar ningún repository. Si te encontrás editando `memory.py`, `sqlite.py` o `postgres.py`, algo está mal ubicado.
- `move` ya tiene la lógica de "buscar o lanzar `TaskNotFound`": podés extraerla a `get` y reutilizarla en `move`.
- Ojo con el orden de rutas: `/{task_id}` con `task_id: int` no choca con `/` ni con `/{task_id}/status`.

</details>

### 🟡 Intermedio 2 — Prioridad: un campo nuevo atraviesa todas las capas

Agregá `priority` a la tarea: un `Enum` con `low`, `medium` y `high`, **default `medium`**, que el cliente puede mandar al crear. Sumá el filtro `GET /tasks/?priority=high`, combinable con `?status=`.

**Sabés que lo lograste cuando:**

- con `pg_client`, crear sin `priority` devuelve `"priority": "medium"`, y con `"priority": "urgente"` devuelve 422;
- `GET /tasks/?status=backlog&priority=high` devuelve solo las que cumplen las dos condiciones (test con `pg_client` y al menos 3 tareas mezcladas);
- la columna existe **en la base**: `docker compose exec db psql -U taskflow -d taskflow_dev -c "\d tasks"` la muestra con su default;
- el adaptador en memoria también la soporta (los tests del lab siguen en verde);
- anotaste en `docs/tradeoff-journal.md` qué hiciste con la tabla `tasks` que ya existía en `taskflow_dev` y en `taskflow_test`.

<details> <summary>Pistas</summary>

- Contá los lugares que tocaste: schemas, `Protocol`, adaptadores, service, router. Esa cuenta es la razón por la que Ng dice que los datos son lo más difícil de cambiar.
- `create_all` **no agrega columnas** a una tabla que ya existe (el mismo límite que en S04). Tenés dos caminos para las dos bases. Uno es `ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium';` con `docker compose exec db psql ...`. El otro es `DROP TABLE tasks;` para que el `lifespan` y la fixture la recreen, que es válido con datos de prueba. Elegí uno y registralo: es el problema que S07 resuelve con Alembic.
- Con SQLAlchemy Core, el `WHERE` dinámico no necesita juntar strings: encadená `stmt = stmt.where(tasks.c.priority == priority.value)` solo si vino el filtro, como ya hace `list_tasks` con `status`.
- ¿Querés que la base también rechace `'urgente'` si alguien escribe por fuera de la API? Un `CheckConstraint` en la tabla lo resuelve. Lo retomás en S07.

</details>

### 🔴 Desafío 1 — Una sola batería de tests para todos los adaptadores + `DELETE`

Dos partes que se apoyan entre sí:

**Parte A — tests de contrato del repository.** Escribí una fixture `any_client` **parametrizada** para que cada test corra tres veces:

- con `InMemoryTaskRepository`;
- con `SqliteTaskRepository` sobre un archivo temporal;
- con `PostgresTaskRepository` sobre `taskflow_test`, en el contenedor.

Si los tres adaptadores cumplen el mismo `Protocol`, tienen que pasar exactamente los mismos tests.

**Parte B — borrar tareas con regla de negocio.** Agregá `DELETE /tasks/{task_id}` con esta regla:

- solo se pueden borrar tareas en `backlog`;
- si la tarea está en otro estado → 409;
- si no existe → 404;
- si se borra → 204 sin body.

Esto sí requiere extender el `Protocol` y los tres adaptadores.

Cerrá con dos cosas. Actualizá los diagramas de componentes y de estados (¿`DELETE` es una transición a un estado final?). Y agregá una entrada en el journal sobre "borrado físico vs borrado lógico (marcar como archivada)". Numerala con el siguiente número libre cuando la agregues: TJ-004 queda reservada para la decisión de almacenamiento de M07·S06.

**Sabés que lo lograste cuando:**

- `pytest -q -v` muestra cada test con tres variantes (`[memory]`, `[sqlite]`, `[postgres]`) y todas pasan con el contenedor levantado;
- los tests de `DELETE` (204, 404, 409 desde `in_progress`) pasan en las tres variantes;
- en la variante `[postgres]`, después del 204 la fila ya no está en `taskflow_test`: verificalo desde el test con una consulta directa sobre `pg_engine`;
- `tests/test_arquitectura.py` sigue en verde y el service sigue sin importar FastAPI.

<details> <summary>Pistas</summary>

- `@pytest.fixture(params=["memory", "sqlite", "postgres"], ids=...)` + `request.param` adentro de la fixture.
- Para SQLite, usá `tmp_path`, llamá a `init_db(...)` y overrideá `get_repository` con un generador que abra y cierre la conexión.
- Para Postgres, pedí `pg_engine` con `request.getfixturevalue("pg_engine")` y repetí el `TRUNCATE` y el override de `pg_client`.
- En Postgres, el borrado es `delete(tasks).where(tasks.c.id == task_id)`. El resultado tiene `rowcount`, que sirve para saber si había algo que borrar.
- El 204 se declara en el decorador (`status_code=204`) y el endpoint no devuelve nada.
- Si un test pasa en `[memory]` y falla en `[postgres]`, encontraste una diferencia real entre adaptadores (tipos, orden, ids): no es un bug del test, es el valor de esta batería.

</details>

### 🔴 Desafío 2 (opcional) — Front en otro origen: CORS a mano

Serví `static/index.html` desde **otro puerto** y hacelo funcionar contra la API corriendo sobre Postgres (`TASKFLOW_STORAGE=postgres uvicorn app.main:app --reload`).

1. Copiá `static/` a una carpeta `front/` y cambiá las rutas de `fetch` para que apunten a `http://127.0.0.1:8000/tasks/...`.
2. Serví esa carpeta con `python -m http.server 5173` desde `front/` y abrí `http://127.0.0.1:5173/index.html`.
3. Observá el error en la consola del navegador. Agregá `CORSMiddleware` en `main.py` (con `app.add_middleware`, como en S04) solo con ese origen y solo con los métodos que usa la UI.

**Sabés que lo lograste cuando:**

- con `allow_methods` en su default, listar funciona y **crear y mover fallan** (el `POST` y el `PATCH` bloqueados por CORS en la consola);
- al agregar los métodos necesarios, crear y mover funcionan;
- las tareas que creaste desde el front de `:5173` aparecen en `taskflow_dev` (`docker compose exec db psql -U taskflow -d taskflow_dev -c "SELECT id, title, status FROM tasks;"`).

Registrá en el journal por qué el default del lab era servir la UI desde FastAPI.

<details> <summary>Pistas</summary>

- El origen del front es `http://127.0.0.1:5173`: protocolo, dominio y puerto, exacto. `localhost` no es lo mismo que `127.0.0.1`.
- Como `api()` manda `Content-Type: application/json` en todos los requests, hasta el `GET` dispara un preflight (un `OPTIONS` previo). El `GET` pasa porque está en el default de `allow_methods`; el `POST` y el `PATCH`, no.
- `Content-Type` no hace falta agregarlo a `allow_headers`: `CORSMiddleware` lo acepta siempre. Lo que hay que habilitar es el método.
- No uses `allow_origins=["*"]` para "que ande": el ejercicio es entender qué habilitás.

</details>

---

## 7. Ruta de estudio sugerida

El orden tiene dependencias reales: sin la forma del proyecto no se entiende dónde va cada pieza, y sin `Dependencies with yield` los overrides de los tests no tienen sentido.

```mermaid
flowchart TD
    A["1. Best practices for Claude Code<br/>25 min"] --> B["2. Bigger Applications<br/>20 min"]
    B --> C["3. Contrato: Path params Enum, Extra Models,<br/>Response Model, Status Code, Fields<br/>40 min"]
    B --> D["4. sqlite3 (tutorial, placeholders, context manager, Row)<br/>25 min"]
    D --> E["5. SQLite In-Memory + Appropriate Uses<br/>20 min"]
    C --> F["6. Dependencies with yield + SQL Databases<br/>25 min"]
    E --> F
    F --> G["7. Query Params, Body Updates, Handling Errors, MDN 409<br/>30 min"]
    G --> H["8. Testing + Overrides + pytest fixtures<br/>35 min"]
    G --> I["9. Static Files + MDN fetch<br/>20 min"]
    G --> J["10. Lifespan, FastAPI CLI, Uvicorn Settings<br/>20 min"]
    H --> K["11. C4 Component + Mermaid flowchart, sequence, state<br/>30 min"]
    I --> L["Opcional: CORS + HTTPX + enum + Tutorial<br/>35 min"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class F foco
```

1. **Antes de la clase (~45 min):** 1 y 2. Llegás sabiendo cómo vas a dirigir al agente y qué forma tiene el proyecto.
2. **Durante o justo después del lab (~1 h 50 min):** 3 a 7, en paralelo con los pasos 4–12 de la guía. Leé cada página cuando llegás al paso que la usa.
3. **Para cerrar el entregable (~1 h 25 min):** 8 a 11.
4. **Si te sobra tiempo o tu equipo eligió un front aparte:** el bloque opcional.

Si hoy leés una sola cosa, que sea la 6: es el nodo que une todo.

---

## 8. Checklist de autoevaluación

- [ ] Puedo explicar, sin mirar los apuntes, por qué `TaskCreate` no tiene `id`, `status` ni `created_at`.
- [ ] Puedo explicar la diferencia entre un 409 y un 422 con un ejemplo de TaskFlow.
- [ ] Puedo señalar en mi código dónde vive la regla de transiciones y por qué no está en el router ni en el front.
- [ ] Puedo cambiar la persistencia de memoria a SQLite y mostrar con `git status` qué archivos cambiaron (y cuáles no).
- [ ] Puedo explicar por qué `":memory:"` de SQLite no sirve con una conexión por request.
- [ ] Puedo explicar qué hace `app.dependency_overrides` en la fixture `client` y qué pasaría si no lo limpiara.
- [ ] Puedo explicar por qué las tareas desaparecen con `--reload` en modo memoria y qué pasaría con `--workers 2`.
- [ ] Puedo decir cuándo haría falta CORS en TaskFlow y por qué hoy no.
- [ ] Mi diagrama de componentes y mi diagrama de secuencia usan los mismos nombres que mi código.
- [ ] Tengo tres entradas TJ con alternativa descartada y "qué me haría cambiar de idea".
- [ ] Puedo levantar el Postgres de TaskFlow con Docker Compose, sumar un adaptador sin tocar service ni router, y correr los tests contra `taskflow_test`.

---

## 9. Preguntas de repaso

1. En TaskFlow cambiaste de un `dict` a SQLite sin tocar el service ni el router. ¿Qué decisiones de diseño lo hicieron posible, y qué cambio de requisitos te obligaría a tocar el service de todas formas?
2. Un compañero propone validar las transiciones de estado en el router "porque ahí ya está el `try/except`". ¿Qué le contestás? ¿Hay algún escenario donde la regla debería bajar todavía más, a la base de datos?
3. Le pedís al agente el prototipo y te dice "listo, lo probé en `/docs` y anda". ¿Qué le faltó, qué le pedirías en el próximo prompt y cómo verificarías vos que la arquitectura en capas se respetó?
4. Tu equipo tiene que defender `PATCH /tasks/{id}/status` frente a `POST /tasks/{id}/move`. Argumentá a favor de una y decí qué perderías.
5. El prototipo usa SQLite y un repo en memoria. Explicá qué se rompe en cada uno si mañana TaskFlow corre con dos procesos de servidor detrás de un balanceador, y qué pieza de la arquitectura actual te va a facilitar la migración.

---

## 10. Recursos adicionales

**Imprescindible**

- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) — cómo dirigir al agente: verificación que pueda correr, plan mode, `CLAUDE.md` efectivo. (25 min)
- [Bigger Applications - Multiple Files — FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/) — el esqueleto de carpetas y `APIRouter` por recurso. (20 min)
- [Dependencies with yield — FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/) — abrir y cerrar la conexión por request; la cadena repository → service → endpoint. (15 min)
- [`sqlite3` — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html) — tutorial, placeholders, conexión como context manager, `sqlite3.Row`. (25 min)
- [In-Memory Databases — SQLite](https://www.sqlite.org/inmemorydb.html) — por qué `":memory:"` no sirve con una conexión por request. (5 min)
- [Handling Errors — FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/) — `HTTPException`, `detail` y el 422 automático. (10 min)
- [Testing — FastAPI](https://fastapi.tiangolo.com/tutorial/testing/) — `TestClient` y tests síncronos con pytest. (10 min)
- [Testing Dependencies with Overrides — FastAPI](https://fastapi.tiangolo.com/advanced/testing-dependencies/) — un repositorio limpio por test. (8 min)
- [Component diagram — C4 model](https://c4model.com/diagrams/component) — qué va en el diagrama de componentes. (5 min)

**Recomendado**

- [Path Parameters — Predefined values — FastAPI](https://fastapi.tiangolo.com/tutorial/path-params/) — el `Enum` de `TaskStatus`. (5 min)
- [Extra Models — FastAPI](https://fastapi.tiangolo.com/tutorial/extra-models/) — modelo de entrada vs salida. (10 min)
- [Response Model - Return Type — FastAPI](https://fastapi.tiangolo.com/tutorial/response-model/) — cómo el tipo de retorno filtra la salida. (10 min)
- [Response Status Code — FastAPI](https://fastapi.tiangolo.com/tutorial/response-status-code/) — el 201 al crear. (5 min)
- [409 Conflict — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/409) — la definición del código de la transición inválida. (3 min)
- [Fields — Pydantic](https://pydantic.dev/docs/validation/latest/concepts/fields/) — `Field(min_length=..., max_length=...)`. (10 min)
- [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/) — solo "Create an Engine" y "Create a Session Dependency", por `check_same_thread`. (10 min)
- [Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html) — cuándo SQLite alcanza y cuándo migrar. (15 min)
- [Query Parameters — FastAPI](https://fastapi.tiangolo.com/tutorial/query-params/) — el filtro `?status=`. (8 min)
- [Body - Updates — FastAPI](https://fastapi.tiangolo.com/tutorial/body-updates/) — PATCH vs PUT, `model_copy(update=...)`. (10 min)
- [How to use fixtures — pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html) — fixtures con `yield` y scopes. (15 min)
- [Lifespan Events — FastAPI](https://fastapi.tiangolo.com/advanced/events/) — inicializar la base al arrancar; `on_event` deprecado. (8 min)
- [Static Files — FastAPI](https://fastapi.tiangolo.com/tutorial/static-files/) — servir la UI desde el mismo servidor. (5 min)
- [Using the Fetch API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) — `fetch`, JSON en el body y `response.ok`. (15 min)
- [Settings — Uvicorn](https://uvicorn.dev/settings/) — `--reload`, `--host`, `--port`, `--workers`. (5 min)
- [Flowcharts Syntax — Mermaid](https://mermaid.js.org/syntax/flowchart.html) — notación del diagrama de componentes. (10 min)
- [Sequence diagrams — Mermaid](https://mermaid.js.org/syntax/sequenceDiagram.html) — `alt`/`else` para el ciclo de "mover". (10 min)
- [State diagrams — Mermaid](https://mermaid.js.org/syntax/stateDiagram.html) — la máquina de estados de la tarea. (5 min)

**Opcional**

- Andrew Ng, _AI Engineering Skills Map: Software engineering fundamentals_ (2026), secciones "Managing data" y "Designing system architectures" — el marco que abrió el módulo en S01; disponible en la biblioteca del curso. (10 min)
- [CORS (Cross-Origin Resource Sharing) — FastAPI](https://fastapi.tiangolo.com/tutorial/cors/) — solo si tu equipo arma un front aparte. (10 min)
- [QuickStart — HTTPX](https://www.python-httpx.org/quickstart/) — cliente de consola alternativo. (10 min)
- [`enum` — Support for enumerations (Python)](https://docs.python.org/3/library/enum.html) — la entrada de `StrEnum`. (5 min)
- [Tutorial - User Guide — FastAPI](https://fastapi.tiangolo.com/tutorial/) — instalación con `uv` o `pip`. (5 min)
- [FastAPI CLI](https://fastapi.tiangolo.com/fastapi-cli/) — `fastapi dev` vs `fastapi run`. (5 min)