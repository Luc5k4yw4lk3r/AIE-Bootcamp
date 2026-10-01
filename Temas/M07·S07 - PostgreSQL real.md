# M07·S07 — PostgreSQL real: modelado ER, transacciones y concurrencia en TaskFlow

| | |
|---|---|
| **Sesión** | M07·S07 |
| **Fecha** | [Completar por el profesor: fecha] |
| **Módulo** | 07 — Fundamentos de Software + System Design para AI Engineers · Semana 2 (Gestión de datos y diseño de APIs) |
| **Tema** | TaskFlow deja la memoria y se conecta a PostgreSQL: del modelo de dominio al esquema ER, un ORM separado del dominio, la transacción por request y qué pasa cuando dos personas tocan la misma tarea |
| **Duración estimada de estudio** | ~11 h si recorrés todo: ~5 h 30 min de recursos, ~2 h de notas, ~1 h 30 min de guía práctica y ~3 h de ejercicios. La ruta mínima (recursos imprescindibles + guía + una unidad completa) ronda las 6 h |
| **Punto de partida → entrega** | tag `s06` → tag `s07` del repo `fastapi-full-v0` |

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Traducir** el modelo de dominio de TaskFlow a un esquema relacional —tablas, PK, FK, tablas de enlace con PK compuesta, nulabilidad— y **dibujarlo** como `erDiagram` en `docs/diagrams/s07-er.mmd`, leyéndolo línea por línea contra `app/db/models.py`.
2. **Conectar** el webserver a PostgreSQL desde la capa repository con SQLAlchemy 2.0, con el ORM separado del dominio, y **explicar** cualquier línea del diff `s06 → s07`: por qué el router no cambió y por qué el service sí.
3. **Explicar** qué garantiza una transacción (ACID) y **ubicar** en el código de TaskFlow dónde empieza, dónde se confirma y dónde se deshace: sesión por request con `get_db` y el service como unit of work.
4. **Demostrar** en dos terminales `psql` el aislamiento Read Committed, el *lost update*, el bloqueo con `FOR UPDATE`, el error de serialización y un deadlock, y **elegir** con criterio entre control de concurrencia optimista y pesimista para un caso de TaskFlow.
5. **Evaluar** qué mantiene los datos limpios, consistentes y frescos: qué garantiza la base (FK, `NOT NULL`, `UNIQUE`), qué garantiza solo el dominio (el Enum `Estado`) y qué decisiones de ciclo de vida quedan abiertas (`ON DELETE`).
6. **Diagnosticar** los límites de `create_all` frente a las migraciones —incluido el bug latente del seed con ids fijos sobre `SERIAL`— y **registrar** las decisiones de la sesión como entradas `[s07]` en `docs/trade-offs.md`.

---

## 2. Resumen ejecutivo

En M07·S06 completaste el modelo de dominio de TaskFlow —seis entidades Pydantic relacionadas por id, con dos M:N guardadas de un solo lado— y registraste `ADR-001`: PostgreSQL. Ese Postgres corre en Docker desde M07·S05, pero la app seguía guardando todo en un `dict` que se borraba con cada reinicio. Hoy TaskFlow se conecta de verdad.

La sesión tiene dos mitades. En la primera traducís el dominio a un **esquema relacional** (ocho tablas, claves, nulabilidad) y lo mapeás con **SQLAlchemy 2.0** en `app/db/`, separado del dominio. El repository cambia de implementación sin cambiar de interfaz, y por eso `app/routers/tareas.py` no se toca: es la prueba de que las capas de M07·S04 sirven para algo. En la segunda abrís la caja de la **transacción**: qué garantiza ACID, quién hace `commit` en TaskFlow (el service, como unit of work) y, sobre todo, qué **no** garantiza: dos personas moviendo la misma tarea al mismo tiempo. Lo vas a ver con tus propios ojos en dos terminales `psql`.

¿Por qué le importa a un AI Engineer? Andrew Ng incluye transacciones, concurrencia y datos limpios, consistentes y frescos dentro de la competencia *Managing data*, y advierte que los datos son relativamente difíciles de cambiar **aun cuando los agentes ayuden con las migraciones**. El agente te genera el ORM en un minuto; el esquema y la política de concurrencia los revisás vos, porque son lo más caro de revertir. Y lo que construyas hoy es la fuente de la que, en M07·S08, va a leer un agente.

---

## 3. Conceptos clave / glosario

Lo que ya viste se refresca en una línea. Lo nuevo va con definición, para qué y por qué así.

### Ya vistos (refresco)

| Término | Dónde | Refresco |
|---|---|---|
| Capas router → service → repository → datos | M07·S04 | Cada capa con una responsabilidad; el dominio no importa la persistencia. |
| `Depends` y dependencias con `yield` | M07·S04 | FastAPI llama a la función por vos; con `yield`, lo que va después corre al terminar el request. |
| `def` vs `async def` y el threadpool | M07·S04 | FastAPI corre los endpoints `def` en un pool de threads, así que una llamada bloqueante no frena al resto. |
| `ServicioTareas`, `RepositorioTareasEnMemoria`, `app/dependencies.py`, `Estado` | M07·S05 | El prototipo en capas del que partís; el Enum `Estado` valida `backlog` / `en progreso` / `hecho`. |
| Compose de Postgres (`db`, `taskflow-db`, volumen `taskflow_pgdata`), `.env` / `.env.example` | M07·S05 | La base ya corre en Docker; la configuración viene del entorno. |
| Modelo de dominio, entidad, referencia por id, M:N de un solo lado, `EntidadConTiempos` | M07·S06 | Las seis clases de `app/models/`, relacionadas por id y sin persistencia. |
| Foreign key, integridad referencial, tabla de enlace | M07·S06 | La FK exige que la referencia exista; la tabla de enlace guarda una M:N. Hoy se vuelven reales. |
| Transacción y ACID | M07·S06 | Todo o nada; Atomicidad, Consistencia, aIslamiento, Durabilidad. Hoy se aplican. |
| `ADR-001` y entradas `[sXX]` en `docs/trade-offs.md` | M07·S05–S06 | La bitácora de decisiones del repo; el ADR queda para las decisiones pesadas. |
| Diagrama de clases y multiplicidad | MA·S05 | Cómo se leen `1`, `0..1` y `N` en cada extremo de una relación. |
| Claude Code en plan mode | M07·S01 | El agente propone un plan antes de tocar archivos. |

### Esquema relacional

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **Esquema relacional** | La definición de las tablas de una base: columnas, tipos, claves y restricciones. | Darle al modelo de dominio una forma que la base pueda guardar y proteger. | Es lo más caro de cambiar después: por eso se diseña y se revisa, no se acepta tal como lo genera el agente. |
| **Primary key (PK)** | La columna (o columnas) que identifica cada fila de forma única y no admite `NULL`. | Que cada tarea tenga una identidad estable a la que apuntar. | Es la traducción directa de la identidad de una entidad (S06). |
| **PK compuesta** | Una PK formada por más de una columna, como `(tarea_id, etiqueta_id)` en `tarea_etiqueta`. | Impedir que el mismo par se repita en una tabla de enlace. | Un `id` propio en la tabla de enlace permitiría guardar dos veces "la tarea 3 tiene la etiqueta 2". |
| **Nulabilidad** (`NULL` / `NOT NULL`) | Si una columna puede quedar sin valor. | Traducir la opcionalidad del dominio: una tarea puede no tener responsable, un comentario siempre tiene autor. | Si la base no lo exige, la regla vive solo en el código, y cualquier camino que no pase por ese código la rompe. |
| **Acción referencial** (`ON DELETE`) | Lo que hace la base cuando se borra una fila a la que otras apuntan: `NO ACTION` (default), `RESTRICT`, `CASCADE`, `SET NULL`, `SET DEFAULT`. | Decidir qué pasa con los comentarios cuando se borra su tarea. | Es una decisión de ciclo de vida del dato, no un detalle técnico; el default `NO ACTION` simplemente rechaza el borrado. |
| **Índice sobre FK** | Una estructura que acelera las búsquedas por la columna que referencia (`tareas.proyecto_id`). | Que "traer las tareas de un proyecto" no recorra la tabla entera. | Declarar una FK **no** crea ese índice en PostgreSQL; hay que pedirlo. |
| **`CHECK` / `UNIQUE`** | Restricciones que exigen una condición sobre el valor (`estado IN (...)`) o que no se repita (`email`). | Que la base rechace datos inválidos o duplicados aunque lleguen por fuera de la app. | Sin ellas, la validación vive solo en el dominio. |
| **`SERIAL`** | Un atajo de PostgreSQL que crea una secuencia y pone `DEFAULT nextval(...)` en la columna. | Generar ids automáticos. | Es lo que emite SQLAlchemy si no pedís `Identity()`. Desde PostgreSQL 10, `IDENTITY` lo reemplaza como forma recomendada. |
| **Secuencia** | Un contador de la base que entrega el próximo número con `nextval`. | Asignar ids sin que dos transacciones reciban el mismo. | Un número tomado queda usado aunque la transacción haga rollback: por eso puede haber huecos. |
| **Diagrama ER** (`erDiagram`) | El dibujo de las tablas y sus relaciones con notación *crow's foot* (`\|\|`, `\|o`, `}o`, `}\|`). | Revisar el esquema de un vistazo y discutirlo antes de tocar código. | Un `classDiagram` (S06) muestra objetos; el ER muestra lo que la base guarda, incluidas las tablas de enlace. |

### ORM y conexión

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **ORM** (*Object-Relational Mapper*) | Una librería que traduce entre clases Python y tablas SQL, y genera el SQL por vos. | Leer y escribir filas como objetos sin escribir cada `INSERT` a mano. | La alternativa, SQL crudo, da control total pero obliga a mapear a mano seis entidades y dos M:N. |
| **SQLAlchemy 2.0** | El ORM (y toolkit SQL) que usa TaskFlow, en su estilo 2.0 con anotaciones de tipo. | Definir las tablas en `app/db/models.py` y trabajar con una `Session`. | Es la base de SQLModel y de buena parte del ecosistema; usarlo directo permite separar ORM y dominio. |
| **`DeclarativeBase`** | La clase de la que heredan todos los modelos ORM; acumula sus tablas en `Base.metadata`. | Tener un único registro de tablas para crearlas con `create_all`. | Una sola `Base` por aplicación evita metadatos dispersos. |
| **`Mapped[...]` + `mapped_column(...)`** | La forma 2.0 de declarar una columna: el tipo Python de la anotación decide el tipo SQL y la nulabilidad. | Que el mismo tipo sirva al editor, al type checker y a la base. | `Mapped[int \| None]` es `NULL`; `Mapped[int]`, `NOT NULL`. Escribir `nullable=True` encima es redundante. |
| **`relationship`** | Un atributo que navega a los objetos relacionados (`tarea.etiquetas`) en vez de al id. | Recorrer el grafo de objetos sin escribir JOINs. | Viene con un costo: si no decís cómo cargarlo, carga perezosamente y aparece el N+1. |
| **`secondary=`** | El parámetro de `relationship` que apunta a una tabla de enlace para una M:N. | Que el ORM gestione los `INSERT` / `DELETE` de la tabla intermedia. | Si la tabla de enlace necesitara columnas propias (un rol), se usa un *association object*, no `secondary=`. |
| **Association object** | Una clase ORM para la tabla intermedia cuando la relación tiene datos propios. | Modelar "el usuario es owner en este proyecto". | Mezclarlo con `secondary=` sobre la misma tabla puede leer y escribir datos de forma inconsistente. |
| **Engine** | El objeto que sabe conectarse a la base y mantiene un pool de conexiones. | Crear conexiones una vez y reutilizarlas. | Se crea una sola vez por proceso; abrir una conexión por consulta es lento. |
| **`pool_pre_ping`** | Opción del engine que prueba la conexión cada vez que la saca del pool. | Sobrevivir a un reinicio de la base sin errores de conexión muerta. | Cuesta un viaje corto por checkout, a cambio de no explotar después de un `docker compose down`. |
| **DBAPI / driver** | La librería de bajo nivel que habla el protocolo de la base. En TaskFlow, psycopg 3 (`psycopg[binary]`). | Que SQLAlchemy pueda hablar con PostgreSQL. | El driver se nombra en la URL (`postgresql+psycopg://`) para no depender del default de cada versión. |
| **Database URL** | `dialecto+driver://usuario:password@host:puerto/base`. En TaskFlow, `DATABASE_URL`. | Configurar la conexión desde el entorno. | Viene del entorno (12-factor, S05), no del código: cada alumno puede tener otro puerto. |
| **SQLModel** | Una librería construida sobre SQLAlchemy y Pydantic donde una sola clase es a la vez modelo y tabla. | Escribir menos código en apps chicas. | TaskFlow la descartó: funde dominio y persistencia, y la regla del proyecto es que el dominio no importa persistencia. |

### Patrones de persistencia y sesión

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **Data Mapper** | Una capa que mueve datos entre objetos y base manteniéndolos independientes: los objetos del dominio no necesitan saber que existe una base. | Que `Tarea` (Pydantic) no importe SQLAlchemy. | Es la regla de dependencia de S04 aplicada a la persistencia. En TaskFlow son las funciones `_a_dominio`. |
| **Repository** | Media entre el dominio y la capa de mapeo con una interfaz tipo colección (`crear`, `listar`, `obtener`, `guardar`). | Cambiar memoria por Postgres sin tocar al que lo usa. | La interfaz se conserva; solo cambia lo de adentro. |
| **`Session`** | El objeto de SQLAlchemy que lleva la cuenta de los objetos cargados y cambiados, y la transacción en curso. | Agrupar todo lo que hace un request en una transacción. | Una por request: compartirla entre requests mezclaría sus transacciones. |
| **`sessionmaker`** | Una fábrica de sesiones configurada una vez (`SessionLocal`). | Crear sesiones iguales en cada request. | Se crea a nivel de módulo; lo que se crea por request es la sesión, no la fábrica. |
| **Autobegin** | La sesión abre la transacción sola, apenas hacés la primera operación. | No tener que escribir `begin()`. | Por eso nunca vas a ver un `BEGIN` explícito en TaskFlow. |
| **`flush`** | Enviar a la base el SQL pendiente **dentro** de la transacción abierta, sin confirmarla. | Obtener el `id` de una fila recién insertada antes del `commit`. | El repository hace `flush`; quien decide confirmar es otro. |
| **`commit` / `rollback`** | Confirmar (la transacción se vuelve visible y durable) o deshacer todo lo hecho desde que empezó. | Cerrar una operación de negocio de forma atómica. | En TaskFlow los dos viven en el service, no en el repository ni en `get_db`. |
| **Identity map** | El registro interno de la sesión: cada fila cargada existe una sola vez como objeto. | Que dos `session.get(TareaORM, 1)` en el mismo request devuelvan el mismo objeto. | Evita copias divergentes de la misma fila dentro de una transacción. |
| **`expire_on_commit`** | Si después de un `commit` la sesión marca los objetos como vencidos y los recarga al próximo acceso (default: sí). | Con `False`, leer un objeto después del `commit` sin disparar SQL. | TaskFlow lo apaga: el objeto queda usable si alguien lo lee después de confirmar. |
| **Autoflush** | Hacer `flush` automático antes de cada consulta. | Que una consulta vea los cambios pendientes de la misma sesión. | TaskFlow lo apaga (`autoflush=False`) y hace `flush()` explícito donde lo necesita. |
| **Sesión por request** | Abrir una `Session` al empezar el request y cerrarla al terminar (`get_db` con `yield`). | Una transacción por request, aislada de las demás. | Una sesión global por proceso (lo que era el `dict` de S05) mezclaría requests concurrentes. |
| **Unit of work** | Mantiene la lista de objetos afectados por una transacción de negocio y coordina la escritura de los cambios. | Que "mover la tarea" (y mañana "mover y registrar actividad") se confirme entera o nada. | La `Session` es el mecanismo; `ServicioTareas` decide cuándo confirmar. |
| **Lazy loading** | Cargar una relación recién cuando se accede al atributo, con un `SELECT` aparte. | No traer datos que nadie usa. | Es el default de `relationship`, y es el origen del N+1. |
| **N+1** | 1 consulta para traer N filas, más 1 por cada fila para traer su relación. | Reconocer por qué un listado se vuelve lento al crecer. | Se corrige pidiendo la carga anticipada (`selectinload`); en TaskFlow eso llega en M07·S08. |
| **`echo=True`** | Opción de `create_engine` que imprime cada SQL emitido. | **Ver** lo que hace el ORM en vez de imaginarlo. | Solo para depurar: no se commitea, porque inunda los logs. |
| **`lifespan`** | La función de FastAPI que corre código al arrancar (antes del `yield`) y al apagar (después). | Crear el esquema y sembrar datos mínimos antes de recibir requests. | Es el lugar previsto para el arranque; ponerlo a nivel de módulo correría en cada import. |

### Transacciones, aislamiento y concurrencia

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **Transacción implícita** | En PostgreSQL toda sentencia corre dentro de una transacción; si no escribís `BEGIN`, la base la abre y la confirma sola. | Entender qué pasa con un `UPDATE` suelto en `psql`. | Por eso un `UPDATE` en autocommit es atómico aunque no lo envuelvas. |
| **Savepoint** | Un punto intermedio dentro de una transacción al que se puede volver con `ROLLBACK TO`. | Deshacer una parte sin perder todo. | No lo usa TaskFlow; se nombra para que sepas que existe. |
| **Aislamiento** (*isolation level*) | Cuánto ve una transacción de lo que hacen las otras al mismo tiempo: Read Committed, Repeatable Read, Serializable. | Elegir entre más garantías y más conflictos que reintentar. | Más aislamiento = menos anomalías, más errores de serialización. |
| **Read Committed** | El nivel por defecto de PostgreSQL: cada sentencia ve lo confirmado antes de que empiece. | Es el nivel en que corre TaskFlow, porque el tag no fija otro. | Buen equilibrio para la mayoría de las apps, pero no evita el *lost update*. |
| **MVCC** | Control de concurrencia multiversión: cada sentencia ve un *snapshot* de los datos, y leer nunca bloquea escribir ni escribir bloquea leer. | Que el tablero se lea sin frenarse mientras alguien mueve una tarjeta. | Por eso el problema de TaskFlow no son las lecturas sino dos escrituras basadas en una lectura vieja. |
| **Lost update** | Dos transacciones leen el mismo dato, las dos escriben, y la segunda pisa a la primera sin saberlo. | Nombrar el riesgo de "dos personas tocan la misma tarea". | Es la anomalía que importa en TaskFlow, y Read Committed no la impide. |
| **Check-then-act** | Leer un valor, decidir con él y escribir, en pasos separados. | Reconocer el patrón de código que produce el lost update. | Entre el *check* y el *act*, otro puede cambiar el dato. |
| **Last-writer-wins** | La política implícita de "gana la última escritura". | Describir cómo se comporta hoy `mover_tarea`. | Aceptable para mover una tarjeta; peligrosa cuando la escritura depende de lo leído. |
| **Bloqueo optimista** | Detectar el conflicto al escribir (con una columna de versión) y rechazar la escritura vieja. | Conflictos raros, y transacciones de negocio más largas que un request (el tablero abierto cinco minutos). | No toma locks; a cambio, alguien tiene que manejar el rechazo. |
| **Bloqueo pesimista** (`SELECT … FOR UPDATE`) | Bloquear la fila al leerla para que nadie más la modifique hasta que termine tu transacción. | Conflictos frecuentes dentro de una misma transacción. | Un lock no sobrevive al request, así que no sirve para una edición que dura minutos. |
| **Deadlock** | Dos transacciones esperándose mutuamente. PostgreSQL lo detecta y aborta una. | Saber qué error esperar y cómo evitarlo. | La mejor defensa es tomar los locks siempre en el mismo orden. |
| **SQLSTATE** | Código estándar de cinco caracteres que acompaña cada error de la base (`40001`, `23503`…). | Decidir en el código si un error se reintenta o no. | El texto del mensaje cambia; el código no. |
| **Error de serialización** (`40001`) | El error que devuelve PostgreSQL cuando no puede garantizar el aislamiento pedido. | Señal de que hay que reintentar la transacción entera. | Es un conflicto de *timing*, no un dato inválido. |

### El esquema en el tiempo y la calidad del dato

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **`create_all`** | `Base.metadata.create_all(engine)`: crea las tablas que falten a partir de los modelos ORM. | Tener un esquema funcionando en un prototipo sin herramientas extra. | Es idempotente pero **no altera** tablas existentes: si el modelo cambia, no se entera. |
| **Migración de esquema** | Un script versionado que lleva el esquema de una versión a la siguiente (y, a veces, de vuelta). | Cambiar tablas que ya tienen datos sin perderlos. | Es la frontera entre prototipo y producción; en TaskFlow queda fuera del módulo. |
| **Alembic** | La herramienta de migraciones del ecosistema SQLAlchemy, con *autogenerate*. | Generar migraciones candidatas comparando modelos y base. | Lo que genera siempre hay que revisarlo: un renombre sale como *drop + add* y puede borrar datos. |
| **Seed** | Datos mínimos que se cargan para que la app funcione (el equipo `Core` y el proyecto `General`). | Que `POST /tasks` tenga un proyecto al que apuntar desde el primer arranque. | En el tag se siembra con ids fijos; M07·S08 lo cambia a "buscar o crear por nombre". |
| **Datos limpios / consistentes / frescos** | Limpios: válidos y sin duplicados. Consistentes: las relaciones y reglas se cumplen. Frescos: reflejan el estado actual y se sabe de cuándo son. | Las tres propiedades que Ng pide asegurar al gestionar datos. | Cada una tiene un mecanismo distinto: restricciones, transacciones y timestamps. |
| **Ciclo de vida del dato** | Las etapas de un dato: creación → uso → archivo → borrado. | Decidir qué pasa con los comentarios cuando se borra una tarea, o cuánto se guarda algo. | Se desarrolla en M07·S08 (`docs/datos.md`); hoy se anticipa con `ON DELETE`. |

---

## 4. Notas de estudio por subtema

### 4.0 El mapa de la sesión: un request de punta a punta

Antes de entrar en cada subtema, mirá qué pasa cuando alguien mueve una tarea en el tag `s07`. Todo lo que ves en este diagrama se explica en las secciones 4.2 a 4.6: quién abre la sesión, quién toca la base, quién confirma y quién cierra.

```mermaid
sequenceDiagram
    participant CLI as Cliente
    participant RT as Router tareas.py
    participant DEP as obtener_servicio_tareas
    participant GDB as get_db
    participant SV as ServicioTareas
    participant RP as RepositorioTareasSQL
    participant PG as PostgreSQL

    CLI->>RT: POST /tasks/1/move con estado en progreso
    RT->>DEP: Depends
    DEP->>GDB: Depends
    GDB-->>DEP: Session nueva desde SessionLocal
    DEP-->>RT: ServicioTareas con los dos repos sobre esa Session
    RT->>SV: mover_tarea
    SV->>RP: obtener
    RP->>PG: SELECT de la tarea, abre la transacción
    SV->>RP: guardar
    RP->>PG: UPDATE de estado, con flush y sin confirmar
    SV->>PG: COMMIT
    SV-->>RT: Tarea de dominio
    RT-->>CLI: 200 con la tarea en JSON
    GDB->>PG: close de la Session al terminar el request
```

Tres cosas para retener del diagrama, que el resto de la sesión justifica:

- **Una sesión por request.** `get_db` la abre y la cierra; los dos repos y el service trabajan sobre la misma.
- **El repository habla SQL pero no confirma.** Hace `flush`, que manda el `UPDATE` dentro de la transacción abierta.
- **El `COMMIT` lo hace el service**, mientras el endpoint todavía corre. No lo hace `get_db`, por una razón que vas a ver en 4.4.

---

### 4.1 Del modelo de dominio al esquema ER

**Para qué.** En S06 dibujaste un `classDiagram` con objetos que se referencian por id. Una base relacional no guarda objetos: guarda filas en tablas, y protege las referencias con claves. Si traducís el dominio a tablas sin un procedimiento, el agente lo va a hacer por vos, y va a decidir solo qué es obligatorio, qué se borra en cascada y dónde vive cada M:N. Esta sección es el procedimiento.

**El procedimiento de traducción.** Cada concepto del dominio tiene una forma estándar en el esquema:

| En el dominio (S06) | En el esquema (S07) | En TaskFlow |
|---|---|---|
| Entidad con identidad | Tabla con PK | `Tarea` → tabla `tareas`, `id` PK |
| Referencia por id (N:1) | Columna FK | `Tarea.proyecto_id` → `tareas.proyecto_id` FK a `proyectos.id` |
| Referencia opcional (`int \| None`) | FK nullable | `Tarea.responsable_id` → `tareas.responsable_id` nullable |
| Referencia obligatoria (`int`) | FK `NOT NULL` | `Comentario.autor_id` → `comentarios.autor_id` `NOT NULL` |
| Lista de ids de una M:N (`etiqueta_ids`) | Tabla de enlace con PK compuesta | `tarea_etiqueta (tarea_id, etiqueta_id)` |
| Enum de dominio (`Estado`) | Columna de texto, con o sin `CHECK` | `tareas.estado` `String(20)`, **sin** `CHECK` |
| Vista del dominio | **No** es tabla | `Tablero` (llega en S08) |
| Timestamps de `EntidadConTiempos` | Columnas con default en la base | `created_at` / `updated_at` con `server_default=func.now()` |

Fijate en la fila de la M:N. En S06 la guardaste **de un solo lado** (`Usuario.equipo_ids`, `Tarea.etiqueta_ids`) para no tener dos listas que sincronizar. En la base no hay "lado": hay una tabla con una fila por par, y desde esa tabla se navega en las dos direcciones. Por eso son dos tablas de enlace, `usuario_equipo` y `tarea_etiqueta`, y ninguna lista.

**Ejemplo práctico: el ER de TaskFlow.** Este es el esquema que deja el tag `s07`, leído directamente de `app/db/models.py`:

```mermaid
erDiagram
    EQUIPOS ||--o{ PROYECTOS : "tiene"
    EQUIPOS ||--o{ USUARIO_EQUIPO : "agrupa"
    USUARIOS ||--o{ USUARIO_EQUIPO : "pertenece"
    PROYECTOS ||--o{ TAREAS : "contiene"
    USUARIOS |o--o{ TAREAS : "es responsable de"
    TAREAS ||--o{ COMENTARIOS : "recibe"
    USUARIOS ||--o{ COMENTARIOS : "escribe"
    TAREAS ||--o{ TAREA_ETIQUETA : "lleva"
    ETIQUETAS ||--o{ TAREA_ETIQUETA : "se aplica en"

    EQUIPOS {
        int id PK
        string nombre
    }
    USUARIOS {
        int id PK
        string nombre
        string email UK
    }
    PROYECTOS {
        int id PK
        string nombre
        int equipo_id FK
        string descripcion "nullable"
    }
    TAREAS {
        int id PK
        string titulo
        string descripcion "nullable"
        string estado "default backlog, sin CHECK"
        int proyecto_id FK
        int responsable_id FK "nullable"
    }
    COMENTARIOS {
        int id PK
        int tarea_id FK
        int autor_id FK
        string texto
    }
    ETIQUETAS {
        int id PK
        string nombre
        string color "nullable"
    }
    USUARIO_EQUIPO {
        int usuario_id PK, FK
        int equipo_id PK, FK
    }
    TAREA_ETIQUETA {
        int tarea_id PK, FK
        int etiqueta_id PK, FK
    }
```

**Cómo leer la cardinalidad.** Cada extremo de la línea tiene dos marcas: la de adentro es el mínimo y la de afuera el máximo. `|` es "uno", `o` es "cero", `{` es "muchos".

- `PROYECTOS ||--o{ TAREAS`: una tarea pertenece a **exactamente un** proyecto (`||`, porque `proyecto_id` es `Mapped[int]`, `NOT NULL`); un proyecto tiene **cero o muchas** tareas (`o{`).
- `USUARIOS |o--o{ TAREAS`: una tarea tiene **cero o un** responsable (`|o`), porque `responsable_id` es `Mapped[int | None]`. Compará con `COMENTARIOS`, donde el autor es obligatorio (`autor_id: Mapped[int]`) y por eso la marca es `||`.
- Las M:N no aparecen como una línea `}o--o{`: aparecen como **dos** 1:N hacia la tabla de enlace. Así es como la base las guarda de verdad.
- En las tablas de enlace cada columna es a la vez parte de la PK y FK: se escribe `PK, FK`, separado por coma, que es la forma que documenta Mermaid.
- Los timestamps se omiten por brevedad, igual que en el `.mmd` del tag: todas las tablas de entidad llevan `created_at` / `updated_at`.

**Por qué así.** El diagrama se dibuja **desde el código**, no desde la memoria. Si el ER dice `||` y el modelo dice `Mapped[int | None]`, uno de los dos miente, y el que corre en producción es el modelo. Ese es el ejercicio de la Unidad 1: el `docs/diagrams/s07-er.mmd` del tag tiene dos diferencias con este diagrama, y encontrarlas es leer el ER contra `models.py`.

**Lo que el diagrama no muestra porque el tag no lo declara.** Esta lista es tan importante como el diagrama, porque es la discusión de "datos limpios" de la sesión:

| Qué falta | Consecuencia hoy | Qué haría falta |
|---|---|---|
| `ON DELETE` en las FK | Todas quedan en `NO ACTION`, el default de PostgreSQL. Borrar una tarea que tiene comentarios **falla** con `23503` (`foreign_key_violation`), y borrar un usuario responsable de tareas también. | Decidir por FK: `CASCADE`, `SET NULL` o `RESTRICT` según el ciclo de vida (ejercicio 🟡 de la Unidad 1). |
| Índices sobre las FK | En PostgreSQL, declarar una FK **no** crea un índice sobre la columna que referencia. "Las tareas del proyecto 1" recorre `tareas` entera. | La documentación de PostgreSQL dice que suele ser buena idea indexarlas. Con pocos datos no se nota; con el tablero de S08 sí. |
| `CHECK` sobre `estado` | La base acepta `'archivado'` sin protestar. Solo el Enum `Estado` del dominio lo rechaza, y solo si el dato pasa por la app. | `CHECK (estado IN ('backlog', 'en progreso', 'hecho'))`. |
| `UNIQUE` en `equipos.nombre` y `etiquetas.nombre` | Puede haber dos etiquetas `bug`. | Decidir si el nombre es clave natural. M07·S08 decide **no** agregar ese `UNIQUE` y resolverlo en el seed. |

Ninguna de estas cuatro se implementa en el tag. Quedan como discusión, sin sesión asignada. Lo importante es que sepas que existen y por qué el default no es neutro.

**Las acciones referenciales, en una tabla.** Son cinco y conviene distinguirlas bien:

| Acción | Qué pasa al borrar la fila referenciada | Cuándo tiene sentido |
|---|---|---|
| `NO ACTION` (default) | Se rechaza el borrado si quedan referencias. El chequeo puede postergarse hasta el final de la sentencia (o de la transacción, si la restricción es diferible). | Cuando no decidiste nada. Es seguro, pero obliga a borrar a mano en orden. |
| `RESTRICT` | Igual que `NO ACTION`, pero el chequeo es inmediato y no se puede postergar. | Cuando borrar el padre está prohibido mientras tenga hijos (un proyecto con tareas). |
| `CASCADE` | Se borran también las filas que lo referencian. | Cuando el hijo no tiene sentido sin el padre: las filas de `tarea_etiqueta` de una tarea borrada. |
| `SET NULL` | La FK de los hijos pasa a `NULL`. | Cuando la relación es opcional: el responsable de una tarea. Requiere que la columna sea nullable. |
| `SET DEFAULT` | La FK de los hijos pasa a su valor por defecto. | Raro: un "usuario eliminado" genérico. |

**Errores comunes.**
- **Dibujar la M:N como una línea directa.** `TAREAS }o--o{ ETIQUETAS` es un dibujo conceptual; el esquema real tiene la tabla de enlace en el medio, y es ahí donde vive la PK compuesta.
- **Confundir "la columna es FK" con "la columna es obligatoria".** Son dos decisiones distintas. `responsable_id` es FK y es nullable.
- **Creer que `NO ACTION` significa "no hace nada".** Hace algo: rechaza el borrado.
- **Asumir que la FK crea índice.** En PostgreSQL no lo crea.
- **Convertir el Enum en tabla.** `Estado` es un conjunto cerrado de valores del dominio, no una entidad con identidad.

> 💡 Para profundizar: *Entity Relationship Diagrams* (Mermaid), *5.4. Constraints* (PostgreSQL 16) y *Basic Relationship Patterns* (SQLAlchemy 2.0). Links en la sección 10.

---

### 4.2 El ORM con SQLAlchemy 2.0, separado del dominio

**Para qué.** El dominio de TaskFlow ya existe: `Tarea`, `Proyecto` y compañía en `app/models/`, como clases Pydantic que el router usa para validar el body. Ahora hace falta otra representación de las mismas entidades, la que sabe de tablas, columnas y claves. La pregunta de diseño es si esas dos representaciones son **la misma clase** o **dos clases**. TaskFlow eligió dos, y esta sección explica qué cuesta y qué compra.

**Las tres opciones que se evaluaron** (son las alternativas de la entrada `[s07] Stack de ORM y separación dominio/persistencia`):

| | SQLAlchemy 2.0, ORM separado | SQLModel | SQL crudo (psycopg) |
|---|---|---|---|
| Clases por entidad | Dos: `Tarea` (dominio) y `TareaORM` (persistencia) | Una: Pydantic y tabla a la vez | Una de dominio; el SQL a mano |
| Mapeo | Explícito, en el repository (`_a_dominio`) | Implícito | Manual, fila por fila |
| El dominio importa persistencia | No | Sí | No |
| Código | Medio | Poco | Mucho (6 entidades + 2 M:N) |
| Lo que te da | Cada capa evoluciona por separado; el dominio se testea sin base | Velocidad para empezar | Control total del SQL |
| Elegido en TaskFlow | **Sí** | No | No |

El tutorial oficial de FastAPI para bases SQL usa SQLModel, y es lo primero que un agente va a imitar si no le decís otra cosa. No está mal: para una app chica es una buena elección. TaskFlow la descarta por una regla del proyecto —el dominio nunca importa persistencia—, y esa regla tiene un costo que se paga en cada entidad: escribir el mapeo.

**`app/db/database.py`, línea por línea.** Es el archivo que conecta todo:

```python
import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# DATABASE_URL debe usar el driver de SQLAlchemy + psycopg3: postgresql+psycopg://
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow",
)

# `future=True` es el default en SQLAlchemy 2.0; `pool_pre_ping` evita conexiones muertas.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa común de todos los modelos ORM."""


def get_db() -> Iterator[Session]:
    """Entrega una Session por request; hace rollback ante error y cierra siempre."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

Por qué cada decisión:

- **`DATABASE_URL` desde el entorno, con default.** El default coincide con `.env.example`, así que si no cambiaste nada, conecta igual. Si cambiaste `POSTGRES_PORT` porque el 5432 estaba ocupado, el default ya no sirve y tenés que pasar el `.env` (`uvicorn … --env-file .env`).
- **`postgresql+psycopg://` y no `postgresql://` a secas.** La parte `+psycopg` elige el driver de forma explícita. Sin ella, SQLAlchemy usa el driver por defecto de su versión: en SQLAlchemy 2.0 es psycopg2, y en 2.1 pasó a ser psycopg 3. Como `requirements.txt` pide `sqlalchemy>=2.0` sin techo, al 1 de octubre de 2026 eso instala la 2.1.x (la 2.1.0 se publicó el 24/09/2026 y la 2.1.1 el 25/09/2026, según PyPI). Con el driver explícito, el código conecta igual en las dos versiones; sin él, en 2.0 buscaría un paquete que no instalaste.
- **`engine` a nivel de módulo, una sola vez.** El engine mantiene el pool de conexiones. Crear uno por request sería abrir una conexión TCP nueva cada vez.
- **`pool_pre_ping=True`.** Prueba la conexión cada vez que la saca del pool. Si reiniciaste el contenedor, la conexión vieja está muerta y sin esta opción el primer request fallaría.
- **`SessionLocal = sessionmaker(...)` a nivel de módulo.** Es la fábrica, configurada una vez. Lo que se crea por request es la sesión.
- **`autoflush=False`.** El repositorio hace `flush()` explícito donde lo necesita (`crear` y `guardar`), así que no depende del autoflush. Es más predecible: el SQL sale cuando el código lo pide.
- **`expire_on_commit=False`.** Por defecto, después de un `commit` la sesión marca los objetos como vencidos y los recarga con SQL al próximo acceso. Con `False`, quedan usables. En TaskFlow `_a_dominio` corre antes del `commit`, así que no es imprescindible, pero evita sorpresas si alguien lee el objeto después.
- **`get_db` con `yield`, `except` y `finally`.** Lo ves en detalle en 4.4.

**`app/db/models.py`: las piezas que importan.** No hace falta copiar el archivo entero para entenderlo; estas tres piezas cubren todos los patrones:

```python
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

# --- Tablas de enlace M:N (solo claves foráneas, sin entidad propia) ---
tarea_etiqueta = Table(
    "tarea_etiqueta",
    Base.metadata,
    Column("tarea_id", ForeignKey("tareas.id"), primary_key=True),
    Column("etiqueta_id", ForeignKey("etiquetas.id"), primary_key=True),
)


class TareaORM(Base):
    __tablename__ = "tareas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # El estado se guarda como string; el dominio valida con el Enum Estado.
    estado: Mapped[str] = mapped_column(String(20), default="backlog")
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.id"))
    responsable_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    proyecto: Mapped["ProyectoORM"] = relationship(back_populates="tareas")
    responsable: Mapped["UsuarioORM | None"] = relationship()
    comentarios: Mapped[list["ComentarioORM"]] = relationship(back_populates="tarea")
    etiquetas: Mapped[list["EtiquetaORM"]] = relationship(
        secondary=tarea_etiqueta, back_populates="tareas"
    )


class ComentarioORM(Base):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    tarea_id: Mapped[int] = mapped_column(ForeignKey("tareas.id"))
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    texto: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    tarea: Mapped["TareaORM"] = relationship(back_populates="comentarios")
    autor: Mapped["UsuarioORM"] = relationship()
```

Cómo leerlo, y por qué está escrito así:

- **El sufijo `ORM`** (`TareaORM`, `ComentarioORM`…) evita el choque de nombres con `Tarea`, `Comentario`, etc. del dominio. En el repository conviven las dos y tienen que distinguirse a simple vista.
- **`__tablename__` en plural y en español** (`tareas`, `comentarios`), coherente con los campos en español del dominio.
- **La anotación decide la nulabilidad.** La documentación de SQLAlchemy lo dice así: `Optional[]` (o `X | None`) significa `NULL` y su ausencia `NOT NULL`. Por eso `autor_id: Mapped[int]` es `NOT NULL` y `responsable_id: Mapped[int | None]` es nullable. El `nullable=True` que el agente escribió en `descripcion` y `responsable_id` es **redundante**: no está mal, pero es un buen ejemplo de "leé lo que generó el agente".
- **`default="backlog"` vs `server_default=func.now()`.** No son lo mismo. `default` es un default **del lado de Python**: lo pone el ORM al insertar si no le diste valor. `server_default` vive **en la base**: un `INSERT` hecho a mano en `psql` también lo recibe. Consecuencia práctica: un `INSERT INTO tareas` en `psql` sin `estado` falla por `NOT NULL`, mientras que sin `created_at` funciona.
- **`onupdate=func.now()` lo aplica el ORM**, en los `UPDATE` que él emite. Un `UPDATE` hecho a mano en `psql` **no** toca `updated_at`. Para que la base lo garantizara siempre haría falta un trigger, que no está en el tag.
- **`mapped_column(primary_key=True)` sin `Identity()`** hace que SQLAlchemy emita `SERIAL` para la PK. Funciona, pero tiene una consecuencia que vas a ver en 4.7.
- **La tabla de enlace es una `Table`, no una clase.** No tiene columnas propias, así que no necesita identidad en el ORM: alcanza con `secondary=tarea_etiqueta` en las dos `relationship`. Si mañana la relación necesitara datos propios (por ejemplo, el rol de un usuario en un equipo), se pasaría a un *association object*.
- **`back_populates`** conecta las dos puntas de una relación (`TareaORM.etiquetas` ⇄ `EtiquetaORM.tareas`) para que modificar una actualice la otra en memoria.

**Errores comunes.**
- **Importar `TareaORM` en `app/models/` o en el router.** Rompe la separación. El ORM se importa solo en `app/db/`, en los repositorios y en `app/main.py` (para el seed).
- **Creer que `default=` protege la base.** Solo protege los inserts que pasan por el ORM.
- **Usar `postgresql://` a secas** "porque anda en mi máquina". Anda o no anda según la versión de SQLAlchemy que resuelva `pip`.
- **Olvidar importar los modelos antes de `create_all`.** Si `app/db/models.py` nunca se importó, `Base.metadata` está vacío y `create_all` no crea nada. Por eso `app/main.py` importa `EquipoORM, ProyectoORM` con un `# noqa: F401`.

> ⚠️ Si `pip install -r requirements.txt` instala SQLAlchemy 2.1 y algo falla al arrancar, probá fijar la serie 2.0: `pip install 'sqlalchemy>=2.0,<2.1'`. El tag se escribió contra 2.0. Lo que usa (`DeclarativeBase`, `Mapped`, `sessionmaker`, `secondary=`, driver explícito) no debería verse afectado por los cambios de 2.1, pero tu profesor te confirma en clase si lo probó.

> 💡 Para profundizar: *Table Configuration with Declarative*, *PostgreSQL dialect*, *Engine Configuration* y *What's New in SQLAlchemy 2.1?*; *Installation* de psycopg 3; y el tutorial *SQL (Relational) Databases* de FastAPI como contraste. Links en la sección 10.

---

### 4.3 El repository que mapea ORM ⇄ dominio

**Para qué.** En S05 el service hablaba con `RepositorioTareasEnMemoria`, que guardaba objetos `Tarea` en un `dict`. El comentario del propio archivo lo anticipaba: "en s07 se reemplaza por una versión con ORM sin tocar service ni router". El repository es la costura que hace posible ese reemplazo: el service le pide tareas y le devuelve tareas, y no sabe si por dentro hay un `dict` o PostgreSQL.

**Dos patrones con nombre.** En el catálogo de *Patterns of Enterprise Application Architecture* de Martin Fowler:

- **Data Mapper** es una capa de mappers que mueve datos entre objetos y base manteniéndolos independientes; los objetos en memoria ni siquiera necesitan saber que existe una base. En TaskFlow es `_a_dominio`.
- **Repository** (de Edward Hieatt y Rob Mee) media entre el dominio y la capa de mapeo con una interfaz tipo colección. En TaskFlow es `RepositorioTareasSQL`.

**Ejemplo práctico: `app/repositories/tarea_repository.py` en el tag.**

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TareaORM
from app.models.tarea import Tarea


def _a_dominio(fila: TareaORM) -> Tarea:
    """Convierte una fila ORM en una entidad de dominio Pydantic."""
    return Tarea(
        id=fila.id,
        titulo=fila.titulo,
        descripcion=fila.descripcion,
        estado=fila.estado,
        proyecto_id=fila.proyecto_id,
        responsable_id=fila.responsable_id,
        etiqueta_ids=[e.id for e in fila.etiquetas],
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioTareasSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def crear(self, tarea: Tarea) -> Tarea:
        fila = TareaORM(
            titulo=tarea.titulo,
            descripcion=tarea.descripcion,
            estado=tarea.estado.value,
            proyecto_id=tarea.proyecto_id,
            responsable_id=tarea.responsable_id,
        )
        self._session.add(fila)
        self._session.flush()  # obtiene el id autogenerado sin cerrar la transacción
        return _a_dominio(fila)

    def listar(self) -> list[Tarea]:
        filas = self._session.scalars(select(TareaORM).order_by(TareaORM.id)).all()
        return [_a_dominio(f) for f in filas]

    def obtener(self, tarea_id: int) -> Tarea | None:
        fila = self._session.get(TareaORM, tarea_id)
        return _a_dominio(fila) if fila is not None else None

    def guardar(self, tarea: Tarea) -> Tarea:
        # Actualiza una tarea existente (p. ej. tras cambiarle el estado).
        fila = self._session.get(TareaORM, tarea.id)
        fila.titulo = tarea.titulo
        fila.descripcion = tarea.descripcion
        fila.estado = tarea.estado.value
        fila.proyecto_id = tarea.proyecto_id
        fila.responsable_id = tarea.responsable_id
        self._session.flush()
        return _a_dominio(fila)
```

Por qué está escrito así:

- **La misma interfaz que en memoria** (`crear`, `listar`, `obtener`, `guardar`). Es lo que permite que el router no cambie. Lo único nuevo es el constructor: recibe la `Session` del request.
- **`_a_dominio` es una función, no un método de `TareaORM`.** Si fuera método del ORM, el ORM tendría que importar el dominio, y el mapeo quedaría repartido. Así vive en un solo lugar: el repository, la única capa que conoce las dos representaciones.
- **`estado=tarea.estado.value` al escribir, `estado=fila.estado` al leer.** En la base va el texto (`'en progreso'`, con espacio, porque es el `.value` del Enum). Al leer, Pydantic convierte el texto de vuelta al Enum, y si el texto no es un valor válido, falla ahí.
- **`flush()` en `crear`, no `commit()`.** El `flush` manda el `INSERT` dentro de la transacción abierta, y la base asigna el `id`: por eso `_a_dominio(fila)` ya tiene `id`. Pero la transacción sigue abierta: si después algo falla y el service hace `rollback`, ese `INSERT` desaparece (y el `id` que viste no existe).
- **Ningún método hace `commit`.** La documentación de SQLAlchemy recomienda mantener el ciclo de vida de la sesión, y normalmente el de la transacción, separado y externo a las funciones que acceden a datos. Si cada repo confirmara por su cuenta, una operación de negocio que toca dos repos no podría ser atómica.
- **`session.get(...)` en `obtener` y `guardar`.** Busca por PK y, gracias al identity map, la segunda llamada dentro del mismo request devuelve el mismo objeto sin ir a la base. Por eso `guardar` no paga un `SELECT` extra después de `obtener`.

**`flush` vs `commit`, en una línea cada uno.**

| | `flush()` | `commit()` |
|---|---|---|
| Qué hace | Envía el SQL pendiente a la base | Cierra la transacción y la vuelve visible y durable |
| ¿Otros lo ven? | No (en Read Committed nadie ve lo no confirmado) | Sí |
| ¿Se puede deshacer? | Sí, con `rollback()` | No |
| Quién lo hace en TaskFlow | El repository | El service |

**El N+1 latente, que está en el tag.** Mirá la línea `etiqueta_ids=[e.id for e in fila.etiquetas]`. `fila.etiquetas` es una `relationship` sin estrategia de carga, así que es *lazy*: se carga con un `SELECT` aparte la primera vez que se accede. En `listar()`, `_a_dominio` se llama una vez por fila. Resultado: **1** consulta para traer las tareas, más **1 por cada tarea** para sus etiquetas. Con 3 tareas son 4 consultas; con 500, 501. La documentación de SQLAlchemy lo nombra como el problema N+1 y recomienda `selectinload()` como, en general, la mejor estrategia para colecciones; `raiseload()` sirve para detectarlo, porque convierte la carga perezosa en un error.

El tag **no** lo corrige: acá se diagnostica. M07·S08 usa `selectinload` en el repositorio del tablero, que es donde la lectura pesa. Para verlo con tus propios ojos, activá `echo=True` (paso 9 de la guía y ejercicio 🟡 de la Unidad 2).

**Errores comunes.**
- **Hacer `commit` en el repository** "porque si no, no se guarda". Se guarda: lo confirma el service. El síntoma de un `commit` en el repo es que una operación de dos pasos queda a medias cuando falla el segundo.
- **Devolver `TareaORM` al service.** El service quedaría acoplado al ORM y el router terminaría serializando objetos ORM.
- **Olvidar que `crear` no persiste `etiqueta_ids`.** Mirá el código: `TareaORM(...)` no recibe etiquetas. Si mandás `etiqueta_ids` en el body de `POST /tasks`, se ignoran y la respuesta vuelve con `[]`. Asociar etiquetas a tareas llega con los endpoints de etiquetas, en S10.
- **No ver el N+1 porque "anda rápido".** Con tres tareas en local todo anda rápido. El N+1 se ve contando consultas, no midiendo tiempo.

> 💡 Para profundizar: *Data Mapper*, *Repository* y *Relationship Loading Techniques*. Links en la sección 10.

---

### 4.4 Sesión por request y unit of work

**Para qué.** En S05, `app/dependencies.py` creaba **una** instancia de cada repositorio y del service por proceso: tenía sentido, porque el `dict` era el almacenamiento. Con una base de datos, compartir una `Session` entre requests sería un desastre: dos requests concurrentes mezclarían sus transacciones, y el `rollback` de uno desharía el trabajo del otro. Hace falta **una sesión (y una transacción) por request**, y alguien que decida cuándo confirmarla.

**La sesión por request: `get_db`.** Mirá otra vez las tres ramas:

```python
def get_db() -> Iterator[Session]:
    db = SessionLocal()          # 1. se abre al empezar el request
    try:
        yield db                 # 2. el endpoint (y todo lo que depende de él) corre acá
    except Exception:
        db.rollback()            # 3a. si el endpoint levantó algo, se deshace…
        raise                    #     …y se re-lanza, sí o sí
    finally:
        db.close()               # 3b. se cierra siempre
```

- **El `raise` del `except` es obligatorio.** La documentación de FastAPI sobre dependencias con `yield` advierte que si la dependencia captura una excepción, tiene que re-lanzarla: si no, el cliente recibe un 500 sin registro del error.
- **`close()` sin `commit()` equivale a deshacer.** Si nadie confirmó, la transacción se descarta al cerrar. Por eso `listar_tareas` no confirma nada y no pasa nada malo: solo leyó.

**Por qué el `commit` no vive en `get_db`.** Sería tentador: "al salir del `yield`, si no hubo error, commit". El problema es *cuándo* corre ese código. Según la documentación de FastAPI, el código de salida de una dependencia con `yield` corre por defecto (`scope="request"`) **después de enviar la respuesta**. Un `commit` ahí podría fallar con el `200` ya enviado: el cliente cree que movió la tarea y la base dice que no. Con `scope="function"` el código de salida corre antes, pero el tag eligió otra solución: confirmar **dentro del service**, mientras el endpoint todavía corre. Si el `commit` falla, la excepción viaja al router y el cliente recibe un error.

**La composición por request: `app/dependencies.py`.**

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.proyecto_repository import RepositorioProyectosSQL
from app.repositories.tarea_repository import RepositorioTareasSQL
from app.services.tarea_service import ServicioTareas


def obtener_servicio_tareas(db: Session = Depends(get_db)) -> ServicioTareas:
    repo_tareas = RepositorioTareasSQL(db)
    repo_proyectos = RepositorioProyectosSQL(db)
    return ServicioTareas(repo_tareas, repo_proyectos, db)
```

**Por qué así.** Los dos repos reciben **la misma** sesión, y el service también. Eso hace que todo lo que pase en un request —verificar que el proyecto existe, insertar la tarea— ocurra en una sola transacción. El router sigue pidiendo `Depends(obtener_servicio_tareas)` como en S05: no se enteró del cambio. Crear tres objetos chicos por request es barato; lo caro (el engine y su pool) se creó una vez.

**El service como unit of work: `app/services/tarea_service.py`.**

```python
class ServicioTareas:
    def __init__(
        self,
        repo_tareas: RepositorioTareasSQL,
        repo_proyectos: RepositorioProyectosSQL,
        session: Session,
    ) -> None:
        self._repo_tareas = repo_tareas
        self._repo_proyectos = repo_proyectos
        self._session = session

    def crear_tarea(self, tarea: Tarea) -> Tarea:
        # Regla de negocio: una tarea siempre pertenece a un proyecto existente.
        if not self._repo_proyectos.existe(tarea.proyecto_id):
            raise ProyectoNoEncontrado(tarea.proyecto_id)
        # El estado inicial siempre es BACKLOG, sin importar lo que mande el cliente.
        tarea.id = None
        tarea.estado = Estado.BACKLOG
        try:
            creada = self._repo_tareas.crear(tarea)
            self._session.commit()
            return creada
        except Exception:
            self._session.rollback()
            raise

    def listar_tareas(self) -> list[Tarea]:
        return self._repo_tareas.listar()

    def mover_tarea(self, tarea_id: int, nuevo_estado: Estado) -> Tarea:
        tarea = self._repo_tareas.obtener(tarea_id)
        if tarea is None:
            raise TareaNoEncontrada(tarea_id)
        tarea.estado = nuevo_estado
        try:
            actualizada = self._repo_tareas.guardar(tarea)
            self._session.commit()  # transacción: la tarea queda movida atómicamente
            return actualizada
        except Exception:
            self._session.rollback()
            raise
```

El patrón **Unit of Work**, en el catálogo de P of EAA, mantiene la lista de objetos afectados por una transacción de negocio y coordina la escritura de los cambios y la resolución de problemas de concurrencia. En TaskFlow el trabajo se reparte: la `Session` de SQLAlchemy **es** el mecanismo (lleva la lista de objetos cambiados y los escribe en el `flush`), y el service decide **cuándo** se confirma. ¿Por qué el service? Porque es la capa que sabe dónde termina una operación de negocio: después de verificar la regla ("el proyecto existe") y de escribir.

Qué cambió respecto de S06 y qué no:

- **Cambió el constructor:** suma `session: Session`, y los type hints pasan a los repos SQL.
- **Cambiaron las escrituras:** `crear_tarea` y `mover_tarea` envuelven la escritura en `try: … commit() / except: rollback(); raise`.
- **No cambió la interfaz pública:** `crear_tarea`, `listar_tareas`, `mover_tarea` y las excepciones `ProyectoNoEncontrado` / `TareaNoEncontrada` son las mismas. Por eso `app/routers/tareas.py` no se tocó.

**El trade-off que el diff deja a la vista.** El dominio (`app/models/`) sigue limpio, pero el service ahora importa `sqlalchemy.orm.Session` para poder confirmar. Quedó acoplado a SQLAlchemy. La alternativa es una abstracción propia de unit of work (una clase con `commit()` y `rollback()` que envuelve la sesión): más código, la misma garantía. Para un prototipo, el acoplamiento es razonable. No es un error del tag: es un trade-off que conviene nombrar.

**¿Por qué el `rollback` aparece dos veces** (en el service y en `get_db`)? Porque cubren casos distintos. El del service deshace una escritura que falló en el `flush` o en el `commit`. El de `get_db` cubre cualquier otra excepción que suba desde el endpoint, por ejemplo un `HTTPException` 404 levantado por el router. Hacer `rollback` dos veces no rompe nada.

**Errores comunes.**
- **Una sesión global** (`db = SessionLocal()` a nivel de módulo, "para no crearla cada vez"). Es la sesión por proceso de S05 disfrazada, con los mismos problemas que el `dict` compartido, y peores.
- **Comerse la excepción** en el `except` de `get_db`. El cliente recibe un 500 y nadie sabe por qué.
- **Confirmar en el router.** Funciona, pero el router pasa a conocer la persistencia, y la regla de negocio queda separada del punto donde se confirma.
- **Confundir `close()` con `commit()`.** Cerrar no confirma.

> 💡 Para profundizar: *Session Basics* (SQLAlchemy 2.0), *Dependencies with yield* (FastAPI) y *Unit of Work* (P of EAA). Links en la sección 10.

---

### 4.5 Transacciones y ACID en la práctica

**Para qué.** En S06 definiste ACID como lista de garantías. Hoy la pregunta es concreta: ¿qué te da cada letra **en TaskFlow**, y qué no te da?

**Qué es una transacción, según PostgreSQL.** El tutorial de PostgreSQL 16 la describe como una operación *all-or-nothing* cuyos estados intermedios no ven las demás transacciones. Agrega tres cosas que conviene saber de memoria:

1. PostgreSQL ejecuta **toda** sentencia dentro de una transacción. Si no escribís `BEGIN`, la abre y la confirma sola (transacción implícita).
2. Los cambios de una transacción confirmada quedan en almacenamiento permanente **antes** de que la base la reporte como completa: eso es la durabilidad.
3. Los `SAVEPOINT` permiten deshacer una parte con `ROLLBACK TO` sin perder todo.

**ACID mapeado a TaskFlow:**

| Letra | Qué garantiza | Dónde la ves en TaskFlow | Lo que **no** cubre |
|---|---|---|---|
| **A** — Atomicidad | Todo o nada | Hoy `mover_tarea` toca una sola fila, así que se nota poco. Se va a notar cuando una escritura tenga varios pasos: comentar y tocar `updated_at` de la tarea, o mover y registrar actividad. Por eso el service ya es el dueño del `commit`. | No decide qué es "todo": eso lo define dónde ponés el `commit`. |
| **C** — Consistencia | Las restricciones declaradas se cumplen al confirmar | Las FK: no podés crear un comentario de una tarea que no existe, ni asignar un responsable inexistente. `NOT NULL` en `titulo` y `autor_id`. `UNIQUE` en `usuarios.email`. | Las reglas que **no** declaraste: `estado` no tiene `CHECK`, así que la base acepta `'archivado'`. |
| **I** — Aislamiento | Las transacciones concurrentes no se pisan… hasta cierto punto | Read Committed: nadie ve tu `UPDATE` hasta el `COMMIT`. | El *lost update*: lo ves en 4.6. |
| **D** — Durabilidad | Lo confirmado sobrevive a reinicios | Reiniciás `uvicorn` y las tareas siguen ahí. Con el `dict` de S05, no pasaba. | Que el volumen `taskflow_pgdata` exista: `docker compose down -v` lo borra. |

**Ejemplo práctico: una transacción a mano en `psql`.** Abrí dos terminales con `docker exec -it taskflow-db psql -U taskflow -d taskflow` y seguí el orden:

```sql
-- Terminal A
BEGIN;
UPDATE tareas SET estado = 'hecho' WHERE id = 1;
SELECT estado FROM tareas WHERE id = 1;     -- A ve 'hecho'

-- Terminal B (otra sesión psql)
SELECT estado FROM tareas WHERE id = 1;     -- B ve el valor anterior: A no confirmó

-- Terminal A
ROLLBACK;                                   -- nada pasó: all-or-nothing
```

**Por qué así.** El `BEGIN` explícito convierte las sentencias siguientes en una sola transacción; sin él, el `UPDATE` se confirmaría solo en el acto (transacción implícita) y no habría nada que comparar. La terminal B demuestra dos letras a la vez: el aislamiento (no ve lo no confirmado) y, después del `ROLLBACK`, la atomicidad (el cambio nunca existió).

**La C, en acción: el `23503`.** Hoy no hay endpoint de comentarios, así que para ver la FK en `NO ACTION` insertás uno a mano. **Hacelo dentro de un `BEGIN … ROLLBACK`**, para no dejar filas que el seed de S08 no espera:

```sql
BEGIN;
INSERT INTO usuarios (nombre, email) VALUES ('Ana', 'ana@ejemplo.dev') RETURNING id;
-- anotá el id que devuelve y usalo abajo en lugar de <id_ana>
INSERT INTO comentarios (tarea_id, autor_id, texto) VALUES (1, <id_ana>, 'Reviso el lunes');
DELETE FROM tareas WHERE id = 1;            -- falla: foreign_key_violation (SQLSTATE 23503)
ROLLBACK;
```

El `DELETE` falla porque `comentarios.tarea_id` apunta a la tarea y la FK está en `NO ACTION`: la base prefiere rechazar el borrado antes que dejar un comentario huérfano. Después del error, la transacción queda abortada (cualquier otra sentencia falla hasta el `ROLLBACK`); por eso el `ROLLBACK` va sí o sí.

**Otra C que ahora protege la base, y cómo lo muestra la API.** En S06, `responsable_id` no se validaba: podías crear una tarea con `responsable_id: 999`. Ahora hay FK. Si lo intentás con `POST /tasks`, el `flush` de `crear` falla con `23503`, el service hace `rollback` y re-lanza, y como el router solo traduce `ProyectoNoEncontrado`, el cliente recibe un **500**. La base protegió el dato; la API todavía no traduce ese error a un 4xx. Compará con `proyecto_id: 999`: ese caso lo chequea el service antes de escribir (`existe`) y responde 404.

**Errores comunes.**
- **Probar transacciones en `psql` sin `BEGIN`.** Cada sentencia se confirma sola y no ves nada interesante.
- **Dejar una terminal con una transacción abierta** y olvidarla. Sus locks siguen tomados y la otra terminal se queda esperando "sin motivo".
- **Creer que la C de ACID valida tus reglas de negocio.** Solo valida las restricciones que declaraste.
- **Confundir durabilidad con backup.** La durabilidad protege de un reinicio, no de un `down -v`.

> 💡 Para profundizar: *3.4. Transactions* (tutorial de PostgreSQL 16) y *Appendix A. Error Codes*. Links en la sección 10.

---

### 4.6 Aislamiento y concurrencia: dos personas, la misma tarea

**Para qué.** El plan del módulo eligió TaskFlow, entre otras cosas, porque ejercita "transacciones y concurrencia (dos personas tocando la misma tarea)". Ana y Beto tienen el tablero abierto. Los dos mueven la tarea 1 casi al mismo tiempo. ¿Qué queda en la base? La respuesta depende del nivel de aislamiento, del código y de cuánto dura la "operación" desde el punto de vista del usuario.

**MVCC: por qué las lecturas no son el problema.** La documentación de PostgreSQL explica que cada sentencia ve un *snapshot* de los datos, y que la ventaja central del control de concurrencia multiversión es que **leer nunca bloquea escribir y escribir nunca bloquea leer**. Para TaskFlow, eso significa que el tablero (la lectura intensiva de `ADR-001`) no se frena mientras alguien mueve una tarjeta. El problema son **dos escrituras basadas en una lectura vieja**.

**Los niveles de aislamiento en PostgreSQL.** Según la documentación de PostgreSQL 16, Read Committed es el nivel por defecto; internamente hay solo tres niveles distintos, porque Read Uncommitted se comporta como Read Committed; y su Repeatable Read no permite phantom reads. La tabla, tal como los implementa PostgreSQL:

| Nivel | Dirty read | Non-repeatable read | Phantom read | Anomalía de serialización |
|---|---|---|---|---|
| Read Uncommitted (= Read Committed en PostgreSQL) | No | Posible | Posible | Posible |
| **Read Committed** (default, el de TaskFlow) | No | Posible | Posible | Posible |
| Repeatable Read | No | No | No (en PostgreSQL) | Posible |
| Serializable | No | No | No | No |

**Las anomalías, con un ejemplo de TaskFlow cada una.**

| Anomalía | Qué es | En TaskFlow |
|---|---|---|
| **Dirty read** | Leer algo que otra transacción escribió y todavía no confirmó | Ver la tarea 1 en `hecho` mientras Ana no confirmó, y que después Ana haga rollback. PostgreSQL nunca lo permite. |
| **Non-repeatable read** | Leer la misma fila dos veces en una transacción y obtener valores distintos | Un reporte lee la tarea 1 en `backlog`; Beto la mueve y confirma; el reporte la relee en `en progreso`. |
| **Phantom read** | Repetir una consulta de varias filas y que aparezcan o desaparezcan filas | "¿Cuántas tareas hay en `hecho` en el proyecto 1?" da 4 y, un instante después, 5, dentro de la misma transacción. |
| **Lost update** | Dos transacciones leen, las dos escriben, y la segunda pisa a la primera sin saberlo | Ana marca `hecho`; Beto, que leyó antes, aplica una regla sobre el estado viejo y escribe `backlog`. El `hecho` de Ana desaparece. |

**El lost update, paso a paso.**

```mermaid
sequenceDiagram
    participant ANA as Sesión de Ana
    participant PG as PostgreSQL
    participant BETO as Sesión de Beto

    ANA->>PG: SELECT tarea 1
    PG-->>ANA: estado en progreso
    BETO->>PG: SELECT tarea 1
    PG-->>BETO: estado en progreso
    ANA->>PG: UPDATE estado a hecho y COMMIT
    Note over BETO: decide con el dato que leyó antes
    BETO->>PG: UPDATE estado a backlog y COMMIT
    Note over PG: el hecho de Ana se perdió
```

Es un **check-then-act**: Beto *chequea* (`estado == 'en progreso'`), *decide* (se puede devolver a `backlog`) y *actúa* (escribe), en pasos separados. Entre el chequeo y la escritura, Ana cambió el dato. ¿Por qué Read Committed no lo evita? Porque el `UPDATE` de Beto es `UPDATE tareas SET estado = 'backlog' WHERE id = 1`: el `WHERE` no mira el estado. La documentación de PostgreSQL explica que en Read Committed, si un `UPDATE` encuentra una fila modificada por otra transacción ya confirmada, **reevalúa el `WHERE`** sobre la versión nueva; acá el `WHERE` sigue matcheando y escribe igual. La reproducción con dos sesiones del ORM está en el ejemplo resuelto de la Unidad 4.

**¿Y hoy, en la API de TaskFlow?** `mover_tarea` **no valida transiciones** (decisión de S05) y `guardar` termina escribiendo solo `estado` (el ORM solo incluye en el `UPDATE` las columnas que cambiaron). Si Ana y Beto llaman a `POST /tasks/1/move` a la vez, la segunda escritura espera a que la primera confirme (un `UPDATE` toma un lock de fila implícito) y después la pisa: **last-writer-wins**. Para "mover una tarjeta" es aceptable: lo último que alguien eligió queda. El lost update se vuelve un bug el día que haya **una regla que dependa del estado leído** (validar transiciones) o **una edición de varios campos** (el `PATCH` que llega en S10). Ahí hay que elegir.

**Las dos familias de solución.** Ninguna de las dos está en el tag: el código de abajo es **ilustrativo, no entra al tag** (el canon no tiene columna de versión y `create_all` no la sumaría a una tabla existente). Se muestra para que sepas qué pedirle al agente el día que TaskFlow lo necesite.

*Optimista: columna de versión.* El patrón *Optimistic Offline Lock* (de David Rice, en el catálogo de P of EAA) previene conflictos entre transacciones de negocio concurrentes **detectando** el conflicto y haciendo rollback. En SQLAlchemy se declara así:

```python
# Ilustrativo (NO entra al tag): así se vería TareaORM con bloqueo optimista
class TareaORM(Base):
    __tablename__ = "tareas"
    ...
    version: Mapped[int] = mapped_column(nullable=False)   # NOT NULL: lo pide la doc
    __mapper_args__ = {"version_id_col": version}
# El UPDATE pasa a ser: ... WHERE id = :id AND version = :leida
# Si otra transacción confirmó antes -> 0 filas -> sqlalchemy.orm.exc.StaleDataError
# El service lo traduce a una excepción de dominio y el router a 409 Conflict.
```

Por qué así: la documentación de SQLAlchemy (*Configuring a Version Counter*) explica que con `version_id_col` el ORM agrega la versión al `WHERE` del `UPDATE` y, si matchean cero filas, lanza `StaleDataError`. Recomienda con fuerza que la columna sea `NOT NULL`, y aclara que solo actúa en el flush, no en `UPDATE`/`DELETE` masivos. No toma locks: el segundo en escribir se entera de que llegó tarde.

*Pesimista: `SELECT … FOR UPDATE`.*

```python
# Ilustrativo (NO entra al tag): obtener la fila bloqueada dentro de la transacción del request
from sqlalchemy import select

fila = session.scalars(
    select(TareaORM).where(TareaORM.id == tarea_id).with_for_update()
).one()
# Otra transacción que pida la misma fila FOR UPDATE espera hasta nuestro commit/rollback.
```

Por qué así: según *Explicit Locking* de PostgreSQL, `FOR UPDATE` impide que otras transacciones bloqueen, modifiquen o borren esas filas hasta que termine la transacción actual. El segundo no falla: **espera**. Con `with_for_update(nowait=True)` (el `NOWAIT` de SQL), en vez de esperar falla en el acto con `lock_not_available` (`55P03`).

**La decisión, en una tabla:**

| | Optimista (versión) | Pesimista (`FOR UPDATE`) |
|---|---|---|
| Supone | Conflictos raros | Conflictos frecuentes |
| En el conflicto | El segundo falla (`StaleDataError` → 409) y recarga | El segundo **espera** (o falla con `NOWAIT`, `55P03`) |
| Costo | Cero locks; hay que manejar el reintento o la recarga | Locks retenidos; riesgo de esperas y deadlocks |
| Sirve entre requests (tablero abierto 5 min) | **Sí**, si la versión viaja con el cliente | **No**: un lock no sobrevive al request |
| Caso TaskFlow | Mover o editar una tarea desde la UI | Operaciones de varias filas en una transacción (reordenar una columna, si existiera) |

La fila clave es la de "entre requests". El caso realista de TaskFlow es que Ana tiene el tablero abierto hace cinco minutos y mueve una tarjeta que Beto ya movió. Ninguna transacción de base dura cinco minutos, así que el control tiene que viajar con el cliente: la versión que leyó cuando abrió el tablero. Eso conecta con el diseño de la API de S09–S10.

**Hay una tercera opción, más chica, que no necesita columna nueva:** poner la condición en el propio `UPDATE` (`… WHERE id = 1 AND estado = 'en progreso'`) y mirar cuántas filas afectó. Como Read Committed reevalúa el `WHERE` sobre la versión confirmada, si Ana ya cambió el estado, el `UPDATE` de Beto afecta **0 filas**. Es el ejercicio 🟡 de la Unidad 4.

**Repeatable Read y el error de serialización.** Si subís el aislamiento a Repeatable Read, PostgreSQL detecta el conflicto por vos: si otra transacción confirmó un cambio sobre tu fila después de tu snapshot, tu `UPDATE` falla con

```
ERROR:  could not serialize access due to concurrent update
```

(SQLSTATE `40001`, `serialization_failure`), y según la documentación la aplicación debe abortar la transacción actual y **reintentar la transacción entera desde el principio**. Entera, no solo el `UPDATE`: hay que volver a leer, porque la decisión se tomó con un dato viejo.

**Deadlocks.** Si A bloquea la tarea 1 y después pide la 2, mientras B bloqueó la 2 y pide la 1, se esperan mutuamente para siempre. PostgreSQL detecta los deadlocks y aborta una de las transacciones (`40P01`, `deadlock_detected`); cuál, según la documentación, es difícil de predecir y no conviene depender de eso. La mejor defensa es que todas las transacciones tomen los locks **en un orden consistente** (por ejemplo, siempre por `id` creciente) y, si no se pueden evitar, reintentar.

**Qué errores se reintentan y cuáles no.** El SQLSTATE es lo que decide, no el texto del mensaje:

| SQLSTATE | Condición | Clase | ¿Reintentar? |
|---|---|---|---|
| `40001` | `serialization_failure` | 40 — *Transaction Rollback* | Sí: fue un conflicto de timing |
| `40P01` | `deadlock_detected` | 40 — *Transaction Rollback* | Sí |
| `55P03` | `lock_not_available` (`NOWAIT`) | 55 | Depende: reintentar más tarde o avisar "está ocupada" |
| `23503` | `foreign_key_violation` | 23 — *Integrity Constraint Violation* | **No**: el dato está mal |
| `23505` | `unique_violation` | 23 — *Integrity Constraint Violation* | **No** |

**El patrón de reintento**, en palabras: envolver la transacción entera (leer, decidir, escribir, confirmar) en una función; si falla con un SQLSTATE de la clase 40, hacer `rollback`, abrir una transacción nueva y volver a empezar; cortar después de un número chico de intentos y, si se agotan, propagar el error. Nunca reintentar un error de la clase 23. Lo construís desde cero en el ejercicio 🔴 de la Unidad 4.

**Errores comunes.**
- **"Uso transacciones, así que no tengo problemas de concurrencia."** La transacción no te protege del *check-then-act* en Read Committed.
- **Reintentar solo el `UPDATE`.** Hay que reintentar desde la lectura.
- **Reintentar para siempre.** Bajo carga, un reintento infinito empeora el conflicto.
- **Usar `FOR UPDATE` para una edición que dura minutos.** El lock vive lo que vive la transacción, y la transacción vive lo que vive el request.
- **Esperar que `psql` muestre el mismo texto de error en todas las versiones.** Mirá el SQLSTATE.

> 💡 Para profundizar: *13.1 MVCC*, *13.2 Transaction Isolation* y *13.3 Explicit Locking* de PostgreSQL 16; *Configuring a Version Counter* (SQLAlchemy) y *Optimistic Offline Lock* (P of EAA). Links en la sección 10.

---

### 4.7 `create_all` vs migraciones, y el bug latente del seed

**Para qué.** Las tablas tienen que existir antes del primer request. Hay dos maneras de lograrlo: generarlas desde los modelos al arrancar, o mantener scripts versionados que lleven el esquema de una versión a otra. TaskFlow elige la primera, y esta sección explica dónde está su límite.

**Lo que hace `create_all`.** Según la documentación de SQLAlchemy, `create_all()` comprueba si existe cada tabla y emite el `CREATE` solo de las que faltan. Alterar lo que ya existe queda fuera del alcance de SQLAlchemy, y para eso remite a herramientas de migración como Alembic. En TaskFlow corre en el `lifespan` de `app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import Base, SessionLocal, engine
from app.db.models import EquipoORM, ProyectoORM  # noqa: F401 (registra las tablas)
from app.routers import tareas


def _crear_esquema_y_seed() -> None:
    # create_all es idempotente: crea las tablas que falten a partir de los modelos ORM.
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        # Seed mínimo: equipo y proyecto por defecto (id=1) para las tareas nuevas.
        if db.get(EquipoORM, 1) is None:
            db.add(EquipoORM(id=1, nombre="Core"))
        if db.get(ProyectoORM, 1) is None:
            db.add(ProyectoORM(id=1, nombre="General", equipo_id=1))
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _crear_esquema_y_seed()
    yield


app = FastAPI(title="TaskFlow", version="0.7.0", lifespan=lifespan)
```

Por qué así:

- **El import de `EquipoORM, ProyectoORM`** no es para usarlos solamente en el seed: importar `app.db.models` registra **las ocho** tablas en `Base.metadata`. Sin ese import, `create_all` no tendría nada que crear.
- **`create_all` es idempotente**: la primera vez crea las 8 tablas en el volumen `taskflow_pgdata`; las siguientes no hace nada. Podés reiniciar `uvicorn` las veces que quieras.
- **El seed busca antes de insertar** (`db.get(..., 1) is None`): por eso tampoco duplica datos al reiniciar.
- **`version="0.7.0"`**: la versión de la app acompaña la sesión.

**El límite: la frontera entre prototipo y producción.** Si mañana `TareaORM` suma una columna, `create_all` **no** la agrega a la tabla `tareas` que ya existe en el volumen. La app arranca, y el primer `SELECT` que mencione la columna nueva falla. En un prototipo lo resolvés con `docker compose down -v` (borrás el volumen y todo vuelve a crearse). En producción eso es borrar los datos de los usuarios. Ahí entran las **migraciones**: scripts versionados que hacen `ALTER TABLE` preservando los datos.

**Por qué Alembic queda fuera del módulo.** Es la alternativa descartada en `[s07] Gestión del esquema: create_all vs migraciones`, y el canon del proyecto la deja fuera del módulo. Pero conviene que sepas qué viene: Alembic compara los modelos con la base y genera una migración candidata, y su propia documentación dice que **siempre** hay que revisar y corregir a mano lo que genera *autogenerate*: no detecta renombres de tabla ni de columna (salen como *drop + add*) ni restricciones sin nombre. Un renombre mal generado borra la columna con sus datos. "El agente me generó la migración" no alcanza. Es la frase de Ng llevada al código: los datos son difíciles de cambiar, aun cuando los agentes ayudan con las migraciones.

**El bug latente del seed.** Mirá otra vez `EquipoORM(id=1, ...)` y `ProyectoORM(id=1, ...)`: se insertan con **id explícito**. Ahora juntalo con cómo funciona `SERIAL`. La documentación de PostgreSQL explica que `SERIAL` equivale a crear una secuencia y poner como default de la columna `nextval('tabla_col_seq')`. Y un `DEFAULT` solo se evalúa cuando la columna **se omite** en el `INSERT`. Consecuencia: el seed escribe `id=1` sin pedirle nada a la secuencia de `equipos` ni a la de `proyectos`, y la secuencia sigue creyendo que el próximo número es 1.

En el tag `s07` no explota, porque nadie más inserta equipos ni proyectos. El primer `INSERT` sin id —el `scripts/seed.py` de M07·S08, que suma el equipo `Plataforma` y el proyecto `Onboarding App`— va a pedir `nextval`, va a recibir 1 y va a chocar con la PK (`23505`, `unique_violation`). M07·S08 lo resuelve cambiando el seed del lifespan a "buscar o crear por nombre". Hoy se diagnostica, no se corrige: es el ejercicio 🟡 de la Unidad 2.

**Los huecos en los ids.** La misma documentación aclara que un valor tomado de la secuencia queda usado aunque la fila nunca se inserte, por ejemplo si la transacción hace rollback. Por eso un `POST /tasks` que falla (un `responsable_id` inexistente, por ejemplo) puede "saltear" un id, y la próxima tarea creada no es la siguiente que esperabas. No es un bug: las secuencias están hechas así para no bloquear transacciones concurrentes.

**Errores comunes.**
- **Agregar una columna al modelo y esperar que aparezca.** `create_all` no altera tablas.
- **Usar `down -v` como "migración".** Sirve en tu máquina y en un prototipo; en ningún otro lado.
- **Insertar ids a mano en tablas con `SERIAL`** sin ajustar la secuencia.
- **Asumir que los ids son consecutivos.** No lo son, y no tienen por qué serlo.

> 💡 Para profundizar: *Describing Databases with MetaData* (SQLAlchemy), *8.1. Numeric Types — Serial Types* (PostgreSQL 16) y *Auto Generating Migrations* (Alembic). Links en la sección 10.

---

### 4.8 Datos limpios, consistentes y frescos, y el ciclo de vida del dato

**Para qué.** Andrew Ng, en la sección *Managing data* de su *AI Engineering Skills Map* (2026), pide entender transacciones y concurrencia, asegurar datos **limpios, consistentes y frescos**, y gestionar el **ciclo de vida** del dato. Ya viste las piezas por separado; esta sección las junta en un criterio que podés aplicar a cualquier esquema.

**Cada propiedad tiene su mecanismo, y su hueco en TaskFlow:**

| Propiedad | Mecanismo | Lo que TaskFlow ya tiene | Lo que falta (solo discusión) |
|---|---|---|---|
| **Limpios** (válidos, sin duplicados) | `NOT NULL`, `CHECK`, `UNIQUE`, tipos | `titulo` y `autor_id` `NOT NULL`; `usuarios.email` `UNIQUE`; validación Pydantic en el borde | `CHECK` sobre `estado`; `UNIQUE` en nombres de equipo y etiqueta |
| **Consistentes** (las relaciones y reglas se cumplen) | FK, transacciones, control de concurrencia | FK en todas las referencias; `commit`/`rollback` en el service | Control de concurrencia (versión o `FOR UPDATE`); validación de transiciones |
| **Frescos** (reflejan el estado actual y se sabe de cuándo son) | Timestamps, invalidación de cachés | `created_at` / `updated_at` poblados por la base y por el ORM | `updated_at` garantizado por la base (trigger): hoy un `UPDATE` en `psql` no lo toca |

La regla que sale de la tabla: **lo que solo valida el dominio, solo vale si el dato pasa por el dominio.** El Enum `Estado` protege a la API; no protege a un script, a una migración ni a un `UPDATE` en `psql`. Si alguien escribe `'archivado'` por fuera, el siguiente `GET /tasks` falla al convertir la fila con `_a_dominio`, porque Pydantic rechaza el valor. La base aceptó un dato que la app no puede leer.

**El ciclo de vida, en dos líneas.** Un dato se **crea**, se **usa**, eventualmente se **archiva** y, a veces, se **borra**. En TaskFlow la creación ya deja rastro (`created_at`) y el uso también (`updated_at`). El archivo y el borrado no tienen política todavía, y las FK en `NO ACTION` son la forma en que la base te lo recuerda: no podés borrar una tarea con comentarios hasta que decidas qué pasa con ellos. Esa decisión (borrar en cascada, desasociar, prohibir, o no borrar nunca y marcar como archivado) es de ciclo de vida, no de SQL. El desarrollo completo —frescura por entidad, ciclo de vida, implicaciones para un agente— es el `docs/datos.md` de M07·S08.

**Por qué le importa a un agente.** En S08 un agente externo va a leer el tablero de TaskFlow. Un dato sucio (un estado inválido), inconsistente (un lost update que borró un "hecho") o viejo (un `updated_at` que no se movió) no se queda en la base: termina en el contexto del agente, y el agente responde con confianza sobre algo falso.

> 💡 Para profundizar: la sección *Managing data* de Ng (biblioteca del profesor). Ver sección 10.

---

### 4.9 Mapa de relaciones entre recursos

Cómo se conectan los recursos de la sección 10 entre sí. Las flechas indican "leé este antes que aquel"; la línea punteada, "leelo para comparar". El nodo resaltado es el que sostiene la mitad conceptual de la sesión.

```mermaid
flowchart TD
    NG["Ng: Managing data"] --> MER["Mermaid: erDiagram"]
    MER --> CON["Postgres: constraints y ON DELETE"]
    MER --> REL["SQLAlchemy: relationship patterns"]
    REL --> DEC["SQLAlchemy: declarative y Mapped"]
    DEC --> DIA["SQLAlchemy: dialecto PostgreSQL"]
    PSY["psycopg 3: install"] --> ENG["SQLAlchemy: engines"]
    DIA --> ENG
    ENG --> V21["SQLAlchemy 2.1: cambios"]
    DM["P of EAA: Data Mapper"] --> RP["P of EAA: Repository"]
    RP --> REPO["Repos SQL del tag s07"]
    DEC --> REPO
    REPO --> LOAD["SQLAlchemy: loading y N+1"]
    TXT["Postgres: tutorial de transacciones"] --> SES["SQLAlchemy: Session basics"]
    UOW["P of EAA: Unit of Work"] --> SES
    SES --> DEP["FastAPI: dependencies with yield"]
    DEP --> REPO
    MVCC["Postgres: MVCC"] --> ISO["Postgres: transaction isolation"]
    ISO --> LCK["Postgres: explicit locking"]
    ISO --> ERR["Postgres: error codes"]
    LCK --> ERR
    OOL["P of EAA: Optimistic Offline Lock"] --> VER["SQLAlchemy: version counter"]
    ISO --> VER
    MD["SQLAlchemy: MetaData y create_all"] --> ALE["Alembic: autogenerate"]
    SER["Postgres: serial types"] --> SEED["Seed con ids fijos"]
    MD --> SEED
    FAS["FastAPI: SQL databases"] -.-> REPO

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class ISO foco
```

Lo que el diagrama no alcanza a expresar:
- **De consulta durante el lab, no antes:** engines, dialecto, psycopg, cambios de 2.1, error codes y relationship loading.
- **De contraste, después del lab:** el tutorial de FastAPI con SQLModel. Se lee para comparar con la entrada `[s07]` del ORM, no como receta.
- **Continuidad con el proyecto:** el `classDiagram` de S06 (`s06-modelo-dominio.mmd`) es la entrada del ER de hoy. El N+1 y el seed con ids fijos son dos deudas que S08 paga. La columna de versión y `FOR UPDATE` no tienen sesión asignada.

---

## 5. Guía práctica paso a paso

Este es el lab de la sesión: conectar TaskFlow a PostgreSQL, revisar la migración línea por línea, ver la concurrencia con tus propios ojos y dejar el diagrama ER y las entradas `[s07]`.

**Partís del tag `s06`:** ya tenés el dominio Pydantic completo (seis entidades + `EntidadConTiempos`, relaciones por id, M:N de un solo lado), los repos en memoria (`RepositorioTareasEnMemoria` y `RepositorioProyectosEnMemoria`, sembrado con `Proyecto(id=1, nombre="General", equipo_id=1)`), `ServicioTareas(repo_tareas, repo_proyectos)` con instancias únicas por proceso en `app/dependencies.py`, `version="0.5.0"`, Postgres levantado pero sin conexión, y `ADR-001` en `docs/trade-offs.md`.

**Terminás en el tag `s07`** con: `app/db/database.py`, `app/db/models.py`, `RepositorioTareasSQL` y `RepositorioProyectosSQL`, el service con `commit`/`rollback`, la composición por request, el `lifespan` con `create_all` + seed, `docs/diagrams/s07-er.mmd`, tres entradas `[s07]` en `docs/trade-offs.md`, `requirements.txt` y `.env.example` actualizados, y el README con el paso para levantar con `--env-file .env`.

### Prerrequisitos

- [ ] El repo del equipo en el tag `s06`, con el árbol limpio (`git status` sin cambios pendientes).
- [ ] Docker andando y el compose de S05 funcionando (`docker compose ps` muestra `taskflow-db`).
- [ ] Python 3.12 con el entorno virtual del proyecto activado.
- [ ] Claude Code (o el agente que use el equipo) con el `CLAUDE.md` del repo.
- [ ] Dos terminales libres para las demos de concurrencia.

### Paso 1 — Arrancar la sesión con el agente, en plan mode

**Para qué:** que el agente proponga el plan completo antes de tocar archivos, y que vos lo compares contra lo que pide `sessions/s07.md`. No vas a escribir `models.py` a mano: lo vas a **dirigir y revisar**.

Prompt sugerido (adaptalo, pero no le saques las restricciones):

```text
Arrancamos la sesión s07. Leé sessions/s07.md y CLAUDE.md.
Objetivo: conectar TaskFlow al Postgres del docker-compose desde la capa repository.
Restricciones:
- SQLAlchemy 2.0 con modelos ORM SEPARADOS del dominio (no SQLModel). El dominio en
  app/models/ no importa SQLAlchemy.
- app/db/database.py (engine, SessionLocal, Base, get_db con yield) y app/db/models.py
  con las 6 entidades + tablas de enlace usuario_equipo y tarea_etiqueta. Clases con
  sufijo ORM, tablas en plural y en español.
- DATABASE_URL desde el entorno, con driver explícito postgresql+psycopg://.
- RepositorioTareasSQL y RepositorioProyectosSQL con la MISMA interfaz que los de
  memoria; el mapeo ORM -> dominio en una función _a_dominio. Los repos hacen flush,
  nunca commit.
- ServicioTareas recibe la Session y es el dueño de la transacción (commit/rollback).
  Su interfaz pública no cambia. app/routers/tareas.py NO se toca.
- Esquema con Base.metadata.create_all en el lifespan + seed mínimo. Sin Alembic.
- Capa síncrona. Sin control de concurrencia en el código.
Mostrame el plan antes de tocar archivos.
```

**Verificá:** el plan nombra todos los archivos de "Terminás en el tag `s07`" y ninguno más (si propone tocar `app/routers/tareas.py` o agregar Alembic, corregilo antes de aceptar).

### Paso 2 — Instalar las dependencias

```bash
pip install -r requirements.txt          # suma sqlalchemy>=2.0 y psycopg[binary]>=3.1
```

**Por qué `psycopg[binary]`:** la variante binaria trae todo lo necesario sin prerrequisitos del sistema. La documentación de psycopg 3 prefiere la instalación local (que compila contra las librerías del sistema) para producción, cuando se pueden mantener esas dependencias: es un trade-off para retomar en la semana 4.

**Verificá:** `pip show sqlalchemy` muestra una versión 2.x. Si es 2.1 y algo falla en el paso 5, usá `pip install 'sqlalchemy>=2.0,<2.1'`.

### Paso 3 — Configurar `DATABASE_URL`

```bash
cp .env.example .env                     # si ya existía de S05, agregá solo DATABASE_URL
```

La línea que tiene que estar en `.env`:

```bash
DATABASE_URL=postgresql+psycopg://<usuario>:<password>@localhost:<POSTGRES_PORT>/<POSTGRES_DB>
```

**Placeholders:** con los valores de `.env.example` queda `postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow`. Si en S05 cambiaste `POSTGRES_PORT` (por ejemplo, porque el 5432 estaba ocupado), el puerto de la URL tiene que ser el mismo.

**Verificá:** `grep DATABASE_URL .env` muestra la URL con `+psycopg`.

### Paso 4 — Levantar la base

```bash
docker compose up -d                     # Postgres 16 en taskflow-db
docker compose ps                        # esperá STATUS "healthy" (healthcheck pg_isready)
```

**Verificá:** `taskflow-db` aparece como `healthy`. Si dice `starting`, esperá unos segundos y repetí.

### Paso 5 — Levantar la app

```bash
uvicorn app.main:app --reload --env-file .env
```

**Por qué `--env-file .env`:** carga `DATABASE_URL` en el proceso de Uvicorn. Sin eso, `database.py` usa su default, que coincide con `.env.example` salvo que hayas cambiado el puerto.

**Verificá:** el log de arranque no muestra errores, y `curl -s localhost:8000/health` devuelve `{"status":"ok"}`. Al arrancar, el `lifespan` ya corrió `create_all` y el seed.

### Paso 6 — Comprobar que persiste

```bash
curl -s -X POST localhost:8000/tasks -H "Content-Type: application/json" \
     -d '{"titulo": "Probar Postgres", "proyecto_id": 1}' | python -m json.tool
curl -s -X POST localhost:8000/tasks/1/move -H "Content-Type: application/json" \
     -d '{"estado": "en progreso"}' | python -m json.tool
```

Ahora reiniciá `uvicorn` (`Ctrl+C` y volvé a lanzarlo) y listá:

```bash
curl -s localhost:8000/tasks | python -m json.tool
```

**Verificá:** la tarea sigue ahí después del reinicio, con `created_at` y `updated_at` poblados (en S06 valían `null`). Eso es la D de ACID. Además, `python scripts/client.py` (de S05) tiene que seguir funcionando sin cambios: es la prueba de punta a punta.

> ⚠️ El `id` de la primera tarea puede no ser 1 si hubo intentos fallidos: son los huecos de secuencia de 4.7. Si es otro, usá ese id en el `move` y en las demos.

### Paso 7 — Mirar la base por dentro

```bash
docker exec -it taskflow-db psql -U taskflow -d taskflow
```

```sql
\dt                                  -- 8 tablas: comentarios, equipos, etiquetas, proyectos,
                                     -- tarea_etiqueta, tareas, usuario_equipo, usuarios
\d tareas                            -- columnas, FK a proyectos y usuarios, default de id (nextval)
SELECT id, titulo, estado, created_at, updated_at FROM tareas;
```

**Verificá:** hay 8 tablas; en `\d tareas` el `id` tiene un default `nextval(...)` (el `SERIAL`), y `estado` se guarda como texto (`'en progreso'`, con espacio: es el `.value` del Enum). Salí con `\q`.

### Paso 8 — Revisar el incremento línea por línea

`sessions/s07.md` pide que la migración del almacenamiento se revise **línea por línea**. Comparalo contra el tag de referencia:

```bash
git diff --stat s06 s07                         # qué archivos tocó la sesión
git diff s06 s07 -- app/repositories/           # memoria -> SQL, misma interfaz
git diff s06 s07 -- app/services/tarea_service.py app/dependencies.py app/main.py
```

Si tu equipo todavía no taggeó `s07`, compará tu árbol de trabajo contra `s06` (`git diff s06 -- app/`) y, al lado, el tag `s07` del repo de referencia. Guía de lectura, en orden:

1. **`app/db/database.py`**: URL desde el entorno, engine con `pool_pre_ping`, `SessionLocal` con `autoflush=False` y `expire_on_commit=False`, `Base`, `get_db` (4.2 y 4.4).
2. **`app/db/models.py`**: las dos `Table` de enlace y las seis clases `*ORM` (4.2).
3. **`app/repositories/tarea_repository.py`**: `_a_dominio`, `crear` con `flush`, ningún `commit` (4.3).
4. **`app/repositories/proyecto_repository.py`**: `obtener` / `existe`; ya no siembra, el seed pasó al lifespan.
5. **`app/services/tarea_service.py`**: el constructor suma `session`; `commit`/`rollback` en las escrituras (4.4).
6. **`app/dependencies.py`**: de instancias por proceso a composición por request (4.4).
7. **`app/main.py`**: `lifespan`, `create_all`, seed y `version="0.7.0"` (4.7).
8. **`app/routers/tareas.py`**: **no aparece en el diff**. Esa ausencia es la prueba de que las capas funcionaron.

**Verificá:** podés explicar en voz alta, sin mirar estas notas, por qué el `commit` está en el service y no en el repository ni en `get_db`.

### Paso 9 — Ver el SQL (y el N+1) con `echo=True`

**Para qué:** dejar de imaginar lo que hace el ORM. Editá **temporalmente** `app/db/database.py`:

```python
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)  # SOLO durante el lab
```

Creá dos tareas más con el `curl` del paso 6 y llamá a `curl -s localhost:8000/tasks`. En la terminal de `uvicorn` vas a ver un `SELECT` de `tareas` y, después, un `SELECT` de etiquetas **por cada tarea**: el N+1 de 4.3. Llamá también a un `move` y mirá el `UPDATE`: solo incluye las columnas que cambiaron.

**Verificá y revertí:** contaste 1 + N consultas en el listado. Después volvé `database.py` a como estaba (`git checkout -- app/db/database.py` si no tenías otros cambios en ese archivo). `echo=True` **no se commitea**.

### Paso 10 — Demos de concurrencia, en parejas

Con dos terminales `psql` (paso 7) y, para el lost update, un script descartable **fuera del repo**. Todo lo que insertes a mano va dentro de `BEGIN … ROLLBACK`.

1. **Transacción a mano** (atomicidad y aislamiento): el bloque de 4.5.
2. **Lost update con el ORM**: el script del ejemplo resuelto de la Unidad 4.
3. **`FOR UPDATE`: el segundo espera.**

   ```sql
   -- A
   BEGIN;
   SELECT estado FROM tareas WHERE id = 1 FOR UPDATE;
   -- B
   BEGIN;
   SELECT estado FROM tareas WHERE id = 1 FOR UPDATE;          -- queda esperando
   -- A
   UPDATE tareas SET estado = 'hecho' WHERE id = 1;
   COMMIT;
   -- B: se destraba y ve 'hecho' -> recién ahí decide
   COMMIT;
   ```

   Variante: con `FOR UPDATE NOWAIT` en B, falla en el acto con `lock_not_available` (`55P03`) en vez de esperar.

4. **Repeatable Read: error de serialización.**

   ```sql
   -- B
   BEGIN ISOLATION LEVEL REPEATABLE READ;
   SELECT estado FROM tareas WHERE id = 1;                     -- snapshot tomado
   -- A (sin BEGIN: autocommit de psql)
   UPDATE tareas SET titulo = titulo || ' (editada)' WHERE id = 1;
   -- B
   UPDATE tareas SET estado = 'backlog' WHERE id = 1;
   -- ERROR:  could not serialize access due to concurrent update    (SQLSTATE 40001)
   ROLLBACK;                                                   -- y reintentar la transacción entera
   ```

5. **Deadlock por orden inconsistente** (necesitás dos tareas, ids 1 y 2):

   ```sql
   -- A: BEGIN; UPDATE tareas SET titulo = titulo WHERE id = 1;
   -- B: BEGIN; UPDATE tareas SET titulo = titulo WHERE id = 2;
   -- A: UPDATE tareas SET titulo = titulo WHERE id = 2;       -- espera a B
   -- B: UPDATE tareas SET titulo = titulo WHERE id = 1;       -- ciclo: PostgreSQL aborta una (40P01)
   -- en la que sobrevive: COMMIT o ROLLBACK
   ```

   PostgreSQL aborta una de las dos con `deadlock_detected` (`40P01`). El texto exacto del mensaje puede variar; lo que importa es el código.

**Verificá:** anotaste, para cada demo, qué terminal esperó, cuál falló y con qué SQLSTATE. Esas notas te sirven para la Unidad 4.

> ⚠️ Los `UPDATE` hechos a mano en `psql` **no** tocan `updated_at`: `onupdate=func.now()` lo aplica el ORM en sus propios `UPDATE`, no la base. No te sorprendas si después de las demos `updated_at` no se movió.

### Paso 11 — El diagrama ER

Escribí `docs/diagrams/s07-er.mmd` **leyendo `app/db/models.py`**, no copiando. La referencia es el ER de 4.1. Si el agente generó el archivo, revisalo contra el modelo con dos preguntas por relación: ¿la marca del lado "uno" coincide con la nulabilidad de la FK? ¿las claves de las tablas de enlace dicen `PK, FK`?

**Verificá:** el diagrama renderiza (en GitHub o en tu editor), tiene 8 tablas, `USUARIOS |o--o{ TAREAS` y `PK, FK` en las dos tablas de enlace.

### Paso 12 — Las tres entradas `[s07]` en `docs/trade-offs.md`

Van con la plantilla del archivo (`### [sXX] Título`, Fecha, Decisión, Alternativas, Elección, Por qué, Consecuencias), la más reciente arriba y **por encima** de `## [s06] ADR-001`. **No** son ADR: son entradas de la bitácora.

1. `[s07] Stack de ORM y separación dominio/persistencia` — SQLAlchemy 2.0 con ORM separado vs SQLModel vs SQL crudo (psycopg). Elegido: ORM separado, mapeo en el repository, psycopg 3 síncrono.
2. `[s07] Gestión del esquema: create_all vs migraciones` — `create_all` + seed vs Alembic. Elegido: `create_all`. Consecuencia: no versiona ni altera tablas existentes.
3. `[s07] Capa de datos síncrona vs asíncrona` — síncrona (`def`, `Session`, psycopg sync) vs `AsyncSession`. Elegido: síncrona. FastAPI corre los `def` en un threadpool.

**Verificá:** cada entrada tiene al menos dos alternativas reales y una consecuencia que alguien pueda usar dentro de tres sesiones.

### Paso 13 — README, commit y tag

Actualizá el README: el paso 3 de "cómo correr" pasa a `uvicorn app.main:app --reload --env-file .env`, más un párrafo "s07 — PostgreSQL real". Después:

```bash
git add -A
git commit -m "s07: PostgreSQL real con SQLAlchemy, repos SQL, ER y trade-offs"
git tag s07
```

**Verificá:** `git diff --stat s06 s07` en tu repo muestra los mismos archivos que el del repo de referencia, y `app/routers/tareas.py` no aparece.

### Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| La app no conecta al arrancar (conexión rechazada) | La base no está `healthy` o el puerto no coincide | `docker compose ps`; revisá `POSTGRES_PORT` y la URL |
| Error de que falta el módulo `psycopg2` | URL sin `+psycopg` con SQLAlchemy 2.0 | Usá `postgresql+psycopg://` |
| Error de que la tabla `tareas` no existe | `create_all` no corrió o no vio los modelos | Revisá el import de `app.db.models` en `app/main.py` |
| Datos raros de pruebas anteriores | Restos en el volumen `taskflow_pgdata` | `docker compose down -v` (borra el volumen) y volvé a levantar |
| Una terminal `psql` "colgada" | La otra tiene una transacción abierta con locks | `COMMIT` o `ROLLBACK` en la otra |
| `POST /tasks` devuelve 500 | `responsable_id` inexistente: la FK lo rechaza | Esperado (4.5): mirá el log de `uvicorn` |

> 📝 **Nota para el profesor:** lo de arriba está escrito con estos defaults, ajustalos si tu plan es otro. **Timing (180 min):** 40 de concepto (dominio → ER, transacción y aislamiento) / 60 de taller guiado (pasos 1 a 8) / 45 de práctica autónoma en parejas (paso 10, con dos terminales) / 20 de puesta en común (el ER de cada equipo contra el de 4.1, y optimista vs pesimista para TaskFlow) / 15 de cierre (pasos 11 a 13); si falta tiempo, lo primero que sale es el deadlock del paso 10. **Equipos y entrega:** los mismos equipos de S05, cada uno parte de su tag `s06` y entrega con commits `s07: …` y tag `s07`; rúbrica de 4 criterios (anda; el ER coincide con `models.py`; cada `[s07]` tiene alternativas y consecuencia; el equipo explica una línea cualquiera del diff). **Construcción:** el material asume que el incremento se construye dirigiendo al agente y revisando el diff contra el tag de referencia, no escribiendo `models.py` a mano. **SQLAlchemy 2.1:** `sqlalchemy>=2.0` instala hoy la 2.1.x; conviene correr el tag `s07` con 2.1.1 antes de la clase para confirmar o descartar el fallback a `<2.1`. **ER del tag:** `docs/diagrams/s07-er.mmd` del repo de referencia usa `PK_FK` y `USUARIOS ||--o{ TAREAS`; el material enseña `PK, FK` y `|o--o{`, y usa la diferencia como ejercicio (Unidad 1, 🟢) sin decir que el archivo esté roto. Confirmá si corregís el `.mmd` en el repo de referencia. **Datos de las demos:** Ana y Beto como personas, la tarea creada en el paso 6 y una segunda para el deadlock; todo lo insertado a mano va en `BEGIN … ROLLBACK`.

---

## 6. Checklist de autoevaluación

- [ ] Puedo traducir una entidad de dominio a una tabla y justificar cada PK, FK y nulabilidad sin mirar los apuntes.
- [ ] Puedo leer un `erDiagram` y decir qué significa `|o--o{` frente a `||--o{`, y verificarlo contra `app/db/models.py`.
- [ ] Puedo explicar por qué una M:N se guarda en una tabla de enlace con PK compuesta y no en una lista.
- [ ] Puedo explicar por qué TaskFlow tiene `Tarea` y `TareaORM` separados, qué cuesta y qué compra, frente a SQLModel.
- [ ] Puedo explicar la diferencia entre `flush` y `commit` y por qué el repository nunca confirma.
- [ ] Puedo explicar por qué el `commit` vive en el service y no en el código de salida de `get_db`.
- [ ] Puedo reproducir un lost update y explicar por qué Read Committed no lo evita.
- [ ] Puedo elegir entre bloqueo optimista y pesimista para un caso de TaskFlow y justificarlo con la duración de la operación.
- [ ] Puedo decir qué SQLSTATE se reintentan y cuáles no, y por qué se reintenta la transacción entera.
- [ ] Puedo explicar qué no hace `create_all` y por qué el seed con ids fijos es un bug latente con `SERIAL`.

---

## 7. Preguntas de repaso

1. **Te piden revisar el esquema que generó un agente para una app con usuarios, tareas y etiquetas. ¿Qué mirás primero y por qué?** Pensá en nulabilidad frente a opcionalidad del dominio, en cómo están resueltas las M:N, en las acciones `ON DELETE` y en los índices de las FK.
2. **En TaskFlow el dominio no importa SQLAlchemy, pero el service sí importa `Session`. ¿Es una contradicción? ¿Qué harías si el equipo quisiera eliminar ese acoplamiento, y cuánto costaría?**
3. **Dos usuarios mueven la misma tarea al mismo tiempo en TaskFlow. Describí qué pasa hoy en la base, paso a paso, y en qué momento ese comportamiento deja de ser aceptable.**
4. **Un usuario tiene el tablero abierto hace diez minutos y edita una tarea que otro ya cambió. ¿Por qué `SELECT … FOR UPDATE` no resuelve este caso y qué diseño propondrías para la API?**
5. **Tu equipo usa `create_all` y quiere agregar una columna a `tareas` en un entorno con datos reales. ¿Qué pasa si solo cambian el modelo? ¿Qué proponés, y qué revisarías en lo que genere la herramienta de migraciones?**

---

## 8. Recursos adicionales

### Imprescindibles

- [13.2. Transaction Isolation — PostgreSQL 16](https://www.postgresql.org/docs/16/transaction-iso.html) — el recurso central de la mitad conceptual: niveles, anomalías, error de serialización y reintento (35 min; 13.2.1 y 13.2.2 obligatorias, 13.2.3 Serializable opcional).
- [Session Basics — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) — autobegin, `sessionmaker`, `expire_on_commit` y la sesión por request (25 min).
- [5.4. Constraints — PostgreSQL 16](https://www.postgresql.org/docs/16/ddl-constraints.html) — PK, FK y acciones `ON DELETE`; `CHECK` y `UNIQUE` de consulta (25 min).
- [Entity Relationship Diagrams — Mermaid](https://mermaid.js.org/syntax/entityRelationshipDiagram.html) — la sintaxis del entregable (15 min).
- [Dependencies with yield — FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/) — cuándo corre el código de salida y por qué hay que re-lanzar (15 min).
- [`fastapi-full-v0` en el tag `s07`](https://github.com/Luc5k4yw4lk3r/fastapi-full-v0/tree/s07) — el repo de referencia, para comparar, no para copiar (30 min).

### Recomendados

- [Table Configuration with Declarative — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html) — `Mapped`, `mapped_column` y nulabilidad (20 min).
- [Basic Relationship Patterns — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html) — 1:N, M:N con `secondary=` y association object (20 min).
- [Relationship Loading Techniques — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html) — lazy loading, N+1, `selectinload` y `raiseload` (15 min).
- [3.4. Transactions — tutorial de PostgreSQL 16](https://www.postgresql.org/docs/16/tutorial-transactions.html) — all-or-nothing, transacción implícita y savepoints (10 min).
- [13.1. Introduction (MVCC) — PostgreSQL 16](https://www.postgresql.org/docs/16/mvcc-intro.html) — snapshots y por qué leer no bloquea escribir (5 min).
- [13.3. Explicit Locking — PostgreSQL 16](https://www.postgresql.org/docs/16/explicit-locking.html) — `FOR UPDATE` y deadlocks (20 min; 13.3.2 y 13.3.4).
- [Configuring a Version Counter — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/versioning.html) — el bloqueo optimista en el ORM (10 min).
- [Data Mapper — P of EAA](https://martinfowler.com/eaaCatalog/dataMapper.html) (5 min).
- [Repository — P of EAA](https://martinfowler.com/eaaCatalog/repository.html) (5 min).
- [Unit of Work — P of EAA](https://martinfowler.com/eaaCatalog/unitOfWork.html) (5 min).
- [Optimistic Offline Lock — P of EAA](https://martinfowler.com/eaaCatalog/optimisticOfflineLock.html) (5 min).
- [Describing Databases with MetaData — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/core/metadata.html) — solo "Creating and Dropping Database Tables" y "Altering Database Objects through Migrations" (10 min).

### Opcionales

- [PostgreSQL dialect — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html) — URL por driver y `SERIAL` vs `IDENTITY` (10 min).
- [Engine Configuration — SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/core/engines.html) — Database URLs, `echo` y `pool_pre_ping` (10 min).
- [What's New in SQLAlchemy 2.1? — migration_21](https://docs.sqlalchemy.org/en/21/changelog/migration_21.html) — solo la lista de cambios incompatibles (5 min).
- [Installation — psycopg 3](https://www.psycopg.org/psycopg3/docs/basic/install.html) — binaria vs local vs Python puro (5 min).
- [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/) — de contraste: SQLModel y tablas al arrancar (15 min).
- [Auto Generating Migrations — Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) — para saber qué viene y por qué hay que revisar (15 min).
- [8.1. Numeric Types — Serial Types — PostgreSQL 16](https://www.postgresql.org/docs/16/datatype-numeric.html) — solo 8.1.4 (5 min).
- [Appendix A. PostgreSQL Error Codes — PostgreSQL 16](https://www.postgresql.org/docs/16/errcodes-appendix.html) — la tabla de SQLSTATE (consulta, 3 min).
- Andrew Ng (2026), *AI Engineering Skills Map: Software engineering fundamentals*, sección "Managing data" — biblioteca del profesor, sin URL pública (5 min).
