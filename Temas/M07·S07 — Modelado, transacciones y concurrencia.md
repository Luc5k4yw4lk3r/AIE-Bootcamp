# M07·S07 — Modelado, transacciones y concurrencia + FastAPI ↔ PostgreSQL

**Módulo:** 07 — Fundamentos de Software + System Design para AI Engineers **Fecha:** [Completar por el profesor: fecha] **Duración estimada de estudio:** ~7 horas en total: lectura de recursos (~3,5 h) y ejercicios (~3,5 h). La guía práctica se hace en el lab en equipo, dentro de las 3 horas de la sesión en clase.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Modelar** el dominio completo de TaskFlow como diagrama entidad-relación —cardinalidades, tablas intermedias N:M y la membresía con rol como _association object_— y **mapearlo** a modelos SQLAlchemy 2.0.
2. **Proteger** la consistencia de los datos desde la base con `NOT NULL`, `UNIQUE`, `CHECK`, PK, FK y una política `ON DELETE` decidida relación por relación, y **explicar** qué garantiza la base y qué queda en el service.
3. **Conectar** el webserver a PostgreSQL desde la capa repository con un `SqlAlchemyTaskRepository` que cumple el `Protocol` de S05, **sin tocar** ni el service ni el router (salvo un `except`).
4. **Migrar** el esquema y los datos de SQLite a PostgreSQL con Alembic, dirigiendo al agente y **revisando** la migración autogenerada con un checklist antes de aplicarla.
5. **Reproducir** un _lost update_ entre dos sesiones, **arreglarlo** con bloqueo optimista (`version_id_col` → 409) y **contrastarlo** con el pesimista (`SELECT … FOR UPDATE`) y con los niveles de aislamiento de PostgreSQL.
6. **Decidir** el ciclo de vida del dato en TaskFlow —frescura con `updated_at` y caché, soft vs hard delete, qué pasa al borrar un usuario— y **registrar** TJ-005 (ORM) y TJ-006 (concurrencia) en el trade-off journal.

---

## 2. Resumen ejecutivo

En **M07·S05** levantaste el prototipo de TaskFlow con una sola entidad, la `Tarea`, detrás de un `Protocol` que te dejaba cambiar de un `dict` a SQLite sin tocar el service. En **M07·S06** usaste los patrones de acceso de TaskFlow para concluir que es un problema relacional, levantaste `postgres:16-alpine` con Docker Compose y mediste con `EXPLAIN` el índice del tablero. Hoy esa decisión se vuelve código.

Primero **modelás el dominio entero**: usuarios, equipos, proyectos, tareas, comentarios, etiquetas, la membresía con rol y la relación tarea↔etiqueta. Después lo **protegés en la base**, porque la base es la última línea de defensa: un `CHECK` sobre el estado de la tarea vale aunque mañana alguien escriba un script que se saltee la API. Lo mapeás con SQLAlchemy 2.0, versionás el esquema con Alembic y escribís un repository nuevo que enchufás en `dependencies.py`, igual que en S05.

No es tu primer Postgres ni tu primer SQLAlchemy: en **M07·S04** levantaste Postgres con Docker Compose, le hablaste con SQLAlchemy Core (`Table`, `engine`, `engine.begin()`) y viste que `create_all` no modifica tablas que ya existen. Lo nuevo de hoy es el **ORM declarativo**, las **migraciones** con Alembic y la **concurrencia**.

El eje conceptual es la **concurrencia**. Ana y Beto tienen el tablero abierto y mueven la misma tarjeta casi al mismo tiempo. Sin control, uno pisa al otro y la regla de transiciones de S05 se viola sin que nadie se entere. Lo vas a reproducir, lo vas a arreglar con una columna `version` y vas a ver la alternativa pesimista en dos terminales.

¿Por qué importa en tu rol? Como dice Andrew Ng en su _AI Engineering Skills Map_, los datos son relativamente difíciles de cambiar, **aun cuando los agentes ayuden con las migraciones**. El agente te va a generar la migración en segundos; revisarla es trabajo tuyo, porque un error de datos es de los más caros de revertir.

---

## 3. Conceptos clave / glosario

Solo los términos **nuevos** de hoy.

**Modelado**

- **Cardinalidad:** cuántas instancias de una entidad se relacionan con cuántas de otra, con mínimo y máximo: una tarea pertenece a **exactamente un** proyecto; un proyecto tiene **cero o más** tareas. _Analogía:_ cuántas llaves abren cuántas puertas.
- **Tabla intermedia (N:M):** tabla con dos FK que representa una relación muchos-a-muchos: `task_labels` une tareas con etiquetas. _Analogía:_ el registro de inscripciones entre alumnos y materias.
- **Association object:** una tabla intermedia que además lleva datos propios (el `role` de `project_members`) y por eso se mapea como una clase del ORM. _Analogía:_ la inscripción que además guarda la nota.
- **Normalización:** organizar las tablas para que cada dato viva en un solo lugar y dependa solo de la clave de su tabla. Evita que actualizar un dato obligue a tocarlo en diez filas. _Analogía:_ tener un único contacto por persona en la agenda, no una copia por cada grupo de WhatsApp.
- **`ON DELETE`:** qué hace la base con las filas que referencian a otra que se borra: impedirlo (`RESTRICT`/`NO ACTION`), borrarlas también (`CASCADE`) o dejar la referencia en `NULL` (`SET NULL`). _Analogía:_ qué pasa con los inquilinos cuando se demuele el edificio.

**ORM y migraciones**

- **ORM declarativo:** el segundo estilo de SQLAlchemy, que S04 nombró sin usar: en vez de `Table` + `Column` y consultas explícitas (Core), clases de Python mapeadas a tablas, y el ORM traduce las operaciones sobre esos objetos a SQL. _Analogía:_ un traductor simultáneo entre Python y SQL.
- **Session (SQLAlchemy):** el objeto con el que el ORM habla con la base: lleva la transacción en curso, recuerda qué objetos cargaste (_identity map_) y qué cambiaste (_unit of work_), y lo manda todo junto en el flush/commit. _Analogía:_ el carrito de compras: vas agregando y recién al pagar se confirma todo.
- **Identity map:** dentro de una sesión, cada fila se representa con **un solo objeto**: si pedís dos veces la tarea 1, recibís la misma instancia (mientras tu código la siga referenciando: ver el error común de 4.6). _Analogía:_ un único expediente por caso en la oficina.
- **Migración (Alembic):** script versionado que lleva el esquema de una revisión a la siguiente (`upgrade`) y de vuelta (`downgrade`). Las revisiones se encadenan como commits. _Analogía:_ git, pero para la estructura de la base.
- **Autogenerate:** alembic compara tus modelos con la base y **propone** una migración candidata. Es un borrador, no una verdad. _Analogía:_ el autocorrector: acierta mucho y a veces cambia "Lucía" por "Lucha".
- **Expand/contract:** cambiar una columna en dos (o más) migraciones: primero **agregás** lo nuevo y convivís con lo viejo, después migrás los datos y recién al final **quitás** lo viejo. _Analogía:_ construir el puente nuevo antes de demoler el viejo.

**Transacciones y concurrencia**

- **Savepoint:** punto de guardado dentro de una transacción: podés deshacer hasta ahí sin perder lo anterior. _Analogía:_ guardar partida antes del jefe final.
- **Lost update:** dos transacciones leen el mismo dato, cada una escribe en base a lo que leyó, y la segunda pisa a la primera sin saberlo. _Analogía:_ dos personas editando la misma planilla offline y subiendo su copia.
- **Bloqueo optimista:** no bloquea nada: cada fila lleva una `version` y el `UPDATE` solo aplica si la versión sigue siendo la que leíste. Si no, falla y el cliente recarga. _Analogía:_ reservar asiento: si cuando pagás ya no está, te avisan y elegís otro.
- **Bloqueo pesimista:** bloquea la fila al leerla (`SELECT … FOR UPDATE`) y los demás esperan hasta que termine tu transacción. _Analogía:_ llevarte la llave del baño.
- **Nivel de aislamiento:** cuánto ve una transacción de lo que hacen las otras mientras corre. En PostgreSQL: Read Committed (el default), Repeatable Read, Serializable. _Analogía:_ qué tan gruesa es la pared entre dos oficinas.
- **MVCC:** _Multi-Version Concurrency Control_: la base guarda varias versiones de cada fila para que cada sentencia vea una foto (_snapshot_) consistente. Por eso leer no bloquea escribir. _Analogía:_ mirar una foto del tablero mientras otro mueve las tarjetas reales.
- **Deadlock:** dos transacciones esperan cada una un lock que tiene la otra. PostgreSQL lo detecta y aborta una. _Analogía:_ dos autos en un puente de una mano, ninguno retrocede.

**Rendimiento y ciclo de vida**

- **N+1:** traer una lista con 1 consulta y después hacer 1 consulta más por cada elemento para cargar una relación. _Analogía:_ ir al súper una vez por cada ingrediente.
- **Soft delete:** "Borrar" marcando la fila (`archived_at`) en vez de eliminarla. _Analogía:_ mandar a la papelera en vez de vaciarla.

**Ya vistos, solo como refresco:** ACID y normalizar vs desnormalizar (M07·S06); índice compuesto y columna líder, `EXPLAIN ANALYZE`, cache-aside con TTL y `CachedTaskRepository` (M07·S06); `Protocol`, excepciones de dominio, 409 vs 422 y la tabla de transiciones (M07·S05); dependencias con `yield` y `get_db` con `engine.begin()`, SQLAlchemy Core, la URL `postgresql+psycopg://` con `pool_pre_ping` y el límite de `create_all` (M07·S04); Docker Compose y por qué el host es `db` dentro de Compose y `localhost` desde tu máquina (M07·S04); diagrama de clases y multiplicidades (MA·S05); trade-off journal `TJ-NNN` (M07·S01).

---

## 4. Notas de estudio por subtema

### El mapa de lo que vas a construir

Este es el diagrama ancla de la sesión. Compará con el de S05: el service y el `Protocol` son los mismos; cambia lo que hay abajo.

```mermaid
flowchart LR
    RT["routes/tasks.py"] --> SV["TaskService"]
    SV --> PR["TaskRepository (Protocol)"]
    DEPS["dependencies.py"] -.->|"TASKFLOW_STORAGE=postgres"| PR
    PR -->|"implementa"| CR["CachedTaskRepository<br/>(S06, opcional)"]
    CR -->|"envuelve"| SR["SqlAlchemyTaskRepository"]
    SR --> SES["Session<br/>(una por request)"]
    MOD["app/db/models.py"] --> SR
    SES --> PG[("PostgreSQL<br/>taskflow_app")]
    MOD --> ALB["Alembic<br/>migrations/"]
    ALB -->|"crea y versiona el esquema"| PG

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class SR foco
```

Dos ideas para llevarte del dibujo: `models.py` alimenta **a la vez** al repository (para leer y escribir) y a Alembic (para crear el esquema), y **nadie más** crea tablas: ni `create_all`, ni pgloader, ni un `schema.sql` a mano.

---

### 4.1 Modelar entidades y relaciones: el ER de TaskFlow

**El procedimiento.** Ya lo aplicaste en MA·S05 para sacar clases de un PRD; para un modelo de datos es el mismo, con dos preguntas extra:

1. **Sustantivos → entidades.** Del plan: Usuario, Equipo, Proyecto, Tarea, Comentario, Etiqueta.
2. **Verbos → relaciones.** "Un equipo _agrupa_ proyectos", "un proyecto _contiene_ tareas", "un usuario _es responsable de_ tareas", "una tarea _lleva_ etiquetas".
3. **Cardinalidad mínima y máxima de cada lado.** ¿Una tarea puede existir sin proyecto? No → mínimo 1. ¿Puede no tener responsable? Sí → mínimo 0. ¿Cuántas etiquetas? Muchas, y cada etiqueta en muchas tareas → N:M.
4. **¿La relación tiene datos propios?** "Ana es _owner_ del proyecto X" — el rol no es de Ana ni del proyecto: es **de la relación**. Cuando pasa eso, la relación se vuelve entidad (tabla con columnas propias).

**Cómo se traduce cada cardinalidad a tablas:**

- **1:N** → FK en el lado "muchos": `tasks.project_id` apunta a `projects.id`.
- **1:N opcional** → FK _nullable_: `tasks.assignee_id` puede ser `NULL`.
- **N:M** → tabla intermedia con dos FK que forman la PK: `task_labels(task_id, label_id)`.
- **N:M con datos** → tabla intermedia con columnas extra: `project_members(project_id, user_id, role)`.

**Normalización aplicada.** Las tres primeras formas normales, en versión práctica y con contraejemplos de TaskFlow:

```sql
-- ❌ Viola 1FN: un campo con varios valores. ¿Cómo buscás "todas las tareas con 'bug'"?
CREATE TABLE tasks_mal_1 (id int, title text, labels text);   -- labels = 'bug,urgente'

-- ❌ Viola 2FN: project_name depende solo de project_id, que es PARTE de la clave (project_id, user_id).
CREATE TABLE project_members_mal (project_id int, user_id int, role text, project_name text,
                                  PRIMARY KEY (project_id, user_id));

-- ❌ Viola 3FN: team_id depende de project_id, no de la tarea (dependencia transitiva).
--    Si el proyecto cambia de equipo, hay que actualizar todas sus tareas.
CREATE TABLE tasks_mal_3 (id int PRIMARY KEY, project_id int, team_id int, title text);
```

La versión correcta es la del diagrama: etiquetas en su tabla, el nombre del proyecto solo en `projects`, y el equipo de una tarea se obtiene con un `JOIN` a `projects`. En S06 viste cuándo **conviene desnormalizar** (lecturas muy calientes); hoy el punto de partida es normalizado y cualquier desnormalización se justifica con un patrón de acceso medido.

**El ER de TaskFlow.** Es el entregable de la sesión (`docs/datos/s07-modelo-er.md`):

```mermaid
erDiagram
    USERS ||--o{ TEAM_MEMBERS : "pertenece a"
    TEAMS ||--o{ TEAM_MEMBERS : "tiene"
    TEAMS ||--o{ PROJECTS : "agrupa"
    PROJECTS ||--o{ PROJECT_MEMBERS : "da acceso"
    USERS ||--o{ PROJECT_MEMBERS : "participa con rol"
    PROJECTS ||--o{ TASKS : "contiene"
    USERS |o--o{ TASKS : "es responsable de"
    TASKS ||--o{ COMMENTS : "recibe"
    USERS |o--o{ COMMENTS : "escribe"
    PROJECTS ||--o{ LABELS : "define"
    TASKS ||--o{ TASK_LABELS : "lleva"
    LABELS ||--o{ TASK_LABELS : "se aplica en"

    USERS {
        int id PK
        string email UK
        string name
        timestamptz created_at
    }
    TEAMS {
        int id PK
        string name UK
    }
    TEAM_MEMBERS {
        int team_id PK, FK
        int user_id PK, FK
    }
    PROJECTS {
        int id PK
        int team_id FK "ON DELETE RESTRICT"
        string name "UNIQUE con team_id"
    }
    PROJECT_MEMBERS {
        int project_id PK, FK
        int user_id PK, FK
        string role "owner, member o viewer"
    }
    TASKS {
        int id PK
        int project_id FK "ON DELETE CASCADE"
        string title
        text description "nullable"
        string status "CHECK backlog, in_progress, done"
        int position
        int assignee_id FK "nullable, ON DELETE SET NULL"
        date due_date "nullable"
        int version "bloqueo optimista"
        timestamptz created_at
        timestamptz updated_at
    }
    COMMENTS {
        int id PK
        int task_id FK "ON DELETE CASCADE"
        int author_id FK "nullable, ON DELETE SET NULL"
        text body
        timestamptz created_at
    }
    LABELS {
        int id PK
        int project_id FK "ON DELETE CASCADE"
        string name "UNIQUE con project_id"
    }
    TASK_LABELS {
        int task_id PK, FK
        int label_id PK, FK
    }
```

**Cómo leerlo.** La notación es _crow's foot_: `||` es "exactamente uno", `|o` "cero o uno", `o{` "cero o más" y `|{` "uno o más". Entonces `PROJECTS ||--o{ TASKS` se lee "un proyecto tiene cero o más tareas; cada tarea pertenece exactamente a un proyecto", y `USERS |o--o{ TASKS` dice que la tarea puede no tener responsable. Los atributos llevan `PK`, `FK` o `UK` (unique).

**Dos tablas intermedias, dos estatus distintos.** `TEAM_MEMBERS` y `TASK_LABELS` son N:M puros: en el ORM se declaran con `secondary=`. `PROJECT_MEMBERS` lleva `role`, así que es un **association object**, una clase propia:

```python
# app/db/models.py (extracto) — N:M puro vs association object
task_labels = Table(                                    # N:M puro: solo dos FK
    "task_labels", Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
)

class Task(Base):
    ...
    labels: Mapped[list[Label]] = relationship(secondary=task_labels)

class ProjectMember(Base):                              # association object: tiene "role"
    __tablename__ = "project_members"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(10))
    project: Mapped[Project] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship()
```

Con el association object, agregar a Ana como owner es crear un objeto: `session.add(ProjectMember(project_id=1, user_id=ana.id, role="owner"))`.

> ⚠️ **Error común:** no declares **a la vez** un `relationship(secondary="project_members")` y la clase `ProjectMember` escribiendo sobre la misma tabla. La doc de SQLAlchemy advierte que los datos se pueden leer y escribir de forma inconsistente; si necesitás las dos vistas, la de `secondary=` va con `viewonly=True`.

**Lo que el diagrama no puede expresar.** "Solo puede ser miembro de un proyecto quien es miembro del equipo del proyecto." Una FK simple no lo cubre: queda como regla en el service (o como FK compuesta, si querés profundizar). Es la frontera entre **lo que garantiza la base** y **lo que garantiza el código**, y conviene tenerla escrita.

> 📝 **Nota para el profesor:** el modelo asume tres decisiones que conviene confirmar en clase: roles **por proyecto** (`project_members.role`) y `team_members` sin rol, siguiendo el plan ("roles por proyecto"); etiquetas **por proyecto** (`UNIQUE (project_id, name)`), mientras que el ejemplo de S06 las tenía globales; y que el grupo cursó MA·S05, porque la sección referencia multiplicidades como ya vistas. Si no lo cursó, sumá cinco minutos de multiplicidad.

📎 Para profundizar: [Basic Relationship Patterns — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html) · [Entity Relationship Diagrams — Mermaid](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)

---

### 4.2 Datos limpios y consistentes: restricciones y `ON DELETE`

"Datos limpios" en TaskFlow quiere decir que la base **rechaza** lo que no tiene sentido, aunque llegue por un camino que no es la API (un script de copia, un `psql`, un agente que escribe directo). Pydantic valida el request; la base valida **el dato**, venga de donde venga.

**Las restricciones que vas a usar y qué rechaza cada una:**

```sql
-- Cada una de estas sentencias FALLA contra el esquema de TaskFlow:
INSERT INTO tasks (project_id, title, status) VALUES (1, 'X', 'archivada');   -- CHECK status_valid
INSERT INTO tasks (project_id, title) VALUES (1, NULL);                        -- NOT NULL en title
INSERT INTO tasks (project_id, title) VALUES (999, 'X');                       -- FK: el proyecto 999 no existe
INSERT INTO labels (project_id, name) VALUES (1, 'bug'), (1, 'bug');           -- UNIQUE (project_id, name)
INSERT INTO project_members VALUES (1, 1, 'admin');                            -- CHECK role_valid
```

En SQLAlchemy se declaran en el modelo, y Alembic las lleva a la base:

```python
class Task(Base):
    ...
    __table_args__ = (
        CheckConstraint("status IN ('backlog', 'in_progress', 'done')", name="status_valid"),
        Index("ix_tasks_board", "project_id", "status", "position"),   # el índice del tablero de S06
    )
```

El `CHECK` sobre `status` es el `TaskStatus` de S05 repetido en la base, y a propósito: si mañana un script escribe `'archivada'`, la base lo frena.

**Tres datos de la doc de PostgreSQL que evitan errores:**

- **El `ON DELETE` por defecto es `NO ACTION`**: si no decís nada, borrar un proyecto con tareas falla. `RESTRICT` se comporta parecido pero es más estricto (no se puede diferir al final de la transacción).
- **Declarar una FK no crea un índice sobre la columna que referencia.** La doc dice que suele ser buena idea crearlo. Por eso `tasks.assignee_id`, `comments.task_id` y `projects.team_id` llevan `index=True`. `labels.project_id` y `tasks.project_id` ya quedan cubiertos por ser columna líder de otro índice (`UNIQUE (project_id, name)` y `ix_tasks_board`), la misma regla de columna líder que viste en S06.
- **En un `UNIQUE`, dos `NULL` no se consideran iguales** por defecto. Si alguna vez necesitás "único incluso con NULL", existe `NULLS NOT DISTINCT`.

**La política `ON DELETE` de TaskFlow, relación por relación.** No hay una respuesta universal: cada FK responde "¿qué significa esta fila si desaparece la otra?".

|Relación|Acción|Por qué|
|---|---|---|
|`projects.team_id` → `teams`|`RESTRICT`|No se borra un equipo con proyectos vivos: primero hay que decidir qué pasa con ellos|
|`tasks.project_id` → `projects`|`CASCADE`|Una tarea no tiene sentido fuera de su proyecto|
|`tasks.assignee_id` → `users`|`SET NULL`|Si se va la persona, la tarea queda sin responsable, no desaparece|
|`comments.task_id` → `tasks`|`CASCADE`|El comentario es parte de la tarea|
|`comments.author_id` → `users`|`SET NULL`|Se conserva la conversación sin el dato personal ("usuario eliminado")|
|`project_members.*`, `team_members.*`, `task_labels.*`|`CASCADE`|Filas de relación: sin uno de los extremos, no existen|
|`labels.project_id` → `projects`|`CASCADE`|Las etiquetas son por proyecto|

En el modelo, cada decisión es un argumento:

```python
assignee_id: Mapped[int | None] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"), index=True     # nullable por el "| None"
)
```

> ⚠️ **Error común — "en SQLite andaba":** SQLite trae las FK **desactivadas por defecto** y hay que activarlas por conexión con `PRAGMA foreign_keys = ON`. El prototipo de S05 nunca lo hizo, así que tus datos pueden traer referencias rotas que PostgreSQL va a rechazar al copiarlas. Si el script de copia falla por una FK, es un hallazgo, no un bug del script.

> ⚠️ **Error común:** `SET NULL` sobre una columna `NOT NULL` es una contradicción que PostgreSQL te deja declarar y te explota recién cuando borrás. Si elegís `SET NULL`, la columna tiene que ser `Mapped[... | None]`.

> 📝 **Nota para el profesor:** la tabla es el default del material. Si preferís `CASCADE` en `comments.author_id` (borrar un usuario borra sus comentarios), cambia la discusión de ciclo de vida de 4.5: ahí se argumenta a favor de `SET NULL`.

📎 Para profundizar: [5.4. Constraints — PostgreSQL 16](https://www.postgresql.org/docs/16/ddl-constraints.html) · [SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html) (secciones 1–2)

---

### 4.3 Transacciones ACID en la práctica

En S06 definiste ACID. Hoy lo mapeás a TaskFlow, letra por letra:

- **A — Atomicidad.** Reordenar una columna del tablero toca varias filas: o se mueven todas o ninguna.
- **C — Consistencia.** Los `CHECK` y las FK de 4.2: ninguna transacción puede dejar una tarea con estado inválido o apuntando a un proyecto inexistente.
- **I — Aislamiento.** Lo que ve Beto mientras Ana está a mitad de mover una tarea. Es el tema de 4.4.
- **D — Durabilidad.** Cuando `COMMIT` vuelve OK, el cambio sobrevive aunque se corte la luz.

**Toda sentencia es una transacción.** PostgreSQL ejecuta **toda** sentencia dentro de una transacción; si no escribís `BEGIN`, pone un `BEGIN`/`COMMIT` implícito alrededor. Cuando necesitás que varias sentencias sean _all-or-nothing_, las envolvés vos:

```sql
BEGIN;
UPDATE tasks SET position = position + 1 WHERE project_id = 1 AND status = 'done';
UPDATE tasks SET status = 'done', position = 0 WHERE id = 42;
COMMIT;          -- o ROLLBACK; y no pasó nada
```

**Savepoints: deshacer una parte sin perder el resto.** Querés etiquetar una tarea con tres etiquetas y, si una ya está, ignorarla sin tirar las otras:

```sql
BEGIN;
INSERT INTO task_labels VALUES (42, 1);
SAVEPOINT antes_de_bug;
INSERT INTO task_labels VALUES (42, 2);     -- falla: ya existía (PK duplicada)
ROLLBACK TO antes_de_bug;                   -- deshace solo esto
INSERT INTO task_labels VALUES (42, 3);
COMMIT;                                     -- quedan la 1 y la 3
```

En SQLAlchemy, el savepoint es `session.begin_nested()` (que antes hace flush de lo pendiente):

```python
from sqlalchemy.exc import IntegrityError

for label_id in (1, 2, 3):
    try:
        with session.begin_nested():                       # SAVEPOINT
            session.execute(task_labels.insert().values(task_id=42, label_id=label_id))
    except IntegrityError:
        pass                                               # ROLLBACK TO SAVEPOINT: sigue con la próxima
session.commit()
```

**La `Session` de SQLAlchemy.** Tres comportamientos que tenés que conocer:

1. **Autobegin:** la sesión abre la transacción sola apenas hacés algo (un `get`, un `add`). No hay `session.begin()` obligatorio.
2. **Unit of work:** los cambios sobre objetos (`task.status = "done"`) se acumulan y se mandan en el **flush**, que ocurre como mucho en el `commit()`.
3. **`expire_on_commit`:** por defecto, al confirmar, los objetos se marcan como vencidos. El próximo acceso a `task.title` hace un `SELECT` nuevo. Es correcto (ves el dato real), pero con `echo=True` vas a ver una consulta "de más".

**¿Dónde va el `commit`?** La doc de SQLAlchemy da dos reglas: mantener el ciclo de vida de la sesión **separado y externo** a las funciones que acceden a los datos, y en una app web crear la sesión al principio del request, hacer commit al final de los requests que escriben y cerrarla al terminar. En TaskFlow eso queda así:

- **Abrir y cerrar la sesión:** `dependencies.py` (con `yield`), nunca el repository.
- **Hacer `commit`:** explícito en los métodos de escritura del repository (`add`, `update_status`).

¿Por qué no en el código de salida de la dependencia, que parece más prolijo? Por la trampa central de la sesión: con una dependencia con `yield`, **por defecto el código de salida corre después de enviar la respuesta**. Si el `commit()` vive ahí y falla (un `UNIQUE` violado, un conflicto de versión), el cliente **ya recibió un 200** por un cambio que no se guardó.

```python
# ❌ Parece prolijo, pero el commit corre DESPUÉS de mandar la respuesta
def get_session():
    with SessionLocal() as session:
        yield session
        session.commit()          # si falla acá, el cliente ya tiene su 200

# ✅ TaskFlow: el commit ocurre dentro del endpoint, donde el router todavía puede responder 409
def update_status(self, task_id, status):
    ...
    self.session.commit()
```

**¿Y el `get_db` de S04?** Hacía justamente lo del ❌: `with engine.begin()` alrededor del `yield`, con el commit en el código de salida. Para aquel CRUD alcanzaba, porque el error esperable (un email duplicado) lo detectaba el service antes de escribir y, si igual pasaba, Postgres lo rechazaba en el `execute`, dentro del handler. Con el ORM cambia: los cambios viajan en el flush, que ocurre recién en el `commit()`, y ahí es donde aparece el conflicto de versión de 4.4. Si ese commit corriera después de la respuesta, el cliente ya tendría su 200.

FastAPI ofrece una alternativa, `Depends(..., scope="function")`, que corre el código de salida alrededor de la función del endpoint, **antes** de la respuesta. El material se queda con el commit explícito en el repository porque deja el error visible donde el router lo puede traducir.

**El trade-off de esa decisión.** Con el commit en el repository, **cada método de escritura es su propia transacción**. Si mañana un caso de uso necesita dos escrituras atómicas (crear tarea + registrar actividad), el repository no alcanza: la transacción tiene que subir al service (una unidad de trabajo que abarque las dos). Anotalo: es la clase de decisión que el agente toma sin avisarte.

> ⚠️ **Error común:** después de un error dentro de una transacción, PostgreSQL rechaza todo lo que sigue hasta que hagas `ROLLBACK`. En SQLAlchemy, si atrapás una excepción de la base y querés seguir usando la sesión, primero `session.rollback()`.

📎 Para profundizar: [3.4. Transactions — tutorial de PostgreSQL 16](https://www.postgresql.org/docs/16/tutorial-transactions.html) · [Session Basics — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) · [Transactions and Connection Management — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html) · [Dependencies with yield — FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)

---

### 4.4 Concurrencia: lost update, optimista vs pesimista, aislamiento

**El problema de TaskFlow no son las lecturas.** PostgreSQL usa MVCC: cada sentencia ve un _snapshot_, y según su doc, leer nunca bloquea escribir y escribir nunca bloquea leer. Por eso el tablero (lectura intensiva, el P1 de S06) no se frena mientras alguien mueve una tarjeta. El problema son **dos escrituras que se basan en una lectura vieja**.

**Las anomalías, con un ejemplo TaskFlow cada una:**

- **Dirty read:** Beto ve el `done` que Ana escribió pero todavía no confirmó; Ana hace rollback y Beto actuó sobre algo que nunca existió. PostgreSQL no lo permite en ningún nivel.
- **Non-repeatable read:** dentro de la misma transacción, Beto lee la tarea 1 en `in_progress`, Ana la confirma en `done`, Beto la relee y ve `done`.
- **Phantom read:** Beto cuenta las tareas `done` del proyecto (5), Ana confirma una tarea nueva en `done`, Beto repite la consulta y aparecen 6.
- **Lost update:** Ana y Beto leen `in_progress`; Ana escribe `done`; Beto escribe `backlog` basándose en lo que leyó. El `done` de Ana desaparece.
- **Write skew:** la regla es "todo proyecto tiene al menos un owner". Hay dos owners. Cada uno, en paralelo, cuenta owners (2), ve que puede irse y se pasa a `member`. Cada escritura toca **una fila distinta**, ninguna pisa a la otra… y el proyecto queda sin owners.

**El lost update de TaskFlow no es solo "el último gana".** Mirá la regla de transiciones de S05: `in_progress → backlog` vale, `done → backlog` no. Beto valida su movimiento contra el estado que **leyó** (`in_progress`), pero cuando escribe la tarea ya está en `done`. Resultado: se aplicó una transición prohibida. Es un _check-then-act_ sobre datos obsoletos, y es exactamente lo que hace el repository de S05:

```python
# S05 (SQLite): lee en el service, escribe sin condición en el repo
self.con.execute("UPDATE tasks SET status = ? WHERE id = ?", (status.value, task_id))
```

**Solución 1 — bloqueo optimista con `version`.** Cada tarea lleva un contador. El `UPDATE` exige que la versión siga siendo la leída y la incrementa:

```sql
UPDATE tasks SET status = 'backlog', version = 4
WHERE id = 1 AND version = 3;       -- si alguien ya la pasó a 4: 0 filas afectadas
```

En SQLAlchemy son dos líneas en el modelo, y el ORM arma ese `WHERE` solo:

```python
class Task(Base):
    ...
    version: Mapped[int] = mapped_column(server_default="1")    # NOT NULL, como pide la doc
    __mapper_args__ = {"version_id_col": version}
```

Si el `UPDATE` matchea cero filas, el ORM lanza `sqlalchemy.orm.exc.StaleDataError`. El repository la traduce a una excepción de dominio y el router a un **409**:

```mermaid
sequenceDiagram
    participant A as Ana, request 1
    participant PG as PostgreSQL
    participant B as Beto, request 2
    A->>PG: SELECT tarea 1 → in_progress, version 3
    B->>PG: SELECT tarea 1 → in_progress, version 3
    A->>PG: UPDATE status done, version 4 WHERE version = 3
    PG-->>A: 1 fila, COMMIT
    B->>PG: UPDATE status backlog, version 4 WHERE version = 3
    PG-->>B: 0 filas → StaleDataError
    B-->>B: rollback y 409 al cliente
```

¿Por qué Beto no se queda esperando? En Read Committed, cuando su `UPDATE` encuentra la fila modificada por una transacción ya confirmada, PostgreSQL **reevalúa el `WHERE` sobre la versión nueva** de la fila. `version = 3` ya no se cumple, y el `UPDATE` afecta 0 filas.

> ⚠️ **Error común — los masivos se saltean el control:** `version_id_col` **solo actúa en el flush** de objetos. Un `session.execute(update(Task).where(...).values(status="done"))` no pasa por ahí y pisa sin mirar la versión. Si el agente te genera un `update()` masivo para "optimizar", perdiste la protección.

**Solución 2 — bloqueo pesimista con `SELECT … FOR UPDATE`.** Bloqueás la fila al leerla. Según la doc de PostgreSQL, `FOR UPDATE` bloquea a las demás transacciones que intenten `UPDATE`, `DELETE` o `SELECT FOR UPDATE` sobre esas filas **hasta que termine la transacción actual**:

```sql
BEGIN;
SELECT status, version FROM tasks WHERE id = 1 FOR UPDATE;   -- otro que haga lo mismo, espera
-- validás la transición con el estado REAL
UPDATE tasks SET status = 'done', version = version + 1 WHERE id = 1;
COMMIT;                                                       -- recién acá se libera
```

En el ORM: `session.get(Task, task_id, with_for_update=True)` o `select(Task).where(...).with_for_update()`. Con `nowait=True` agregás `NOWAIT`: en vez de esperar, falla en el acto, y la API puede responder 409 sin dejar el request colgado. Existe también `SKIP LOCKED`, que saltea las filas bloqueadas: sirve para colas de trabajo (lo vas a ver en S09), no para uso general. El locking clause no se puede combinar con `GROUP BY`, `DISTINCT` ni agregados: `SELECT count(*) … FOR UPDATE` no vale.

**¿Cuál elegir?**

||Optimista (`version`)|Pesimista (`FOR UPDATE`)|
|---|---|---|
|Supone|Conflictos raros|Conflictos frecuentes|
|En el conflicto|El segundo falla (409) y recarga o reintenta|El segundo **espera** (o falla con `NOWAIT`)|
|Costo|Cero locks; hay que manejar el reintento|Locks retenidos; riesgo de esperas y deadlocks|
|Sirve entre requests (tablero abierto 5 min)|**Sí**, si la versión viaja con el cliente|**No**: no se retiene un lock entre requests|
|Caso TaskFlow|Editar título, mover desde la UI|Reordenar posiciones de una columna (varias filas)|

**El caso "tablero abierto hace cinco minutos".** Ana abre el tablero, se va a tomar un café, vuelve y mueve una tarjeta que Beto editó en el medio. Ninguna transacción de base dura cinco minutos, así que el control tiene que **viajar con el cliente**: el front manda la `version` que vio, y el servidor la compara. Es el patrón _Optimistic Offline Lock_, de David Rice en el catálogo de _Patterns of Enterprise Application Architecture_ de Martin Fowler: prevenir conflictos entre transacciones de negocio concurrentes detectando el conflicto y haciendo rollback. HTTP tiene su versión estándar: el cliente manda `If-Match` con el `ETag` que recibió y, si no coincide, el servidor responde `412 Precondition Failed`. La alternativa simple es un `expected_version` en el body y 409. El contrato definitivo se diseña en S10; hoy lo practicás en el ejercicio 🔴.

**Niveles de aislamiento en PostgreSQL.** Según la doc de PostgreSQL 16:

- **Read Committed es el default.** Cada sentencia ve lo confirmado hasta ese momento.
- PostgreSQL implementa en la práctica **tres** niveles distintos: Read Uncommitted se comporta como Read Committed, y su Repeatable Read ya no permite phantom reads.
- En **Repeatable Read**, la transacción ve una foto fija desde su primera consulta. Si intentás actualizar una fila que otro confirmó después, recibís `ERROR: could not serialize access due to concurrent update`, y la doc indica abortar y **reintentar la transacción entera** desde el principio. Estos errores de serialización tienen SQLSTATE `40001`.
- **Serializable** está pensado para detectar también los casos tipo write skew, abortando una de las transacciones con el mismo tipo de error.

Podés subir el aislamiento de **una** operación sin cambiar el de toda la app:

```python
# Solo esta transacción corre en SERIALIZABLE (ej.: quitar un owner, el caso write skew)
session.connection(execution_options={"isolation_level": "SERIALIZABLE"})
# ...o para todo el engine (no recomendado para TaskFlow):
# create_engine(URL, isolation_level="REPEATABLE READ")
```

**El patrón de reintento.** Ante un error de serialización, lo correcto es repetir **la transacción entera** (volver a leer, volver a validar, volver a escribir), con un límite:

```python
from sqlalchemy.exc import DBAPIError


def run_with_retry(session_factory, operation, attempts: int = 3):
    """operation(session) hace TODA la transacción: leer, validar, escribir, commit."""
    for attempt in range(1, attempts + 1):
        with session_factory() as session:
            try:
                return operation(session)
            except DBAPIError as exc:
                session.rollback()
                sqlstate = getattr(exc.orig, "sqlstate", None)
                if sqlstate != "40001" or attempt == attempts:
                    raise                     # otro error, o se acabaron los intentos
```

**Deadlocks.** Dos transacciones que toman locks en orden inverso se esperan mutuamente. PostgreSQL detecta el ciclo solo y aborta una de las dos con un error de deadlock; su doc aclara que cuál se aborta es difícil de predecir, y que la mejor defensa es **tomar los locks siempre en el mismo orden**. En TaskFlow eso se traduce en una línea al reordenar:

```sql
SELECT id FROM tasks WHERE project_id = 1 AND status = 'done' ORDER BY id FOR UPDATE;
```

> 💡 **Tip:** la transacción abortada por deadlock también se reintenta entera. El mismo `run_with_retry` sirve si aceptás también el SQLSTATE `40P01` (`deadlock_detected`, según el apéndice de códigos de error de PostgreSQL), además del `40001`.

📎 Para profundizar (PostgreSQL 16): [13.1. Introduction (MVCC)](https://www.postgresql.org/docs/16/mvcc-intro.html) · [13.2. Transaction Isolation](https://www.postgresql.org/docs/16/transaction-iso.html) · [13.3. Explicit Locking](https://www.postgresql.org/docs/16/explicit-locking.html) · [SELECT — The Locking Clause](https://www.postgresql.org/docs/16/sql-select.html) · [Appendix A. Error Codes](https://www.postgresql.org/docs/16/errcodes-appendix.html) · [Configuring a Version Counter — SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/versioning.html) · [Optimistic Offline Lock](https://martinfowler.com/eaaCatalog/optimisticOfflineLock.html) · [If-Match — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match)

---

### 4.5 Frescura y ciclo de vida del dato

**Frescura: `updated_at`.** Saber cuándo cambió una tarea sirve para el cliente ("editada hace 2 min"), para la caché y para depurar:

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
)
```

> ⚠️ **Error común:** `onupdate` lo aplica **el ORM** en cada `UPDATE` que pasa por el flush. Un `UPDATE` hecho a mano en `psql`, o un `update()` masivo, **no** lo toca. Si querés que lo garantice la base, eso es un trigger (fuera de alcance hoy).

**La caché de S06 sobre el repo nuevo.** El `CachedTaskRepository` envuelve ahora al `SqlAlchemyTaskRepository` sin cambios: invalidar al escribir sigue siendo el mecanismo y el TTL la red de seguridad. El `get` previo a mover sigue **sin caché**, por la misma razón que en S06 (la regla de transiciones tiene que ver el estado real) y, desde hoy, por una razón más: **la `version` que se compara tiene que ser la de la base**. Un `get` cacheado con versión vieja convierte cada movimiento en un 409.

**Read-your-writes.** Si Ana mueve una tarea y al recargar el tablero la ve en la columna vieja (porque la lista venía de caché), para ella el sistema "no guardó". La regla mínima: toda escritura invalida la lista cacheada de ese proyecto **antes** de responder.

**Ciclo de vida del dato.** Todo dato pasa por **creación → uso → archivo → borrado**, y cada etapa es una decisión de diseño:

- **Soft delete (archivar).** Una tarea "borrada" desde la UI pasa a `archived_at = now()`. Se puede restaurar y la historia no se pierde. El precio: **todas** las consultas tienen que filtrar, y es muy fácil olvidarse.

```python
archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

stmt = select(Task).where(Task.project_id == project_id, Task.archived_at.is_(None))
```

- **Hard delete.** `DELETE` real. Las FK con `CASCADE` se llevan comentarios y etiquetas.
- **Retención.** "Las tareas archivadas hace más de 90 días se borran" es un job periódico:

```sql
DELETE FROM tasks WHERE archived_at < now() - interval '90 days';
```

Si TaskFlow guardara actividad histórica por años, la retención se resolvería mejor con **particionado**: según la doc de PostgreSQL, las cargas y borrados masivos se hacen agregando o quitando particiones, lo que evita el costo de un `DELETE` grande. La misma doc da una regla práctica: vale la pena cuando la tabla superaría la memoria física del servidor. **TaskFlow hoy no lo necesita**; lo retomás en S19.

**¿Qué pasa cuando se borra un usuario?** Es donde el modelado toca la ley. El art. 17 del RGPD da a la persona el derecho a obtener la supresión de sus datos personales sin dilación indebida, en los supuestos que enumera. Con la política de 4.2:

```sql
DELETE FROM users WHERE id = 7;
-- tasks.assignee_id = 7    -> NULL   (la tarea queda sin responsable)
-- comments.author_id = 7   -> NULL   (el comentario queda, la UI muestra "usuario eliminado")
-- project_members, team_members de 7 -> borradas (CASCADE)
```

Con `CASCADE` en `comments.author_id` borrarías también la conversación entera, y los demás miembros perderían contexto. `SET NULL` conserva el contexto sin el dato personal. Ojo: si el **cuerpo** del comentario tiene datos personales, `SET NULL` no alcanza; privacidad y gobierno en serio quedan fuera de esta sesión.

📎 Para profundizar: [5.11. Table Partitioning — PostgreSQL 16](https://www.postgresql.org/docs/16/ddl-partitioning.html) (solo 5.11.1) · [Art. 17 RGPD](https://gdpr-info.eu/art-17-gdpr/) (compilación no oficial del texto, apartado 1)

---

### 4.6 FastAPI ↔ PostgreSQL desde la capa repository

**El ORM declarativo de SQLAlchemy 2.0.** Una clase por tabla, con `Mapped[...]` y `mapped_column(...)`. La regla que más errores te ahorra al leer lo que genera el agente: **la anotación decide la nulabilidad**.

```python
title: Mapped[str] = mapped_column(String(200))             # NOT NULL
description: Mapped[str | None] = mapped_column(Text)        # NULL
due_date: Mapped[date | None]                                # NULL, tipo inferido: DATE
```

Otras tres piezas del modelo que conviene entender:

- **`Identity()`** en las PK: en PostgreSQL 10+ reemplaza a `SERIAL`. Sin argumentos genera `GENERATED BY DEFAULT AS IDENTITY`, que **acepta ids explícitos**. Lo necesitás para copiar los datos de SQLite con sus ids. (El `schema.sql` de S06 usaba `GENERATED ALWAYS`, que los rechaza.)
- **`status` como `String` + `CHECK`**, no como `sqlalchemy.Enum`: repite la regla de `TaskStatus` en la base y esquiva una limitación de autogenerate con los enums.
- **`DateTime(timezone=True)`** para que las fechas sean `timestamptz`, como dice el ER.

**El engine y el driver.** Es el mismo `engine` de `config/db.py` en S04, y la URL lleva el driver explícito por el mismo motivo: instalás psycopg 3 (`psycopg[binary]`), pero según la doc de SQLAlchemy 2.0 el dialecto PostgreSQL usa **psycopg2** por defecto. Con `postgresql://` a secas, SQLAlchemy busca psycopg2 y falla al no encontrarlo. La URL lleva siempre el driver explícito:

```python
engine = create_engine(
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_app",
    pool_pre_ping=True,     # descarta conexiones muertas del pool antes de usarlas
    echo=True,              # loguea cada SQL: tu herramienta de "entender para dirigir"
)
SessionLocal = sessionmaker(engine)     # UNA vez, a nivel de módulo
```

Lo nuevo respecto de S04 es `sessionmaker`: en vez de pedirle al engine una `Connection` (Core), le pedís una `Session` (ORM).

**El repository nuevo.** Cumple el mismo `Protocol` de S05 (`add`, `list_tasks`, `get`, `update_status`) y convierte el objeto ORM al contrato Pydantic: **el objeto ORM nunca sale del repository**.

```python
def get(self, task_id: int) -> TaskOut | None:
    task = self.session.get(Task, task_id)
    if task is None:
        return None
    self._read[task_id] = task               # referencia fuerte: el identity map es débil
    return self._to_out(task)

def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
    task = self.session.get(Task, task_id)   # la MISMA instancia que leyó get() (identity map)
    task.status = status.value
    try:
        self.session.commit()                # UPDATE ... WHERE id = :id AND version = :v_leída
    except StaleDataError:
        self.session.rollback()
        raise ConcurrentUpdate(task_id)
    return self._to_out(task)
```

**Por qué funciona sin tocar el service.** `TaskService.move()` de S05 hace `repo.get(id)`, valida la transición y llama a `repo.update_status(id, nuevo)`. Las dos llamadas usan **la misma sesión** del request, así que `session.get()` en `update_status` devuelve la misma instancia del identity map, con la `version` que se validó. Si otro request confirmó en el medio, el `UPDATE` matchea 0 filas y la regla de transiciones **nunca se aplica sobre un estado viejo**. `ConcurrentUpdate` vive en un módulo neutro, `app/errors.py`: así el repository no importa nada del service (regla de dependencia de S04) y el router no importa nada de `repositories/` (lo exige `tests/test_arquitectura.py` de S05).

> ⚠️ **Error común — el identity map guarda referencias débiles:** según la doc de SQLAlchemy, los objetos dentro de la sesión están _weakly referenced_: si tu código deja de apuntarlos, salen de la sesión y el garbage collector los libera (salvo los pendientes, los marcados para borrar o los que tienen cambios sin flushear). `get()` devuelve un `TaskOut`, no el objeto ORM, así que sin el `self._read[task_id] = task` la instancia se libera al salir de `get()`, y `update_status` **relee la fila de la base con la versión nueva**: el `UPDATE` pasa, y la transición prohibida también. Sin esa línea, un `PATCH` que compite con otro movimiento responde 200 y deja `done → backlog`; con ella, 409 (lo probás en el 🔴 Desafío 1).

**N+1: el tablero con etiquetas.** Por defecto, las relaciones se cargan _lazy_: el primer acceso a `task.labels` dispara un `SELECT`. Si el tablero muestra las etiquetas de 50 tarjetas, son 1 + 50 consultas:

```python
# ❌ N+1: una consulta por tarea al tocar t.labels
for t in session.scalars(select(Task).where(Task.project_id == 1)):
    print(t.title, [l.name for l in t.labels])

# ✅ 2 consultas en total: tareas + todas sus etiquetas con un IN (...)
from sqlalchemy.orm import selectinload
stmt = select(Task).where(Task.project_id == 1).options(selectinload(Task.labels))
```

La doc de SQLAlchemy describe `selectinload()` como en general la mejor estrategia para colecciones; `joinedload()` va mejor para muchos-a-uno (`task.project`). Y `raiseload()` convierte cualquier carga perezosa en error: ponelo en los tests y el N+1 deja de ser silencioso.

> ⚠️ **Error común — lo que el agente va a imitar:** el tutorial oficial de FastAPI sobre bases SQL usa **SQLModel** (construido sobre SQLAlchemy y Pydantic) y `create_all` al arrancar. Para TaskFlow no sirve tal cual: `create_all` **no altera tablas existentes** (lo viste en S04, donde el `lifespan` corría `meta.create_all(engine)`), así que en cuanto hay datos lo reemplaza Alembic (el propio tutorial recomienda Alembic para producción). Y TaskFlow separa el contrato (`TaskOut`, Pydantic) del modelo de persistencia (ORM): esa es la decisión TJ-005.

> ⚠️ **Error común:** `order_by(Task.status)` ordena **alfabéticamente** (`backlog`, `done`, `in_progress`), el mismo error común de S06.

📎 Para profundizar: [Table Configuration with Declarative](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html) · [Relationship Loading Techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html) · [State Management — Session Referencing Behavior](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html) · [PostgreSQL dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html) · [Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html) · [Installation — psycopg 3](https://www.psycopg.org/psycopg3/docs/basic/install.html) · de contraste: [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

### 4.7 Migrar de SQLite a PostgreSQL con Alembic

**Por qué migraciones y no `create_all`.** Una migración es un archivo versionado que dice cómo pasar el esquema de la revisión N a la N+1 y de vuelta. Alembic guarda en la tabla `alembic_version` en qué revisión está cada base, así que tu laptop, la de tu compañero y producción pueden estar en revisiones distintas y saber exactamente qué les falta. Y PostgreSQL tiene **DDL transaccional**: si una migración falla a la mitad, no deja el esquema a medias.

**Por qué "de" SQLite y no "sobre" SQLite.** SQLite casi no soporta `ALTER`; Alembic lo compensa con un _batch mode_ que recrea la tabla y copia los datos. Solo lo necesitás si querés mantener Alembic también contra el SQLite de los tests. Para TaskFlow, el esquema nuevo nace en PostgreSQL y los datos viejos se **copian**.

**El flujo: generar → revisar → aplicar.**

```bash
alembic revision --autogenerate -m "esquema inicial taskflow"   # genera el borrador
# ABRIR migrations/versions/<rev>_esquema_inicial_taskflow.py y REVISAR
alembic upgrade head                                            # aplicar
alembic current                                                 # en qué revisión estás
alembic downgrade -1                                            # volver una atrás
```

La doc de Alembic es tajante: _"It is always necessary to manually review and correct the candidate migrations that autogenerate produces."_ No es burocracia. Autogenerate detecta tablas y columnas agregadas o quitadas, cambios de nulabilidad, índices, `UNIQUE` con nombre, FK y cambios de tipo, pero **no detecta renames** (salen como _drop_ + _add_) ni restricciones sin nombre.

**El rename que borra datos.** Supongamos que en el modelo renombrás `assignee` a `assignee_name`. Autogenerate propone:

```python
# ❌ Lo que genera autogenerate: borra la columna CON SUS DATOS y crea una vacía
def upgrade():
    op.add_column("tasks", sa.Column("assignee_name", sa.String(100), nullable=True))
    op.drop_column("tasks", "assignee")

# ✅ Lo que tiene que decir
def upgrade():
    op.alter_column("tasks", "assignee", new_column_name="assignee_name")

def downgrade():
    op.alter_column("tasks", "assignee_name", new_column_name="assignee")
```

**Nombres de restricciones.** Para poder borrar o modificar una restricción en una migración futura, tiene que tener un nombre predecible. Una línea en `Base` lo resuelve:

```python
NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)
```

La plantilla `ck` usa `%(constraint_name)s`: por eso todo `CheckConstraint` lleva `name=`. El `CHECK` de estado termina llamándose `ck_tasks_status_valid`.

**Expand/contract: `assignee` (texto) → `assignee_id` (FK).** En S05, `assignee` era un string libre; el ER lo quiere como FK a `users`. Hacerlo en un paso sería perder los nombres. Se hace en etapas:

1. **Expand (hoy):** se agrega `assignee_id` nullable y `assignee` queda. Conviven.
2. **Migrar datos (cuando haya usuarios reales, S14):** una migración de datos llena `assignee_id` buscando el usuario por nombre.
3. **Contract (después):** cuando nada lee `assignee`, se borra en otra migración.

```python
# Paso 2, una migración futura (no se corre hoy): backfill
def upgrade():
    op.execute("""
        UPDATE tasks t SET assignee_id = u.id
        FROM users u
        WHERE t.assignee_id IS NULL AND t.assignee = u.name
    """)
```

**Columnas `NOT NULL` sobre tablas con datos.** En una migración posterior, agregar una columna `NOT NULL` sin default a una tabla con filas falla, porque las filas existentes no tienen valor. Por eso `version` lleva `server_default="1"`.

**Copiar los datos.** El esquema lo crea Alembic; los datos los copia un script (paso 6 de la guía). Dos detalles:

- Se insertan los ids originales, así que la secuencia de la identity sigue en 1 y el próximo `INSERT` choca con `duplicate key`. Se corrige con `setval(pg_get_serial_sequence('tasks', 'id'), max(id))`: `pg_get_serial_sequence` devuelve la secuencia también para columnas identity.
- La alternativa es **pgloader**, que migra SQLite → PostgreSQL en una línea y por defecto crea tablas, índices y resetea secuencias. Si lo usás, que cargue **solo datos** (`data only`) sobre el esquema de Alembic. Si pgloader crea el esquema, Alembic pierde el control de la historia.

> ⚠️ **Error común:** si el `lifespan` de S05 crea tablas al arrancar, que lo haga solo para `sqlite`. Con `postgres`, Alembic y la app se pelearían por el esquema: nada de `meta.create_all` como en el `lifespan` de S04 o en el de los ejercicios de S05.

> ⚠️ **Error común:** si la password de la URL tiene `%`, `config.set_main_option` de Alembic la interpreta (usa la interpolación de `configparser`): duplicalo, `%%`.

> 📝 **Nota para el profesor:** el material crea una **base nueva `taskflow_app`** en el mismo servidor de S06, gestionada solo por Alembic; la base `taskflow` queda como evidencia del `EXPLAIN` de TJ-004. El cambio `assignee` → `assignee_id` se deja en fase _expand_ (backfill y drop, en S14). Si preferís resolverlo hoy, el backfill de arriba sirve, pero hace falta crear usuarios antes.

📎 Para profundizar: [Tutorial — Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) · [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) · [The Importance of Naming Constraints](https://alembic.sqlalchemy.org/en/latest/naming.html) · [Batch Migrations](https://alembic.sqlalchemy.org/en/latest/batch.html) · [SQLite to Postgres — pgloader](https://pgloader.readthedocs.io/en/latest/ref/sqlite.html) · [`pg_get_serial_sequence` — PostgreSQL 16](https://www.postgresql.org/docs/16/functions-info.html)

---

### 4.8 Entregables: el diagrama ER y las decisiones del journal

El ER de 4.1 va en `docs/datos/s07-modelo-er.md`, **junto a la tabla `ON DELETE`** de 4.2: el diagrama dice qué se relaciona con qué, y la tabla dice qué pasa cuando algo desaparece. Dos reglas para que el `erDiagram` no se rompa: la nulabilidad va en el comentario (sin `?` en el atributo) y los comentarios entre comillas, sin paréntesis.

Y dos entradas nuevas en el trade-off journal:

- **TJ-005 — ORM.** Alternativas: SQLAlchemy 2.0 puro, SQLModel (lo que usa el tutorial de FastAPI), SQL a mano con `psycopg`. Default propuesto: SQLAlchemy, con los modelos ORM separados del contrato Pydantic.
- **TJ-006 — Concurrencia.** Optimista con `version_id_col` para mover y editar, pesimista con `FOR UPDATE` en orden de `id` para reordenar, Read Committed como aislamiento global. _Qué me haría cambiar de idea:_ una tasa medida de 409 alta.

### Mapa de relaciones entre recursos

Cómo se apoyan entre sí los recursos de la sesión. El nodo resaltado es el que une la teoría de concurrencia con el código:

```mermaid
flowchart TD
    NG["Ng: Managing data"] --> REL["SQLAlchemy: relationship patterns"]
    MER["Mermaid: erDiagram"] --> REL
    REL --> CON["Postgres: constraints y ON DELETE"]
    CON --> SQF["SQLite: foreign keys"]
    REL --> DEC["SQLAlchemy: declarative Mapped"]
    DEC --> DIA["SQLAlchemy: dialecto y engines"]
    PSY["psycopg 3: install"] --> DIA
    TXT["Postgres: tutorial transactions"] --> SES["SQLAlchemy: Session basics"]
    SES --> DEP["FastAPI: dependencies with yield"]
    DIA --> REPO["Lab: SqlAlchemyTaskRepository"]
    DEP --> REPO
    MVCC["Postgres: MVCC"] --> ISO["Postgres: transaction isolation"]
    ISO --> LCK["Postgres: explicit locking"]
    ISO --> VER["SQLAlchemy: version counter"]
    OOL["Rice: Optimistic Offline Lock"] --> VER
    VER --> REPO
    DEC --> NAM["Alembic: naming conventions"]
    NAM --> ALT["Alembic: tutorial"]
    ALT --> AUT["Alembic: autogenerate"]
    AUT --> MIG["Lab: migración y copia"]
    SQF --> MIG
    MIG --> REPO
    REPO --> LOAD["SQLAlchemy: loading y N+1"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class VER foco
```

Lo que el diagrama no muestra: el tutorial de FastAPI con SQLModel y el Full Stack FastAPI Template son **de contraste** (se leen después del lab, para comparar decisiones); partitioning y el art. 17 alimentan la discusión de ciclo de vida sin dependencias; `threading.Barrier`, `If-Match` y los tests con rollback son stretch.

---

## 5. Guía práctica paso a paso — Lab: TaskFlow sobre PostgreSQL

**Qué vas a tener al final:** TaskFlow corriendo sobre PostgreSQL con el ER completo, el esquema versionado con Alembic, los datos del prototipo copiados, el lost update reproducido y arreglado, un test de concurrencia y el diagrama ER commiteado.

**Prerrequisitos**

- El repo `taskflow` con lo de S05–S06 (tag `s06`), el venv activado y los tests de S05 en verde.
- Docker con el `docker-compose.yml` y el `.env` de S06 (servicio `db` con `postgres:16-alpine`, usuario y password `taskflow` por defecto, puerto `127.0.0.1:5432`). Está documentado en el material de S06; no se repite acá. Si ya tenés otro Postgres en el 5432, mapeá `5433:5432` y cambiá el puerto en `TASKFLOW_DATABASE_URL`.
- El archivo `taskflow.db` del prototipo (si no lo tenés, el lab funciona igual: se copian 0 tareas).

**Placeholders:** `<rev>` es el id que Alembic le asigna a tu migración; `<N>` es un número que depende de tus datos.

---

### Paso 1 — Rama y dependencias

```bash
git checkout -b s07-postgres
pip install "sqlalchemy>=2.0,<2.1" "psycopg[binary]" alembic
```

- `sqlalchemy>=2.0,<2.1`: a la fecha de consulta del material (23/09/2026, PyPI), la última estable es la **2.0.54** y la 2.1 existe solo como _release candidate_ (2.1.0rc2). Fijar `<2.1` evita traer una pre-release o, cuando salga, una versión mayor que no se probó en clase.
- `psycopg[binary]`: psycopg 3 en versión binaria, la que su doc recomienda para desarrollo (para producción recomienda la instalación local; lo retomás en S16). Soporta PostgreSQL 10 a 18 y Python 3.10 a 3.15.
- `alembic`: el material sigue la doc de Alembic 1.20.

Agregá las tres líneas a tu `requirements.txt`. Si hiciste los ejercicios de S05, `sqlalchemy` y `psycopg[binary]` ya están: solo sumás `alembic`.

**✅ Verificación:**

```bash
python -c "import sqlalchemy, psycopg, alembic; print(sqlalchemy.__version__)"
# salida esperada: 2.0.<algo>
```

---

### Paso 2 — Base nueva `taskflow_app`

```bash
docker compose up -d db
docker compose exec db psql -U taskflow -d taskflow -c "CREATE DATABASE taskflow_app;"
export TASKFLOW_DATABASE_URL="postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_app"
```

La base `taskflow` de S06 (con las 200.000 tareas del seed y el `schema.sql` a mano) queda intacta como evidencia de TJ-004. `taskflow_app` la va a manejar **solo Alembic**.

`TASKFLOW_DATABASE_URL` cumple el papel de `DATABASE_URL` en S04; lleva el prefijo `TASKFLOW_` como el resto de las variables del proyecto. El host es `localhost` y no `db` porque la API corre en tu venv, fuera de la red de Compose: es la "alternativa sin Docker" de S04.

**✅ Verificación:**

```bash
docker compose exec db psql -U taskflow -d taskflow_app -c "\dt"
# salida esperada: "Did not find any relations." (la base existe y está vacía)
```

> ⚠️ Las credenciales `taskflow:taskflow` son los defaults del `.env` local de S06. Nunca las uses fuera de tu máquina.

---

### Paso 3 — Modelos SQLAlchemy (`app/db/models.py`)

Creá `app/db/__init__.py` vacío y `app/db/models.py`:

```python
# app/db/models.py
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Identity, Index, MetaData,
    String, Table, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NAMING = {  # convención recomendada por Alembic: nombres predecibles para migrar
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)


team_members = Table(
    "team_members", Base.metadata,
    Column("team_id", ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

task_labels = Table(
    "task_labels", Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    members: Mapped[list[User]] = relationship(secondary=team_members)
    projects: Mapped[list["Project"]] = relationship(back_populates="team")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    team: Mapped[Team] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
    memberships: Mapped[list["ProjectMember"]] = relationship(back_populates="project")
    __table_args__ = (UniqueConstraint("team_id", "name"),)


class ProjectMember(Base):  # association object: la relación tiene un dato propio (role)
    __tablename__ = "project_members"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(10))
    project: Mapped[Project] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship()
    __table_args__ = (
        CheckConstraint("role IN ('owner', 'member', 'viewer')", name="role_valid"),
    )


class Label(Base):
    __tablename__ = "labels"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50))
    __table_args__ = (UniqueConstraint("project_id", "name"),)


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), server_default="backlog")
    position: Mapped[int] = mapped_column(server_default="0")
    assignee: Mapped[str | None] = mapped_column(String(100))  # legado S05 (expand/contract)
    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    due_date: Mapped[date | None]
    version: Mapped[int] = mapped_column(server_default="1")  # NOT NULL: lo pide la doc
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="tasks")
    labels: Mapped[list[Label]] = relationship(secondary=task_labels)
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="task", order_by="Comment.created_at"
    )

    __table_args__ = (
        CheckConstraint("status IN ('backlog', 'in_progress', 'done')", name="status_valid"),
        Index("ix_tasks_board", "project_id", "status", "position"),  # el índice del tablero de S06
    )
    __mapper_args__ = {"version_id_col": version}


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    task: Mapped[Task] = relationship(back_populates="comments")
```

**✅ Verificación:**

```bash
python -c "from app.db.models import Base; print(sorted(Base.metadata.tables))"
# salida esperada:
# ['comments', 'labels', 'project_members', 'projects', 'task_labels', 'tasks', 'team_members', 'teams', 'users']
```

Nueve tablas de negocio. Si falla con un error de import, revisá que exista `app/db/__init__.py`.

---

### Paso 4 — Inicializar Alembic

Desde la raíz del repo:

```bash
alembic init migrations
```

Crea `alembic.ini`, y en `migrations/` los archivos `env.py`, `script.py.mako` y la carpeta `versions/`. Editá `migrations/env.py` en dos lugares:

```python
# migrations/env.py — arriba, junto a los otros imports
import os
from app.db.models import Base

# ...después de la línea "config = context.config":
config.set_main_option("sqlalchemy.url", os.environ["TASKFLOW_DATABASE_URL"])

# ...y reemplazá "target_metadata = None" por:
target_metadata = Base.metadata
```

Así la URL sale de la variable de entorno (no queda una password en `alembic.ini`) y autogenerate sabe contra qué modelos comparar.

**✅ Verificación:**

```bash
alembic current
# no tiene que dar error; todavía no muestra ninguna revisión
```

Si falla porque no encuentra el módulo `app`, corré los comandos desde la raíz del repo o anteponé `PYTHONPATH=.`.

---

### Paso 5 — Generar la migración con el agente, revisarla y aplicarla

Pedíselo al agente en plan mode, con la revisión como parte del encargo:

```text
Leé app/db/models.py y migrations/env.py. Generá la migración inicial con
`alembic revision --autogenerate -m "esquema inicial taskflow"`. NO la apliques.
Después revisá el archivo generado contra este checklist y reportame cada ítem
como OK o con lo que corregiste:
1. Están las 9 tablas de negocio y upgrade() no tiene ningún drop_table (en downgrade() sí van).
2. Los CheckConstraint tienen nombre (ck_tasks_status_valid, ck_project_members_role_valid).
3. Cada FK tiene este ondelete: projects.team_id RESTRICT; tasks.assignee_id y
   comments.author_id SET NULL; todas las demás CASCADE.
4. Están ix_tasks_board y los índices de assignee_id, comments.task_id y projects.team_id.
5. No hay ningún par drop_column + add_column que en realidad sea un rename.
6. downgrade() es el inverso real de upgrade().
```

**Después revisala vos**, con el archivo abierto: el reporte del agente no reemplaza tu lectura. El checklist completo:

1. ¿Están las 9 tablas de negocio y ningún `drop_table` inesperado?
2. ¿Los `CheckConstraint` salieron con nombre (`ck_tasks_status_valid`, `ck_project_members_role_valid`)?
3. ¿Cada FK tiene el `ondelete` que decidió el equipo?
4. ¿Está `ix_tasks_board` y están los índices de las FK?
5. **¿Hay algún par `drop_column` + `add_column` que en realidad es un rename?** Reescribilo con `op.alter_column(..., new_column_name=...)`.
6. ¿El `downgrade()` es el inverso real del `upgrade()`?
7. (Para migraciones futuras sobre tablas con filas) ¿una columna nueva `NOT NULL` trae `server_default`?

Cuando pasa el checklist:

```bash
alembic upgrade head
alembic current
# salida esperada: <rev> (head)
docker compose exec db psql -U taskflow -d taskflow_app -c "\dt"
# salida esperada: 10 tablas -> alembic_version, comments, labels, project_members,
#   projects, task_labels, tasks, team_members, teams, users
docker compose exec db psql -U taskflow -d taskflow_app -c "\d tasks"
# mirá al pie: ck_tasks_status_valid, ix_tasks_board, ix_tasks_assignee_id y las dos FK
#   propias (project_id ON DELETE CASCADE, assignee_id ON DELETE SET NULL); abajo, en
#   "Referenced by", las de comments y task_labels
```

**✅ Prueba de ida y vuelta:** `alembic downgrade -1` tiene que dejar solo `alembic_version`, y `alembic upgrade head` volver a las 10 tablas. Si el downgrade falla, el ítem 6 no estaba OK.

---

### Paso 6 — Copiar los datos del prototipo (`scripts/copy_sqlite_to_pg.py`)

```python
# scripts/copy_sqlite_to_pg.py — copia los datos del prototipo (el esquema ya lo creó Alembic)
import os
import sqlite3
from datetime import datetime

from sqlalchemy import create_engine, text

src = sqlite3.connect(os.getenv("TASKFLOW_DB", "taskflow.db"))
src.row_factory = sqlite3.Row
rows = src.execute(
    "SELECT id, title, description, assignee, status, created_at FROM tasks"
).fetchall()

engine = create_engine(os.environ["TASKFLOW_DATABASE_URL"])
with engine.begin() as conn:                                  # todo o nada
    conn.execute(text("INSERT INTO teams (id, name) VALUES (1, 'Equipo demo') ON CONFLICT DO NOTHING"))
    conn.execute(text("INSERT INTO projects (id, team_id, name) VALUES (1, 1, 'Inbox') ON CONFLICT DO NOTHING"))
    if rows:
        conn.execute(
            text("""INSERT INTO tasks (id, project_id, title, description, assignee, status, position, created_at)
                    VALUES (:id, 1, :title, :description, :assignee, :status, :id, :created_at)"""),
            [dict(r) | {"created_at": datetime.fromisoformat(r["created_at"])} for r in rows],
        )
    for table in ("teams", "projects", "tasks"):              # la secuencia sigue en 1: moverla
        conn.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT max(id) FROM {table}))"
        ))
print(f"copiadas {len(rows)} tareas")
```

Qué hace y por qué:

- Crea el equipo "Equipo demo" y el proyecto "Inbox" (id 1): el ER exige que toda tarea tenga proyecto, y el contrato de S05 (`TaskCreate`) no lo tiene. El repository va a usar `default_project_id=1`. Las rutas por proyecto (`/projects/{id}/tasks`) se diseñan en S10.
- `engine.begin()` es una transacción: si una fila falla (por ejemplo, un `status` inválido que SQLite aceptó), **no se copia nada**.
- El `setval` final mueve cada secuencia al máximo id copiado.

```bash
python scripts/copy_sqlite_to_pg.py
# salida esperada: copiadas <N> tareas
```

**✅ Verificación:**

```bash
docker compose exec db psql -U taskflow -d taskflow_app -c "SELECT count(*), max(id) FROM tasks;"
# count = <N> del paso anterior
```

> ⚠️ Si el script falla por un `CHECK` o una FK, no lo "arregles" desactivando la restricción: el problema está en los datos de SQLite (que no validaba FK por defecto). Corregí el dato en origen y volvé a correr.

---

### Paso 7 — El repository nuevo

Creá la excepción en un módulo neutro (el `Protocol` de `repositories/base.py` **no cambia**):

```python
# app/errors.py — ni service ni repositories: lo importan el repo y el router
class ConcurrentUpdate(Exception):
    """Otro request modificó la tarea entre la lectura y la escritura."""
```

```python
# app/repositories/sqlalchemy_repo.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from ..db.models import Task
from ..errors import ConcurrentUpdate
from ..schemas import TaskCreate, TaskOut, TaskStatus


class SqlAlchemyTaskRepository:
    def __init__(self, session: Session, default_project_id: int = 1) -> None:
        self.session = session              # la sesión la abre y la cierra dependencies.py
        self.default_project_id = default_project_id
        self._read: dict[int, Task] = {}     # lo que leyó get() en este request (error común de 4.6)

    @staticmethod
    def _to_out(t: Task) -> TaskOut:        # ORM -> contrato Pydantic: el ORM no sale del repo
        return TaskOut(
            id=t.id, title=t.title, description=t.description,
            assignee=t.assignee, status=TaskStatus(t.status), created_at=t.created_at,
        )

    def add(self, data: TaskCreate) -> TaskOut:
        task = Task(project_id=self.default_project_id, title=data.title,
                    description=data.description, assignee=data.assignee)
        self.session.add(task)
        self.session.commit()               # commit explícito: el error se ve DENTRO del endpoint
        return self._to_out(task)

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskOut]:
        stmt = select(Task).order_by(Task.status, Task.position, Task.id)
        if status is not None:
            stmt = stmt.where(Task.status == status.value)
        return [self._to_out(t) for t in self.session.scalars(stmt)]

    def get(self, task_id: int) -> TaskOut | None:
        task = self.session.get(Task, task_id)
        if task is None:
            return None
        self._read[task_id] = task           # referencia fuerte: el identity map es débil
        return self._to_out(task)

    def update_status(self, task_id: int, status: TaskStatus) -> TaskOut:
        task = self.session.get(Task, task_id)  # identity map: la MISMA instancia que leyó get()
        task.status = status.value
        try:
            self.session.commit()           # UPDATE ... WHERE id = :id AND version = :v_leída
        except StaleDataError:
            self.session.rollback()
            raise ConcurrentUpdate(task_id)
        return self._to_out(task)
```

En el router, el único cambio es un `except` más en el endpoint de mover (junto a los de `TaskNotFound` e `InvalidTransition` de S05), y el import correspondiente:

```python
# app/routes/tasks.py
from ..errors import ConcurrentUpdate      # NO de repositories/: lo prohíbe test_arquitectura.py
...
    except ConcurrentUpdate:
        raise HTTPException(status_code=409, detail="Task was modified by someone else; reload")
```

---

### Paso 8 — Enchufarlo en `dependencies.py`

Si hiciste los ejercicios de S05, ya tenés una rama `postgres` con el `PostgresTaskRepository` (Core, `engine.begin()` y `create_all`). Esta versión la reemplaza. El `engine` pasa a apuntar a `taskflow_app`, el commit baja al repository (4.3) y el `lifespan` deja de crear tablas (4.7). `postgres.py` puede quedar en el repo como referencia, pero `dependencies.py` ya no lo usa.

Agregá el engine y la rama `postgres` a `get_repository`. El resto del archivo (la rama `sqlite`, el repo en memoria, la caché de S06 y `get_task_service`) queda como estaba:

```python
# app/dependencies.py (versión S07, lo nuevo)
import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .repositories.sqlalchemy_repo import SqlAlchemyTaskRepository

STORAGE = os.getenv("TASKFLOW_STORAGE", "memory")          # "memory" | "sqlite" | "postgres"
DATABASE_URL = os.getenv(
    "TASKFLOW_DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_app",  # driver EXPLÍCITO
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("TASKFLOW_SQL_ECHO") == "1",             # ver el SQL que emite el ORM
)                                                           # no conecta hasta el primer uso
SessionLocal = sessionmaker(engine)                         # una vez, a nivel de módulo


def get_repository() -> Iterator[TaskRepository]:
    if STORAGE == "postgres":
        with SessionLocal() as session:                     # una sesión por request; se cierra sola
            repo: TaskRepository = SqlAlchemyTaskRepository(session)
            yield CachedTaskRepository(repo, _redis) if CACHE == "redis" else repo
    elif STORAGE == "sqlite":
        ...  # igual que S05/S06
    else:
        yield _memory_repo
```

La línea de `CachedTaskRepository` es la prueba de lo que anticipaba S06: el decorator envuelve al repo nuevo **sin cambios**.

**✅ Verificación de punta a punta:**

```bash
TASKFLOW_STORAGE=postgres TASKFLOW_SQL_ECHO=1 uvicorn app.main:app --reload
# en otra terminal:
curl -s localhost:8000/tasks/ | python -m json.tool     # las mismas tareas que tenías en SQLite
curl -s -X POST localhost:8000/tasks/ -H "Content-Type: application/json" \
     -d '{"title": "Primera tarea en Postgres"}'        # 201, con id = max(id) + 1
pytest -q                                               # los de S05 siguen en verde, test_arquitectura incluido
git status                                              # services/ intacto
```

En la terminal de Uvicorn vas a ver el SQL: buscá el `INSERT INTO tasks`. Si el `POST` responde con error de `duplicate key`, el `setval` del paso 6 no corrió.

---

### Paso 9 — Reproducir el lost update y ver cómo lo frena `version` (`scripts/lost_update.py`)

```python
# scripts/lost_update.py — determinístico: intercala dos sesiones en un solo hilo
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.db.models import Task

engine = create_engine(os.environ["TASKFLOW_DATABASE_URL"])
TASK_ID = int(os.getenv("TASK_ID", "1"))


def reset() -> None:
    with Session(engine) as s:
        s.get(Task, TASK_ID).status = "in_progress"
        s.commit()


# --- 1. Como escribía el repo de S05: UPDATE sin control -----------------------
reset()
with engine.connect() as ana, engine.connect() as beto:
    leido_ana = ana.execute(text("SELECT status FROM tasks WHERE id = :id"), {"id": TASK_ID}).scalar_one()
    leido_beto = beto.execute(text("SELECT status FROM tasks WHERE id = :id"), {"id": TASK_ID}).scalar_one()
    print(f"[sin control] ambos leen: {leido_ana} / {leido_beto}")
    ana.execute(text("UPDATE tasks SET status = 'done' WHERE id = :id"), {"id": TASK_ID}); ana.commit()
    # Beto valida contra lo que LEYÓ (in_progress -> backlog es válida)... pero ya está en done
    beto.execute(text("UPDATE tasks SET status = 'backlog' WHERE id = :id"), {"id": TASK_ID}); beto.commit()
with Session(engine) as s:
    print(f"[sin control] estado final: {s.get(Task, TASK_ID).status}  <- el 'done' de Ana se perdió")

# --- 2. Con el ORM y version_id_col ---------------------------------------------
reset()
with Session(engine) as ana, Session(engine) as beto:
    t_ana, t_beto = ana.get(Task, TASK_ID), beto.get(Task, TASK_ID)
    print(f"[con version] ambos leen: {t_ana.status} v{t_ana.version}")
    t_ana.status = "done"
    ana.commit()                                   # version pasa a v+1
    t_beto.status = "backlog"
    try:
        beto.commit()                              # UPDATE ... AND version = v -> 0 filas
        print("[con version] Beto pisó a Ana (no debería pasar)")
    except StaleDataError:
        beto.rollback()
        print("[con version] StaleDataError -> la API respondería 409")
```

```bash
python -m scripts.lost_update        # con -m, la raíz del repo entra al path y `import app` resuelve
# salida esperada:
# [sin control] ambos leen: in_progress / in_progress
# [sin control] estado final: backlog  <- el 'done' de Ana se perdió
# [con version] ambos leen: in_progress v<N>
# [con version] StaleDataError -> la API respondería 409
```

> ⚠️ **Error común:** `python scripts/lost_update.py` falla con `ModuleNotFoundError: No module named 'app'`, porque Python pone en el path la carpeta del script (`scripts/`), no la raíz. Corré desde la raíz con `python -m scripts.lost_update` (o `PYTHONPATH=. python scripts/lost_update.py`). Lo mismo vale para los scripts de los ejercicios que importan `app`. `copy_sqlite_to_pg.py` no importa nada de `app`, por eso el paso 6 anda con `python scripts/...`.

Leé la parte 1 dos veces: no es solo "el último gana". Se aplicó `done → backlog`, **una transición prohibida por la regla de S05**. El script arma su propio engine, así que `TASKFLOW_SQL_ECHO` no lo afecta: si querés ver el `UPDATE … AND tasks.version = …` que emite el ORM, agregá `echo=True` al `create_engine` del script.

---

### Paso 10 — Pesimista, aislamiento y deadlock en dos terminales

Abrí dos terminales (A y B) con:

```bash
docker compose exec db psql -U taskflow -d taskflow_app
```

**(a) `FOR UPDATE`: el segundo espera**

```sql
-- A
BEGIN;
SELECT status, version FROM tasks WHERE id = 1 FOR UPDATE;   -- devuelve la fila
-- B
BEGIN;
SELECT status, version FROM tasks WHERE id = 1 FOR UPDATE;   -- QUEDA ESPERANDO (sin prompt)
-- A
UPDATE tasks SET status = 'done', version = version + 1 WHERE id = 1;
COMMIT;
-- B: se destraba y devuelve status = done con la versión nueva -> ahí validaría la transición
COMMIT;
```

✅ Lo lograste si B quedó colgada hasta el `COMMIT` de A. Repetí con `FOR UPDATE NOWAIT` en B: en vez de esperar, tiene que fallar en el acto con `ERROR: could not obtain lock on row in relation "tasks"` (SQLSTATE `55P03`).

**(b) Repeatable Read: error de serialización**

```sql
-- B
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT status FROM tasks WHERE id = 1;                        -- snapshot tomado
-- A
UPDATE tasks SET title = title || ' (editada)', version = version + 1 WHERE id = 1;  -- autocommit
-- B
UPDATE tasks SET status = 'backlog' WHERE id = 1;
-- ERROR:  could not serialize access due to concurrent update
ROLLBACK;                                                     -- y reintentar la transacción entera
```

**(c) Deadlock: orden inconsistente** (recortable si falta tiempo)

```sql
-- A: BEGIN; UPDATE tasks SET position = position + 1 WHERE id = 1;
-- B: BEGIN; UPDATE tasks SET position = position + 1 WHERE id = 2;
-- A: UPDATE tasks SET position = position + 1 WHERE id = 2;   -- espera a B
-- B: UPDATE tasks SET position = position + 1 WHERE id = 1;   -- ciclo
```

✅ PostgreSQL detecta el ciclo y aborta **una** de las dos con `ERROR: deadlock detected` (SQLSTATE `40P01`); la otra sigue. Hacé `ROLLBACK` en las dos para limpiar. (Necesitás al menos dos tareas: si solo copiaste una, creá otra con `curl`.)

**(d) La forma correcta de reordenar el tablero:**

```sql
BEGIN;
SELECT id FROM tasks WHERE project_id = 1 AND status = 'done' ORDER BY id FOR UPDATE;
UPDATE tasks SET position = position + 1 WHERE project_id = 1 AND status = 'done';
UPDATE tasks SET status = 'done', position = 0, version = version + 1 WHERE id = 1;
COMMIT;
```

Todos toman los locks en orden de `id`: dos reordenamientos simultáneos se ordenan en fila en vez de trabarse.

---

### Paso 11 — Test de concurrencia (`tests/test_concurrency.py`)

Este test corre **solo contra PostgreSQL**: SQLite no reproduce el aislamiento ni `FOR UPDATE` de Postgres. Si no hay `TASKFLOW_DATABASE_URL`, se saltea.

```python
# tests/test_concurrency.py
import os

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.db.models import Task

URL = os.getenv("TASKFLOW_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="necesita PostgreSQL (TASKFLOW_DATABASE_URL)")


@pytest.fixture
def engine():
    eng = create_engine(URL)
    yield eng
    eng.dispose()


@pytest.fixture
def task_id(engine):
    with Session(engine) as s:
        task = Task(project_id=1, title="test concurrencia", status="in_progress")
        s.add(task)
        s.commit()
        tid = task.id
    yield tid
    with Session(engine) as s:                     # limpieza (un delete masivo: acá está bien)
        s.execute(delete(Task).where(Task.id == tid))
        s.commit()


def test_concurrent_move_raises_stale(engine, task_id):
    with Session(engine) as ana, Session(engine) as beto:
        t_ana, t_beto = ana.get(Task, task_id), beto.get(Task, task_id)
        t_ana.status = "done"
        ana.commit()
        t_beto.status = "backlog"
        with pytest.raises(StaleDataError):
            beto.commit()
```

**✅ Verificación:**

```bash
pytest -q tests/test_concurrency.py                    # 1 passed (con la variable exportada)
env -u TASKFLOW_DATABASE_URL pytest -q tests/test_concurrency.py   # 1 skipped
```

> 💡 **Tip:** para tests contra Postgres que **no** necesitan dos conexiones reales, la doc de SQLAlchemy tiene una receta que une la sesión a una transacción externa y hace rollback al final (`join_transaction_mode="create_savepoint"`): la base queda limpia sin borrar a mano.

---

### Paso 12 — Entregables y cierre

1. `docs/datos/s07-modelo-er.md` con el `erDiagram` de 4.1 y la tabla `ON DELETE` de 4.2 (verificá que renderice en GitHub).
2. TJ-005 y TJ-006 en `docs/tradeoff-journal.md`.
3. Commit y tag:

```bash
git add app/db app/errors.py app/repositories app/routes app/dependencies.py migrations alembic.ini \
        scripts tests docs requirements.txt
git commit -m "S07: TaskFlow sobre PostgreSQL con Alembic y bloqueo optimista"
git push -u origin s07-postgres
git tag s07 && git push origin s07
```

**Stretch (si te sobra tiempo):** reproducí la carrera con hilos reales: dos hilos que llaman a `PATCH /tasks/1/status` a la vez, sincronizados con `threading.Barrier(2)` para que arranquen simultáneamente. El 409 va a aparecer "a veces", y vas a entender por qué el script determinístico del paso 9 es mucho mejor para debuggear.

> 📝 **Nota para el profesor:** el reparto propuesto de los 180 min es el estándar de la semana 2: 40 min de concepto (modelado + concurrencia) / 60 min de taller guiado (modelos + Alembic + repository, pasos 1–8 de la guía) / 45 min de práctica autónoma (lost update y las dos terminales `psql`, pasos 9–11) / 20 min de puesta en común (ER entre equipos y TJ-006) / 15 min de cierre y entrega. Es mucho para 3 h: si hay que recortar, lo primero que sale es el deadlock (paso 10c) y el stretch de `If-Match`.
> 
> **Defaults del lab:** los mismos equipos de 3 de S05–S06; entrega en la rama `s07-postgres` con `app/db/models.py`, `app/errors.py`, `migrations/`, `app/repositories/sqlalchemy_repo.py`, `scripts/copy_sqlite_to_pg.py`, `scripts/lost_update.py`, `tests/test_concurrency.py`, `docs/datos/s07-modelo-er.md` y TJ-005/TJ-006, con tag `s07`; variables `TASKFLOW_STORAGE=postgres` y `TASKFLOW_DATABASE_URL` con las credenciales locales del compose de S06; los tests de S05 siguen en memoria/SQLite y solo el de concurrencia corre contra Postgres. `models.py` usa `DateTime(timezone=True)` en los timestamps para que coincida con los `timestamptz` del ER.

---

## 6. Ejercicios

Todos los ejercicios corren contra el **Postgres del `docker-compose.yml`** (`docker compose up -d db`), en la base `taskflow_app` que maneja Alembic, con `TASKFLOW_DATABASE_URL` exportada como en el paso 2. Los tests nuevos de esta sección no se saltean: si Postgres está apagado, tienen que fallar.

### 🟢 Básico 1 — Probar que la base rechaza lo que no tiene sentido

Escribí `scripts/check_constraints.py` que intente, contra `taskflow_app`, cinco escrituras inválidas: una tarea con `status = 'archivada'`, una tarea sin título, una tarea en el proyecto 999, dos etiquetas `'bug'` en el mismo proyecto y un miembro con `role = 'admin'`. Cada intento tiene que ir **dentro de un savepoint** (`session.begin_nested()`) para que el fallo de uno no aborte a los demás, y el script imprime una línea por intento.

**Sabés que lo lograste cuando** la salida son cinco líneas `RECHAZADO: <qué intento> -> IntegrityError`, ninguna `ACEPTADO`, y al final `SELECT count(*) FROM labels WHERE name = 'bug'` no cambió respecto de antes de correrlo.

<details> <summary>Pistas</summary>

- El esqueleto: `with Session(engine) as s:` y adentro, por cada intento, `try: with s.begin_nested(): s.add(...); s.flush()` / `except IntegrityError: print(...)`.
- Sin `flush()` dentro del savepoint, el `INSERT` no se manda y no hay nada que falle.
- Para no dejar basura, terminá con `s.rollback()` en vez de `s.commit()`.
- ¿La tarea sin título falla en la base o antes, en Python? Probá con `Task(project_id=1, title=None)`.

</details>

### 🟢 Básico 2 — Verificar la política `ON DELETE` en `psql`

En `psql` contra el contenedor (`docker compose exec db psql -U taskflow -d taskflow_app`), en una transacción que termine con `ROLLBACK` (para no romper tus datos), creá un usuario, asignale una tarea (`assignee_id`), hacé que comente otra, y borralo. Después intentá borrar el equipo 1 (que tiene proyectos) y, por último, borrá el proyecto 1. Consultá el estado después de cada `DELETE`.

**Sabés que lo lograste cuando** tu archivo `docs/datos/s07-on-delete-check.sql` tiene las sentencias y, como comentario, lo que observaste: tras borrar el usuario, `assignee_id` y `author_id` quedan en `NULL` y sus filas de membresía desaparecen; borrar un equipo **con** proyectos falla por la FK (y explicás por qué con `RESTRICT`); tras borrar el proyecto, sus tareas, comentarios y etiquetas desaparecen. Todo coincide con la tabla de 4.2.

<details> <summary>Pistas</summary>

- Empezá con `BEGIN;` y terminá con `ROLLBACK;`.
- Para ver el efecto: `SELECT id, assignee_id FROM tasks WHERE id = …;` y `SELECT id, author_id FROM comments WHERE …;`.
- El orden importa: si borrás el proyecto antes de intentar con el equipo, el equipo ya no tiene proyectos y el `DELETE` pasa.
- Después de un error, la transacción queda abortada: usá un `SAVEPOINT` antes del `DELETE` que esperás que falle, y `ROLLBACK TO` después.

</details>

### 🟡 Intermedio 1 — Medir el N+1 del tablero y arreglarlo

Escribí `scripts/board_queries.py` que cree (si no existen) 3 etiquetas en el proyecto 1, se las asigne a 20 tareas, y después liste el tablero imprimiendo título y etiquetas de cada tarea **dos veces**: una sin opciones de carga y otra con `selectinload(Task.labels)`. Contá las consultas SQL de cada versión registrando un listener sobre el engine (`sqlalchemy.event.listen(engine, "before_cursor_execute", ...)`) que incremente un contador.

**Sabés que lo lograste cuando** la salida muestra algo como `sin selectinload: 21 consultas` y `con selectinload: 2 consultas` (1 + N contra 2) y, como tercera variante, una versión con `raiseload(Task.labels)` que **falla** al tocar `t.labels`, lo que atrapás e imprimís como `raiseload: carga perezosa bloqueada`.

<details> <summary>Pistas</summary>

- Reseteá el contador entre versiones y usá una **sesión nueva** para cada una: si reusás la sesión, el identity map ya tiene las etiquetas cargadas y la segunda versión "hace trampa".
- La firma del listener recibe `(conn, cursor, statement, parameters, context, executemany)`.
- Para asignar etiquetas por ORM: `task.labels.append(label)`.
- `raiseload` está en `sqlalchemy.orm`, igual que `selectinload`.

</details>

### 🟡 Intermedio 2 — Soft delete con una segunda migración

Agregá a `Task` la columna `archived_at: Mapped[datetime | None]` (timestamptz), generá la migración con autogenerate, **revisala** con el checklist y aplicala. Después modificá `SqlAlchemyTaskRepository.list_tasks` para que no devuelva tareas archivadas, y agregá un método `archive(task_id)` al repository (fuera del `Protocol` por ahora) que ponga `archived_at = now()` y haga commit.

**Sabés que lo lograste cuando:** `alembic history` muestra dos revisiones encadenadas (la segunda con `down_revision` apuntando a la primera); `alembic downgrade -1 && alembic upgrade head` corre sin error; y un test nuevo contra Postgres crea una tarea, la archiva y verifica que ya no aparece en `list_tasks()` pero sigue existiendo con `session.get(Task, id)`. Podés tomar la conexión de `test_concurrency.py`, pero **sin** su `skipif`: con Postgres apagado, el test tiene que fallar, no saltearse.

<details> <summary>Pistas</summary>

- ¿Esta columna necesita `server_default`? Pensalo con el ítem 7 del checklist: es nullable.
- En el filtro, `Task.archived_at.is_(None)`, no `Task.archived_at == None` (funciona, pero los linters lo marcan).
- Archivar es un `UPDATE` de la tarea: ¿incrementa la `version`? ¿Debería? Anotá tu respuesta.
- ¿El índice del tablero `(project_id, status, position)` sigue sirviendo con el filtro nuevo? Mirá el `EXPLAIN` como en S06.

</details>

### 🔴 Desafío 1 — Bloqueo optimista de punta a punta por la API

Llevá el control de versión hasta el cliente (el caso "tablero abierto hace cinco minutos"):

1. Agregá `version: int` a `TaskOut` y a `_to_out`.
2. Agregá `expected_version: int | None = None` a `TaskStatusUpdate`.
3. Si viene `expected_version` y no coincide con la versión que leyó el service, el service lanza `ConcurrentUpdate` (o una excepción de dominio propia) **antes** de validar la transición, y el router responde **409**. Sin `expected_version`, el comportamiento es el de hoy.
4. Escribí un test con `TestClient` contra Postgres que simule la carrera **dentro** de un mismo request: usá `monkeypatch` para envolver `SqlAlchemyTaskRepository.get` de modo que, después de leer, otra sesión independiente modifique y confirme la misma tarea. El `PATCH` tiene que responder 409 aunque **no** mande `expected_version` (lo frena `version_id_col`).
5. Registrá en TJ-006 por qué elegiste `expected_version` + 409 en vez de `If-Match` + 412 (o al revés).

**Sabés que lo lograste cuando** tenés tres tests en verde contra Postgres: (a) `PATCH` con `expected_version` correcta → 200 y la `version` de la respuesta aumentó en 1; (b) `PATCH` con `expected_version` vieja → 409 y la tarea **no** cambió en la base; (c) la carrera simulada con `monkeypatch` → 409. Y los tests de S05 siguen en verde, los de memoria y los de `pg_client` si hiciste sus ejercicios: el repo en memoria no tiene `version`, así que decidí qué devuelve.

<details> <summary>Pistas</summary>

- Para (c), dentro del wrapper: llamá al `get` original, y después abrí `with Session(engine) as otra:` que cambie el título de la tarea y haga commit. El `update_status` siguiente va a encontrar otra versión.
- En el repo en memoria, una opción simple es un contador que incrementás en `update_status`.
- El service no tiene que importar nada de SQLAlchemy: comparás contra `task.version` del `TaskOut`.
- Si tu `CachedTaskRepository` está activo, ¿de dónde sale la versión que compara el service? Revisá 4.5.

</details>

### 🔴 Desafío 2 (opcional) — Reordenar el tablero sin deadlocks

Implementá `PATCH /tasks/{id}/position` con body `{"status": "...", "position": N}`, que mueva la tarea a otra columna y posición desplazando las demás. Hacelo con bloqueo pesimista: `select(Task).where(...).order_by(Task.id).with_for_update()` sobre la columna destino, dentro de **una** transacción, con el patrón `run_with_retry` de 4.4 envolviendo la operación entera.

**Sabés que lo lograste cuando** un test que lanza dos reordenamientos simultáneos sobre la misma columna con dos hilos y `threading.Barrier(2)` termina siempre con posiciones `0..N-1` sin huecos ni duplicados (verificalo con `SELECT position FROM tasks WHERE project_id = 1 AND status = 'done' ORDER BY position`), sin errores de deadlock, en 20 corridas seguidas.

<details> <summary>Pistas</summary>

- Esta operación toca varias filas: el commit por método del repository no alcanza. ¿Dónde vive la transacción? (Releé el trade-off de 4.3.)
- Mover la tarea también debería respetar la regla de transiciones de S05.
- Para las 20 corridas alcanza con un `for` dentro del test que resetee las posiciones en cada vuelta.

</details>

---

## 7. Ruta de estudio sugerida

Los recursos tienen dependencias reales: la doc de versionado no se entiende sin la de aislamiento, y autogenerate no se entiende sin el tutorial de Alembic. Este es el orden, con tiempos:

```mermaid
flowchart TD
    R1["1. SQLAlchemy relationship patterns<br/>25 min"] --> R2["2. Postgres constraints<br/>30 min"]
    R1 --> R3["3. SQLAlchemy declarative<br/>25 min"]
    R4["4. Postgres tutorial transactions<br/>10 min"] --> R5["5. SQLAlchemy Session basics<br/>30 min"]
    R5 --> R6["6. FastAPI dependencies with yield<br/>15 min"]
    R7["7. Postgres MVCC<br/>5 min"] --> R8["8. Postgres transaction isolation<br/>40 min"]
    R8 --> R9["9. SQLAlchemy version counter<br/>15 min"]
    R8 --> R10["10. Postgres explicit locking<br/>25 min"]
    R3 --> R11["11. Alembic naming<br/>10 min"]
    R11 --> R12["12. Alembic tutorial<br/>30 min"]
    R12 --> R13["13. Alembic autogenerate<br/>20 min"]
    R2 --> LAB["Lab<br/>3 h"]
    R6 --> LAB
    R9 --> LAB
    R13 --> LAB
    LAB --> R14["14. Relationship loading y N+1<br/>20 min"]
    LAB --> R15["15. Contraste: FastAPI SQL y Full Stack Template<br/>40 min"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class R8 foco
```

- **Antes de la clase (~2 h):** 1, 4, 5, 7 y 8. La doc de aislamiento (8) es la más densa y la que más rinde: leé 13.2.1 y 13.2.2 con calma; 13.2.3 (Serializable) es opcional.
- **Durante el lab, de consulta:** la doc del dialecto PostgreSQL, _Engine Configuration_ y la instalación de psycopg 3; se abren cuando las necesitás, no antes.
- **Después (~2 h):** 2, 3, 9–13 para consolidar lo que hiciste, y 14–15 para comparar tus decisiones con las de otros.
- **Opcionales sin dependencias:** Rice (_Optimistic Offline Lock_, 5 min) antes del 🔴 1; MDN `If-Match` y `threading.Barrier` para los stretch; partitioning y art. 17 RGPD para la discusión de ciclo de vida; Alembic batch y pgloader solo si los vas a usar.

---

## 8. Checklist de autoevaluación

- [ ] Puedo dibujar el ER de TaskFlow de memoria y explicar por qué `project_members` es un association object y `task_labels` no.
- [ ] Puedo explicar, para cada FK de TaskFlow, qué pasa al borrar la fila referenciada y por qué se eligió esa acción.
- [ ] Sé por qué las FK que se consultan llevan índice explícito en PostgreSQL.
- [ ] Puedo explicar por qué el `commit` de TaskFlow va en el repository y no en el código de salida de la dependencia.
- [ ] Puedo reproducir un lost update con dos sesiones y explicar por qué viola la regla de transiciones de S05.
- [ ] Puedo explicar qué `UPDATE` emite el ORM con `version_id_col` y por qué un `update()` masivo se saltea el control.
- [ ] Sé cuándo usaría bloqueo optimista y cuándo `SELECT … FOR UPDATE` en TaskFlow, y por qué el pesimista no sirve entre requests.
- [ ] Puedo nombrar el nivel de aislamiento por defecto de PostgreSQL y qué hacer ante un error de serialización.
- [ ] Puedo revisar una migración autogenerada y detectar un rename disfrazado de drop + add.
- [ ] Puedo explicar qué es expand/contract con el caso `assignee` → `assignee_id`.

---

## 9. Preguntas de repaso

1. Tu agente generó un repository que hace `session.execute(update(Task).where(Task.id == task_id).values(status=new))` "porque es una sola consulta y es más rápido". El modelo tiene `version_id_col`. ¿Qué problema introduce, cómo lo detectarías con un test y cómo lo reescribirías?
2. Ana tiene el tablero de TaskFlow abierto desde hace diez minutos y mueve una tarjeta que Beto editó en el medio. Diseñá cómo lo detecta el sistema: qué viaja en el request, qué compara el servidor, qué código HTTP devuelve y qué hace el front. ¿Por qué no sirve un `SELECT … FOR UPDATE` para este caso?
3. Un compañero propone `ON DELETE CASCADE` en todas las FK de TaskFlow "para que borrar sea simple". Argumentá a favor y en contra con dos relaciones concretas, incluyendo qué pasa cuando un usuario pide que se borren sus datos.
4. La regla "todo proyecto tiene al menos un owner" puede violarse aunque ninguna escritura pise a otra. Explicá cómo, por qué ni la columna `version` ni un `FOR UPDATE` sobre una sola fila lo evitan, y qué dos soluciones tenés en PostgreSQL.
5. Autogenerate te propone una migración con `op.drop_column("tasks", "assignee")` y `op.add_column("tasks", sa.Column("assignee_name", ...))`. ¿Qué pasa si la aplicás en una base con datos? ¿Cómo la corregís y cómo verificarías que el `downgrade` funciona?

---

## 10. Recursos adicionales

**Imprescindible**

- [Session Basics — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) — secciones "Basics of Using a Session" y "When do I construct a Session…" (30 min).
- [13.2. Transaction Isolation — PostgreSQL 16](https://www.postgresql.org/docs/16/transaction-iso.html) — 13.2.1 y 13.2.2 (40 min).
- [Configuring a Version Counter — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/versioning.html) — primera sección (15 min).
- [Auto Generating Migrations — Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) (20 min).
- [Tutorial — Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) — hasta "Running our Second Migration" + "Downgrading" (30 min).
- [5.4. Constraints — PostgreSQL 16](https://www.postgresql.org/docs/16/ddl-constraints.html) (30 min).
- [Basic Relationship Patterns — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html) — one-to-many, many-to-one, many-to-many y association object (25 min).
- [Table Configuration with Declarative — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html) — `mapped_column` y anotaciones `Mapped` (25 min).

**Recomendado**

- [3.4. Transactions — tutorial de PostgreSQL 16](https://www.postgresql.org/docs/16/tutorial-transactions.html) (10 min).
- [13.1. Introduction (MVCC) — PostgreSQL 16](https://www.postgresql.org/docs/16/mvcc-intro.html) (5 min).
- [13.3. Explicit Locking — PostgreSQL 16](https://www.postgresql.org/docs/16/explicit-locking.html) — 13.3.2 y 13.3.4 (25 min).
- [Relationship Loading Techniques — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html) — lazy, `selectinload`, `raiseload` (20 min).
- [The Importance of Naming Constraints — Alembic](https://alembic.sqlalchemy.org/en/latest/naming.html) (10 min).
- [Dependencies with yield — FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/) — repaso + sección de `scope` (15 min).
- [Transactions and Connection Management — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html) — `begin_nested`, aislamiento, tests con rollback (20 min).
- [PostgreSQL dialect — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html) — DBAPIs, isolation level, `Identity` (15 min).
- [Engine Configuration — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/core/engines.html) — Database URLs, `echo`, `pool_pre_ping` (10 min).
- [Installation — psycopg 3](https://www.psycopg.org/psycopg3/docs/basic/install.html) (5 min).
- [Entity Relationship Diagrams — Mermaid](https://mermaid.js.org/syntax/entityRelationshipDiagram.html) (15 min).
- [SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html) — secciones 1–2 (5 min).
- [Optimistic Offline Lock — catálogo de P of EAA](https://martinfowler.com/eaaCatalog/optimisticOfflineLock.html) — David Rice (5 min).
- [System Information Functions — `pg_get_serial_sequence` — PostgreSQL 16](https://www.postgresql.org/docs/16/functions-info.html) (3 min, de consulta).
- [State Management — Session Referencing Behavior — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html) — por qué el repository guarda lo que leyó (5 min).
- [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/) — de contraste, después del lab (20 min).
- Andrew Ng, _AI Engineering Skills Map_ (The Batch, 2026), sección _Managing data_ — biblioteca del profesor, sin enlace público (5 min).

**Opcional**

- [SELECT — The Locking Clause — PostgreSQL 16](https://www.postgresql.org/docs/16/sql-select.html) — `NOWAIT`, `SKIP LOCKED` (10 min).
- [Appendix A. PostgreSQL Error Codes — PostgreSQL 16](https://www.postgresql.org/docs/16/errcodes-appendix.html) — `40001`, `40P01`, `55P03` (de consulta).
- [If-Match — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match) (5 min).
- [threading — Barrier Objects — Python docs](https://docs.python.org/3/library/threading.html) — solo `Barrier` (5 min).
- [5.11. Table Partitioning — PostgreSQL 16](https://www.postgresql.org/docs/16/ddl-partitioning.html) — solo 5.11.1 (10 min).
- [Art. 17 RGPD — Derecho de supresión](https://gdpr-info.eu/art-17-gdpr/) — compilación no oficial, apartado 1 (5 min).
- [Running "Batch" Migrations for SQLite — Alembic](https://alembic.sqlalchemy.org/en/latest/batch.html) (10 min).
- [SQLite to Postgres — pgloader](https://pgloader.readthedocs.io/en/latest/ref/sqlite.html) (10 min).
- [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) — FastAPI + SQLModel + PostgreSQL + Docker Compose; explorá solo `backend/` (20 min).