# M07·S05 — Lab integrador + kickoff de TaskFlow: el prototipo mínimo en capas

|                                  |                                                                                                                                                                                        |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sesión**                       | M07·S05                                                                                                                                                                                |
| **Fecha**                        | [Completar por el profesor: fecha]                                                                                                                                                     |
| **Módulo**                       | 07 — Fundamentos de Software + System Design para AI Engineers · Semana 1 (Full-stack y el webserver FastAPI)                                                                          |
| **Tema**                         | Arranca TaskFlow: prototipo FastAPI en capas con `Tarea` y `Proyecto` en memoria, cliente `httpx`, PostgreSQL en Docker con Compose (sin conectar), diagramas y bitácora de trade-offs |
| **Duración estimada de estudio** | ~8 h: ~4 h de recursos y notas + ~4 h de ejercicios                                                                                                                                    |
| **Punto de partida → entrega**   | tag `bootstrap` → tag `s05` del repo `fastapi-full-v0`                                                                                                                                 |

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Explicar** qué es TaskFlow, qué no es, y por qué el prototipo de hoy recorta el dominio a dos entidades en memoria sin que eso sea "hacerlo mal" (la arquitectura como blanco móvil).
2. **Dirigir** a un agente de código sobre un repo preparado —`CLAUDE.md`, `sessions/s05.md`, protocolo de sesión, plan mode— y cerrarle el bucle con una verificación que él mismo pueda correr.
3. **Construir** un webserver FastAPI en capas (router → service → repository → datos) con tres endpoints de tareas —crear, listar y `POST /tasks/{tarea_id}/move`— y con `app/dependencies.py` como único punto de cableado.
4. **Levantar y verificar** PostgreSQL 16 en Docker con `docker-compose.yml` y `.env`, entendiendo cada línea del servicio, aunque la app todavía no se conecte.
5. **Diagramar** en Mermaid los componentes del prototipo y el ciclo de una request de punta a punta, coherentes con el código.
6. **Registrar y defender** tres trade-offs del prototipo en `docs/trade-offs.md`, con la alternativa descartada y su consecuencia.

---

## 2. Resumen ejecutivo

Esta sesión cierra la semana 1 y **no enseña componentes nuevos de FastAPI: los integra**. En M07·S03 levantaste tu primer webserver (path operations, Pydantic, Uvicorn, Swagger) y dibujaste el ciclo de una request; en M07·S04 separaste el código en capas router → service → repository, usaste `Depends` y `APIRouter`, y dibujaste el diagrama de componentes. Hoy todo eso se vuelve **TaskFlow**: una API de gestión de tareas para equipos, tipo mini-Trello, **sin ningún componente de IA**, que vas a construir en equipo entre S05 y S12, con un tag de git por sesión.

El prototipo de hoy es chico a propósito: `Tarea` y `Proyecto` en memoria, tres endpoints, un cliente `httpx` y un Postgres levantado en Docker al que la app todavía no le habla. Como dijo Andrew Ng en su *AI Engineering Skills Map* (que abrió el módulo en S01), la arquitectura correcta depende de la fase del proyecto, y los datos son la decisión más difícil de cambiar después. Por eso la capa repository y `app/dependencies.py` existen desde el día uno: en S07 se cambia memoria por Postgres tocando solo el cableado.

¿Por qué importa para un AI Engineer? Porque el núcleo de IA de un producto vive siempre adentro de una app como esta, y el que dirige al agente es quien sabe dónde va cada cosa. Hoy practicás exactamente eso con el `CLAUDE.md` del repo, la regla de oro "no te adelantes" y el trade-off journal que arrancó en S01, que ahora vive en `docs/trade-offs.md`.

---

## 3. Conceptos clave / glosario

Lo que ya viste se refresca en una línea y se referencia. Lo nuevo va con definición, para qué y por qué así.

### Ya vistos (refresco)

| Término | Dónde | Refresco |
|---|---|---|
| FastAPI, path operation, Pydantic, Uvicorn, Swagger UI (`/docs`) | M07·S03 | El framework, la ruta + método, el modelo que valida, el servidor ASGI y la doc interactiva autogenerada. |
| `Depends`, `APIRouter`, capas router → service → repository, regla de dependencia | M07·S04 | Inyección de dependencias, mini-app de rutas, y las capas donde las dependencias apuntan siempre hacia adentro. |
| Diagrama de secuencia / de componentes | M07·S03 / M07·S04 | Quién le habla a quién en el tiempo / qué piezas tiene un sistema y cómo se conectan. |
| Trade-off journal | M07·S01 | La bitácora de decisiones: alternativas, elección y por qué. |
| `CLAUDE.md`, plan mode, explore → plan → implement → commit | MA·S04, M07·S01 | El archivo de contexto persistente del agente y el flujo de trabajo en fases. |
| C4, Mermaid, ADR, máquina de estados | MA·S05 | Notaciones de modelado y registro de decisiones. |
| Tablero Kanban backlog / en progreso / hecho | MA·S06 | Las columnas que hoy son los valores del Enum `Estado`. |
| Twelve-Factor VI (procesos stateless) | M07·S02 | El estado no vive en el proceso sino en un datastore. |
| Docker | Módulo 03 | Lo usaste para auto-hostear n8n; acá se repasa lo justo para Compose. |

### Proyecto y forma de trabajo

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **TaskFlow** | La API de gestión de tareas para equipos (tipo mini-Trello) que construye el módulo entre S05 y S12. Seis entidades en su forma final; hoy, dos. | Tener un proyecto común donde aplicar datos, API, arquitectura y operación, y comparar decisiones entre equipos. | Sin LLM a propósito: el foco queda en los fundamentos y no en la incertidumbre de un modelo. |
| **Prototipo mínimo** (a veces llamado *walking skeleton*) | La versión más fina posible que ya atraviesa todas las capas, del cliente hasta el almacenamiento. | Validar la arquitectura de punta a punta antes de engordar cualquier capa. | La alternativa —hacer una capa completa por vez— descubre los problemas de integración al final, cuando son caros. |
| **Tag por sesión** | Una etiqueta de git (`bootstrap`, `s05`, `s06`…) que marca el estado del repo al cierre de cada sesión. | Saber exactamente desde dónde parte cada sesión y poder volver a cualquier punto. | Un tag es inmutable y legible; una rama se mueve y un hash no se recuerda. |
| **Spec de sesión** (`sessions/s05.md`) | El archivo del repo con Objetivo, Entra, NO entra y Entregables de la sesión. | Que el agente (y vos) sepan qué se construye hoy y qué no. | Una spec en archivo sobrevive a la conversación y se versiona; un prompt largo se pierde. |
| **Regla de oro "no te adelantes"** | La regla del `CLAUDE.md` del repo: solo se implementa el alcance de la sesión activa; lo futuro se menciona como "viene después". | Evitar que el agente meta auth, caching o tests exhaustivos que nadie pidió. | Un agente tiende a "completar" con buenas prácticas genéricas; cada sesión tiene que poder entenderse y defenderse. |
| **Verificación ejecutable** | Un chequeo que el agente puede correr solo para saber si terminó (acá: `python scripts/client.py` y `docker compose ps`). | Que "listo" sea un hecho comprobable y no una impresión. | Sin ella, según la guía de Claude Code, vos pasás a ser el bucle de verificación. |

### FastAPI en capas

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **Router** (`app/routers/tareas.py`) | La capa que recibe HTTP, valida con Pydantic, llama al service y traduce el resultado (o el error) a HTTP. | Que todo lo que sabe de HTTP viva en un solo lugar. | Si el service conociera `HTTPException`, no se podría reusar desde un script, un worker o un test sin FastAPI. |
| **Service** (`ServicioTareas`) | La capa con las reglas de negocio: "toda tarea nace en `backlog`", "toda tarea pertenece a un proyecto existente". | Tener las reglas en un lugar que no depende de HTTP ni de la base. | Es la capa que no cambia cuando cambia la persistencia (S07) o el contrato HTTP (S09). |
| **Repository** (`RepositorioTareasEnMemoria`) | La capa que guarda y recupera entidades, con métodos como `crear`, `listar`, `obtener`, `guardar`. | Esconder *dónde* viven los datos detrás de una interfaz chica. | Hoy es un `dict`; en S07, Postgres. El service no se entera. |
| **Cableado** (`app/dependencies.py`) | El único archivo que sabe qué implementación concreta se usa: crea los repos, crea el service y lo expone con `obtener_servicio_tareas()`. | Cambiar una implementación por otra tocando un solo archivo. | Si cada router armara sus propios objetos, el cambio a Postgres tocaría N archivos. |
| **Excepción de dominio** (`TareaNoEncontrada`, `ProyectoNoEncontrado`) | Una excepción propia que expresa un problema del negocio, sin códigos HTTP. | Que el service avise "no existe" sin saber que existe HTTP; el router decide que eso es un 404. | Respeta la regla de dependencia de S04: el dominio no importa el framework. |
| **`HTTPException`** | La excepción de FastAPI que corta el request y devuelve un código y un cuerpo `{"detail": ...}`. | Responder un error HTTP desde cualquier punto del borde. | Se *lanza*, no se devuelve: así corta la ejecución aunque esté en una función auxiliar. |

### Modelo y datos

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **Pydantic único** | Usar la misma clase Pydantic (`Tarea`) como body de entrada, entidad de dominio y respuesta. | Escribir menos código y no mapear entre clases en un prototipo. | La alternativa (dataclass de dominio + schemas en el router) desacopla mejor pero exige mapeos; es el trade-off 1 del proyecto. |
| **`class Estado(str, Enum)`** | Un conjunto cerrado de valores (`backlog`, `en progreso`, `hecho`) que además son strings. | Que un estado inválido se rechace con 422 sin escribir validación. | Heredar de `str` hace que el JSON y la documentación lo traten como string; un `str` suelto aceptaría cualquier texto. |
| **422 Unprocessable Entity** | El código que FastAPI devuelve solo cuando el request no pasa la validación de Pydantic. | Avisarle al cliente que el contenido no cumple el contrato. | Lo genera el framework: tu código ni se ejecuta. |
| **201 Created** | El código que indica que se creó un recurso. | Distinguir "creé algo" de un 200 genérico. | Es la convención tras crear un registro; se fija en el decorador. |
| **`dict` indexado por id** | Guardar las entidades en `dict[int, Tarea]`, con la clave igual al id. | Buscar, actualizar y mover por id de forma directa. | Una `list` obliga a recorrer todo para encontrar una tarea; el `dict` se parece al acceso por clave primaria de una base. |
| **Estado en el proceso** | Datos que viven en la memoria del proceso de Python y desaparecen cuando el proceso termina. | Arrancar sin base de datos para ver la capa repository sin ruido. | Es la contracara del factor VI de S02: hoy se acepta como limitación del prototipo. |

### Cliente e infraestructura

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **`httpx.Client`** | Un cliente HTTP de Python que reutiliza la conexión entre requests al mismo host. | Ejercitar la API desde un script repetible (`scripts/client.py`). | Comparado con llamadas sueltas, reutiliza la conexión; como context manager, la cierra al salir. |
| **`base_url`** | Parámetro del `Client` que se antepone a cada ruta. | Escribir `client.get("/tasks")` en vez de repetir el host en cada línea. | Cambiar de servidor es cambiar una constante. |
| **Docker Compose** | La herramienta que define en un archivo YAML los servicios, volúmenes y configuración de una app multi-contenedor. | Levantar Postgres con un comando, igual en todas las máquinas del equipo. | Un `docker run` con diez flags no se versiona ni se revisa; un archivo sí. |
| **Servicio** (Compose) | Una entrada bajo `services:` (acá, `db`) que describe una imagen y cómo correrla. | Declarar qué contenedores forman la app. | Analogía: la imagen es la receta, el contenedor es el plato servido, el servicio es la línea del menú. |
| **Volumen con nombre** (`taskflow_pgdata`) | Almacenamiento persistente que Docker administra y que sobrevive al contenedor. | Que los datos de Postgres no se borren al recrear el contenedor. | Sin volumen, los datos viven en la capa del contenedor y se pierden al recrearlo. |
| **Healthcheck** | Un comando que Docker corre periódicamente para saber si el servicio funciona de verdad. | Distinguir "el contenedor corre" de "la base acepta conexiones". | Un proceso vivo puede todavía estar arrancando; el healthcheck pregunta lo que importa. |
| **`pg_isready`** | La utilidad de PostgreSQL que informa por código de salida si el servidor acepta conexiones. | Ser el `test` del healthcheck. | Usa el código de salida (0 = acepta), que es justo lo que Docker interpreta. |
| **Interpolación `${VAR:-default}`** | Sintaxis de Compose que toma el valor de una variable o un default si no está definida o está vacía. | Que el compose levante aunque no exista `.env`. | Con `${VAR}` a secas, una variable faltante deja un valor vacío. |
| **`.env` / `.env.example`** | `.env` tiene tu configuración local y no se commitea; `.env.example` es la plantilla versionada. | Separar config de código (Twelve-Factor, factor III). | Si `.env` se commitea, las credenciales quedan en el historial de git para siempre. |
| **`DATABASE_URL`** | La cadena de conexión a la base, en una sola variable. | Que la app sepa dónde está Postgres sin hardcodearlo. | Hoy existe pero nadie la lee: la app se conecta recién en S07. |

### Documentación

| Término | Qué es | Para qué se usa | Por qué así |
|---|---|---|---|
| **Diagrama de componentes (C4)** | El diagrama que descompone un único container (acá, la app FastAPI) en sus componentes, y muestra alrededor los elementos de soporte. | Mostrar qué piezas tiene el código y quién usa a quién. | C4 fija el nivel de zoom: ni la arquitectura entera ni las clases una por una. |
| **Bloque `alt`** (secuencia) | Una caja con caminos alternativos (`alt` / `else`) en un diagrama de secuencia. | Dibujar el 404 y el 200 en el mismo diagrama. | Dos diagramas casi iguales se desincronizan; un `alt` los mantiene juntos. |
| **Entrada `[s05]`** de `docs/trade-offs.md` | Un registro de decisión con fecha, decisión, alternativas, elección, por qué y consecuencias, encabezado `### [s05] título`. | Que la decisión y su porqué sobrevivan a la conversación con el agente. | Sin numeración: el prefijo de sesión ya ordena; la serie `ADR-NNN` arranca recién en S06. |

---

## 4. Notas de estudio por subtema

### El mapa de hoy

Antes de los detalles, la pieza central de la sesión: así queda el prototipo al cierre. Es también, casi literal, el diagrama de componentes que vas a entregar.

```mermaid
flowchart TD
    CLI["Cliente httpx<br/>(scripts/client.py)"] -->|"HTTP"| UVI["Uvicorn<br/>(servidor ASGI)"]
    UVI --> RT
    subgraph APP["Aplicación FastAPI (app/)"]
        RT["Router<br/>app/routers/tareas.py"] --> SV["Service<br/>app/services/tarea_service.py"]
        SV --> RPT["Repositorio Tareas (memoria)<br/>app/repositories/tarea_repository.py"]
        SV --> RPP["Repositorio Proyectos (memoria)<br/>app/repositories/proyecto_repository.py"]
        DEP["Cableado<br/>app/dependencies.py"] -.->|"inyecta"| RT
        MOD["Modelos de dominio<br/>app/models/"]
    end
    APP -.->|"se conectará en s07"| DB[("PostgreSQL 16<br/>docker-compose<br/>no conectada aún")]

    classDef ojo fill:#FFFBEB,stroke:#B45309,stroke-width:2px
    class DB ojo
```

Leelo de arriba abajo: el cliente habla HTTP con Uvicorn, Uvicorn le pasa el request a la app, el router delega en el service, el service usa dos repositorios en memoria. `dependencies.py` es quien arma esa cadena. Abajo, Postgres ya existe pero la flecha es punteada: **está presente, no conectado**. Esa flecha punteada es la promesa de S07.

---

### 4.1 Kickoff de TaskFlow: dominio, recorte y arquitectura como blanco móvil

**Para qué.** Hasta S04 cada uno tenía su webserver de práctica. A partir de hoy, todos los equipos construyen **el mismo proyecto**, para que las decisiones, los diagramas y las revisiones se puedan comparar. Sin un proyecto común, una discusión de trade-offs se vuelve "en el mío funcionaba".

**Qué es TaskFlow.** Una API de gestión de tareas para equipos, tipo mini-Trello: equipos que colaboran en proyectos, proyectos con tareas que se mueven entre estados (backlog → en progreso → hecho), tareas con responsable, comentarios y etiquetas. **Qué no es:** no tiene ningún componente de IA/LLM propio. Más adelante (S08) va a exponer un tablero pensado para que un agente *externo* lo consuma, pero TaskFlow no incorpora ningún modelo.

**El dominio completo vs el recorte de hoy.**

| Al final del módulo | Hoy (S05) |
|---|---|
| 6 entidades: `Usuario`, `Equipo`, `Proyecto`, `Tarea`, `Comentario`, `Etiqueta` + 2 relaciones M:N | 2 entidades: `Tarea` y `Proyecto` (con un solo proyecto sembrado, `General`) |
| PostgreSQL con ORM | Memoria (`dict` por id) + Postgres levantado pero sin conectar |
| API v1 en `/v1/...`, paginación, filtros | Tres endpoints en `/tasks` |
| Frontend en HTML + vanilla JS | Un script `httpx` |

**La hoja de ruta.** Cada sesión parte del tag de la anterior y entrega el suyo:

| Sesión | Agrega | Parte de |
|---|---|---|
| **S05** | Prototipo mínimo en capas, memoria, compose con Postgres, cliente `httpx` | `bootstrap` |
| S06 | Modelo de dominio completo + decisión de almacenamiento (`ADR-001`) | `s05` |
| S07 | PostgreSQL real: ORM, repository con mapeo ORM ⇄ dominio, modelo ER | `s06` |
| S08 | Datos para agentes: seed idempotente y endpoint de tablero autocontenido | `s07` |
| S09 | Contrato de la API v1 (top-down) | `s08` |
| S10 | Implementación completa de la API v1 (cierra el backend) | `s09` |
| S11 | Frontend estático: del HTML al DOM | `s10` |
| S12 | El frontend habla con la API (entregable final) | `s11` |

**La arquitectura como blanco móvil.** Andrew Ng, en *AI Engineering Skills Map* (2026), plantea que la arquitectura correcta depende de la fase: la de un prototipo rápido puede no servir para el primer sistema en producción, y esa a su vez puede cambiar al escalar. También dice que los datos son la base del software y relativamente difíciles de cambiar, aun con agentes ayudando en las migraciones. Las dos ideas explican el recorte de hoy:

- **Memoria y dos entidades** no es "hacerlo mal": es la arquitectura de la fase 1. Ya sabemos que se reemplaza en S06–S07.
- **Postgres en Docker desde hoy**, aunque nadie lo use: la decisión de datos es la que más cuesta revertir, así que la infraestructura se fija temprano y el cambio de S07 queda acotado al cableado.

**Ejemplo práctico: cómo se lee el recorte en el repo.** `sessions/s05.md` lo dice en dos listas:

```markdown
## Entra
- FastAPI en capas con entidades **Tarea** y **Proyecto** en **memoria**.
- Endpoints: crear tarea, listar tareas, mover tarea de estado (`backlog → en progreso → hecho`).
- Cliente mínimo como script `httpx` que ejercita los endpoints.
- `docker-compose.yml` con el servicio de **PostgreSQL** + `.env.example` con `DATABASE_URL`.

## NO entra
- ORM.
- Conexión a Postgres desde la app.
- Auth.
- El modelo completo de entidades (eso es s06).
- HTML / frontend.
```

*Por qué así:* la lista **NO entra** vale tanto como la de **Entra**. Un agente que lee solo "hacé una API de tareas" agrega usuarios, login y una base real, porque son "buena práctica". La exclusión explícita es la línea más barata para evitarlo (es lo que en MA·S04 llamamos alcance excluido).

**Errores comunes.**
- Pensar que el prototipo "es un borrador que se tira". No se tira: se *evoluciona*. Por eso las capas existen desde hoy.
- Agregar entidades de S06 "porque ya que estamos". Rompe la comparación entre equipos y te deja sin la discusión de modelado de la próxima sesión.

---

### 4.2 Dirigir al agente con el repo preparado

El código de hoy lo escribe, en buena parte, el agente. Lo que vos aportás es **dirección**: qué se construye, qué no, en qué capa va cada cosa y cómo se sabe que terminó. El repo `fastapi-full-v0` en el tag `bootstrap` ya trae esa dirección escrita, así que hoy no la redactás: la **usás**.

**Qué trae el repo en `bootstrap`.**
- `CLAUDE.md`: las reglas del proyecto y el protocolo de sesión.
- `sessions/s05.md` … `s12.md`: el alcance de cada sesión.
- `docs/trade-offs.md`: la plantilla de la bitácora, vacía.
- `requirements.txt` sin paquetes y `.python-version` con `3.12`.



---

### 4.3 FastAPI en capas: router → service → repository

**Para qué.** Que un cambio de *dónde se guardan los datos* (S07) o de *cómo se ve la URL* (S09) no obligue a reescribir las reglas de negocio. Cada capa tiene una sola razón para cambiar.

**Cómo se reparten las responsabilidades:**

| Capa | Archivo | Sabe de | No sabe de |
|---|---|---|---|
| Router | `app/routers/tareas.py` | HTTP, códigos, `HTTPException`, Pydantic del body | Dónde se guardan los datos |
| Service | `app/services/tarea_service.py` | Reglas de negocio, excepciones de dominio | FastAPI, HTTP |
| Repository | `app/repositories/*.py` | Cómo se guarda y recupera | HTTP, reglas de negocio |
| Cableado | `app/dependencies.py` | Qué clase concreta se usa | Nada más |

La regla de dependencia es la de S04: `routers → services → repositories → models`. El service **no importa FastAPI**.

**Ejemplo práctico 1: el service y sus excepciones de dominio.**

```python
# app/services/tarea_service.py
from app.models.estado import Estado
from app.models.tarea import Tarea
from app.repositories.proyecto_repository import RepositorioProyectosEnMemoria
from app.repositories.tarea_repository import RepositorioTareasEnMemoria


class ProyectoNoEncontrado(Exception):
    """El proyecto referenciado por la tarea no existe."""


class TareaNoEncontrada(Exception):
    """No hay ninguna tarea con ese id."""


class ServicioTareas:
    def __init__(
        self,
        repo_tareas: RepositorioTareasEnMemoria,
        repo_proyectos: RepositorioProyectosEnMemoria,
    ) -> None:
        # Recibe los repos ya armados: no los crea. Quién los crea lo decide dependencies.py.
        self._repo_tareas = repo_tareas
        self._repo_proyectos = repo_proyectos

    def crear_tarea(self, tarea: Tarea) -> Tarea:
        # Regla de negocio: una tarea siempre pertenece a un proyecto existente.
        if not self._repo_proyectos.existe(tarea.proyecto_id):
            raise ProyectoNoEncontrado(tarea.proyecto_id)
        # El estado inicial siempre es BACKLOG, sin importar lo que mande el cliente.
        tarea.id = None
        tarea.estado = Estado.BACKLOG
        return self._repo_tareas.crear(tarea)

    def listar_tareas(self) -> list[Tarea]:
        return self._repo_tareas.listar()

    def mover_tarea(self, tarea_id: int, nuevo_estado: Estado) -> Tarea:
        tarea = self._repo_tareas.obtener(tarea_id)
        if tarea is None:
            raise TareaNoEncontrada(tarea_id)
        tarea.estado = nuevo_estado
        return self._repo_tareas.guardar(tarea)
```

*Por qué así:*
- **Excepciones propias en vez de `HTTPException`:** el service dice "no existe", no "404". Si mañana el mismo service lo usa un script de seed o un worker, "404" no significa nada ahí.
- **Recibe los repos por constructor:** el service no hace `RepositorioTareasEnMemoria()` adentro. Si lo hiciera, cambiar a Postgres sería editar el service, que es exactamente lo que queremos evitar.
- **`tarea.id = None` y `tarea.estado = Estado.BACKLOG`:** como `Tarea` es la misma clase para el body (ver 4.4), el cliente *puede* mandar `id` y `estado`. El service los pisa, porque las reglas de negocio viven acá.
- **`mover_tarea` no valida transiciones.** Cualquier estado puede pasar a cualquier otro, incluido `hecho → backlog`. El Enum solo garantiza que el destino sea uno de los tres. Es una decisión abierta del proyecto: ¿quién decide qué movimientos son válidos y dónde viviría esa regla? La vas a explorar en el ejercicio 🔴 de la Unidad 1, en una rama de práctica.

**Ejemplo práctico 2: el router traduce dominio a HTTP.**

```python
# app/routers/tareas.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import obtener_servicio_tareas
from app.models.estado import Estado
from app.models.tarea import Tarea
from app.services.tarea_service import (
    ProyectoNoEncontrado,
    ServicioTareas,
    TareaNoEncontrada,
)

router = APIRouter(prefix="/tasks", tags=["tareas"])


class MoverTarea(BaseModel):
    """Cuerpo del endpoint de mover: solo el estado destino (validado por el Enum)."""

    estado: Estado


@router.post("", response_model=Tarea, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    tarea: Tarea,
    servicio: ServicioTareas = Depends(obtener_servicio_tareas),
) -> Tarea:
    try:
        return servicio.crear_tarea(tarea)
    except ProyectoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto {tarea.proyecto_id} no existe",
        )


@router.get("", response_model=list[Tarea])
def listar_tareas(
    servicio: ServicioTareas = Depends(obtener_servicio_tareas),
) -> list[Tarea]:
    return servicio.listar_tareas()


@router.post("/{tarea_id}/move", response_model=Tarea)
def mover_tarea(
    tarea_id: int,
    cuerpo: MoverTarea,
    servicio: ServicioTareas = Depends(obtener_servicio_tareas),
) -> Tarea:
    try:
        return servicio.mover_tarea(tarea_id, cuerpo.estado)
    except TareaNoEncontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La tarea {tarea_id} no existe",
        )
```

*Por qué así:*
- **`APIRouter(prefix="/tasks", tags=["tareas"])`:** la doc de FastAPI lo describe como un "mini `FastAPI`". El `prefix` agrupa las rutas y no termina en `/`; los `tags` agrupan los endpoints en Swagger.
- **`@router.post("")` y no `"/"`:** con el prefix, la URL queda exactamente `/tasks`. Con `"/"` quedaría `/tasks/`, con barra final, que es otra ruta.
- **`Depends(obtener_servicio_tareas)` sin paréntesis:** le pasás la *función*, no su resultado. FastAPI la llama en cada request. Si escribieras `Depends(obtener_servicio_tareas())`, le pasarías un objeto ya construido y FastAPI no sabría qué hacer con él.
- **`Depends` como valor por defecto y no con `Annotated`:** en S04 usaste `Annotated[ServicioTareas, Depends(...)]`. Las dos formas son válidas; el repo usa la primera. Lo importante es ser consistente dentro del proyecto.
- **`try/except` que traduce:** es el único lugar donde "no existe" se convierte en 404. `raise HTTPException` (no `return`) corta el request y el cliente recibe `{"detail": "La tarea 7 no existe"}`.
- **`MoverTarea` vive en el router:** es la forma del body de *este* endpoint, no una entidad del dominio. Por eso no está en `app/models/`.
- **Rutas en inglés (`/tasks`, `/move`) y campos en español (`titulo`, `estado`):** es el estado real del proyecto en este tag. En S09 se diseña el contrato v1 y ahí se revisa; hoy no se toca.

**Ejemplo práctico 3: el cableado.**

```python
# app/dependencies.py
from app.repositories.proyecto_repository import RepositorioProyectosEnMemoria
from app.repositories.tarea_repository import RepositorioTareasEnMemoria
from app.services.tarea_service import ServicioTareas

# Instancias a nivel de módulo: se crean UNA vez, cuando Python importa este archivo.
_repo_proyectos = RepositorioProyectosEnMemoria()
_repo_tareas = RepositorioTareasEnMemoria()
_servicio_tareas = ServicioTareas(_repo_tareas, _repo_proyectos)


def obtener_servicio_tareas() -> ServicioTareas:
    # El provider que usa Depends: devuelve siempre el mismo service ya cableado.
    return _servicio_tareas
```

*Por qué así:* las instancias se crean una sola vez por proceso. Si `obtener_servicio_tareas()` hiciera `ServicioTareas(RepositorioTareasEnMemoria(), ...)` adentro, **cada request vería un `dict` vacío**: creás una tarea, la listás y no está. Es el error más típico que comete un agente con este patrón, y lo vas a provocar a propósito en el ejercicio 🟢 de la Unidad 1. Además, este es **el único archivo que nombra las clases concretas**: en S07 se cambian acá los repos en memoria por los de PostgreSQL, y router y service no se tocan.

**Errores comunes.**
- **Importar `HTTPException` en el service** "porque es más corto". Rompe la regla de dependencia y te ata a FastAPI.
- **Atrapar `Exception` en el router.** Te traga errores reales (bugs) y los convierte en 404 falsos. Atrapá solo las excepciones de dominio que sabés traducir.
- **Olvidarse de que las rutas son `def`.** FastAPI corre las rutas síncronas en un threadpool (S04). Con memoria compartida eso tiene una consecuencia que vemos en 4.5.

**Para profundizar:** FastAPI — *Bigger Applications - Multiple Files*, *Dependencies* y *Handling Errors*.

---

### 4.4 El modelo mínimo: Pydantic único y `Estado` como Enum

Necesitás una forma de describir una tarea que sirva para validar lo que llega, representar el dominio y serializar lo que sale. Y necesitás que "estado" solo pueda ser uno de tres valores, sin escribir un `if` por cada caso.

**Ejemplo práctico: los tres modelos.**

```python
# app/models/estado.py
from enum import Enum


class Estado(str, Enum):
    BACKLOG = "backlog"
    EN_PROGRESO = "en progreso"
    HECHO = "hecho"
```

```python
# app/models/tarea.py
from pydantic import BaseModel

from app.models.estado import Estado


class Tarea(BaseModel):
    id: int | None = None            # lo asigna el repository; el cliente puede omitirlo
    titulo: str                      # único campo obligatorio
    descripcion: str | None = None
    estado: Estado = Estado.BACKLOG  # el service lo fuerza a BACKLOG al crear
    proyecto_id: int = 1             # por defecto, el proyecto sembrado "General"
```

```python
# app/models/proyecto.py
from pydantic import BaseModel


class Proyecto(BaseModel):
    id: int
    nombre: str
```

*Por qué así:*
- **`class Estado(str, Enum)`** es el patrón de la doc de FastAPI para valores predefinidos. Heredar de `str` hace que la documentación sepa que los valores son strings, que Swagger muestre los tres disponibles y que en el JSON viaje el *valor*, no el nombre del miembro. La doc lo muestra en un path param; acá se usa en el body (`MoverTarea.estado`), y el mecanismo es el mismo: un valor fuera del Enum da **422 sin una línea de validación propia**.
- **Nombre del miembro ≠ valor.** En Python escribís `Estado.EN_PROGRESO`; en el JSON viaja `"en progreso"`, con espacio. Mandar `"EN_PROGRESO"` o `"en_progreso"` da 422.
- **`id` y `estado` con default:** como `Tarea` es a la vez body de entrada y respuesta, tienen que poder omitirse al crear. El precio: el cliente *puede* mandarlos, y el service los ignora.
- **`proyecto_id: int = 1`:** toda tarea cae por defecto en `General`. Hoy no hay endpoints de proyectos.

**Pydantic único: lo que ganás y lo que pagás.** Es el trade-off 1 del proyecto.

| | Pydantic para todo (elegido) | `@dataclass` de dominio + schemas Pydantic en el router |
|---|---|---|
| Código | Una clase por entidad | Dos clases por entidad + mapeo |
| Validación y serialización | Gratis, de FastAPI | Gratis en el borde, a mano en el dominio |
| Acoplamiento | El dominio depende de Pydantic | El dominio es Python puro |
| Contrato de entrada | El cliente ve `id` y `estado` como campos del body aunque se ignoren | El body de crear solo tiene lo que el cliente puede mandar |

`response_model=Tarea` valida la salida, publica su JSON Schema en el OpenAPI y **filtra** la respuesta a los campos declarados. Con una sola clase, entrada y salida son idénticas: no podés esconder ni agregar nada distinto en la respuesta. Por eso, cuando el contrato crezca, aparecen schemas separados.

**Errores comunes.**
- **Agregar ya `responsable_id`, `created_at` o etiquetas.** Es el modelo completo de S06.
- **Creer que Pydantic revalida al asignar.** `tarea.estado = nuevo_estado` no pasa por validación; funciona porque `nuevo_estado` ya llegó validado como `Estado`.

**Para profundizar:** FastAPI — *Path Parameters* (sección de valores predefinidos), *Response Model - Return Type*, *Response Status Code*.

---

### 4.5 Datos en memoria

**Para qué.** Arrancar sin base de datos te deja ver la capa repository "desnuda": qué operaciones necesita el service, sin SQL ni conexiones en el medio. Lo que aprendas acá es la interfaz que S07 reimplementa sobre Postgres.

**Ejemplo práctico: los dos repositorios.**

```python
# app/repositories/tarea_repository.py
from app.models.tarea import Tarea


class RepositorioTareasEnMemoria:
    def __init__(self) -> None:
        self._tareas: dict[int, Tarea] = {}  # clave = id de la tarea
        self._siguiente_id: int = 1          # contador propio, arranca en 1

    def crear(self, tarea: Tarea) -> Tarea:
        tarea.id = self._siguiente_id  # el id lo asigna el repositorio, no el cliente
        self._tareas[tarea.id] = tarea
        self._siguiente_id += 1
        return tarea

    def listar(self) -> list[Tarea]:
        return list(self._tareas.values())

    def obtener(self, tarea_id: int) -> Tarea | None:
        return self._tareas.get(tarea_id)  # None si no existe: decide el service

    def guardar(self, tarea: Tarea) -> Tarea:
        # Persiste una tarea ya existente (p. ej. tras cambiarle el estado).
        self._tareas[tarea.id] = tarea
        return tarea
```

```python
# app/repositories/proyecto_repository.py
from app.models.proyecto import Proyecto


class RepositorioProyectosEnMemoria:
    def __init__(self) -> None:
        # Sembramos un proyecto por defecto para que las tareas tengan dónde vivir.
        self._proyectos: dict[int, Proyecto] = {
            1: Proyecto(id=1, nombre="General"),
        }

    def obtener(self, proyecto_id: int) -> Proyecto | None:
        return self._proyectos.get(proyecto_id)

    def existe(self, proyecto_id: int) -> bool:
        return proyecto_id in self._proyectos
```

*Por qué así:*
- **`dict` y no `list`:** buscar, actualizar o mover por id es acceso directo por clave; con una lista habría que recorrerla. El `dict` además modela lo que va a hacer PostgreSQL: buscar por clave primaria.
- **El id lo asigna el repository:** igual que una base con una columna autoincremental. Si lo asignara el cliente, dos clientes podrían pisarse los ids.
- **`obtener` devuelve `None`, no lanza:** el repository informa; el service decide si "no existe" es un error de negocio. Separar esas dos cosas es lo que permite que el service sea el que lanza `TareaNoEncontrada`.
- **No hay `Protocol` ni clase base.** Los repos son clases concretas y el service las tipa por nombre. Para un prototipo alcanza; el contrato real es "los mismos métodos con los mismos nombres", y S07 lo respeta.
- **`General` sembrado:** sin proyectos no se podría crear ninguna tarea, y todavía no hay endpoint para crearlos.

**Qué significa que el estado viva en el proceso.**
- Cada vez que Uvicorn reinicia (y con `--reload` reinicia cada vez que guardás un archivo), **todas las tareas desaparecen** y el contador vuelve a 1.
- Si algún día corrieras varios procesos, cada uno tendría su propio `dict`: un request crearía la tarea en uno y el siguiente la buscaría en otro. Es el factor VI de S02 visto desde el lado incorrecto, y vuelve en el escalado de la semana 3.

**Gotchas.**
- **`guardar` parece no hacer falta.** `obtener` devuelve el *mismo objeto* que está en el `dict`, así que `tarea.estado = ...` ya lo modifica "adentro". En memoria funciona aunque te olvides de llamar a `guardar`; **en S07, con Postgres, no**. Por eso el service lo llama igual: la interfaz tiene que valer para las dos implementaciones.
- **`_siguiente_id += 1` no es atómico.** Las rutas son `def`, FastAPI las corre en un threadpool, y dos requests simultáneos podrían leer el mismo valor del contador. En un prototipo de un usuario no se nota; la concurrencia es tema de S07. Hoy se **nombra**, no se corrige.

---

### 4.6 Los endpoints y cómo correrlos

**Para qué.** Tener claro el contrato —qué manda el cliente, qué recibe y con qué código— es lo que te permite escribir el cliente, el diagrama de secuencia y la verificación sin adivinar.

| Endpoint | Body | Respuestas |
|---|---|---|
| `POST /tasks` | `{"titulo": "...", "descripcion": "...", "proyecto_id": 1}` (solo `titulo` obligatorio) | **201** con la `Tarea` creada (`estado: "backlog"`); **404** si `proyecto_id` no existe; **422** si falta `titulo` |
| `GET /tasks` | — | **200** con la lista de tareas (sin filtros ni paginación: llegan en S09–S10) |
| `POST /tasks/{tarea_id}/move` | `{"estado": "en progreso"}` | **200** con la tarea actualizada; **404** si la tarea no existe; **422** si `estado` no es uno de los tres valores |
| `GET /health` | — | **200** `{"status": "ok"}` |

**Ejemplo práctico: la app.**

```python
# app/main.py
from fastapi import FastAPI

from app.routers import tareas

app = FastAPI(title="TaskFlow", version="0.5.0")

app.include_router(tareas.router)


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    """Chequeo simple para verificar que el servidor responde."""
    return {"status": "ok"}
```

*Por qué así:*
- **`main.py` solo arma:** crea la app, monta el router y define `/health`. No tiene lógica de tareas. Si mañana hay cinco routers, son cinco `include_router`.
- **`version="0.5.0"`:** aparece en Swagger y te dice de un vistazo contra qué versión del prototipo estás probando.
- **`/health` fuera del router de tareas:** no es un recurso del dominio sino infraestructura (por eso `tags=["infra"]`). Es lo primero que consulta el cliente: si falla, no tiene sentido seguir.

**Cómo correrlo** (desde la raíz del repo, con el venv activo):

```bash
uvicorn app.main:app --reload
# Swagger en http://127.0.0.1:8000/docs
```

- `app.main:app` significa "módulo `app/main.py`, objeto `app`". Por eso se corre desde la raíz: si estás dentro de `app/`, Python no encuentra el paquete `app`.
- Uvicorn escucha por defecto en `127.0.0.1:8000`.
- `--reload` reinicia al guardar un archivo: cómodo en desarrollo, y **borra todas las tareas en memoria**. Además, según la doc de Uvicorn, `--reload` y `--workers` son mutuamente excluyentes.
- Swagger (`/docs`, visto en S03) te deja probar los tres endpoints y ver los tres valores del Enum en un desplegable.

**Errores comunes.**
- Correr `uvicorn main:app` (como en S03) en vez de `uvicorn app.main:app`: en este repo `main.py` está dentro del paquete `app/`.
- Sorprenderse porque "desaparecieron las tareas": guardaste un archivo y `--reload` reinició el proceso.

**Para profundizar:** Uvicorn — *Settings*.

---

### 4.7 Cliente `httpx`: la verificación ejecutable

**Para qué.** Probar a mano en Swagger está bien una vez. Para que el agente (y vos) puedan comprobar en segundos que todo sigue funcionando después de cada cambio, necesitás un script que recorra los endpoints en orden. Ese script es `scripts/client.py`.

**Ejemplo práctico.**

```python
# scripts/client.py
import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        print("== health ==")
        print(client.get("/health").json())

        print("\n== crear tareas ==")
        t1 = client.post("/tasks", json={"titulo": "Diseñar el tablero"}).json()
        t2 = client.post(
            "/tasks",
            json={"titulo": "Escribir el README", "descripcion": "Breve"},
        ).json()
        print(t1)
        print(t2)

        print("\n== listar tareas ==")
        for tarea in client.get("/tasks").json():
            print(tarea)

        print("\n== mover la primera tarea a 'en progreso' ==")
        movida = client.post(
            f"/tasks/{t1['id']}/move",
            json={"estado": "en progreso"},
        ).json()
        print(movida)

        print("\n== listar tareas (después de mover) ==")
        for tarea in client.get("/tasks").json():
            print(tarea)


if __name__ == "__main__":
    main()
```

*Por qué así:*
- **`httpx.Client` y no llamadas sueltas:** el `Client` reutiliza la conexión TCP entre requests al mismo host (menos latencia, menos CPU). Con `httpx.get(...)` suelto se abriría una conexión por request.
- **`with ... as client`:** es la forma recomendada por la doc; al salir del bloque, las conexiones se cierran solas, aunque haya una excepción.
- **`base_url`:** se antepone a cada ruta. Si mañana el server corre en otro puerto, cambiás una constante.
- **`timeout=5.0` explícito:** coincide con el default documentado de HTTPX, pero escribirlo deja la decisión a la vista de quien lee.
- **`json=`:** serializa el `dict` a JSON y pone el header correcto. Mandar `data=` mandaría un formulario y el server respondería 422.
- **`t1['id']` para mover:** el script no asume que la primera tarea tiene id 1; usa el que devolvió el server. Si lo corrés dos veces sin reiniciar, la segunda vez los ids son 3 y 4, y el script sigue funcionando.

**Gotcha importante.** El script **no llama a `raise_for_status()`**. Si un endpoint devuelve 404 o 422, el script imprime el JSON de error (`{'detail': ...}`) y sigue como si nada. Para ser una verificación de verdad, un error tiene que *cortar* la ejecución con un código de salida distinto de cero. Lo mejorás en la Unidad 2, en tu rama de práctica.

```bash
python scripts/client.py      # en otra terminal, con el servidor levantado
```

**Para profundizar:** HTTPX — *QuickStart* y *Clients*.

---

### 4.8 PostgreSQL en Docker con Compose (sin conectar)

**Para qué.** Que la base de datos del proyecto esté definida en un archivo versionado y se levante igual en todas las máquinas del equipo, **desde hoy**, aunque la app recién la use en S07. Cuando llegue S07, la infraestructura ya está probada y el cambio queda en el código.

**Repaso mínimo de Docker** (lo usaste en el módulo 03 para n8n):
- **Imagen:** la plantilla inmutable (`postgres:16`).
- **Contenedor:** una instancia corriendo de esa imagen (`taskflow-db`).
- **Volumen:** almacenamiento que vive fuera del contenedor (`taskflow_pgdata`).
- **Compose:** describe en YAML los servicios, volúmenes y configuración, y los levanta con un comando. El **proyecto** de Compose agrupa y aísla esos recursos bajo un nombre.

**Ejemplo práctico: `docker-compose.yml`.**

```yaml
services:
  db:
    image: postgres:16
    container_name: taskflow-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-taskflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-taskflow}
      POSTGRES_DB: ${POSTGRES_DB:-taskflow}
    ports:
      # Puerto del host configurable: si el 5432 ya está ocupado por otra base,
      # definí POSTGRES_PORT en tu .env (y ajustá DATABASE_URL en consecuencia).
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - taskflow_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taskflow}"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  taskflow_pgdata:
```

*Por qué así, línea por línea:*
- **`services: db:`** — un solo servicio. La app FastAPI **no** está en el compose: corre con `uvicorn` en tu máquina. Meterla ahora sería adelantarse.
- **`image: postgres:16`** — versión mayor fijada. Con la 16, el directorio de datos es `/var/lib/postgresql/data`; desde la 18, la imagen lo cambia de lugar. Si alguien "actualiza" a `postgres:latest` sin tocar el volumen, el path deja de coincidir. Fijar la versión es la defensa.
- **`container_name: taskflow-db`** — nombre fijo para poder hacer `docker exec -it taskflow-db ...`. El precio, según la doc de Compose: con `container_name` el servicio no se puede escalar a más de un contenedor. Para una base es irrelevante; si alguien copia el patrón a la app, no.
- **`restart: unless-stopped`** — se reinicia solo (por ejemplo, al reiniciar Docker), salvo que lo hayas detenido vos explícitamente.
- **`environment:` con `${VAR:-default}`** — Compose lee el `.env` del directorio del proyecto e interpola. `:-` usa el default si la variable no está definida **o está vacía**; con `-` solo, si no está definida. Resultado: el compose levanta aunque no hayas creado `.env`. `POSTGRES_PASSWORD` es la única variable obligatoria de la imagen; `POSTGRES_USER` crea el superusuario y `POSTGRES_DB` la base.
- **`ports: "${POSTGRES_PORT:-5432}:5432"`** — formato `HOST:CONTENEDOR`. Adentro, Postgres siempre escucha en 5432; afuera, en el puerto que elijas. Si ya tenés otro Postgres en el 5432, cambiás `POSTGRES_PORT` en `.env`.
- **`volumes:` + clave `volumes:` de nivel superior** — volumen con nombre, declarado arriba y montado en el servicio. Los datos sobreviven a `docker compose down`; **no** a `docker compose down -v`.
- **`healthcheck` con `pg_isready`** — el contenedor pasa a *healthy* cuando la base acepta conexiones. `pg_isready` responde por código de salida: 0 acepta, 1 rechaza (por ejemplo, mientras arranca), 2 sin respuesta, 3 no se intentó. Ese código 1 existe justamente porque "corriendo" y "lista" son cosas distintas.

**Ejemplo práctico: `.env.example`.**

```bash
# --- s05: PostgreSQL en Docker ---
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=taskflow
POSTGRES_DB=taskflow

# Puerto del host donde se publica Postgres.
POSTGRES_PORT=5432

# Cadena de conexión que usará la app. En s05 la base ya levanta, pero la app
# TODAVÍA NO se conecta: DATABASE_URL empieza a usarse recién en s07.
DATABASE_URL=postgresql://taskflow:taskflow@localhost:5432/taskflow
```

*Por qué así:*
- **`.env.example` versionado + `.env` en `.gitignore`:** es el factor III de *The Twelve-Factor App*: la config (credenciales, handles a la base) va en variables de entorno, separada del código. El test que propone: ¿podrías publicar el código ya mismo sin comprometer credenciales? El `.gitignore` del repo lo dice en un comentario: "nunca commitear secretos".
- **Credenciales `taskflow`/`taskflow` en el ejemplo:** son valores de desarrollo local, no secretos de un entorno real. El `.env` de cada uno, con lo que ponga, no se sube.
- **`DATABASE_URL` ya existe aunque nadie la lea:** deja fijado hoy dónde va a buscar la app su base en S07. El esquema es `postgresql://`, sin driver; el cambio de formato es parte de S07.

**Cómo levantarlo y verificarlo.**

```bash
cp .env.example .env          # Compose lee .env para interpolar
docker compose up -d          # levanta Postgres en segundo plano
docker compose ps             # STATUS debería pasar a "healthy"
# alternativa que espera al healthcheck:  docker compose up -d --wait
docker exec -it taskflow-db psql -U taskflow -d taskflow -c "select version();"
docker compose down           # apaga; los datos quedan en taskflow_pgdata
```

- `-d` corre en segundo plano. `--wait` espera a que el servicio esté *healthy* (e implica `-d`): el comando no vuelve hasta que `pg_isready` da OK. Es una verificación que el agente también puede correr.
- El `psql` por `docker exec` prueba que la base existe y acepta login **sin** que la app se conecte y sin instalar Postgres en tu máquina.

> ⚠️ **La trampa del primer `up`.** Las variables `POSTGRES_*` de la imagen **solo tienen efecto si el contenedor arranca con el directorio de datos vacío**; una base preexistente queda intacta. Si cambiás la contraseña o el nombre de la base en `.env` *después* del primer `up`, no pasa nada: el volumen ya tiene la base inicializada. Para reinicializar: `docker compose down -v`, que **borra el volumen y todos sus datos**.

> 💡 El archivo se llama `docker-compose.yml` en este proyecto. La doc de Docker prefiere hoy `compose.yaml` y acepta `docker-compose.yml` por compatibilidad hacia atrás: funciona igual, y el nombre del proyecto no se cambia.

**Errores comunes.**
- **Puerto 5432 ocupado** por otro Postgres local: el `up` falla al publicar el puerto. Solución: `POSTGRES_PORT=5433` en `.env` (y el mismo puerto en `DATABASE_URL`).
- **`docker-compose` con guion** en vez de `docker compose`: la sesión asume Compose v2.
- **Commitear `.env`** porque "son credenciales de prueba". El hábito es lo que importa.

**Para profundizar:** Docker — *How Compose works*, *Define services in Docker Compose*, *Variable interpolation*, *docker compose up*; la imagen oficial `postgres` en Docker Hub; `pg_isready` en la doc de PostgreSQL 16; *The Twelve-Factor App* — III. Config.

> 📝 **Nota para el profesor:** se asume Docker con Compose v2 instalado antes de la clase. Si alguien no lo tiene, el prototipo igual funciona (la app no se conecta a la base) y el entregable del compose se completa en pareja o en casa.

---

### 4.9 Diagramas como entregable

**Para qué.** El diagrama es la forma de comprobar que entendés lo que el agente construyó: si no podés dibujar quién llama a quién, todavía no lo entendés. Y como es Mermaid en `docs/diagrams/`, vive junto al código, se versiona y se revisa en el mismo commit.

**Los dos diagramas de hoy:**
- `docs/diagrams/s05-componentes.mmd` — el **diagrama de componentes** (C4): descompone un único container, la app FastAPI, en sus componentes (router, service, repositorios, modelos, cableado). Uvicorn, el cliente `httpx` y PostgreSQL son **elementos de soporte**, por fuera. Es el diagrama ancla de la sección 4. Según C4, este nivel es para arquitectos y desarrolladores, y es opcional: lo dibujás porque acá agrega valor, no por ritual.
- `docs/diagrams/s05-secuencia-request.mmd` — el **ciclo de una request** de `POST /tasks/1/move`. En S03 dibujaste cliente → Uvicorn → router → handler; hoy la secuencia gana service y repository, y el primer `alt` con sentido.

**Ejemplo práctico: la secuencia de mover una tarea.**

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente (httpx)
    participant U as Uvicorn
    participant R as Router (tareas.py)
    participant S as Service (tarea_service.py)
    participant RP as Repositorio Tareas (memoria)

    C->>U: POST /tasks/1/move con estado "en progreso"
    U->>R: request ASGI
    Note over R: Pydantic valida el body<br/>(estado fuera del Enum: 422)
    R->>S: mover_tarea(1, EN_PROGRESO)
    S->>RP: obtener(1)
    RP-->>S: Tarea o None
    alt tarea no existe
        S-->>R: raise TareaNoEncontrada
        R-->>C: 404 Not Found
    else tarea existe
        S->>S: tarea.estado = EN_PROGRESO
        S->>RP: guardar(tarea)
        RP-->>S: Tarea actualizada
        S-->>R: Tarea
        R-->>U: 200 OK + JSON
        U-->>C: 200 OK + JSON
    end
```

*Por qué así:*
- **`actor` para el cliente y `participant` para el resto:** distingue quién inicia de quién responde.
- **Alias (`participant R as Router (tareas.py)`):** IDs cortos en el código, nombres legibles en el render, con el archivo para que el diagrama se pueda cruzar con el repo.
- **`autonumber`:** al discutir en clase decís "en el paso 6…" y todos miran lo mismo.
- **`alt` / `else`:** el 404 y el 200 en un solo diagrama, que no se desincroniza.
- **La nota del 422:** la validación del body ocurre *antes* de que tu función se ejecute; el service ni se entera. Es por eso que el 422 no aparece como un camino del service.
- **Flechas punteadas (`-->>`) para las respuestas:** convención de secuencia: sólida = llamada, punteada = retorno.

> 💡 El archivo del repo puede estar escrito con `graph TD` y etiquetas de flecha sin comillas: también es Mermaid válido. Lo que importa es que el diagrama coincida con el código. Una trampa conocida de la doc de Mermaid: la palabra `end` en minúscula dentro del texto de un nodo de flowchart rompe el diagrama.

**Errores comunes.**
- **Dibujar lo que debería ser y no lo que es.** Si el diagrama tiene una flecha service → Postgres, miente: hoy esa conexión no existe.
- **Diagramas que no se actualizan** cuando cambia el código. La regla del `CLAUDE.md`: se actualizan en la misma sesión.

**Para profundizar:** C4 model — *Component diagram*; Mermaid — *Flowcharts Syntax* y *Sequence diagrams*.

---

### 4.10 Bitácora de trade-offs

**Para qué.** Dentro de dos semanas nadie va a recordar por qué el endpoint es `POST .../move` y no `PATCH`. La bitácora guarda la decisión *y su porqué*, que es lo que vas a tener que defender. En la evaluación del módulo, la bitácora pesa por sí misma: se evalúa que veas y justifiques decisiones, no solo que funcione.

**La plantilla del repo** (`docs/trade-offs.md`, una entrada por decisión, la más reciente arriba, **sin numeración**):

```text
### [sXX] Título corto de la decisión
- **Fecha:** AAAA-MM-DD
- **Decisión:** qué se decidió, en una frase.
- **Alternativas consideradas:**
  - Opción A — ...
  - Opción B — ...
- **Elección:** cuál se eligió.
- **Por qué:** justificación.
- **Consecuencias / a revisar más adelante:** (opcional)
```

*Por qué así:* es el formato de decisión documentada que viste con los ADR de Nygard en MA·S05 (contexto, alternativas, decisión, consecuencias), aligerado para decisiones de prototipo. La serie numerada `ADR-NNN` arranca recién en S06, con `ADR-001` para la elección de base de datos.

**Las tres decisiones del prototipo:**

| Decisión | Alternativas | Elección y por qué | Consecuencia |
|---|---|---|---|
| Representación de entidades sin ORM | `@dataclass` de dominio + schemas Pydantic en el router vs Pydantic para todo | **Pydantic para todo:** menos código y menos mapeos; validación y serialización gratis | El dominio queda acoplado a Pydantic; `id` y `estado` son campos del body que el server ignora o fuerza. Revisar en S07 |
| Almacenamiento en memoria | `dict` indexado por id vs `list` | **`dict`:** buscar y actualizar por id directo; modela lo que hará Postgres buscando por clave primaria | El estado vive mientras corre el proceso; persistencia real en S07 |
| Endpoint para mover el estado | `PATCH /tasks/{tarea_id}` (update parcial, REST más "puro") vs `POST /tasks/{tarea_id}/move` (acción explícita, estilo RPC) | **`POST .../move`:** expresa directo la acción del tablero y es fácil de leer | Se aparta del estilo REST orientado a recursos; se revisa al diseñar el contrato en S09 |

**Ejemplo práctico: una entrada completa** (la de almacenamiento, redactada como la escribiría un equipo):

```markdown
### [s05] Almacenamiento en memoria (capa repository)
- **Fecha:** AAAA-MM-DD
- **Decisión:** guardar las tareas en un `dict[int, Tarea]` indexado por id, con el id asignado por el repositorio.
- **Alternativas consideradas:**
  - `list[Tarea]` — la más intuitiva, pero encontrar una tarea por id obliga a recorrer toda la lista.
  - `dict[int, Tarea]` — acceso directo por id; listar es `values()`.
- **Elección:** `dict` indexado por id.
- **Por qué:** los tres endpoints que operan sobre una tarea la buscan por id; además se parece al acceso por clave primaria que hará Postgres en s07.
- **Consecuencias / a revisar más adelante:** con `--reload` perdemos todas las tareas en cada cambio de código. El contador de ids no es seguro ante requests concurrentes; lo revisamos con la concurrencia de s07.
```

*Por qué así:* cada alternativa trae su costo, no solo su nombre; el "por qué" se apoya en un hecho del proyecto (los endpoints buscan por id), no en una preferencia; y la consecuencia nombra cuándo se revisa.

**Errores comunes.**
- **Copiar las entradas del repo de referencia.** Cada equipo redacta las suyas, con su fecha y su justificación.
- **Bitácora sin alternativa descartada.** "Elegimos `dict` porque es mejor" no es un trade-off.
- **Escribir la bitácora al final, de memoria.** Se escribe cuando se toma la decisión; el `CLAUDE.md` le pide al agente que la registre en el momento.



---

## 5. Guía práctica paso a paso

Partís del tag `bootstrap`: ya tenés `CLAUDE.md`, `sessions/s05.md`, la plantilla vacía de `docs/trade-offs.md`, `requirements.txt` sin paquetes y `.python-version` (3.12). Terminás con el tag `s05`: prototipo en capas, cliente, compose, dos diagramas y tres trade-offs.

**Prerrequisitos**
- Python 3.12, git y una cuenta de GitHub.
- Docker con Compose v2 (`docker compose`, con espacio).
- Claude Code (o Cursor) configurado, como en M07·S01.
- Tu equipo de trabajo y un repo vacío del equipo en GitHub.

**Placeholders a reemplazar:** `<URL-del-repo-del-equipo>` (la URL del repo vacío que creó tu equipo) y `AAAA-MM-DD` en la bitácora (la fecha de hoy).

#### Paso 1 — Armar el repo del equipo desde `bootstrap` (una sola persona)

```bash
git clone https://github.com/Luc5k4yw4lk3r/fastapi-full-v0.git
cd fastapi-full-v0
git checkout -b main bootstrap            # rama nueva main que arranca en el tag bootstrap
git remote set-url origin <URL-del-repo-del-equipo>
git push -u origin main
git push origin bootstrap                 # el protocolo del agente verifica que exista este tag
```

Después, el resto del equipo clona el repo del equipo (no el de referencia).
**Verificá:** `git log --oneline -1` muestra el commit de `bootstrap` y `git tag` lista `bootstrap`.

> ⚠️ No mires todavía el tag `s05` del repo de referencia: es la solución. Se revisa al final, para comparar.

#### Paso 2 — Entorno virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate               # Windows: .venv\Scripts\activate
```

**Verificá:** `python --version` muestra 3.12.

#### Paso 3 — Arrancar la sesión con el agente

Abrí Claude Code en plan mode y pegá el prompt de arranque de 4.2. **Verificá:** el agente leyó `sessions/s05.md`, comprobó el tag `bootstrap`, propuso un plan por capa y **se detuvo a esperar tu confirmación**. Si empezó a escribir código sin plan, cortalo y volvé a pedirlo.

Para cada decisión (representación de entidades, almacenamiento en memoria, cómo exponer "mover") exigí dos alternativas con su costo. Elegí y pedile que la registre en `docs/trade-offs.md`.

#### Paso 4 — Dependencias

`requirements.txt` al cierre de la sesión:

```text
# --- s05 ---
fastapi>=0.115
uvicorn[standard]>=0.30
httpx>=0.27
```

```bash
pip install -r requirements.txt
```

*Por qué así:* `fastapi` y `uvicorn[standard]` por separado (no `fastapi[standard]` como en S03): el repo declara cada dependencia en la sesión que la introduce, y así `requirements.txt` cuenta la historia del proyecto. `httpx` es dependencia directa porque lo usa `scripts/client.py`. **No** agregues `sqlalchemy` ni `psycopg`: son de S07.
**Verificá:** `pip list` muestra `fastapi`, `uvicorn` y `httpx`.

#### Paso 5 — Modelos, repositorios, service, cableado, router y app

Dejá que el agente los genere **en este orden**, de adentro hacia afuera, y revisá cada archivo contra las notas antes de pasar al siguiente:

| Orden | Archivo                                                          | Revisalo contra |
| ----- | ---------------------------------------------------------------- | --------------- |
| 1     | `app/models/estado.py`, `tarea.py`, `proyecto.py`                | 4.4             |
| 2     | `app/repositories/tarea_repository.py`, `proyecto_repository.py` | 4.5             |
| 3     | `app/services/tarea_service.py`                                  | 4.3 (ejemplo 1) |
| 4     | `app/dependencies.py`                                            | 4.3 (ejemplo 3) |
| 5     | `app/routers/tareas.py`                                          | 4.3 (ejemplo 2) |
| 6     | `app/main.py`                                                    | 4.6             |

*Por qué de adentro hacia afuera:* cada capa solo importa las de abajo, así que cada archivo nuevo se apoya en algo que ya existe y ya revisaste.

**Verificá en cada paso** (con preguntas, no solo leyendo):
- ¿`tarea_service.py` importa algo de `fastapi`? Tiene que ser **no**.
- ¿Algún archivo que no sea `dependencies.py` hace `RepositorioTareasEnMemoria()`? Tiene que ser **no**.
- ¿El agente te explicó cada archivo en 2-3 líneas? Si no, pedíselo: es una regla del `CLAUDE.md`.

Commit por avance coherente, por ejemplo:

```bash
git add app/
git commit -m "s05: agregar capas de tareas en memoria"
```

#### Paso 6 — Correr el servidor

```bash
uvicorn app.main:app --reload
```

**Verificá:**
- La terminal muestra que Uvicorn escucha en `http://127.0.0.1:8000`.
- `curl http://127.0.0.1:8000/health` responde `{"status":"ok"}`.
- En `http://127.0.0.1:8000/docs` ves `POST /tasks`, `GET /tasks`, `POST /tasks/{tarea_id}/move` y `GET /health`; en el body de `move`, el desplegable de `estado` muestra `backlog`, `en progreso` y `hecho`.
- Desde Swagger, `POST /tasks/999/move` responde 404 y un estado `"terminado"` responde 422.

#### Paso 7 — Cliente `httpx`

Pedile al agente `scripts/client.py` (4.7). En **otra** terminal, con el server levantado:

```bash
python scripts/client.py
```

**Verificá:** ves `{'status': 'ok'}`, dos tareas creadas con `'estado': 'backlog'`, la primera movida a `'en progreso'` y el listado final con ese cambio. Ninguna línea con `'detail'`.

#### Paso 8 — Postgres en Docker (puede hacerlo otra persona del equipo en paralelo)

Pedile al agente `docker-compose.yml` y `.env.example` (4.8) y confirmá que `.gitignore` incluye `.env`.

```bash
cp .env.example .env
docker compose up -d
docker compose ps
docker exec -it taskflow-db psql -U taskflow -d taskflow -c "select version();"
```

**Verificá:** `docker compose ps` muestra `taskflow-db` con STATUS *healthy* (puede tardar unos segundos; repetí el comando), y `psql` imprime una versión de PostgreSQL 16. `git status` **no** muestra `.env`.

Si el puerto 5432 está ocupado: `POSTGRES_PORT=5433` en `.env`, el mismo puerto en `DATABASE_URL`, y `docker compose up -d` de nuevo.

#### Paso 9 — Diagramas

Pedile al agente (o escribí vos) `docs/diagrams/s05-componentes.mmd` y `docs/diagrams/s05-secuencia-request.mmd` (4.9). **Verificá:** cada caja del diagrama de componentes corresponde a un archivo que existe; la flecha hacia Postgres es punteada; la secuencia tiene el `alt` 404 / 200. Pegá cada diagrama en un visor de Mermaid (o la vista previa de tu editor) para confirmar que renderiza.

#### Paso 10 — Bitácora

Revisá que `docs/trade-offs.md` tenga las tres entradas `[s05]` con alternativa descartada, porqué y consecuencia, **redactadas por tu equipo** (4.10).

#### Paso 11 — Cierre de sesión

Escribile al agente: **"cerramos la sesión"**. Tiene que verificar los entregables de `sessions/s05.md`, hacer el commit final y crear el tag `s05`. Después:

```bash
git push origin main
git push origin s05
```

**Verificá el entregable completo:**
- [ ] `uvicorn app.main:app --reload` levanta y `python scripts/client.py` recorre `/health` + los tres endpoints sin errores.
- [ ] `docker compose ps` muestra `taskflow-db` *healthy*.
- [ ] `docs/diagrams/s05-componentes.mmd` y `docs/diagrams/s05-secuencia-request.mmd` existen y coinciden con el código.
- [ ] `docs/trade-offs.md` tiene 3 entradas `[s05]` con fecha de tu equipo.
- [ ] Commits con prefijo `s05:` y tag `s05` en el repo del equipo.

Recién ahora, compará con el tag `s05` del repo de referencia (`git fetch` del repo de referencia o miralo en GitHub): las diferencias de nombres internos son normales; las de capas, no.



---

## 6. Checklist de autoevaluación

- [ ] Puedo explicar qué es TaskFlow, qué no es, y por qué hoy tiene solo `Tarea` y `Proyecto` en memoria, sin mirar los apuntes.
- [ ] Puedo explicar qué hace el protocolo "arrancamos la sesión s05" y por qué el agente necesita una verificación que pueda correr.
- [ ] Puedo decir en qué capa vive cada archivo del prototipo y qué no puede importar.
- [ ] Puedo explicar por qué el service lanza `TareaNoEncontrada` y no `HTTPException`.
- [ ] Puedo explicar por qué `app/dependencies.py` crea las instancias a nivel de módulo, y qué pasa si no.
- [ ] Puedo predecir el código de respuesta (201, 200, 404 o 422) de cualquier request a los tres endpoints.
- [ ] Puedo explicar qué pasa con las tareas cuando `--reload` reinicia el servidor, y por qué.
- [ ] Puedo explicar cada línea del servicio `db` de `docker-compose.yml`, incluida la trampa de las variables de inicialización.
- [ ] Puedo dibujar de memoria la secuencia de `POST /tasks/1/move` con sus caminos 404 y 200.
- [ ] Puedo defender las tres decisiones `[s05]` de la bitácora con su alternativa descartada y su consecuencia.

---

## 7. Preguntas de repaso

1. En TaskFlow, la persistencia pasa de memoria a PostgreSQL en S07 "tocando solo el cableado". ¿Qué decisiones de diseño de hoy hacen posible esa promesa, y cuál de ellas sería la primera en romperla si se hiciera distinto?
2. El endpoint para mover una tarea es `POST /tasks/{tarea_id}/move` y no `PATCH /tasks/{tarea_id}`. Defendé la elección y después atacala: ¿qué gana y qué pierde un cliente de la API con cada opción?
3. Hoy `mover_tarea` acepta cualquier transición de estado. Si tuvieras que agregar la regla, ¿en qué capa viviría, cómo la expresarías y qué código HTTP devolverías? ¿Qué cambiaría si mañana existiera un segundo cliente (un script de seed) que también mueve tareas?
4. Tu prototipo usa una sola clase Pydantic `Tarea` para entrada, dominio y respuesta. Contá un escenario concreto en el que esa decisión empiece a doler y qué cambiarías.
5. Un compañero dice: "levantar Postgres hoy es una pérdida de tiempo, la app ni lo usa". ¿Qué le contestás? Incluí qué verificaste hoy del compose y qué riesgos de S07 ya quedaron resueltos.

---

## 8. Recursos adicionales

### Imprescindibles
- [Repositorio de referencia `fastapi-full-v0`](https://github.com/Luc5k4yw4lk3r/fastapi-full-v0) — el punto de partida (`bootstrap`) y la solución (`s05`). Explorá README, `CLAUDE.md` y `sessions/s05.md`.
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) — verificación ejecutable, explore → plan → code, qué va en un `CLAUDE.md`.
- [FastAPI — Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/) — la forma de `app/routers/` y `include_router`.
- [Docker — Define services in Docker Compose](https://docs.docker.com/reference/compose-file/services/) — cada clave del servicio `db` (healthcheck, ports, volumes, restart, container_name).
- [postgres — Docker Official Image](https://hub.docker.com/_/postgres) — variables de entorno, PGDATA y la advertencia sobre el directorio de datos vacío.

### Recomendados
- Andrew Ng, *AI Engineering Skills Map: Software engineering fundamentals* (2026), secciones *Managing data* y *Designing system architectures* — biblioteca del curso.
- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) — repaso de `Depends`.
- [FastAPI — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — `HTTPException` y el 422 automático.
- [FastAPI — Path Parameters (valores predefinidos)](https://fastapi.tiangolo.com/tutorial/path-params/) — el patrón `class Estado(str, Enum)`.
- [FastAPI — Response Model - Return Type](https://fastapi.tiangolo.com/tutorial/response-model/) — qué filtra `response_model`.
- [HTTPX — QuickStart](https://www.python-httpx.org/quickstart/) — `json=`, `raise_for_status()`, timeouts.
- [HTTPX — Clients](https://www.python-httpx.org/advanced/clients/) — `Client`, context manager y `base_url`.
- [Docker — Variable interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) — `.env` y `${VAR:-default}`.
- [The Twelve-Factor App — III. Config](https://12factor.net/config) — config en variables de entorno.
- [C4 model — Component diagram](https://c4model.com/diagrams/component) — qué va en el diagrama de componentes.
- [Mermaid — Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html) — `alt`, alias, `autonumber`.

### Opcionales
- [FastAPI — Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/) — `status.HTTP_201_CREATED` y compañía.
- [Uvicorn — Settings](https://uvicorn.dev/settings/) — host, puerto, `--reload` y `--workers`.
- [Docker — How Compose works](https://docs.docker.com/compose/intro/compose-application-model/) — servicio, volumen, proyecto.
- [Docker — docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/) — `-d` y `--wait`.
- [PostgreSQL 16 — pg_isready](https://www.postgresql.org/docs/16/app-pg-isready.html) — los códigos de salida.
- [Mermaid — Flowcharts Syntax](https://mermaid.js.org/syntax/flowchart.html) — `subgraph`, flechas punteadas y la trampa de `end`.
