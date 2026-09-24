# M07·S04 — Componentes avanzados de FastAPI y separación en capas

**Módulo:** 07 — Fundamentos de Software + System Design para AI Engineers **Fecha:** [Completar por el profesor: fecha] **Duración estimada de estudio:** ~5 horas en total: lectura de recursos (~2 h), guía práctica del lab (~1h30-2h) y ejercicios (~1h-1h30). A eso se suman las 3 horas de la sesión en clase.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Explicar** qué problema resuelve la inyección de dependencias de FastAPI (`Depends`) y **usarla** para entregarle a cada request su propia conexión a la base de datos.
2. **Escribir** un middleware HTTP en FastAPI y **explicar** en qué orden se ejecutan cuando hay más de uno.
3. **Modularizar** un webserver con `APIRouter`, organizando las rutas por recurso con `prefix` y `tags`.
4. **Refactorizar** un webserver de un solo archivo a una arquitectura en capas (router → service → repository → datos) y **relacionarla** con la Clean Architecture.
5. **Levantar** PostgreSQL con Docker Compose y **conectarlo** a la app con SQLAlchemy, con la conexión inyectada como dependencia.
6. **Explicar** por qué una llamada a una LLM API es el caso clásico tanto de procesamiento asíncrono (`async def`) como de caching, y **escribir** un endpoint `async` que lo demuestre.

---

## 2. Resumen ejecutivo

En M07·S03 armaste tu primer webserver con FastAPI: cada endpoint hacía todo en el mismo archivo (recibir el request, validar, hablar con la base, armar la respuesta). En esta sesión lo convertís en algo que se parece a una aplicación real.

**Qué vas a hacer:**

- **Separar responsabilidades en capas:** el **router** atiende HTTP, el **service** aplica las reglas de negocio y el **repository** habla con la base. Es la **Clean Architecture** aplicada a un backend concreto.
- **Usar dos mecanismos de FastAPI que sostienen esa separación:**
    - **`Depends`**, que le entrega a cada handler lo que necesita (por ejemplo, una conexión) sin que lo tenga que construir.
    - **Middleware**, que envuelve todos los requests para hacer algo común a todos (medir tiempo, loguear, leer una cookie).
- **Persistir en PostgreSQL**, la base que vas a usar en producción, levantada con **Docker Compose**. Un solo comando levanta la base y la API, sin instalar Postgres en tu máquina.
- **Cerrar con IA:** una llamada a una LLM API tarda segundos y cuesta plata. Por eso es a la vez el ejemplo perfecto de operación **async** y de algo que conviene **cachear**.

**Por qué importa para un AI Engineer:** con las capas separadas podés reemplazar un mock por un modelo real, cambiar de base de datos o sumar caché sin reescribir toda la app.

---

## 3. Conceptos clave / glosario

**Inyección de dependencias y capas**

- **Dependency Injection (DI) / `Depends`:** en vez de que una función cree lo que necesita, se lo entregan desde afuera. En FastAPI se declara con `Depends(func)`. _Analogía:_ pedir que te alcancen la herramienta en vez de fabricarla cada vez.
- **Función de dependencia:** una función común, sin decorador de ruta, que FastAPI ejecuta antes del handler. Su resultado llega al handler como parámetro.
- **`Annotated`:** permite empaquetar tipo + dependencia en un alias reutilizable, por ejemplo `DbDep = Annotated[Connection, Depends(get_db)]`.
- **Service (capa de servicio):** donde viven las reglas de negocio, o sea, qué se hace con el dato. No sabe cómo se guarda.
- **Repository:** la capa que ejecuta las consultas contra la base. Es la única que conoce SQL.
- **Clean Architecture:** modelo de Robert C. Martin que organiza el código en círculos concéntricos. Las dependencias solo apuntan hacia adentro.
- **Regla de dependencia:** el código de un círculo interno nunca menciona nada de un círculo externo.

**Middleware y routers**

- **Middleware:** función que envuelve **todos** los requests y responses; corre antes y después de cualquier ruta.
- **`call_next`:** la función con la que el middleware le pasa el request a la ruta y recibe la response.
- **`APIRouter`:** una "mini app" que agrupa rutas de un mismo recurso. Se monta en la app principal con `app.include_router()`.
- **`prefix` / `tags`:** `prefix` antepone un path común (`/users`) a todas las rutas del router; `tags` las agrupa en `/docs`.

**Persistencia**

- **ORM / SQLAlchemy:** SQLAlchemy es la librería que traduce entre Python y una base SQL. Tiene dos estilos: _Core_ (tablas y consultas explícitas, el que usamos acá) y _ORM declarativo_ (clases mapeadas a tablas).
- **PostgreSQL:** motor de base de datos relacional que corre como **servidor**: acepta muchas conexiones concurrentes y es el estándar en producción.
- **Driver (`psycopg`):** el "cable" entre SQLAlchemy y Postgres. SQLAlchemy arma la consulta y el driver la manda a la base.
- **Connection string (`DATABASE_URL`):** dice a qué base conectarse, con qué credenciales. Ejemplo: `postgresql+psycopg://app:app@db:5432/store` (motor+driver, usuario:clave, host, puerto, base).
- **Transacción:** un grupo de operaciones que se guarda completo (`COMMIT`) o se descarta completo (`ROLLBACK`). No quedan guardados a medias.
- **Engine / pool de conexiones:** el `engine` mantiene conexiones abiertas y las presta a cada request, en vez de abrir una nueva cada vez.

**Docker**

- **Imagen:** un paquete con el sistema, las dependencias y el código, listo para ejecutarse. Se construye con un `Dockerfile`.
- **Contenedor:** una imagen corriendo. Está aislado de tu máquina.
- **Docker Compose:** archivo (`docker-compose.yml`) que define varios contenedores y cómo se conectan. Se levantan todos con `docker compose up`.
- **Servicio (en Compose):** cada contenedor declarado en el compose (`db`, `api`). Dentro de la red de Compose, cada servicio es accesible **por su nombre**.
- **Volumen:** almacenamiento que sobrevive aunque borres el contenedor. Ahí vive la data de Postgres.
- **Variable de entorno:** valor que se le pasa al proceso desde afuera (por ejemplo `DATABASE_URL`). Así las credenciales no quedan escritas en el código.

**Concurrencia, sesión y caching**

- **I/O-bound vs. CPU-bound:** I/O-bound pasa el tiempo **esperando** algo externo (red, disco, una API); CPU-bound pasa el tiempo **calculando**.
- **Concurrencia vs. paralelismo:** concurrencia es alternar entre tareas mientras alguna espera (sirve para I/O). Paralelismo es ejecutar tareas al mismo tiempo en núcleos distintos (sirve para CPU).
- **`async def` / `await`:** sintaxis para esperar una operación sin bloquear el servidor mientras tanto.
- **Threadpool:** conjunto de hilos donde FastAPI ejecuta las rutas declaradas con `def` normal, para que no bloqueen al resto.
- **Estado de sesión:** información de un cliente que persiste entre requests.
- **`SessionMiddleware`:** middleware de Starlette que guarda la sesión en una cookie firmada, accesible como `request.session`.
- **Cookie firmada vs. cifrada:** una cookie firmada se puede leer pero no modificar. Una cifrada no se puede ni leer sin la clave.
- **`HttpOnly`:** atributo que impide que JavaScript lea la cookie.
- **Caching (prompt / exact / semantic):** _prompt cache_ evita reprocesar el inicio repetido de un prompt; _exact cache_ evita repetir la misma consulta exacta; _semantic cache_ evita repetir consultas que significan lo mismo.
- **Política de evicción (LRU / LFU / FIFO):** qué se saca de una caché llena. LRU saca lo usado hace más tiempo, LFU lo que menos veces se usó y FIFO lo más viejo.
- **Hashing vs. cifrado:** el hash es de una sola vía (no se puede revertir) y el cifrado es reversible. Las contraseñas **se hashean**.

---

## 4. Notas de estudio por subtema

Cada subtema sigue el mismo formato: **qué es → para qué sirve → por qué se hace así → ejemplo → errores comunes**.

### El diagrama ancla: el webserver en capas

Toda la sesión responde una pregunta: **¿qué pasa entre que llega un request y se guarda (o se lee) un dato?**

```mermaid
flowchart LR
    CLI["Cliente"] --> MW["Middleware<br/>(ej. X-Process-Time)"]
    MW --> ROUTER["Router<br/>(APIRouter)"]
    ROUTER --> SERVICE["Service<br/>(regla de negocio)"]
    SERVICE --> REPO["Repository<br/>(acceso a datos)"]
    REPO --> DB[("PostgreSQL<br/>(contenedor Docker)")]
    DEP["Depends<br/>(conexión a la BD)"] -.-> ROUTER

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class SERVICE foco
```

|Capa|Pregunta que responde|Nunca debería…|
|---|---|---|
|**Middleware**|¿Qué le hago a _todos_ los requests?|tener lógica de un endpoint puntual|
|**Router**|¿Cómo traduzco HTTP ↔ Python?|tener reglas de negocio ni SQL|
|**Service**|¿Qué está permitido y qué se transforma?|importar `fastapi` ni `sqlalchemy`|
|**Repository**|¿Cómo leo y escribo en la base?|decidir nada; solo ejecuta|
|**Datos**|¿Dónde vive el dato?|—|

**Por qué el service está resaltado:** es la capa que más suele faltar. Tener carpetas `routes/` y `models/` no es "arquitectura en capas" si la regla de negocio sigue dentro del handler. Eso separa **archivos**, no **responsabilidades**.

**Un detalle que el diagrama simplifica:** FastAPI solo resuelve `Depends` en la firma de las rutas. Entonces la conexión se inyecta en el **router**, y de ahí se pasa a mano como parámetro al **service** y al **repository**. Esas dos capas no saben nada de FastAPI. La respuesta hace el camino inverso: repository → service → router → middleware → cliente.

---

### 1. Inyección de dependencias (`Depends`)

**Qué es.** En vez de que el handler abra su propia conexión a la base, la declara como parámetro y FastAPI se la entrega ya lista.

**Para qué sirve.**

- **Una sola definición:** "cómo se crea una conexión" se escribe una vez, no en cada archivo.
- **Tests más simples:** en un test podés reemplazar la dependencia por una falsa, sin tocar una base real.


```python
# repositories/db.py
from collections.abc import Iterator
from typing import Annotated
from fastapi import Depends
from sqlalchemy.engine import Connection
from config.db import engine


def get_db() -> Iterator[Connection]:
    with engine.begin() as connection:   # abre conexión + transacción
        yield connection                 # ← acá corre el handler
    # al salir del with: COMMIT si todo salió bien, ROLLBACK si hubo error, y cierra


DbDep = Annotated[Connection, Depends(get_db)]
```

**Ejemplo.** En el router escribís `def create_user(user: UserCreate, db: DbDep)`. Cada request recibe **su propia** conexión, que se cierra sola al terminar.

**El antipatrón que esto evita.** Abrir una conexión global al importar el módulo (`con = engine.connect()`) tiene tres problemas: todos los requests comparten la misma conexión, nunca se cierra y no se puede cambiar por otra en un test.

> ⚠️ **Errores comunes:**
> 
> - Escribir `Depends(get_db())`, con paréntesis. Así Python ejecuta la función **una sola vez**, al definir la ruta, justo lo que `Depends` evita. Va sin paréntesis: `Depends(get_db)`.
> - Hacer `yield` sin `with` ni `try/finally`. Si el handler falla, la conexión queda abierta.

📎 Para profundizar: [Dependencies — FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

### 2. Middleware

**Qué es.** Una función que envuelve **toda** la aplicación: corre antes de que el request llegue a cualquier ruta, y después de que la response esté lista.

**Para qué sirve.** Para lo que aplica a todos los endpoints por igual: medir tiempo, loguear, leer una cookie, agregar headers. Así no lo repetís en cada handler.

**Por qué así.** Se declara con `@app.middleware("http")` sobre una función `async` que recibe el `request` y `call_next`:

```python
# main.py
import time
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()                 # ANTES de la ruta
    response = await call_next(request)         # la ruta se ejecuta acá
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"  # DESPUÉS
    return response
```

**Ejemplo.** `curl -i localhost:8000/users/` devuelve, entre los headers, `x-process-time: 0.0034`.

**Orden con varios middlewares.** Pensalo como capas de cebolla, no como una fila. Con `add_middleware`, **el último que agregás es el más externo** y corre primero sobre el request.

> ⚠️ **Errores comunes:**
> 
> - Olvidar `await call_next(request)` o no devolver la `response`. En los dos casos el servidor queda sin responder.
> - Asumir que los middlewares corren en el orden en que se registran. Es al revés.

📎 Para profundizar: [Middleware — FastAPI](https://fastapi.tiangolo.com/tutorial/middleware/)

---

### 3. Routers con `APIRouter`

**Qué es.** Una "mini app" que agrupa las rutas de un mismo recurso en su propio archivo.

**Para qué sirve.** Para que `main.py` no crezca sin control. Cada recurso (`users`, `assistant`) tiene su archivo, y `main.py` solo los monta.

**Por qué así.**

- `prefix="/users"`: todas las rutas del archivo empiezan con `/users`, sin repetirlo en cada una.
- `tags=["users"]`: agrupa las rutas en `/docs`.
- `dependencies=[...]` (opcional): aplica una dependencia a todas las rutas del router.

```python
# routes/user.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")          # → GET /users/
def list_users():
    ...
```

```python
# main.py
from routes.user import router as user_router
app.include_router(user_router)
```

> ⚠️ **Errores comunes:**
> 
> - Crear el router y no llamar a `app.include_router(...)`. Las rutas no existen y devuelven 404.
> - Duplicar el prefijo: con `prefix="/users"`, escribir `@router.get("/users/{id}")` genera `/users/users/{id}`.

📎 Para profundizar: [Bigger Applications - Multiple Files — FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

---

### 4. Arquitectura en capas y Clean Architecture

**Qué es.** La **Clean Architecture** (Robert C. Martin, 2012) organiza el código en círculos concéntricos, del más estable al más cambiante:

- **Entities:** las reglas de negocio de más alto nivel.
- **Use Cases:** las reglas propias de la aplicación.
- **Interface Adapters:** traducen entre el mundo externo y el interno.
- **Frameworks & Drivers:** los detalles concretos (base de datos, framework web).

Su regla central es la **regla de dependencia**: _"source code dependencies can only point inwards"_. El código de adentro nunca conoce al de afuera.

**Para qué sirve.** Para que los detalles (qué base, qué framework) se puedan cambiar sin tocar las reglas de negocio.

**Cómo se mapea a nuestro webserver:**

|Capa del webserver|Capa de Clean Architecture|Qué hace|
|---|---|---|
|**Router**|Interface Adapter (controller)|Traduce un request HTTP a una llamada de función.|
|**Service**|Use Case|Aplica la regla de negocio (ej.: hashear la contraseña).|
|**Repository**|Interface Adapter (gateway)|Traduce la operación a una consulta SQL.|
|**PostgreSQL**|Frameworks & Drivers|El detalle concreto de dónde vive el dato.|

**Ejemplo de la regla de dependencia en acción.** El service no importa SQLAlchemy: le pide los datos al repository. Por eso, al pasar de SQLite a Postgres, **el service y el router no cambiaron ni una línea**. Solo cambiaron la configuración y el repository.

**Otro ejemplo: los errores.** El service no tira `HTTPException`, porque no sabe que existe HTTP. Tira excepciones propias (`EmailAlreadyRegistered`) y el router las traduce a un código HTTP (409). Así el mismo service serviría para un CLI o un bot.

> ⚠️ **Error común:** pensar "para un CRUD tan chico no vale la pena" y meter la consulta SQL "solo esta vez" en el service o en el router. Cada excepción rompe la regla de dependencia, y acumuladas te devuelven al handler que hacía todo. Anotá esta decisión en tu trade-off journal: para un CRUD de dos campos quizás no se justifica; para un backend que vas a mantener meses, casi seguro que sí.

📎 Para profundizar: [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

### 5. Persistencia con PostgreSQL + Docker

**Qué es.**

- **PostgreSQL:** una base de datos que corre como servidor, no como archivo.
- **SQLAlchemy:** la librería con la que tu código habla con ella, a través del driver `psycopg`.
- **Docker Compose:** levanta Postgres (y tu API) en contenedores.

**Para qué sirve.**

- **Postgres:** es lo que vas a usar en producción y acepta muchas conexiones concurrentes.
- **Docker:** cualquiera clona el repo, corre `docker compose up` y tiene exactamente el mismo entorno, sin instalar Postgres.

**Por qué así.** Tres piezas, cada una en su archivo:

1. **`config/db.py`** lee la URL de una variable de entorno y crea el `engine`:
    
    ```python
    import os
    from sqlalchemy import MetaData, create_engine
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/store")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    meta = MetaData()
    ```
    
2. **`docker-compose.yml`** define dos servicios: `db` (Postgres) y `api` (tu app). La API se conecta a la base usando el **nombre del servicio** como host: `@db:5432`.
    
3. **`repositories/db.py`** entrega una conexión con transacción por request (subtema 1).
    

**Ejemplo: por qué el host es `db` y no `localhost`.** Dentro de un contenedor, `localhost` es **el propio contenedor**. Docker Compose crea una red interna donde cada servicio se llama por su nombre:

- desde la API (dentro de Docker): `postgresql+psycopg://app:app@db:5432/store`
- desde tu máquina (psql, DBeaver): `postgresql+psycopg://app:app@localhost:5432/store`

**Qué cambia respecto de SQLite:**

||SQLite|PostgreSQL|
|---|---|---|
|Dónde vive|Un archivo `store.db`|Un servidor, en un contenedor|
|URL|`sqlite:///./store.db`|`postgresql+psycopg://usuario:clave@host:5432/base`|
|`check_same_thread=False`|Obligatorio|No existe: Postgres maneja concurrencia de verdad|
|Id del registro recién creado|`result.lastrowid`|`INSERT ... RETURNING` (devuelve la fila en la misma consulta)|
|Instalación|Viene con Python|Un contenedor + el driver `psycopg`|

> ⚠️ **Errores comunes:**
> 
> - **Usar `localhost` como host dentro de Docker:** la API no encuentra la base (_connection refused_). Tiene que ser `db`.
> - **Que la API arranque antes que Postgres:** falla al conectarse. Se resuelve con `healthcheck` + `depends_on: condition: service_healthy`.
> - **Escribir las credenciales en el código:** van en variables de entorno, con un `.env` que no se sube a git.
> - **Esperar que `create_all` modifique una tabla existente:** crea tablas nuevas, pero no agrega columnas a las que ya existen. Para eso están las migraciones (Alembic).
> - **Perder los datos sin querer:** `docker compose down -v` borra el volumen y, con él, la base. Sin `-v`, los datos quedan.

📎 Para profundizar: [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/) y [FastAPI in Containers — Docker](https://fastapi.tiangolo.com/deployment/docker/)

---

### 6. Async, sesión y caching: la LLM API como caso clásico

#### Async vs. sync

**Qué es.** `async def` + `await` permite que el servidor atienda otros requests **mientras espera** algo externo.

**Para qué sirve.** Para operaciones **I/O-bound**, las que pasan el tiempo esperando:

||I/O-bound|CPU-bound|
|---|---|---|
|Qué hace|Espera una respuesta externa (red, disco, API)|Usa el procesador (procesar imagen, ML)|
|Se beneficia de|Concurrencia (`async`/`await`)|Paralelismo real (varios procesos)|
|Ejemplo|Llamar a una LLM API|Redimensionar una imagen|

**Por qué así.** El criterio oficial de FastAPI:

- **`async def`** cuando usás librerías compatibles con `await` (un cliente HTTP async, por ejemplo).
- **`def`** con librerías síncronas, o ante la duda. FastAPI corre esas rutas en un **threadpool**, así que no bloquean al resto del servidor.

Por eso las rutas de `users` son `def`: SQLAlchemy con `psycopg`, tal como lo usamos acá, es síncrono.

**Ejemplo.** Un endpoint que llama a un LLM tarda ~2 segundos. Con `async def` + `await`, durante esos 2 segundos el servidor sigue respondiendo otros requests.

> ⚠️ **Error común:** usar `time.sleep()` (o cualquier llamada bloqueante) dentro de un `async def`. Bloquea **todo** el servidor. Adentro de `async`, siempre `await asyncio.sleep()` o un cliente async como `httpx.AsyncClient`.

#### Sesión

**Qué es.** `SessionMiddleware` (de Starlette) guarda datos de cada cliente en una **cookie firmada**, accesible como diccionario en `request.session`.

**Para qué sirve.** Para recordar algo de un usuario entre requests: su carrito, su idioma, si ya se logueó.

**Por qué así.**

- **Firmada, no cifrada:** el cliente la puede leer, pero no modificar.
- **`HttpOnly`:** JavaScript no puede leerla.
- **Parámetros:** se configura con `secret_key`, `max_age` (por defecto dos semanas), `same_site` y `https_only`.

**Una idea para llevarse:** sesión y middleware son la misma pieza vista de dos lados. `SessionMiddleware` es un middleware que lee y escribe una cookie en cada request.

#### Caching

**Qué es.** Guardar el resultado de algo costoso para no repetirlo.

**Para qué sirve (en IA).** Una llamada a un LLM es lenta, cara y muchas veces repetida: el mismo system prompt, el mismo documento, la misma pregunta.

**Tipos de caché:**

|Tipo|Qué evita|Quién lo controla|
|---|---|---|
|_KV cache_|Recalcular dentro de la inferencia|El proveedor del modelo|
|_Prompt cache_|Reprocesar el inicio repetido de un prompt|Vos (lo activás en la API)|
|_Exact cache_|Repetir la misma consulta exacta|Vos (en tu app)|
|_Semantic cache_|Repetir consultas que significan lo mismo|Vos (en tu app)|

**Ejemplo con números** (Chip Huyen, _AI Engineering_, O'Reilly 2025):

- Un system prompt de 1.000 tokens con un millón de llamadas diarias suma ~1.000 millones de tokens repetidos por día.
- Anthropic promete hasta 90 % menos de costo y 75 % menos de latencia con prompt caching.

**Qué NO cachear:** respuestas que dependen del usuario o del momento. _Ejemplo:_ si cacheás "¿cuál es la política de devoluciones?" y la respuesta depende de la membresía, le vas a mostrar a un usuario la respuesta de otro. Eso es una **fuga de datos**, no solo un error.

> ⚠️ **Error común:** cachear sin expiración ni política de evicción. La caché crece sin límite o sirve respuestas viejas.

📎 Para profundizar: [Concurrency and async / await — FastAPI](https://fastapi.tiangolo.com/async/) y [Middleware — Starlette](https://starlette.dev/middleware/)

---

### 7. El diagrama de componentes, con archivos reales

El entregable visual de la sesión es este diagrama, con los nombres de archivo de **tu** proyecto en cada caja:

```mermaid
flowchart LR
    C["Cliente"] --> MW["Middleware<br/>main.py"]
    MW --> R["Router<br/>routes/user.py"]
    R --> S["Service<br/>services/user_service.py"]
    S --> RP["Repository<br/>repositories/user_repository.py"]
    RP --> DB[("PostgreSQL<br/>servicio db en docker-compose.yml")]
    DEP["Depends(get_db)<br/>repositories/db.py"] -.->|inyecta la conexión| R

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class S foco
```

- **Middleware:** no es una capa más de la cadena, **envuelve** a todas.
- **`Depends`:** es el enchufe entre el router y la infraestructura.

> 💡 **Test para saber si lo entendiste:** dibujalo de memoria y respondé: _si mañana cambiás Postgres por otra base, ¿qué archivos tocás?_ Respuesta: solo `config/db.py` y el repository.

---

### Mapa de relaciones entre recursos

Los recursos se organizan en **tres tracks** independientes entre sí. Dentro de cada track, el orden importa.

```mermaid
flowchart TD
    ROUT["FastAPI: Bigger Applications<br/>(APIRouter)"] --> CA["Clean Architecture<br/>(Robert C. Martin)"]
    DEP["FastAPI: Dependencies<br/>(Depends)"] --> SQLDB["FastAPI: SQL Databases"]
    SQLDB --> DOCK["FastAPI in Containers<br/>(Docker)"]
    SQLDB --> CA
    MW["FastAPI: Middleware"] --> SESS["Starlette: Middleware<br/>(SessionMiddleware)"]
    ASYNC["FastAPI: Concurrency<br/>and async / await"] --> CACHE["Caching en apps de IA<br/>(wiki interna)"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class CA foco
```

**Clean Architecture** está resaltada porque ahí convergen los hilos: explica por qué modularizar rutas y por qué inyectar la conexión en vez de importarla global.

---

## 5. Guía práctica paso a paso

Esta sesión se dirige a un agente de código (como en M07·S01 a S03), pero **vos tenés que leer y entender cada archivo que genera**. Para cada archivo, esta guía te dice:

- 📍 **Capa:** dónde encaja en la arquitectura.
- 🎯 **Para qué:** qué problema resuelve.
- 🧠 **Por qué así:** las decisiones que tomó.
- 🧪 **Ejemplo:** cómo verlo funcionar.

Usala para armar el prompt al agente y para verificar lo que produjo.

**Prerequisitos:**

- El proyecto de M07·S03 (`webserver-fastapi/`).
- **Docker Desktop** instalado y abierto (verificá con `docker --version` y `docker compose version`).
- Claude Code configurado en tu terminal.

### Paso 1 — La estructura final

```
webserver-fastapi/
├── docker-compose.yml        ← levanta Postgres + API
├── Dockerfile                ← cómo se construye la imagen de la API
├── requirements.txt          ← dependencias de Python
├── .env.example              ← plantilla de credenciales
├── .dockerignore / .gitignore
├── main.py                   ← arma la app: middleware + routers
├── config/
│   └── db.py                 ← engine: a qué base nos conectamos
├── models/
│   └── user.py               ← forma de la tabla
├── schemas/
│   └── user.py               ← forma del JSON que entra y sale
├── repositories/
│   ├── db.py                 ← get_db: la conexión por request
│   └── user_repository.py    ← las consultas SQL
├── services/
│   └── user_service.py       ← las reglas de negocio
└── routes/
    ├── user.py               ← endpoints /users
    └── assistant.py          ← endpoint async que simula un LLM
```

**Orden de construcción:** de abajo hacia arriba. Primero infraestructura y datos, después repository, service y por último router. Así cada capa ya tiene lista la pieza que necesita.

---

### Paso 2 — `requirements.txt`: las dependencias

- 📍 **Capa:** infraestructura.
- 🎯 **Para qué:** lista lo que el `Dockerfile` instala dentro de la imagen.
- 🧠 **Por qué así:**
    - `psycopg` es el driver que conecta SQLAlchemy con Postgres.
    - Usamos `bcrypt` directo en vez de `passlib[bcrypt]`: `passlib` está sin mantenimiento y falla con las versiones nuevas de `bcrypt`.

```text
fastapi[standard]>=0.115   # framework + uvicorn + email-validator
sqlalchemy>=2.0            # toolkit SQL
psycopg[binary]>=3.2       # driver de Postgres
bcrypt>=4.2                # hashing de contraseñas
```

---

### Paso 3 — `Dockerfile`: la imagen de la API

- 📍 **Capa:** infraestructura (Frameworks & Drivers).
- 🎯 **Para qué:** empaqueta Python, las dependencias y tu código en una imagen que corre igual en cualquier máquina. Se terminó el "en mi máquina anda".
- 🧠 **Por qué así:**
    - **Primero** se copia `requirements.txt` y se instala, y **después** se copia el código. Docker cachea cada paso: si cambiás `main.py`, no reinstala las dependencias.
    - `--host 0.0.0.0` hace que la app escuche desde fuera del contenedor. Con `127.0.0.1`, tu navegador no llega.

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Paso 4 — `docker-compose.yml`: Postgres + API con un comando

- 📍 **Capa:** infraestructura (orquestación).
- 🎯 **Para qué:** define los dos contenedores (`db` y `api`) y cómo se conectan. `docker compose up --build` levanta todo.
- 🧠 **Por qué así:**
    - **Host `db`:** la API se conecta a `db:5432` porque dentro de la red de Compose cada servicio se llama por su nombre.
    - **`healthcheck` + `depends_on`:** la API espera a que Postgres esté listo. Si no, arranca antes y falla al conectarse.
    - **Volumen `pgdata`:** los datos sobreviven a un `docker compose down`.
    - **Montaje `.:/app` + `--reload`:** editás en tu editor y la app se recarga sola.
    - **`${VAR:-default}`:** toma el valor de `.env` y, si no existe, usa el default.

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-app}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-app}
      POSTGRES_DB: ${POSTGRES_DB:-store}
    ports:
      - "5432:5432"            # opcional: para inspeccionar la base desde tu máquina
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 2s
      timeout: 3s
      retries: 15

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+psycopg://${POSTGRES_USER:-app}:${POSTGRES_PASSWORD:-app}@db:5432/${POSTGRES_DB:-store}
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

Y el `.env.example`, la plantilla de credenciales. Copiala como `.env`: el `.env` **no** se sube a git.

```bash
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=store
```

🧪 **Ejemplo:** `docker compose up db -d` y después `docker compose exec db psql -U app -d store -c "SELECT 1;"`. Si devuelve `1`, la base está viva.

---

### Paso 5 — `config/db.py`: a qué base nos conectamos

- 📍 **Capa:** infraestructura (Frameworks & Drivers).
- 🎯 **Para qué:** es el **único** lugar que sabe a qué base se conecta la app. Crea el `engine` (el pool de conexiones) y `meta` (el catálogo de tablas).
- 🧠 **Por qué así:**
    - **URL desde `DATABASE_URL`:** nunca hardcodeada. Cambiar de entorno es cambiar una variable.
    - **Sin `check_same_thread`:** era una limitación exclusiva de SQLite.
    - **`pool_pre_ping=True`:** verifica que la conexión siga viva antes de usarla. Sirve si Postgres se reinició.
    - **Fallback con `localhost`:** permite correr la API fuera de Docker (ver paso 13).

```python
# config/db.py
import os
from sqlalchemy import MetaData, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/store",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
meta = MetaData()
```

---

### Paso 6 — `models/user.py`: la forma de la tabla

- 📍 **Capa:** datos.
- 🎯 **Para qué:** define la tabla `users` para que SQLAlchemy pueda crearla y armar consultas en Python (`select(users).where(...)`).
- 🧠 **Por qué así:**
    - **Estilo _Core_** (`Table` + `Column`): explícito, se ve la tabla tal cual es.
    - **`unique=True` en `email`:** la base misma impide duplicados; es la última red de seguridad.
    - **La columna `password`:** guarda el **hash**, nunca el texto plano.
- **No confundir con `schemas/`:** `models/` es cómo se **guarda** el dato; `schemas/` es cómo **entra y sale** por HTTP.

```python
# models/user.py
from sqlalchemy import Column, DateTime, Integer, String, Table, func
from config.db import meta

users = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=False),  # hash bcrypt
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
```

---

### Paso 7 — `schemas/user.py`: el contrato HTTP

- 📍 **Capa:** borde HTTP (lo usa el router).
- 🎯 **Para qué:**
    - **Validar la entrada:** si el email es inválido, FastAPI responde 422 solo.
    - **Filtrar la salida:** el router declara `response_model=UserRead`, y lo que no esté en `UserRead` no sale.
    - **Documentar:** genera la documentación de `/docs`.
- 🧠 **Por qué dos clases:** `UserCreate` es lo que **entra** (con password). `UserRead` es lo que **sale** (sin password). Con una sola clase terminarías devolviendo el hash.

```python
# schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt usa hasta 72 bytes


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
```

🧪 **Ejemplo:** `{"name":"Ana","email":"ana@mail.com","password":"secreta123"}` entra, y sale `{"id":1,"name":"Ana","email":"ana@mail.com","created_at":"..."}`.

---

### Paso 8 — `repositories/db.py`: una conexión por request

- 📍 **Capa:** puente entre FastAPI y la infraestructura.
- 🎯 **Para qué:** `get_db()` le entrega a cada request su conexión y la cierra al terminar.
- 🧠 **Por qué así:**
    - **`engine.begin()`:** abre una **transacción**. Si el request sale bien hace `COMMIT`; si hay una excepción, `ROLLBACK`. El repository no necesita llamar a `commit()`.
    - **`DbDep`:** incluye `Depends`, así que solo lo usa el router.
    - **`DbConnection`:** es solo el tipo, sin nada de FastAPI. Lo usan el service y el repository.

```python
# repositories/db.py
from collections.abc import Iterator
from typing import Annotated
from fastapi import Depends
from sqlalchemy.engine import Connection
from config.db import engine


def get_db() -> Iterator[Connection]:
    with engine.begin() as connection:
        yield connection


DbDep = Annotated[Connection, Depends(get_db)]   # para el router
DbConnection = Connection                        # para service y repository
```

🧪 **Qué pasa en un `POST /users`:**

1. FastAPI ve `db: DbDep` en la firma y ejecuta `get_db()` hasta el `yield`.
2. El handler usa la conexión: se la pasa al service, que se la pasa al repository.
3. Cuando el handler termina, se hace commit (o rollback, si hubo error) y la conexión se cierra.

---

### Paso 9 — `repositories/user_repository.py`: las consultas

- 📍 **Capa:** repository (Interface Adapter en Clean Architecture).
- 🎯 **Para qué:** es el **único** archivo que ejecuta SQL sobre `users`. Traduce pedidos simples ("creá este usuario", "buscá por email") a consultas.
- 🧠 **Por qué así:**
    - **Recibe la conexión, no la crea.**
    - **Devuelve `dict`,** no objetos de SQLAlchemy, para que la base no "se filtre" a las capas de arriba.
    - **No decide nada:** no hashea ni valida.
    - **Postgres no tiene `lastrowid`:** se usa `.returning(users)`, que devuelve la fila recién creada en la misma consulta.

```python
# repositories/user_repository.py
from sqlalchemy import insert, select
from models.user import users
from repositories.db import DbConnection


def create_user(db: DbConnection, name: str, email: str, hashed_password: str) -> dict:
    stmt = (
        insert(users)
        .values(name=name, email=email, password=hashed_password)
        .returning(users)
    )
    return dict(db.execute(stmt).one()._mapping)


def get_user(db: DbConnection, user_id: int) -> dict | None:
    row = db.execute(select(users).where(users.c.id == user_id)).first()
    return dict(row._mapping) if row else None


def get_user_by_email(db: DbConnection, email: str) -> dict | None:
    row = db.execute(select(users).where(users.c.email == email)).first()
    return dict(row._mapping) if row else None


def list_users(db: DbConnection) -> list[dict]:
    rows = db.execute(select(users).order_by(users.c.id)).all()
    return [dict(r._mapping) for r in rows]
```

✅ **Verificación:** este archivo no importa `APIRouter`, `Request` ni `HTTPException`.

---

### Paso 10 — `services/user_service.py`: las reglas de negocio

- 📍 **Capa:** service (Use Case en Clean Architecture).
- 🎯 **Para qué:** reúne todo lo que la app **decide**, en un solo lugar y fácil de testear.
- 🧠 **Reglas de este archivo:**
    1. La contraseña se guarda **hasheada**, nunca en texto plano.
    2. No puede haber dos usuarios con el mismo email.
    3. Pedir un usuario inexistente es un error.
- 🧠 **Por qué así:**
    - **No importa `fastapi` ni `sqlalchemy`.**
    - **Tira excepciones propias,** no `HTTPException`: el router decide qué código HTTP corresponde.

```python
# services/user_service.py
import bcrypt
from repositories import user_repository
from repositories.db import DbConnection
from schemas.user import UserCreate


class EmailAlreadyRegistered(Exception):
    """El email ya pertenece a otro usuario."""


class UserNotFound(Exception):
    """No existe un usuario con ese id."""


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def register_user(db: DbConnection, data: UserCreate) -> dict:
    if user_repository.get_user_by_email(db, data.email):
        raise EmailAlreadyRegistered(data.email)
    hashed = _hash_password(data.password)
    return user_repository.create_user(db, data.name, data.email, hashed)


def get_user(db: DbConnection, user_id: int) -> dict:
    user = user_repository.get_user(db, user_id)
    if user is None:
        raise UserNotFound(user_id)
    return user


def list_users(db: DbConnection) -> list[dict]:
    return user_repository.list_users(db)
```

✅ **Verificación:** `grep -E "fastapi|sqlalchemy" services/user_service.py` no devuelve nada.

---

### Paso 11 — `routes/user.py`: los endpoints

- 📍 **Capa:** router (Interface Adapter / controller).
- 🎯 **Para qué:** traducir HTTP ↔ Python y nada más: recibe el JSON validado y la conexión, llama al service y devuelve la respuesta con el código correcto.
- 🧠 **Por qué así:**
    - **Handlers de 2-3 líneas.** Si uno crece, hay una regla de negocio que debería estar en el service.
    - **Es la única capa donde aparece `Depends`** (vía `DbDep`).
    - **Traduce errores de dominio a HTTP:** `EmailAlreadyRegistered` → 409 y `UserNotFound` → 404.
    - **Son `def`, no `async`,** porque la base se usa de forma síncrona. FastAPI las corre en el threadpool.

```python
# routes/user.py
from fastapi import APIRouter, HTTPException, status
from repositories.db import DbDep
from schemas.user import UserCreate, UserRead
from services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DbDep):
    try:
        return user_service.register_user(db, user)
    except user_service.EmailAlreadyRegistered:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese email ya está registrado")


@router.get("/", response_model=list[UserRead])
def list_users(db: DbDep):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: DbDep):
    try:
        return user_service.get_user(db, user_id)
    except user_service.UserNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
```

---

### Paso 12 — `routes/assistant.py`: el endpoint async que simula un LLM

- 📍 **Capa:** router.
- 🎯 **Para qué:** muestra el caso clásico de operación **I/O-bound**. El `sleep` ocupa el lugar de la llamada real a la API del modelo.
- 🧠 **Por qué así:** con `async def` + `await asyncio.sleep`, mientras este request espera, el servidor atiende otros. Con `time.sleep` bloquearía todo.

```python
# routes/assistant.py
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/assistant", tags=["assistant"])


class Question(BaseModel):
    question: str


@router.post("/ask")
async def ask_assistant(body: Question):
    await asyncio.sleep(2)  # simula la latencia de red de una LLM API
    return {"answer": f"Respuesta simulada a: {body.question}"}
```

---

### Paso 13 — `main.py`: donde se conecta todo

- 📍 **Capa:** punto de entrada.
- 🎯 **Para qué:** crea la app, crea las tablas al arrancar, registra el middleware y monta los routers. No tiene lógica propia.
- 🧠 **Por qué así:**
    - **`lifespan`:** es el hook oficial para "al arrancar" y "al apagar". Al arrancar crea las tablas (`create_all`); al apagar cierra el pool (`dispose`).
    - **`import models.user`:** parece no usarse, pero es necesario. Al importarlo, la tabla se registra en `meta` y recién ahí `create_all` la conoce.
    - **El middleware:** envuelve a todos los routers.

```python
# main.py
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

import models.user  # noqa: F401  (registra la tabla en meta)
from config.db import engine, meta
from routes.assistant import router as assistant_router
from routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    meta.create_all(engine)   # al arrancar: crea tablas si no existen
    yield
    engine.dispose()          # al apagar: cierra el pool de conexiones


app = FastAPI(title="Webserver FastAPI + Postgres", lifespan=lifespan)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
    return response


app.include_router(user_router)
app.include_router(assistant_router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}
```

---

### Paso 14 — Levantar y verificar de punta a punta

```bash
cp .env.example .env
docker compose up --build
```

Abrí `http://localhost:8000/docs`: tenés que ver los grupos `users`, `assistant` e `infra`.

**Checklist de verificación:**

```bash
# 1. Crear usuario → 201
curl -X POST localhost:8000/users/ -H "Content-Type: application/json" \
  -d '{"name":"Ana","email":"ana@mail.com","password":"secreta123"}'

# 2. Mismo email → 409 (regla del service)
curl -X POST localhost:8000/users/ -H "Content-Type: application/json" \
  -d '{"name":"Ana2","email":"ana@mail.com","password":"otraclave1"}'

# 3. Email inválido → 422 (validación del schema)
curl -X POST localhost:8000/users/ -H "Content-Type: application/json" \
  -d '{"name":"X","email":"no-es-mail","password":"secreta123"}'

# 4. Header del middleware
curl -i localhost:8000/users/          # buscá: x-process-time

# 5. La contraseña quedó hasheada en Postgres
docker compose exec db psql -U app -d store -c "SELECT id, email, password FROM users;"

# 6. Async: en dos terminales, casi a la vez
curl -X POST localhost:8000/assistant/ask -H "Content-Type: application/json" -d '{"question":"hola"}'
curl localhost:8000/health             # responde al instante, aunque el otro siga esperando
```

**Comandos útiles:**

|Comando|Qué hace|
|---|---|
|`docker compose up --build`|Construye la imagen y levanta todo|
|`docker compose up db -d`|Levanta solo Postgres, en segundo plano|
|`docker compose logs -f api`|Muestra los logs de la API en vivo|
|`docker compose down`|Apaga todo (los datos quedan)|
|`docker compose down -v`|Apaga todo y **borra los datos**|

**Alternativa sin Docker para la API** (útil para usar el debugger): `docker compose up db -d`, después creá un venv, `pip install -r requirements.txt` y `uvicorn main:app --reload`. La app usa el fallback `localhost:5432` de `config/db.py`.

### Paso 15 — Stretch opcional: LLM real + caching

1. Reemplazá el `asyncio.sleep(2)` por una llamada real con `httpx.AsyncClient()` al endpoint `POST /v1/messages` de la Claude API (el que usaste con `curl` en M07·S02).
2. Agregá una caché exacta: un `dict` en memoria, con un hash de la pregunta como clave.

> 📝 **Nota para el profesor:** la guía asume la distribución estándar de semanas 1-2 para los 180 minutos:
> 
> - ~40 min de concepto y demo del antipatrón conexión global vs. `Depends`
> - ~60 min de taller guiado refactorizando a capas
> - ~45 min de práctica autónoma con el endpoint async
> - ~20 min de puesta en común de diagramas
> - ~15 min de trade-off journal
> 
> **Docker suma fricción el primer día.** Pedí que lleguen con Docker Desktop instalado y que hayan corrido `docker run hello-world`. Contemplá ~10 min extra para resolver problemas de instalación (virtualización desactivada en Windows, puerto 5432 ocupado por un Postgres local).
> 
> El lab es **individual**, dirigido con **Claude Code**, con entrega en la misma carpeta `webserver-fastapi/` de S03.

---

## 6. Ejercicios

### 🟢 Básico 1 — Antipatrón vs. `Depends`

Mirá este fragmento:

```python
# db.py
from sqlalchemy import create_engine
engine = create_engine("postgresql+psycopg://app:app@localhost:5432/store")
con = engine.connect()  # se ejecuta una sola vez, al importar el módulo
```

```python
# routes/items.py
from db import con
from sqlalchemy import select
from models import items

@router.get("/items")
def list_items():
    return con.execute(select(items)).fetchall()
```

Explicá dos problemas concretos de este patrón y escribí la versión corregida con `Depends`.

**Sabés que lo lograste cuando:** nombraste al menos dos problemas reales y tu versión declara un `get_db` con `yield`, inyectado como `Depends(get_db)`. Problemas posibles:

- Todas las requests comparten una conexión.
- Nunca se cierra.
- La URL y las credenciales están hardcodeadas.
- No se puede testear con otra base.

<details> <summary>Pista</summary>

Pensá qué pasa si dos requests llegan a la vez y uno deja la conexión en medio de una transacción fallida.

</details>

### 🟢 Básico 2 — ¿`async def` o `def`?

Para cada endpoint, decidí `async def` o `def` y justificá con I/O-bound vs. CPU-bound:

a) Llama a la API de un LLM y espera la respuesta. b) Redimensiona una imagen subida por el usuario. c) Hace una consulta simple a Postgres con SQLAlchemy Core, de forma síncrona. d) Hace tres llamadas a APIs externas distintas y junta las respuestas.

**Sabés que lo lograste cuando:**

- **a y d:** `async def`, porque son I/O-bound y esperan red.
- **b:** pide paralelismo real, no `async`, porque es CPU-bound.
- **c:** conviene `def`, porque la librería es síncrona.

<details> <summary>Pista</summary>

Concurrencia es alternar mientras algo espera; paralelismo es usar más CPU al mismo tiempo.

</details>

### 🟡 Intermedio 1 — Refactor a capas

Tomá un router de S03 que hace todo en el handler y separalo en router → service → repository. El service tiene que aplicar al menos una regla de negocio real (por ejemplo, no permitir precio negativo) y tirar una excepción propia, que el router traduce a un código HTTP.

**Sabés que lo lograste cuando:**

- el router no importa `sqlalchemy`;
- el service no importa nada de `fastapi`;
- el repository es el único archivo con `select`, `insert`, `update` o `delete`;
- la app funciona de punta a punta desde `/docs`.

<details> <summary>Pista</summary>

Ante cada línea preguntate: _¿esto es una regla de negocio, o una forma concreta de guardar el dato?_

</details>

### 🟡 Intermedio 2 — Dos middlewares y el orden importa

Agregá un segundo middleware que loguee el método y el path de cada request. Registralo junto con el de `X-Process-Time` y respondé por escrito: ¿en qué orden se ejecutan? Comprobalo con un `print` distinto en cada uno.

**Sabés que lo lograste cuando:** tu respuesta escrita coincide con lo que ves en la consola (`docker compose logs -f api`) y podés explicar por qué.

<details> <summary>Pista</summary>

Revisá qué dice la documentación oficial sobre `add_middleware` y el orden de ejecución.

</details>

### 🔴 Desafío 1 — El webserver de S03, en capas y en Docker

Refactorizá el proyecto completo de S03 dirigiendo a tu agente de código. Tiene que incluir:

- capas router/service/repository;
- Postgres levantado con Docker Compose;
- al menos un middleware;
- al menos una regla de negocio real.

Documentá en tu trade-off journal si valió la pena la separación en capas para un CRUD tan chico.

**Sabés que lo lograste cuando:**

- otra persona clona tu repo, corre `docker compose up --build` y la app funciona sin instalar nada más;
- podés explicar qué hace cada capa sin mirar el código;
- tu diagrama de componentes coincide con lo que construiste;
- hay una entrada nueva en el trade-off journal.

<details> <summary>Pista</summary>

Empezá por `docker-compose.yml` y `config/db.py`. Verificá que la base responde antes de escribir una sola ruta.

</details>

### 🔴 Desafío 2 — Async + caching, con datos reales

Reemplazá el `asyncio.sleep(2)` por una llamada real a una LLM API con `httpx.AsyncClient()` y agregá una caché exacta en memoria: la clave es un hash de la pregunta y el valor es la respuesta. Medí con `X-Process-Time` la diferencia entre la primera llamada y una segunda idéntica.

**Sabés que lo lograste cuando:**

- el endpoint sigue siendo `async def` con `await`;
- la segunda llamada es notablemente más rápida;
- podés explicar por qué esta caché (exact) no sirve para dos preguntas distintas que significan lo mismo.

<details> <summary>Pista</summary>

`hashlib` de la librería estándar alcanza. La API key va como variable de entorno en el `docker-compose.yml`, nunca en el código.

</details>

---

## 7. Ruta de estudio sugerida

Tres tracks en paralelo. Dentro de cada track, el orden importa.

```mermaid
flowchart TD
    A1["Dependencies<br/>(17 min)"] --> A2["SQL Databases<br/>(22 min)"]
    A2 --> A5["FastAPI in Containers<br/>(15 min)"]
    A3["Bigger Applications<br/>(15 min)"] --> A4["Clean Architecture<br/>(14 min)"]
    A2 --> A4
    B1["Middleware FastAPI<br/>(9 min)"] --> B2["Middleware Starlette<br/>(10 min)"]
    C1["Concurrency async/await<br/>(12 min)"] --> C2["Caching en IA - wiki<br/>(15 min)"]
```

|Track|Recurso|Tiempo|Por qué en ese orden|
|---|---|---|---|
|Capas y persistencia|Dependencies (FastAPI)|15-18 min|Base para entender `Depends`.|
|Capas y persistencia|SQL Databases (FastAPI)|20-25 min|Usa `Depends` con `yield` para la sesión de BD.|
|Capas y persistencia|FastAPI in Containers (FastAPI)|15 min|Cómo empaquetar la app en una imagen de Docker.|
|Capas y persistencia|Bigger Applications (FastAPI)|15 min|`APIRouter`, independiente de `Depends`.|
|Capas y persistencia|The Clean Architecture (R. C. Martin)|12-15 min|El marco que explica por qué separar en capas.|
|Middleware y sesión|Middleware (FastAPI)|8-10 min|El mecanismo general.|
|Middleware y sesión|Middleware (Starlette)|10 min|`SessionMiddleware` como caso concreto.|
|Async y caching|Concurrency and async / await (FastAPI)|12 min|Por qué una LLM API pide `async def`.|
|Async y caching|Caching en apps de IA (wiki interna)|15 min|Por qué esa misma llamada conviene cachearla.|

---

## 8. Checklist de autoevaluación

- [ ] Puedo explicar qué resuelve `Depends` y por qué una conexión global es un antipatrón.
- [ ] Puedo escribir un middleware que modifique la respuesta.
- [ ] Puedo explicar el orden de ejecución con varios middlewares.
- [ ] Puedo organizar rutas con `APIRouter`, `prefix` y `tags`.
- [ ] Puedo dibujar de memoria el diagrama de capas con los archivos reales de mi proyecto.
- [ ] Puedo relacionar esas capas con las de Clean Architecture.
- [ ] Puedo levantar Postgres con Docker Compose y explicar por qué la API usa el host `db` y no `localhost`.
- [ ] Puedo explicar qué hace `engine.begin()` en `get_db` (commit o rollback automático).
- [ ] Puedo decidir si una función debería ser `async def` o `def`.
- [ ] Puedo explicar por qué una LLM API es a la vez caso de async y de caching.
- [ ] Puedo explicar la diferencia entre una cookie firmada y una cifrada, y qué hace `HttpOnly`.

---

## 9. Preguntas de repaso

1. Un compañero abre la conexión a la base como variable global al importar el módulo. ¿Qué problemas le señalarías y cómo lo resolverías con `Depends`?
2. ¿Por qué el service no debería importar SQLAlchemy? ¿Qué se rompe exactamente si lo hace?
3. Tu API en Docker tira _connection refused_ al conectarse a Postgres. Nombrá dos causas probables y cómo verificarías cada una.
4. ¿Por qué un endpoint que llama a una LLM API es buen candidato tanto para `async def` como para caching? ¿Qué problema resuelve cada técnica?
5. Al pasar de SQLite a Postgres, ¿qué archivos cambiaron y cuáles no? ¿Qué te dice eso sobre la separación en capas?

---

## 10. Recursos adicionales

**Imprescindible**

- [Dependencies — FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/): `Depends` y sus casos de uso oficiales.
- [Middleware — FastAPI](https://fastapi.tiangolo.com/tutorial/middleware/): el mecanismo general, con el ejemplo de `X-Process-Time`.
- [Bigger Applications - Multiple Files — FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/): `APIRouter`, `prefix`, `tags` y routers anidados.
- [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/): la sesión de BD como dependencia.
- [FastAPI in Containers - Docker — FastAPI](https://fastapi.tiangolo.com/deployment/docker/): cómo escribir el `Dockerfile` de una app FastAPI.

**Recomendado**

- [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html): el post original, con la regla de dependencia.
- [Concurrency and async / await — FastAPI](https://fastapi.tiangolo.com/async/): cuándo usar `async def` y cuándo `def`.
- [Docker Compose — Get started](https://docs.docker.com/compose/gettingstarted/): servicios, redes y volúmenes, paso a paso.

**Opcional**

- [Middleware — Starlette](https://starlette.dev/middleware/): `SessionMiddleware` y los otros middlewares incluidos (CORS, GZip).
- [postgres — Docker Hub](https://hub.docker.com/_/postgres): variables de entorno de la imagen oficial (`POSTGRES_USER`, `POSTGRES_DB`, etc.).
- Chip Huyen, _AI Engineering: Building Applications with Foundation Models_ (O'Reilly, 2025): capítulo sobre caching en apps de IA. Disponible en la wiki interna del bootcamp.