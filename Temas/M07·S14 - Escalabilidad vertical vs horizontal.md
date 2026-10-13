# M07·S14 — Escalabilidad vertical vs horizontal 

**Módulo:** 07 — Fundamentos de Software + System Design para AI Engineers
**Sesión:** 14 de 22 · **semana 3** (arquitectura, escalabilidad, seguridad y confiabilidad) · ritmo pausado
**Fecha:** [Completar por el profesor: fecha]
**Duración de la clase:** 3 h · **sin lab nuevo**: el foco es entender y dibujar
**Duración estimada de estudio:** ~3 h 30 min (lectura de notas ~70 min · recursos originales ~110 min · ejercicios ~60 min)

---

## 1. De qué va esta sesión

En **M07·S13** dibujaste la arquitectura de tu sistema "para 100k usuarios", pero el taller se cortó justo antes del escalado: los balanceadores y las réplicas quedaron marcados como pregunta abierta. Hoy abrimos esa pregunta.

El tema tiene dos direcciones y las dos son fáciles de enunciar: **scale up** es poner una máquina más grande; **scale out** es poner más máquinas iguales repartiéndose el trabajo. Lo difícil —y lo que se lleva el alumno— es saber en qué escalón estás, qué síntoma te empuja al siguiente, y qué pagás en cada paso. Por eso la sesión es casi toda pizarra: vamos a **evolucionar un diagrama** desde single server hasta una arquitectura escalada, escribiendo en cada flecha qué gano, qué pago y qué lo dispara.

> ⚠️ **Lo que hoy NO se responde.** Los algoritmos del load balancer, las health checks y la eliminación del SPOF con redundancia son **S15**: hoy el balanceador y el SPOF se **nombran** donde el escalado los necesita, sin entrar en detalle. El manejo de fallos de una dependencia caída, lenta o rate-limiteada —reintentos, timeouts, degradación elegante— es **S16**: acá el rate limit aparece como **límite de escalado**, no como falla a manejar. Sharding, indexing y replicación de la base son **S21**. Y la granularidad (monolito vs microservicios) ya se discutió en S13 y no se vuelve a abrir.

---

## 2. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

1. **Medir** la carga de un sistema con el vocabulario correcto —carga, capacidad, latencia en percentiles, throughput y disponibilidad— y explicar por qué el promedio de latencia engaña.
2. **Explicar** cuándo el scale up (vertical) es la jugada correcta y nombrar sus dos límites reales: el techo físico y el punto único de falla.
3. **Justificar** el scale out (horizontal) con la aritmética de la disponibilidad: calcular qué aporta una caja redundante y qué le resta una dependencia dura nueva.
4. **Identificar** qué estado hay que sacar de un servidor para que cualquier instancia pueda atender cualquier request, y elegir adónde moverlo.
5. **Diagnosticar** el cuello de botella antes de escalar, y argumentar por qué agregar réplicas puede no mejorar nada (o empeorarlo).
6. **Evolucionar y defender** en pizarra el diagrama de una arquitectura desde single server hasta una arquitectura escalada, escribiendo en cada paso qué gano, qué pago y qué síntoma lo dispara —incluido el caso de una app que llama a una LLM API, donde el techo suele estar en el proveedor.

---

## 3. Resumen ejecutivo

En **M07·S01** arrancaste la bitácora de trade-offs con la idea de que el salto de mid a senior es poder decir *por qué esto y no aquello*. En **S02** dibujaste el single server y viste qué es el estado y dónde vive; en **S04** cortaste el webserver en capas y conociste el caso I/O-bound de la llamada a un modelo; en **S05–S07** llevaste los datos a PostgreSQL; en **S09** viste colas, WebSockets y `202 Accepted`; en **S13** convertiste un contexto en una arquitectura. Hoy esa arquitectura **crece**.

Tres ideas sostienen la clase:

1. **Scale out no es "sumar servidores": es sacar el estado de los servidores.** Mientras una instancia recuerde algo que las otras no saben, no tenés dos servidores: tenés uno y un problema.
2. **Escalar la cosa equivocada no sirve.** Si el cuello de botella es la base de datos, más web servers no ayudan — y el cuello **se muda** a medida que escalás.
3. **La redundancia se paga en complejidad y se cobra en disponibilidad** — y esa disponibilidad se calcula. Con dos fórmulas (dependencias duras y componentes redundantes) podés discutir un diagrama con números en vez de con gustos.

Para el rol de AI Engineer hay un cuarto hilo propio: en una app que llama a un modelo, **el techo frecuentemente no es tu CPU, es el proveedor**. Los rate limits son de tu organización, no de tu servidor, así que diez réplicas comparten la misma cuota. Ahí las palancas cambian: caching, repartir entre modelos, colas y batches, y un **model gateway** como última caja del diagrama.

No hay lab nuevo. Hay pizarra, aritmética, tres demos de cinco minutos y una entrada en la bitácora de trade-offs.

---

## 4. Conceptos clave / glosario

### Bloque A — Medir antes de escalar

| Término | Qué es, para qué se usa y por qué así |
|---|---|
| **Carga** | El trabajo que le llega al sistema por unidad de tiempo (requests por segundo, tokens por minuto, usuarios concurrentes). **Para qué:** es la variable independiente de toda discusión de escalado; sin carga declarada, "escala" no significa nada. **Por qué así:** se mide siempre en el pico y no en el promedio, porque el sistema se cae en el pico. |
| **Capacidad** | La carga máxima que el sistema aguanta **antes de degradarse** (no antes de caerse). **Para qué:** es el número contra el que se compara la carga para decidir si hay que escalar. **Por qué así:** se define contra un umbral de calidad (latencia aceptable), no contra el punto de ruptura: un sistema "que todavía responde" en 40 segundos ya está fuera de capacidad. |
| **Latencia** | El tiempo que pasa entre que un cliente manda un request y recibe la respuesta. Es una **distribución**, no un número. **Para qué:** es lo que siente el usuario. **Por qué en percentiles:** el promedio lo arruina un solo outlier, y el usuario no vive en el promedio. |
| **Percentil (p50, p90, p95, p99)** | El valor por debajo del cual cae ese porcentaje de los requests: p95 = 1.200 ms significa que 95 de cada 100 requests tardaron menos que eso. **Para qué:** describir la cola de la distribución, que es donde viven los usuarios enojados. **Por qué así:** porque "promedio 390 ms" puede ser un servicio que responde en 100 ms y una vez cada diez se cuelga tres segundos. |
| **TTFT** (*time to first token*) | En una respuesta en streaming de un modelo, el tiempo hasta el primer token. **Para qué:** es la latencia *percibida* de un chat; el total importa menos si el texto ya empezó a aparecer. **Por qué así:** medir solo el tiempo total esconde la única parte que el usuario mira de entrada. |
| **Throughput** | Trabajo completado por unidad de tiempo: requests por segundo, o —cuando cada request tarda segundos porque espera a un modelo— **requests completados por minuto (RPM)**. **Para qué:** es lo que escalás cuando agregás recursos. **Por qué en RPM:** con foundation models un request puede durar segundos, así que "por segundo" da números menores a 1 y deja de ser legible. |
| **Goodput** | Los requests por unidad de tiempo que **cumplen el objetivo de latencia**, no los que simplemente terminan. **Para qué:** distinguir "atender más" de "atender bien". **Por qué así:** es el antídoto contra el reflejo de celebrar el throughput: podés duplicar requests atendidos y empeorarle la experiencia a todos. |
| **Disponibilidad** | El porcentaje del tiempo (sobre un período: mes, año) en que el sistema está disponible para usarse. **Para qué:** convertir "queremos que no se caiga" en un número discutible. **Por qué así:** porque sin objetivo numérico un diagrama de redundancia no tiene criterio de parada —siempre se puede agregar una caja más. |
| **"Los nueves"** | La forma corta de nombrar objetivos de disponibilidad: 99 %, 99,9 %, 99,99 %. Cada nueve extra divide el tiempo caído permitido. **Para qué:** traducir el objetivo a una ventana de caída tolerable. **Por qué así:** es más honesto discutir "¿aceptamos 8 horas caídos por año?" que "¿queremos alta disponibilidad?". |
| **Dependencia dura** | Un componente sin el cual tu servicio **no puede responder** (la base de datos de la que lee cada request). Su contracara es la dependencia blanda: si se cae, degradás pero seguís. **Para qué:** saber qué multiplica tu disponibilidad y qué no. **Por qué importa:** cada dependencia dura nueva **baja** el techo de disponibilidad del conjunto, aunque la hayas agregado "para mejorar la arquitectura". |

### Bloque B — Las dos direcciones del escalado

| Término | Qué es, para qué se usa y por qué así |
|---|---|
| **Scale up / escalado vertical** | Darle más recursos a la misma máquina: más CPU, más RAM, disco más rápido. **Para qué:** ganar capacidad **sin tocar una línea de código**. **Por qué es el primer paso razonable:** no agrega ningún componente nuevo ni ninguna complejidad operativa, y es la única jugada que no exige que la app esté preparada. |
| **Scale out / escalado horizontal** | Poner más máquinas iguales que se reparten la carga. **Para qué:** ganar capacidad y, sobre todo, **redundancia**. **Por qué así:** no tiene el techo del vertical, pero exige que la app cumpla una condición previa (ser stateless) y que haya algo que reparta el tráfico. |
| **Escalabilidad** | La relación entre la ganancia de throughput y el aumento de recursos: idealmente, duplicar recursos duplica el throughput. **Para qué:** medir si el escalado te está rindiendo. **Por qué así:** definirla como relación (y no como "aguanta mucho") deja ver que la pendiente puede ser menor que 1 —y que a veces es negativa. |
| **Contención** | La demora por esperar o encolarse para usar un recurso compartido (la base, un lock, el disco). **Para qué:** explicar por qué la réplica número 10 aporta menos que la número 2. **Por qué este nombre:** separa el problema "hay cola para entrar" de la otra fuente de pérdida, que es la coherencia. |
| **Coherencia** | La demora que cuesta poner los datos consistentes entre copias. **Para qué:** explicar el costo oculto de tener estado replicado. **Por qué así:** junto con la contención es lo que se come la ganancia del scale out, y modelarla es lo que hace la **ley de Amdahl**. |
| **Punto único de falla (SPOF)** | Un componente cuya caída tira el sistema entero porque no tiene reemplazo. **Para qué:** encontrar en el diagrama la caja que no puede faltar. **Por qué así:** es un atributo del *diagrama*, no del hardware: lo detectás tapando cada caja con el dedo y preguntando "¿sigue funcionando?". *(Eliminarlo con redundancia es tema de M07·S15; hoy lo nombramos y lo dibujamos.)* |
| **Dominio de falla** | El alcance de lo que se cae junto: un proceso, una máquina, una zona, una región. **Para qué:** decidir *cuán separadas* tienen que estar las réplicas. **Por qué así:** dos réplicas en la misma máquina te protegen de un crash del proceso, no de que se caiga la máquina; dos máquinas en la misma zona no te protegen de la zona. |
| **Load balancer** | El componente que recibe el tráfico y lo reparte entre las instancias. **Para qué:** darle una sola puerta de entrada a N réplicas. **Por qué se nombra hoy y se estudia en S15:** sin él el scale out no se puede dibujar, pero sus algoritmos y sus health checks son el tema de la sesión que viene. |
| **Autoscaling** | Agregar o quitar instancias automáticamente según una métrica (CPU, largo de la cola) o un calendario. **Para qué:** seguir la curva de carga sin alguien mirando un panel. **Por qué requiere stateless:** si la instancia que el autoscaler apaga tenía datos en memoria, el autoscaling destruye trabajo. *(Las métricas y alertas que lo disparan son de M07·S20.)* |
| **Scale in** | La mitad que se olvida del elástico: retirar instancias. **Para qué:** bajar costo cuando la carga baja. **Por qué hay que diseñarlo:** una instancia se puede apagar **a mitad de un trabajo**, así que hace falta apagado limpio, reintentos del cliente, checkpoints o trabajo encolado para que otra lo retome. |

### Bloque C — Lo que se complica: el estado

| Término | Qué es, para qué se usa y por qué así |
|---|---|
| **Stateless** (servicio) | Un servicio que no retiene datos ni estado persistente local: todo lo que necesita viene en el request o lo lee de un backing service. **Para qué:** poder agregar, quitar y reiniciar instancias sin perder el trabajo en vuelo. **Por qué es la condición del scale out:** es lo que permite que *cualquier* instancia atienda *cualquier* request. |
| **Share-nothing** | Los procesos no comparten memoria ni disco entre sí. **Para qué:** que una instancia no dependa de lo que otra tenga cargado. **Por qué así:** el disco local y la memoria sirven como caché de una sola transacción, pero la app nunca puede asumir que eso va a estar en un request futuro. *(Factor VI de 12-Factor, visto en M07·S02.)* |
| **Backing service** | Un servicio externo con estado del que la app depende por la red: base de datos, cache, cola, session store. **Para qué:** darle un lugar al estado que la app no puede guardar. **Por qué así:** convierte el estado en una dependencia explícita, configurable por entorno, en vez de un detalle invisible dentro del proceso. |
| **Session affinity / sticky sessions** | Que el balanceador mande siempre los requests de un mismo cliente al mismo servidor. **Para qué (según quien la usa):** hacer funcionar una app que guarda sesión en memoria sin reescribirla. **Por qué se evita:** limita el escalado (el tráfico de un usuario pesado no se distribuye) y vuelve costoso agregar, quitar o perder servidores. 12-Factor es terminante: *"Sticky sessions are a violation of twelve-factor and should never be used or relied upon"*. |
| **Session store** | Un datastore compartido donde vive el estado de sesión, típicamente con expiración por tiempo (Memcached o Redis son los candidatos que menciona 12-Factor). **Para qué:** sacar la sesión del proceso sin perderla. **Por qué con expiración:** el estado de sesión es naturalmente temporal; dejarlo en una tabla sin TTL es acumular basura para siempre. |
| **Cookie firmada** | La otra salida al problema de la sesión: el estado viaja con el cliente en una cookie que el servidor **firma** para detectar manipulación. **Para qué:** quedarte sin session store y aun así ser stateless. **Por qué "firmada" y no "cifrada":** la firma garantiza que el cliente no la modifique, pero el contenido es legible — ahí no va nada sensible. |
| **Pooler de conexiones** | Un intermediario que mantiene un puñado de conexiones a la base y las presta a muchos clientes. **Para qué:** desacoplar "cuántas réplicas tengo" de "cuántas conexiones abre mi base". **Por qué aparece solo:** cuando multiplicás réplicas, multiplicás pools, y el límite de conexiones de la base se agota antes que su CPU. *(El detalle de escalar la capa de datos es de M07·S21.)* |
| **Cuello de botella** | El recurso que primero se satura y fija la capacidad del conjunto. **Para qué:** saber qué escalar. **Por qué importa el "solo uno":** escalar cualquier otra cosa no mueve la aguja, y en un sistema con estado **las partes con estado son el candidato más probable**. |

### Bloque D — Cuando el techo es de otro

| Término | Qué es, para qué se usa y por qué así |
|---|---|
| **Rate limit** | El tope de uso que el proveedor de una API te impone por unidad de tiempo. **Para qué (de su lado):** proteger el servicio compartido. **Por qué te condiciona:** se fija a nivel de **organización** (y de proyecto o workspace), no por servidor ni por usuario, así que no crece porque agregues réplicas. |
| **RPM / ITPM / OTPM** | Requests por minuto, tokens de entrada por minuto, tokens de salida por minuto. **Para qué:** saber qué métrica te va a frenar primero. **Por qué varias:** se alcanza el límite con la que llegue primero, y en apps con prompts largos casi nunca es la de requests. |
| **Token bucket** | El algoritmo con el que se implementan esos límites: un balde de capacidad que se **repone continuamente** en vez de resetearse en intervalos fijos. **Para qué:** tolerar ráfagas cortas sin abrir la puerta a un pico sostenido. **Por qué importa saberlo:** explica que no exista un "minuto cero" al que esperar, y que convenga subir el tráfico de a poco. |
| **429 vs 529** | **429** (`rate_limit_error`) = **tu** organización llegó a su límite (de tasa o de gasto). **529** (`overloaded_error`) = la API está temporalmente sobrecargada, algo que puede pasar con tráfico alto de todos los usuarios. **Para qué:** no confundir "me pasé yo" con "le pasó al proveedor". **Por qué así:** la respuesta correcta es distinta, y ninguna de las dos se arregla escalando tu webserver. |
| **Backoff exponencial con jitter** | Reintentar esperando cada vez más, con una demora aleatoria agregada. **Para qué:** no volver a pegarle todos juntos al servicio que ya dijo que no. **Por qué con jitter:** sin aleatoriedad, todos los clientes reintentan en el mismo instante y reconstruyen el pico que causó el 429. *(El manejo de fallos completo es de M07·S16.)* |
| **Model gateway** | Una capa propia entre tu backend y los modelos, con interfaz unificada para varios proveedores. **Para qué:** un solo lugar donde ver la cuota, cachear, repartir entre modelos, loguear y aplicar fallbacks. **Por qué así:** en su forma más simple es un wrapper con una función por proveedor y un endpoint que despacha; si una API cambia, se actualiza un solo lugar. |

> 💡 Si un término te suena de antes, es porque lo es: `stateless`, `share-nothing` y backing service se vieron en **M07·S02**; `SessionMiddleware`, caching e I/O-bound en **M07·S04**; colas y `202 Accepted` en **M07·S09**; el formato de la bitácora de trade-offs, en **M07·S01**. Hoy todos vuelven con una pregunta nueva: *¿y si hay dos copias del servidor?*

---

## 5. Notas de estudio por subtema

### El diagrama ancla: los siete escalones

Todo lo que sigue cuelga de este diagrama. No es una receta a aplicar entera: es el **orden en que los problemas aparecen**, y la gracia es saber en qué escalón estás y qué síntoma te empuja al siguiente.

```mermaid
flowchart LR
    P1["1 · Single server"] --> P2["2 · Separar la base"]
    P2 --> P3["3 · Scale up"]
    P3 --> P4["4 · Sacar el estado"]
    P4 --> P5["5 · N replicas + load balancer"]
    P5 --> P6["6 · Cola + workers"]
    P6 --> P7["7 · Gateway al modelo"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class P4 foco
```

El escalón 4 está resaltado porque es la bisagra: **es el único que no agrega hardware y sin el cual los tres siguientes no funcionan.** Los escalones 1 a 5 son de esta sesión; el load balancer en detalle es de **M07·S15**, las réplicas y el sharding de la base son de **M07·S21**, y el manejo de fallos del proveedor es de **M07·S16**.

El caso que vamos a usar en todos los ejemplos es genérico a propósito: una **API de soporte interno**, hecha con FastAPI, con PostgreSQL y una llamada a una LLM API para redactar el borrador de respuesta a cada ticket. Es el stack que ya construiste en S03–S07, más la pieza de IA.

---

### 5.1 Vocabulario mínimo para decidir

**El problema que resuelve.** Toda discusión de escalado sin números termina en opiniones: "está lento", "aguanta poco", "hay que meterle más máquina". El vocabulario de este subtema es lo que convierte esa charla en una decisión: cuánta carga hay, cuánta capacidad tenemos, qué latencia aceptamos y qué disponibilidad nos comprometimos a dar.

**Carga, capacidad y latencia no son lo mismo.** Son tres preguntas distintas:

- **Carga** → ¿cuánto trabajo llega? (y, sobre todo, cuánto llega en el pico)
- **Capacidad** → ¿cuánto trabajo aguantamos antes de degradarnos?
- **Latencia** → ¿cuánto espera *un* usuario?

Confundirlas produce decisiones malas. Un sistema puede tener capacidad de sobra y latencia terrible (cada request hace tres queries lentas, pero entran mil en paralelo), o latencia excelente y capacidad mínima (responde en 20 ms hasta que llegan 50 usuarios juntos). **Escalar arregla capacidad, no latencia:** si un request tarda 4 segundos porque espera a un modelo, con diez réplicas va a seguir tardando 4 segundos.

**La latencia es una distribución, y el promedio miente.** El ejemplo clásico: diez requests con TTFT de 100, 102, 100, 100, 99, 104, 110, 90, **3.000** y 95 ms. El promedio es **390 ms**, un número que no describe a ninguno de los diez: hace parecer al servicio mucho más lento de lo que es, cuando lo que hay es un outlier. Por eso se mira **p50, p90, p95 y p99** (Huyen, *AI Engineering*, cap. 9).

```python
# Percentiles a mano, con el método de rango más cercano (nearest-rank):
# el p-ésimo percentil es el valor en la posición ceil(p/100 * n) de la lista ordenada.
import math

ttft_ms = [100, 102, 100, 100, 99, 104, 110, 90, 3000, 95]

def percentil(muestras, p):
    ordenadas = sorted(muestras)
    # ceil en vez de round: el p95 tiene que dejar *al menos* el 95 % por debajo.
    # Si redondeáramos, con pocas muestras el p95 se correría hacia el p90 y
    # esconderíamos justo la cola que queremos ver.
    k = max(1, math.ceil(p / 100 * len(ordenadas)))
    return ordenadas[k - 1]

print(sum(ttft_ms) / len(ttft_ms))   # 390.0  <- el promedio, inútil acá
print(percentil(ttft_ms, 50))        # 100
print(percentil(ttft_ms, 90))        # 110
print(percentil(ttft_ms, 95))        # 3000  <- con 10 muestras, el p95 *es* el outlier
```

**Por qué así.** Calcular percentiles sobre diez muestras es una trampa pedagógica útil: el p95 de diez requests es literalmente el peor o el segundo peor. Para que un p95 signifique algo necesitás cientos o miles de muestras de la misma ventana de tiempo. La alternativa que se descarta es reportar promedio y máximo: el promedio esconde la cola y el máximo es un solo evento, posiblemente un timeout de red.

**Throughput y goodput.** Throughput es trabajo completado por unidad de tiempo. En apps de IA se mide muchas veces en **RPM** (requests completados por minuto) porque un request puede durar segundos, y hay un trade-off conocido con la latencia: el **batching** mejora el throughput y empeora la latencia de cada request individual. El **goodput** agrega el filtro que importa: cuántos de esos requests cumplieron el objetivo de latencia. Es el mejor argumento contra "agregamos réplicas y listo" — podés subir el throughput y bajar el goodput.

**Disponibilidad: el número que hace discutible todo el diagrama.** Disponibilidad es el porcentaje de tiempo en que el sistema está disponible, calculado sobre un período. Y la traducción a tiempo caído es la tabla que conviene tener pegada en la pared:

| Objetivo | Indisponibilidad máxima por año |
|---|---|
| 99 % | 3 días 15 horas |
| 99,9 % | 8 horas 45 minutos |
| 99,95 % | 4 horas 22 minutos |
| 99,99 % | 52 minutos |
| 99,999 % | 5 minutos |

*(Tabla de la sección Availability del Reliability Pillar de AWS Well-Architected; coincide con la Availability Table del Apéndice A del SRE Book de Google, que la da desde 90 % y por año, trimestre, mes, semana, día y hora, asumiendo que no hay downtime planificado.)*

Dos refinamientos que cambian cómo se usa:

- **No excluyas el mantenimiento planificado** del tiempo total. AWS lo dice explícitamente, y el argumento es del usuario: va a querer usar el servicio también durante tu ventana de mantenimiento. Esto le pone precio al reinicio del scale up.
- **Para servicios que se caen parcialmente** —solo algunas réplicas, o carga que varía a lo largo del día— suele ser más útil una métrica agregada por **operaciones**: respuestas exitosas sobre requests válidos. Con N réplicas las caídas dejan de ser binarias, y medir en minutos caídos deja de describir lo que pasó.

> ⚠️ Pedir "cinco nueves" porque suena bien es el error más caro de la sesión. Diseñar para disponibilidades más altas aumenta el costo: exige testing y validación exhaustivos ante fallas, automatizar la recuperación, y **restringe el conjunto de dependencias que podés elegir** (no podés apoyarte en algo menos disponible que tu objetivo). A disponibilidades muy altas hasta la innovación se resiente, porque hay que desplegar más despacio.

**Gotchas del subtema**

- Decir "latencia: 200 ms" sin decir el percentil ni la ventana de medición. Siempre `p95 en la última hora`.
- Medir la latencia del servidor y creer que es la del usuario: faltan DNS, TLS, red y render (todo eso lo recorriste en **M07·S02**).
- Comprometer un SLO sin mirar las dependencias: tu objetivo no puede ser mejor que el de las cosas de las que dependés duro.

**Para profundizar:** [Availability Table — Google SRE Book, Apéndice A](https://sre.google/sre-book/availability-table/) · [Availability — AWS Well-Architected, Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/availability.html)

---

### 5.2 Scale up (vertical): el default honesto, con fecha de vencimiento

**El problema que resuelve.** La carga creció y hay que atenderla **esta semana**, sin reescribir la app ni introducir tres componentes nuevos. El scale up es, para eso, la respuesta correcta —y hay que decirlo sin culpa: *no* es el error del principiante.

**Por qué es el primer paso razonable.** Tres razones, en orden de peso:

1. **Cero cambios de código.** Una instancia más grande corre el mismo binario. No hay que volver stateless nada, no hay que coordinar nada.
2. **Cero complejidad nueva.** El diagrama sigue teniendo las mismas cajas. No hay un balanceador nuevo que configurar, ni una cache que invalidar, ni un session store que se pueda caer.
3. **Es la única jugada que no exige preparación previa.** El scale out requiere que la app ya cumpla una condición (stateless). El scale up no requiere nada.

**Lo que se paga: el reinicio.** La máquina más grande no aparece en caliente. En Compute Engine, por ejemplo, el tipo de máquina de una instancia se puede cambiar **después de detenerla**; el procedimiento vale para las series de primera y segunda generación (con exclusiones), las instancias bare metal no admiten el cambio, y si la VM pertenece a un managed instance group, detenerla puede provocar que se recree. Es **un** proveedor y **un** camino —otros admiten resize en caliente con límites—, pero el punto pedagógico queda: el scale up se cobra en una **ventana de mantenimiento**.

Y no pasa solo arriba del stack. En PostgreSQL, `max_connections` tiene como default **típicamente 100** conexiones (puede ser menos según lo que soporte el kernel, determinado en `initdb`) y **solo se puede fijar al arrancar el servidor**; el motor dimensiona recursos como la memoria compartida en función de ese valor. Es decir: subirle el techo de conexiones a tu base también es un reinicio.

```bash
# Scale up de la base: mirar el techo actual antes de tocar nada.
# `SHOW` lee el valor efectivo; `max_connections` no se puede cambiar en caliente,
# así que este número es un dato de diseño, no un parámetro que se ajusta en el momento.
docker compose exec db psql -U postgres -c "SHOW max_connections;"
```

**Por qué así:** la alternativa sería "lo subo cuando haga falta", y justamente eso es lo que la doc no permite — hacen falta un cambio de configuración y un reinicio del servidor, o sea una ventana de indisponibilidad planificada, de las que no conviene excluir del cálculo de disponibilidad.

**Los dos límites reales.** El scale up se termina por dos razones, y solo una es la que todo el mundo nombra:

- **Techo físico.** No se puede agregar CPU y memoria sin límite a un solo servidor. Tarde o temprano no hay instancia más grande, o la que hay no te sirve.
- **Punto único de falla.** Y este es el límite que llega **antes**: un servidor único no tiene failover ni redundancia, así que si falla, el servicio se cae por completo. Da igual cuán grande sea la máquina. La máquina más grande del catálogo con un solo nodo sigue teniendo una disponibilidad acotada por la de ese nodo.

> 💡 El criterio práctico: **el scale up se te termina por el SPOF, no por el techo.** El día en que "reiniciar para deployar" o "un crash del proceso" ya no sean aceptables, necesitás una segunda caja — y para eso necesitás el escalón 4.

**Gotchas del subtema**

- Escalar vertical **antes de perfilar**: una query sin índice no se arregla con el doble de CPU, se arregla con el índice. Medí primero.
- Olvidar que la ventana de mantenimiento cuenta contra tu disponibilidad.
- Suponer que la curva de precio tiene una forma determinada: el costo del vertical depende del proveedor y del tamaño. Su problema definitivo no es el precio, es el techo y el dominio de falla.

**Para profundizar:** [Change the machine type of a stopped VM — Compute Engine](https://docs.cloud.google.com/compute/docs/instances/changing-machine-type-of-stopped-instance) · [Connection Settings — PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-connection.html)

---

### 5.3 Scale out (horizontal): la disponibilidad se calcula

**El problema que resuelve.** Necesitás dos cosas que el vertical no da: **capacidad que no tope** y **redundancia**, o sea seguir funcionando cuando una caja se muere.

**Redundancia, con definición.** Redundancia es "la duplicación de componentes de un sistema para aumentar la disponibilidad general de ese sistema". Simple de decir; lo interesante es cuánto aumenta. Y eso es aritmética.

**Fórmula 1 — dependencias duras: se multiplican.** Si tu servicio no puede responder sin A ni sin B, la disponibilidad del conjunto es el producto. Un servicio de 99,99 % que depende duro de dos sistemas independientes de 99,99 % alcanza, teóricamente, **99,97 %**:

```
0,9999 × 0,9999 × 0,9999 = 0,9997  →  99,97 %
```

Esto es contraintuitivo y es la lección más útil del subtema: **agregar cajas al diagrama puede bajar la disponibilidad.** Cada componente nuevo en el camino crítico de un request multiplica.

**Fórmula 2 — componentes redundantes e independientes: se suman los nueves.** Si dos componentes hacen el mismo trabajo y la caída de uno no implica la del otro, el conjunto falla solo cuando fallan los dos. La disponibilidad efectiva es 100 % menos el producto de las tasas de falla:

```
Dos componentes independientes de 99,9 %:
tasa de falla de cada uno = 0,001
0,001 × 0,001 = 0,000001  →  100 % − 0,0001 % = 99,9999 %
Atajo: si todas las cifras son nueves, se suma la cantidad de nueves (3 + 3 = 6).
```

*(Las dos fórmulas están en la sección Availability del Reliability Pillar de AWS. Son aritmética, así que se pueden usar como tales; la tabla de objetivos y las categorías de aplicación por nivel son objetivos de diseño de ese proveedor.)*

> ⚠️ La palabra clave de la fórmula 2 es **independientes**. Dos réplicas en la misma máquina física, con el mismo disco, en la misma zona, alimentadas por la misma base de datos única, no son independientes: comparten dominio de falla y la cuenta no aplica. La redundancia se paga en separación real, no en cantidad de cajas dibujadas.

**Así se ve la arquitectura cuando el scale out ya está hecho:**

```mermaid
flowchart TD
    CLI["Clientes"] --> LB["Load balancer<br/>(S15)"]
    LB --> R1["Replica 1<br/>FastAPI stateless"]
    LB --> R2["Replica 2<br/>FastAPI stateless"]
    LB --> R3["Replica 3<br/>FastAPI stateless"]
    R1 --> SS["Session store<br/>(Redis)"]
    R2 --> SS
    R3 --> SS
    R1 --> POOL["Pooler de conexiones"]
    R2 --> POOL
    R3 --> POOL
    POOL --> PG[("PostgreSQL")]
    R1 --> Q["Cola de trabajos"]
    R2 --> Q
    R3 --> Q
    Q --> W["Workers"]
    W --> PG
    W --> GW["Model gateway"]
    GW --> LLM["LLM API<br/>cuota de la organizacion"]

    classDef ojo fill:#FFFBEB,stroke:#B45309,stroke-width:2px
    class PG,LLM ojo
```

Están marcadas en amarillo las dos cajas que **no** se multiplicaron: la base y la cuota del proveedor. Son los dos cuellos de botella que el scale out del web tier no toca, y los dos temas de los subtemas 5.5 y 5.7.

**Por qué la ganancia no es lineal.** La escalabilidad se mide como la relación entre ganancia de throughput y aumento de recursos —idealmente, duplicar recursos duplica el throughput— y está limitada por la aparición de **cuellos de botella** o **puntos de sincronización**. Formalmente se modela con la **ley de Amdahl**, cuantificando dos pérdidas:

- **contención**: la demora por esperar o encolarse por un recurso compartido;
- **coherencia**: la demora para que los datos se vuelvan consistentes.

Dicho en criollo: cada réplica nueva trae su capacidad de cómputo, pero también su cola frente a la base y su cuota de coordinación. Por eso la réplica 2 suele rendir casi el doble y la réplica 10 casi nada.

**Gotchas del subtema**

- Calcular la fórmula 2 sobre componentes que comparten dominio de falla (ver callout).
- Redundar el componente que **ya** era el más confiable: el término dominante de la multiplicación es el peor, no el mejor.
- Creer que el load balancer es gratis: es una caja nueva en el camino crítico (multiplica) y, si es una sola, un SPOF nuevo. Eso se arregla en **M07·S15**.

**Para profundizar:** [Availability — AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/availability.html) · [Patterns for scalable and resilient apps — Google Cloud](https://docs.cloud.google.com/architecture/scalable-and-resilient-apps) · [Design to scale out — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/scale-out)

---

### 5.4 Qué se complica: estado compartido y sesiones

**El problema que resuelve.** Este es el subtema que convierte el escalón 4 en la bisagra del diagrama. La pregunta es una sola y es brutalmente concreta: **¿qué se rompe cuando hay dos copias de tu servidor?** Respuesta: todo lo que una copia recuerda y la otra no.

**La regla.** Los procesos de una app twelve-factor son **stateless y share-nothing**, y todo dato que deba persistir va a un **backing service** con estado, típicamente una base de datos. La memoria y el disco local sirven como caché de **una sola transacción**, pero la app nunca puede asumir que lo que guardó ahí va a estar en un request futuro. La formulación equivalente, en vocabulario de diseño: **asegurate de que cualquier instancia pueda atender cualquier request.**

**Qué pasa si no.** Aparece la **stickiness** (o session affinity): el balanceador manda siempre al mismo cliente al mismo servidor, porque es el único que tiene sus datos. Un web tier **stateful** obliga al usuario a volver siempre al mismo servidor, lo que agrega overhead y dificulta agregar, quitar o perder servidores; con un web tier **stateless** la sesión vive en un almacén compartido, cualquier servidor atiende cualquier request, y el tier se vuelve más simple, más robusto y autoescalable. Las dos causas típicas de stickiness son **guardar el estado de sesión en memoria** y **usar claves de cifrado propias de cada máquina**.

Esa segunda causa suena abstracta hasta que la ves en tu propio stack. El `SessionMiddleware` de Starlette que usaste en **M07·S04** agrega sesiones HTTP basadas en **cookie firmada**; `secret_key` es un argumento requerido y debería ser un string aleatorio. La cookie se setea **siempre** con `HttpOnly`, y la información de sesión es **legible pero no modificable** por el cliente.

```python
# app/main.py — sesión en cookie firmada, lista para N réplicas
import os
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# La secret_key se LEE del entorno, no se genera.
# Si cada réplica generara la suya (p. ej. con secrets.token_hex()), cada una
# firmaría con una clave distinta y rechazaría las cookies de las otras:
# el usuario perdería la sesión al rotar de réplica y volveríamos a necesitar
# sticky sessions, esta vez sin haberlas pedido.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET_KEY"],  # misma clave en todas las réplicas
)

@app.get("/soporte/ultimo-ticket")
def ultimo_ticket(request: Request):
    # Dato chico y NO sensible: la cookie es legible por el cliente.
    # El contenido del ticket vive en PostgreSQL; acá solo guardamos el id.
    return {"ticket_id": request.session.get("ultimo_ticket_id")}
```

**Por qué así.** Hay dos salidas al problema del estado de sesión y conviene conocer las dos:

| | Cookie firmada (el estado viaja con el cliente) | Session store compartido (Redis/Memcached) |
|---|---|---|
| Componentes nuevos | ninguno | uno, con su propia disponibilidad |
| Tamaño del estado | chico (viaja en cada request) | el que quieras |
| Confidencialidad | firmada ≠ cifrada: legible por el cliente | el cliente solo ve un id opaco |
| Invalidar una sesión ya emitida | difícil (la cookie es válida hasta que expira) | fácil: se borra la entrada |
| Condición para escalar | **misma `secret_key` en todas las réplicas** | que el store sea alcanzable por todas |

La alternativa que ambas descartan es "sesión en memoria del proceso", que es exactamente lo que fuerza las sticky sessions. *(El flujo completo de autenticación —sesiones vs JWT— es de **M07·S16**; acá nos interesa solo la ubicación del estado.)*

**Checklist: qué estado hay que sacar del servidor.** Esta lista es la que conviene recorrer con el dedo sobre tu propio código antes de pedir la segunda réplica:

1. **Sesiones de usuario** → session store compartido o cookie firmada.
2. **Archivos subidos a disco local** → almacenamiento de objetos o la base; si no, el archivo existe solo en la réplica que lo recibió.
3. **Caché en memoria del proceso** (`dict` global, `lru_cache`) → cache compartida, o aceptar explícitamente que cada réplica tenga su copia y que el hit rate baje.
4. **Tareas programadas corriendo dentro de la app** → si N réplicas levantan el mismo scheduler, el job corre N veces. Va a un worker aparte o con un lock compartido.
5. **Conexiones de larga vida** (los WebSockets de **M07·S09**) → el cliente está pegado a *una* réplica; el fan-out de mensajes necesita un canal compartido.
6. **Contadores y rate limiters en memoria** → a un store compartido con operaciones atómicas; si no, tu límite de "100 por minuto" se vuelve de 100×N.
7. **Estado de conversación de un agente** → al mismo lugar que la sesión. Un historial de chat en una variable de módulo funciona perfecto con un proceso y desaparece con dos.

**Gotchas del subtema**

- `--reload` de uvicorn borra el estado en memoria en cada cambio de archivo, así que el bug "se me reinició el contador" aparece en desarrollo y se lo atribuye al reload, no al diseño.
- Guardar datos sensibles en una cookie de sesión creyendo que firmada es cifrada.
- Sacar la sesión pero dejar el `dict` de caché: una sola de las siete filas del checklist sin resolver alcanza para romper la propiedad "cualquier instancia atiende cualquier request".

**Para profundizar:** [The Twelve-Factor App — VI. Processes](https://12factor.net/processes) · [Design to scale out — Azure](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/scale-out) · [SessionMiddleware — Starlette](https://starlette.dev/middleware/)

---

### 5.5 Escalá el cuello de botella, no el sistema

**El problema que resuelve.** El reflejo, cuando algo está lento, es agregar réplicas del componente que sabemos escalar (el web server). El resultado habitual es gastar plata y complejidad sin mover la latencia. La frase a memorizar es directa: **escalar horizontalmente no es una solución mágica para cualquier problema de performance; si la base de datos del backend es el cuello, no ayuda agregar más web servers.** Y el corolario que más rinde: **las partes con estado del sistema son la causa más probable de cuellos de botella.**

**El cuello se muda.** Esto es lo que hace que el tema sea un proceso y no una decisión. Cada vez que destrabás un recurso, el siguiente pasa a ser el límite:

```mermaid
flowchart TD
    MED["Medir primero:<br/>p95, throughput, saturacion por recurso"] --> S1["Sintoma: CPU al tope<br/>en el web tier"]
    MED --> S2["Sintoma: CPU baja<br/>y p95 alto"]
    MED --> S3["Sintoma: errores de<br/>too many connections"]
    MED --> S4["Sintoma: 429 del proveedor"]
    S1 --> A1["Scale up, y despues<br/>replicas stateless"]
    S2 --> A2["No es capacidad:<br/>es espera. Perfilar la query<br/>o sacar el trabajo del request"]
    S3 --> A3["Pooler de conexiones;<br/>despues replicas de lectura (S21)"]
    S4 --> A4["Caching, reparto entre modelos,<br/>cola + batches, subir de tier"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class MED foco
```

**El número que lo hace concreto.** `max_connections` en PostgreSQL es por default del orden de 100 y solo se fija al arrancar el servidor. Ahora hacé la cuenta del escalón 5: si cada réplica abre un pool de 10 conexiones, 10 réplicas son 100 conexiones. Llegaste al techo de la base **sin haber subido un solo punto de carga real**, y el techo no se cambia en caliente. Ese es el momento exacto en que el diagrama necesita un **pooler** delante de la base.

```bash
# El margen de conexiones, en vivo (contra el Postgres en Docker de S05–S07).
# `db` es el nombre del servicio del compose y `postgres` el usuario:
# reemplazalos por los de tu equipo si definieron otros.
docker compose exec db psql -U postgres -c "SHOW max_connections;"
docker compose exec db psql -U postgres -c \
  "SELECT count(*) AS en_uso FROM pg_stat_activity;"
```

**Por qué así.** Se podría estimar el margen de conexiones leyendo el código (réplicas × tamaño del pool), pero `pg_stat_activity` muestra lo que **realmente** está abierto, incluidas las conexiones de tu cliente de administración, de las migraciones y de cualquier worker. La diferencia entre lo que creés que abriste y lo que hay abierto es, muchas veces, el incidente.

**El caso que un AI Engineer ve todo el tiempo: I/O-bound.** Cuando un request pasa su vida esperando a una API externa —un modelo, por ejemplo— el proceso no está calculando: está **esperando** (lo de `async def` vs `def` de **M07·S04**). Consecuencia práctica: **la CPU puede estar al 20 % mientras el sistema está saturado.** Lo que se agota primero no es cómputo, son *slots de espera*: workers del servidor, conexiones a la base que el request mantiene tomadas mientras espera, y la cuota del proveedor. Dos errores típicos salen de ahí:

- mirar el panel de CPU, verlo tranquilo y concluir que "hay capacidad de sobra";
- configurar autoscaling por CPU: nunca dispara, porque la CPU nunca sube.

**El patrón: medir antes de escalar.** Antes de tocar el diagrama, tres preguntas: ¿cuál es el síntoma observable?, ¿qué recurso está saturado?, ¿qué pasa con el p95 si duplico *solo* ese recurso? Si no podés contestar la segunda, todavía no sabés qué escalar.

**Gotchas del subtema**

- Escalar el web tier para arreglar una query lenta.
- Poner un pooler y dejar el pool de cada réplica en su tamaño original: el pooler ayuda si las réplicas piden menos conexiones directas, no si le sumás una capa más al mismo problema.
- Creer que "más workers" es gratis: cada worker es un proceso con su propia memoria y su propia porción de pool.

**Para profundizar:** [Design to scale out — Azure](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/scale-out) · [Connection Settings — PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-connection.html)

---

### 5.6 El diagrama de evolución y cómo se defiende un paso

**El problema que resuelve.** Nadie te va a pedir "la arquitectura escalada". Te van a pedir que expliques **por qué tu sistema está así hoy y qué harías si la carga se duplica**. El diagrama de evolución es la forma de contestar eso: no es un dibujo, es una secuencia de decisiones con su justificación.

El orden canónico, tal como aparece publicado, va más lejos de lo que cubre esta sesión: single server → separar web tier y data tier → vertical vs horizontal → load balancer → replicación de base (primario/réplicas) → cache → CDN → **stateless web tier** → múltiples data centers → message queue → logging, métricas y automatización → sharding (ByteByteGo, *System Design Interview*, cap. 2). De esa lista, hoy trabajamos los primeros pasos y el stateless; el resto tiene dueño: el load balancer en detalle es **S15**, las réplicas de base, la cache y el sharding son **S21**, la cola engancha con el async de **S04** y los protocolos de **S09**, y logging y métricas son **S20**.

**El formato de cada paso.** Una línea, tres campos:

> **Paso N — \<qué cambia en el diagrama\>.** Gano **X** / pago **Y** / lo dispara **Z**.

Y para defenderlo ante una pregunta, el mismo formato de la bitácora de trade-offs de **M07·S01**: **supuesto**, **alternativa descartada**, y **qué tendría que pasar para volver atrás**. Ejemplo escrito entero:

> **Paso 4 — sacar el estado de sesión del proceso a un store compartido.**
> **Gano:** cualquier instancia puede atender cualquier request; habilita réplicas, deploys sin caída y autoscaling.
> **Pago:** una dependencia dura nueva (multiplica mi disponibilidad), un lookup extra por request y cambios de código.
> **Lo dispara:** querer la segunda instancia — o, antes, ver el contador saltar con `--workers 4`.
> **Supuesto:** el estado de sesión es chico y temporal.
> **Alternativa descartada:** sticky sessions en el balanceador. Más barata hoy, pero deja el tráfico de un usuario pesado concentrado en una réplica y vuelve costoso perder un servidor.
> **Qué me haría volver atrás:** si el store resultara menos disponible que mi objetivo, movería la sesión a cookie firmada en vez de volver a memoria.

**Por qué así.** El campo que casi todos omiten es "lo dispara", y es el que distingue un diagrama defendible de una lista de buenas prácticas. Sin un síntoma observable que justifique el paso, la respuesta honesta a "¿por qué pusiste una cola?" es "porque lo vi en un video". **No hay cifras de usuarios en estos escalones a propósito:** cuántos usuarios concurrentes aguanta una caja depende de la app, del hardware y del patrón de acceso, y reconocer el síntoma es la habilidad que se evalúa.

**Gotchas del subtema**

- Dibujar el estado final directamente. Si no podés contar la secuencia, no vas a poder defenderla.
- Poner cajas "porque van": una cache que nadie midió es una dependencia dura más y una fuente de datos viejos.
- Olvidar que la arquitectura es un **blanco móvil**: la del prototipo no es la del primer sistema en producción, y esa cambia otra vez cuando la app escala (Ng, *AI Engineering Skills Map*). Lo que se enseña no es "la arquitectura escalada", es cómo se pasa de una a la siguiente.

**Para profundizar:** [Scale From Zero To Millions Of Users — ByteByteGo, cap. 2](https://bytebytego.com/courses/system-design-interview/scale-from-zero-to-millions-of-users)

---

### 5.7 Enganche con IA: cuando el techo es del proveedor

**El problema que resuelve.** Tu app de soporte está lenta y devuelve errores. Agregás réplicas. Empeora. Esto no es una paradoja: es lo que pasa cuando el recurso saturado está **fuera de tu sistema**.

**La cuota es de la organización, no del servidor.** Los rate limits de la Claude API se aplican **a nivel de organización** (con límites opcionales más bajos por workspace, que no superan el de la organización), se miden en **RPM, ITPM y OTPM** por clase de modelo, dependen del *usage tier* y se implementan con **token bucket**: la capacidad se repone continuamente en vez de resetearse en intervalos fijos. Los de OpenAI se fijan **a nivel de organización y de proyecto, no por usuario**, varían por modelo y se miden en RPM, RPD, TPM, TPD e IPM, alcanzándose con la métrica que llegue primero. Dos proveedores distintos, la misma estructura: **el límite no está asociado a tu infraestructura**, así que diez réplicas comparten exactamente la misma cuota que una.

**Hacé la cuenta antes de dibujar.** Tomemos la cuota del tier Start para Claude Sonnet 5: **1.000 RPM, 2.000.000 ITPM y 400.000 OTPM** *(tabla consultada el 12 de octubre de 2026; estos números cambian, así que una cuenta de capacidad siempre lleva fecha)*. Supongamos que cada ticket de soporte manda 8.000 tokens de entrada y recibe 400 de salida —**supuestos del ejemplo**, no datos:

```
Límite por requests:  1.000 RPM                       → 1.000 req/min
Límite por entrada:   2.000.000 ITPM ÷ 8.000 tokens   →   250 req/min   ← el que manda
Límite por salida:      400.000 OTPM ÷   400 tokens   → 1.000 req/min
```

Tu techo real es **250 requests por minuto**, no 1.000. El límite que manda es el de tokens de entrada, y no se ve en ningún panel de CPU.

**Las palancas, cuando el cuello es la cuota.** Ninguna es "más réplicas":

- **Caching.** Para la mayoría de los modelos de Claude, **solo los tokens de entrada no cacheados cuentan para el ITPM**. Con un límite de 2.000.000 ITPM y 80 % de cache hit se pueden procesar efectivamente 10.000.000 de tokens de entrada por minuto (2 M sin cachear + 8 M cacheados). Lo que en **M07·S04** presentamos como ahorro de costo, acá es **palanca de escala**.
- **Repartir entre modelos.** Los límites se aplican por modelo, así que se pueden usar varios en paralelo hasta su límite respectivo.
- **Cola + batches.** Lo que no es interactivo no tiene por qué pelear por la cuota del minuto: se encola y se procesa aparte.
- **Subir de tier.** La palanca comercial, que también es una decisión de arquitectura.

**429 no es 529.** En la Claude API, **429 `rate_limit_error`** significa que **tu organización** llegó a un rate limit (o a su tope de gasto), e indica qué límite se superó, con header `retry-after`; una subida brusca de uso puede además disparar 429 por **acceleration limits**, y la doc recomienda subir el tráfico gradualmente. **529 `overloaded_error`** significa que la API está temporalmente sobrecargada, lo que puede ocurrir con tráfico alto **de todos los usuarios**. El SDK oficial reintenta las fallas transitorias (conexión, rate limits, 5xx) con backoff exponencial, **dos veces por defecto**, respetando `retry-after`. Y la advertencia de OpenAI que más duele: **los requests fallidos también cuentan** contra el límite del minuto — tratá el `Retry-After` como un **mínimo**, sumale una demora aleatoria, y si no viene usá backoff exponencial **con jitter** para que no reintenten todos los clientes al mismo tiempo.

> ⚠️ **Autoscaling por CPU a ciegas es el peor movimiento posible en este escalón.** Más instancias pegándole al proveedor producen más 429, no más capacidad — y como los fallidos cuentan, el 429 se auto-alimenta. *(Qué hacer con esos fallos —reintentos, timeouts, fallback, degradación elegante— es **M07·S16**; acá el rate limit es un **límite de escalado**, no una falla a manejar.)*

**La última caja del diagrama: el model gateway.** Cuando el cuello es el proveedor, el componente que aparece en el diagrama no es otro web server: es un **gateway** entre tu backend y los modelos. En su forma más simple es un wrapper con una función por proveedor y un endpoint que despacha. Da interfaz unificada (si una API cambia, se actualiza un solo lugar), control de acceso y gestión de costos (no repartir el token de la organización) y —lo que importa hoy— **políticas de fallback ante rate limits o fallas de API**: rutear a modelos alternativos, reintentar tras una espera corta, o manejar la falla de otra forma elegante. Y como todos los requests y respuestas ya pasan por ahí, es un buen lugar para **balanceo de carga**, logging y analytics.

```bash
# Ver cuánta cuota te queda: los headers de la respuesta.
# -D - imprime los headers por stdout; -o /dev/null descarta el body,
# porque acá no nos interesa la respuesta del modelo sino el margen restante.
curl -sS -D - -o /dev/null https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "<MODEL_ID>", "max_tokens": 64, "messages": [{"role": "user", "content": "Hola"}]}'
```

Mirá en la salida `anthropic-ratelimit-requests-remaining`, `anthropic-ratelimit-input-tokens-remaining` y, si hubo 429, `retry-after`. **Placeholders:** `<MODEL_ID>` → el modelo que use tu equipo; `ANTHROPIC_API_KEY` → exportala antes (`export ANTHROPIC_API_KEY=...`). La key va **del backend**, nunca en el frontend (**M07·S02**).

**Por qué así.** Podrías deducir tu margen contando requests en tu propio código, pero esa cuenta es local a una réplica y la cuota es de la organización: solo el proveedor sabe cuánto queda. Por eso el dato autoritativo son sus headers, y por eso tenerlos centralizados en un gateway es la diferencia entre enterarte por un panel o enterarte por un 429.

**Gotchas del subtema**

- Deducir el techo de la cuota mirando solo el RPM: casi siempre manda el límite de tokens.
- Reintentar sin jitter: reconstruís el pico que te rate-limiteó.
- Dejar una tabla de cuotas en la documentación del equipo sin fecha de consulta. Caducan.

**Para profundizar:** [Rate limits — Claude API](https://platform.claude.com/docs/en/api/rate-limits) · [Errors — Claude API](https://platform.claude.com/docs/en/api/errors) · [Rate limits — OpenAI API](https://developers.openai.com/api/docs/guides/rate-limits)

---

### Cómo se relacionan los recursos entre sí

Tres cosas que conviene saber antes de leerlos, y que ningún recurso dice de sí mismo:

- **Azure, ByteByteGo y 12-Factor dicen lo mismo con palabras distintas.** "Cualquier instancia tiene que poder atender cualquier request" aparece como recomendación de diseño (Azure), como paso 8 de la evolución (ByteByteGo) y como regla con prohibición explícita de las sticky sessions (12-Factor). Tres fuentes, una sola idea: es la que conviene repetir.
- **Azure y la doc de PostgreSQL se complementan.** Azure dice "si la base es el cuello, más web servers no ayudan"; PostgreSQL pone el número (`max_connections` del orden de 100, modificable solo al arrancar) que explica *por qué* la base es el cuello tan pronto.
- **La doc de Google Cloud sobre cambiar el machine type y la de PostgreSQL cuentan el mismo trade-off en dos capas**: el scale up, arriba y abajo del stack, se paga con un reinicio. Es el argumento de por qué la primera flecha del diagrama tiene fecha de vencimiento.

Y dos pares que se sostienen entre sí: **AWS y el SRE Book** son dos fuentes independientes de la misma tabla de nueves (AWS agrega la aritmética de composición y el costo de cada nueve); **Anthropic y OpenAI** son dos fuentes primarias independientes de que la cuota es de la organización, lo que permite leerlo como el modelo general de las LLM APIs y no como rareza de un proveedor.

---

## 6. Guía práctica: el taller de pizarra, paso a paso

No hay lab nuevo de código. Lo que sigue es el taller completo, en el orden en que se hace en clase, para que puedas rehacerlo solo. El entregable es un diagrama y una entrada en la bitácora.

### 6.1 Prerequisitos

- **El diagrama de partida.** El que tu equipo produjo en **M07·S13** pensando el sistema "para 100k usuarios". Si no lo terminaron, sirve el diagrama de componentes de **M07·S05**.
- **La tabla de nueves** de la sección 5.1, a mano.
- **Un objetivo de disponibilidad elegido y escrito** antes de dibujar redundancia. Sin objetivo, el diagrama no tiene criterio de parada. Sugerencia: **99,9 %** para una app interna, **99,95 %** si cobra plata.
- Opcional, para las demos: el webserver de S03–S05 corriendo y el Postgres en Docker de S05–S07.

### 6.2 Los siete escalones, con su trade-off

Dibujá **un diagrama por escalón** (o uno que vaya creciendo, marcando lo que cambió), y al lado de cada flecha escribí la línea de tres campos. Esto es el corazón de la sesión.

**Paso 1 — Single server.** Web y base en la misma caja.
*Gano:* la cosa más simple que puede funcionar; un solo lugar donde mirar. *Pago:* la app y la base compiten por CPU, memoria y disco; un dominio de falla único. *Lo dispara:* nada todavía — es el punto de partida, y para un prototipo es la respuesta correcta.
**Verificación:** ¿podés nombrar los componentes que viven dentro de esa caja? Si no, volvé a **M07·S02**.

**Paso 2 — Separar web tier y data tier.** La base se va a su propia caja.
*Gano:* escalar cada tier por separado; un deploy de la app ya no reinicia la base; cada uno se dimensiona según lo que consume. *Pago:* un salto de red en cada query (latencia) y una **dependencia dura** más, que multiplica mi disponibilidad. *Lo dispara:* la app y la base pelean por los mismos recursos, o un reinicio de la app afecta a los datos.
**Verificación:** aplicá la fórmula 1 con el objetivo que elegiste. ¿El conjunto sigue cumpliéndolo?

**Paso 3 — Scale up.** Instancia más grande para el tier saturado.
*Gano:* más capacidad sin tocar código ni agregar cajas. *Pago:* una **ventana de mantenimiento** (en Compute Engine hay que detener la VM; en PostgreSQL, `max_connections` solo se fija al arrancar) y el SPOF intacto. *Lo dispara:* saturación sostenida del recurso, **con el código ya perfilado**.
**Verificación:** ¿medís el recurso que vas a agrandar? Si el síntoma es "p95 alto con CPU baja", este paso no es el tuyo (ver 5.5).

**Paso 4 — Sacar el estado.** Sesiones, archivos, cachés, contadores y schedulers salen del proceso.
*Gano:* "cualquier instancia atiende cualquier request" — la condición de todo lo que sigue, incluido el autoscaling. *Pago:* dependencias nuevas, un lookup por request y cambios de código. *Lo dispara:* querer la segunda instancia; o el contador que salta con `--workers 4`.
**Verificación:** recorré las siete filas del checklist de 5.4 y marcá cada una como *resuelta* o *pendiente, y por qué puede esperar*.

**Paso 5 — N réplicas stateless detrás de un load balancer.**
*Gano:* redundancia (sumá los nueves con la fórmula 2), capacidad casi lineal al principio, deploys sin caída. *Pago:* complejidad operativa, una caja nueva en el camino crítico (que si es una sola es un SPOF nuevo), y **N× conexiones a la base** — acá aparece el pooler. *Lo dispara:* el scale up llegó al techo, o un reinicio dejó de ser aceptable.
**Verificación:** tapá cada caja con el dedo y preguntá "¿sigue funcionando?". Las que digan "no" son tus SPOF; anotalos para **S15**.

**Paso 6 — Cola + workers para el trabajo pesado.** Lo que consume CPU o I/O sale del request.
*Gano:* el request vuelve rápido (`202 Accepted`, de **M07·S09**), el pico se absorbe en la cola, el trabajo pesado escala aparte. *Pago:* asincronía visible para el cliente (necesita poder consultar el estado), idempotencia y reintentos, y que una instancia se puede apagar **a mitad de un trabajo** (scale in: apagado limpio, checkpoints, trabajo que otra instancia retome). *Lo dispara:* el p95 arrastrado por unas pocas operaciones largas dentro del request.
**Verificación:** ¿qué pasa si el worker muere a mitad? Si la respuesta es "se pierde el trabajo", el paso está incompleto.

**Paso 7 — Gateway hacia el modelo.** Solo si la app llama a un modelo.
*Gano:* un lugar donde ver la cuota, cachear, repartir entre modelos, loguear y aplicar fallback. *Pago:* un hop más y un componente propio que mantener. *Lo dispara:* 429 del proveedor mientras tu CPU está al 20 %.
**Verificación:** la cuenta de 5.7 con tu propio tamaño de prompt. ¿Cuál de los tres límites te frena primero?

### 6.3 Las tres demos (opcionales, ~5 min cada una)

**Demo 1 — el estado en memoria se rompe en cuanto hay más de un proceso.** Es la que más rinde: convierte el escalón 4 en algo que se ve en el navegador.

```python
# main.py — contador guardado en memoria del proceso (antipatrón a propósito)
from fastapi import FastAPI

app = FastAPI()
visitas = 0  # estado en memoria: vive en ESTE proceso, no en "el servidor"

@app.get("/visitas")
def contar():
    global visitas
    visitas += 1
    return {"visitas": visitas}
```

```bash
uvicorn main:app --workers 4 --port 8000
```

- `main:app` — módulo `main.py`, objeto `app` (igual que en **S03**).
- `--workers 4` — levanta **4 procesos** que atienden requests en paralelo, cada uno con su propia copia de `visitas`. Es "scale out dentro de una sola máquina", y alcanza para reproducir el problema sin montar nada.
- `--port 8000` — puerto local.
- **Verificación:** refrescá `http://localhost:8000/visitas` varias veces. El número **salta o se repite** según qué proceso te atienda — exactamente lo que va a pasar con N máquinas detrás de un balanceador (**S15**).
- **La corrección** es la de 12-Factor: el contador a un backing service (Redis, o una tabla del Postgres de S07), y ahí con un `UPDATE` atómico y no con un read-modify-write.

> ⚠️ `--workers` **no** se combina con `--reload`. Si lo tenías puesto, sacalo.

**Demo 2 — cuánto margen de conexiones tiene la base.** Los dos comandos de la sección 5.5. **Verificación:** anotá los dos números y contestá en la pizarra: *"si cada réplica abre un pool de 10 conexiones, ¿cuántas réplicas entran antes de chocar con ese techo?"*. El pooler aparece solo en el diagrama.

**Demo 3 — ver la cuota del proveedor en los headers.** El `curl` de la sección 5.7. **Verificación:** los tres headers. **Si no hay API key a mano, se mira la tabla de la doc en pantalla** y se hace la cuenta de capacidad igual. Pregunta de pizarra: *"si corro esto desde 10 réplicas, ¿estos números se multiplican por 10?"* — no: la cuota es de la organización. Si tu equipo usa OpenAI, su guía de rate limits documenta el equivalente.

### 6.4 Entregable

1. **El diagrama de evolución** en `docs/diagramas/s14-evolucion.*` (Excalidraw o Mermaid, a elección, como en **S02**), con los siete pasos y su línea de "gano / pago / lo dispara".
2. **Una entrada nueva en la bitácora de trade-offs** con la decisión *"¿cuándo dejamos de escalar vertical?"*, en el formato `TJ-NNN` de **M07·S01** (o `[sNN]` en `docs/trade-offs.md`, si tu equipo viene usando ese).
3. **El objetivo de disponibilidad elegido**, escrito, con la cuenta de la fórmula 1 sobre tu cadena de dependencias duras.

Esto alimenta el entregable de la semana —*diagrama de arquitectura escalada con topología de redundancia*—, que se completa en **S15**.

### 6.5 Reparto de los 180 minutos

| Tramo | Tiempo | Qué |
|---|---|---|
| Concepto | ~45 min | vocabulario y disponibilidad · vertical · horizontal · qué se complica · enganche IA |
| Pizarra | ~90 min | evolucionar el diagrama, con las tres demos de 5 min intercaladas donde corresponde |
| Puesta en común | ~35 min | cada equipo defiende **un** paso y su trade-off |
| Cierre | ~10 min | entrada de la bitácora |

> 📝 **Nota para el profesor:** el timing, el objetivo de disponibilidad sugerido (99,9 % / 99,95 %), la composición de equipos (default: los mismos de S05), la ruta de entrega `docs/diagramas/s14-evolucion.*`, el formato de la entrada de bitácora (`TJ-NNN` vs `[sNN]`), el proveedor del ejemplo (Anthropic, con la nota de que OpenAI documenta el mismo modelo por organización/proyecto) y qué demos se hacen (se recomienda la 1; la 3 requiere API key) son defaults de este material: ajustalos a tu clase. El ejemplo del taller está escrito sobre un **caso genérico** (API de soporte con FastAPI + PostgreSQL + una LLM API) para que el material sirva aunque el diagrama de cada equipo sea distinto; si preferís que sea sobre el proyecto del curso, es una sustitución de nombres.

---

## 7. Ejercicios

Cuatro unidades. Cada una arranca con la teoría mínima para poder hacerla sola, sigue con un ejemplo resuelto y comentado, y cierra con tres ejercicios graduados: 🟢 completar o modificar, 🟡 guiado, 🔴 desde cero. **Intentá cada ejercicio antes de mirar su solución en la sección 12.**

### Unidad 1 — Medir antes de escalar: percentiles y aritmética de disponibilidad

**Teoría mínima.** Antes de agregar una caja hacen falta dos números: cuánto espera un usuario (latencia en percentiles, nunca promedio) y cuánto nos comprometimos a estar arriba (disponibilidad). La latencia se resume con p50/p90/p95/p99 porque el promedio lo arruina un outlier. La disponibilidad se compone con dos reglas: **dependencias duras se multiplican**; **componentes redundantes e independientes** dan 100 % menos el producto de las tasas de falla. Con eso ya podés decir, con números, qué le aporta cada caja a tu diagrama y qué le resta.

**Ejemplo resuelto.** La API de soporte tiene esta cadena: un load balancer de 99,99 %, un único web server de 99,9 % y un único PostgreSQL de 99,9 %. Todas son dependencias duras. El objetivo declarado es **99,9 %**.

```text
Paso 1 — composición actual (fórmula de dependencias duras: se multiplican)
  0,9999 × 0,999 × 0,999 = 0,997901...  →  99,79 %
  Caída anual implícita: 0,21 % del año.
  Veredicto: NO cumple 99,9 %. Y notá por qué: no hay ningún componente "roto",
  simplemente hay tres multiplicándose.

Paso 2 — ¿y si duplico el web server? (dos de 99,9 %, independientes)
  tasa de falla de cada uno = 0,001
  0,001 × 0,001 = 0,000001  →  99,9999 %   (atajo: 3 nueves + 3 nueves = 6 nueves)

Paso 3 — recomponer la cadena con el web tier redundante
  0,9999 × 0,999999 × 0,999 = 0,998899...  →  99,89 %
  Caída anual implícita: 0,11 % del año (casi la mitad que antes).
  Veredicto: mejoró de verdad… y SIGUE sin cumplir 99,9 %.
```

**Por qué este resultado es la lección entera de la unidad.** Redundar el web tier sí sirvió —le sacó casi la mitad del tiempo caído—, pero no alcanzó, y el motivo es estructural: **una cadena de dependencias duras nunca puede ser más disponible que su peor componente.** El PostgreSQL único de 99,9 % le pone un techo de 99,9 % a todo el sistema, y los otros factores solo pueden bajarlo. Por eso agregar la cuarta, quinta y sexta réplica de web es tirar plata: el término que manda es otro. Las dos salidas honestas son redundar la capa de datos (primario con standby o réplicas de lectura, tema de **S21**) o bajar el objetivo a 99,5 % y declararlo por escrito.

> 💡 Nota honesta sobre esta cuenta: las réplicas solo "suman nueves" si son **independientes**. Dos procesos en la misma máquina no lo son.

#### 🟢 El outlier y el percentil

Tomás esta muestra de TTFT de la API de soporte, en ms: `100, 102, 100, 100, 99, 104, 110, 90, 3000, 95`. Ya sabés que el promedio es 390 ms y que con el método de rango más cercano p50 = 100, p90 = 110 y p95 = 3000.

1. Recalculá promedio, p50, p90 y p95 **quitando** el request de 3.000 ms.
2. Agregá en cambio un segundo outlier de 2.500 ms a la muestra original (11 valores) y recalculá los mismos cuatro números.
3. Contestá en dos líneas: ¿cuál de los cuatro indicadores se movió más en cada caso, y qué te dice eso sobre qué reportar en un panel?

<details><summary>Pista</summary>

Con el método de rango más cercano, la posición del percentil p es `ceil(p/100 × n)` sobre la lista **ordenada**. Ojo: al cambiar `n`, cambian las posiciones.
</details>

**Lo lograste si:** tus cuatro números son correctos en los dos escenarios y podés explicar por qué el p50 casi no se mueve mientras el promedio salta.

#### 🟡 El objetivo de disponibilidad de tu diagrama

Tu equipo declara un objetivo de **99,95 %** para la API de soporte. La cadena de dependencias duras es: load balancer 99,99 % → web tier → PostgreSQL 99,9 % → la LLM API (que para el endpoint de redacción de borradores es una dependencia **dura**) con 99,9 %.

1. Elegí la disponibilidad del web tier en dos escenarios: (a) una sola instancia de 99,9 %; (b) tres instancias independientes de 99,9 %.
2. Calculá la disponibilidad compuesta en los dos escenarios.
3. Decidí si cumplís el objetivo. Si no, nombrá **el término que lo impide** y proponé un cambio que no sea "agregar más web servers".
4. Traducí el resultado a tiempo caído por año usando la tabla de la sección 5.1 (alcanza con ubicarlo entre dos filas).

<details><summary>Pista</summary>

Antes de calcular, mirá qué término es el más chico. Después pensá si ese componente admite redundancia *o* si admite convertirse en dependencia **blanda** (¿qué podría responder tu endpoint si la LLM API no contesta?).
</details>

**Lo lograste si:** identificás que el término dominante no es el web tier, y tu propuesta ataca ese término —por redundancia o por degradación— en vez de replicar lo que ya era confiable.

#### 🔴 La ficha de medición de tu servicio

Sin plantilla: escribí la **ficha de medición** de un servicio real o plausible (puede ser la API de soporte, o lo que estés construyendo). Tiene que incluir:

- la **carga** esperada en el pico y la unidad en que la medís;
- el objetivo de **latencia** con percentil y ventana (ej.: "p95 < 1,5 s en la última hora");
- la definición de **capacidad** del servicio: a partir de qué carga dejás de cumplir ese objetivo;
- el objetivo de **disponibilidad** con su tiempo caído anual, y la **cadena de dependencias duras** con la cuenta de la fórmula 1;
- una frase que justifique por qué **no** elegiste el nueve siguiente.

**Lo lograste si:** cualquier compañero puede leer tu ficha y decirte, sin preguntarte nada, cuál es tu cuello de botella candidato y si tu objetivo de disponibilidad es alcanzable con tu cadena actual.

---

### Unidad 2 — Sacar el estado del servidor

**Teoría mínima.** Scale out no es sumar servidores: es lograr que **cualquier instancia pueda atender cualquier request**. Eso exige que el proceso sea stateless y share-nothing, y que todo lo que deba persistir viva en un backing service. El estado típico a mudar: sesiones, archivos en disco local, cachés en memoria, schedulers, conexiones de larga vida, contadores y rate limiters. Las sticky sessions son el atajo que 12-Factor prohíbe explícitamente, porque limita el escalado y encarece perder un servidor. Para probarlo no hace falta cloud: `--workers 4` ya rompe el estado en memoria.

**Ejemplo resuelto y comentado.** La API de soporte lleva un contador de tickets atendidos por día, que se usa para un panel interno. Está en memoria. Así se rompe y así se arregla:

```python
# ❌ ANTES — app/metrics.py
# Un dict de módulo. Con un solo proceso funciona perfecto, y por eso el bug
# sobrevive hasta producción: no falla, da números distintos según quién atienda.
atendidos_hoy = {"2026-10-12": 0}

def registrar_atencion(fecha: str) -> int:
    atendidos_hoy[fecha] = atendidos_hoy.get(fecha, 0) + 1
    return atendidos_hoy[fecha]
```

```python
# ✅ DESPUÉS — app/repositories/metrics_repo.py
# El contador se va a PostgreSQL (el backing service que ya tenemos de S07),
# y la operación se vuelve ATÓMICA: una sola sentencia que lee y escribe en la base.
from sqlalchemy import text
from sqlalchemy.orm import Session

def registrar_atencion(db: Session, fecha: str) -> int:
    # UPSERT + incremento en la base, no en Python.
    # Alternativa descartada: SELECT, sumar 1 en Python, UPDATE (read-modify-write).
    # Con N réplicas concurrentes eso produce lost updates: dos procesos leen 7,
    # los dos escriben 8, y una atención se pierde. El UPDATE atómico no puede
    # perderla porque el incremento lo hace el motor bajo su propio lock de fila.
    fila = db.execute(
        text("""
            INSERT INTO atenciones_diarias (fecha, total)
            VALUES (:fecha, 1)
            ON CONFLICT (fecha) DO UPDATE
              SET total = atenciones_diarias.total + 1
            RETURNING total
        """),
        {"fecha": fecha},
    ).one()
    return fila.total
```

**Por qué así, en tres decisiones:**

1. **Por qué un backing service y no un dict:** porque el dict vive en *un* proceso. Con `--workers 4` ya hay cuatro contadores distintos, y ninguno es "el" número.
2. **Por qué atómico y no read-modify-write:** porque el problema no es solo *dónde* vive el estado, también es *quién* lo modifica. Si el incremento se calcula en Python, dos réplicas concurrentes pueden perder una atención.
3. **Por qué PostgreSQL y no Redis acá:** porque la base ya existe, ya es una dependencia dura y este dato tiene valor histórico. Redis sería la elección si el dato fuera efímero y de muy alta frecuencia (una sesión, un rate limiter) — y en ese caso se usaría con expiración por tiempo, como recomienda 12-Factor para las sesiones.

#### 🟢 Romper y arreglar el contador

Partí de la **Demo 1** de la sección 6.3 (el endpoint `/visitas` con `--workers 4`).

1. Reproducí el salto del número y describí en una línea qué estás viendo.
2. Modificá el ejemplo para que el contador sobreviva al multiproceso. Podés usar la base del proyecto o Redis, a elección.
3. Volvé a correr con `--workers 4` y verificá que ahora el número sea monótono.
4. Explicá en dos líneas por qué `global visitas` no es el problema de fondo, sino un síntoma.

<details><summary>Pista</summary>

Si usás Postgres, el incremento va en **una sola sentencia**. Si usás Redis, hay una operación que incrementa y devuelve el valor nuevo en un solo viaje — buscá "atómico" en su documentación de comandos de enteros.
</details>

**Lo lograste si:** con cuatro workers el contador avanza de uno en uno, y podés nombrar la operación atómica que lo garantiza.

#### 🟡 Auditoría de estado de un servicio

La API de soporte tiene, hoy, estas siete cosas (todas verdaderas en apps reales):

1. sesión de usuario con `SessionMiddleware` y una `secret_key` generada al arrancar con `secrets.token_hex()`;
2. adjuntos de los tickets guardados en `./uploads/`;
3. un `@lru_cache` sobre la función que carga el catálogo de categorías;
4. un scheduler interno que a las 02:00 manda el resumen diario por email;
5. un WebSocket que empuja el estado del ticket al navegador del agente;
6. un rate limiter propio, "20 requests por minuto por usuario", en un `dict`;
7. el historial de conversación del asistente, en un `dict` por `ticket_id`.

Para cada ítem: decidí si **se rompe** con N réplicas, explicá en una línea **cómo** se rompe, y proponé el destino del estado. Marcá además cuál de los siete es el que produce **stickiness invisible** (el que hace que la app "funcione" pero obligue al usuario a volver siempre al mismo servidor).

<details><summary>Pista</summary>

Hay dos ítems que no pierden datos pero igual se degradan (uno pierde eficacia, otro se ejecuta de más). Y uno de los siete está documentado como causa de stickiness en la guía de Azure.
</details>

**Lo lograste si:** los siete tienen veredicto y destino, identificás el ítem 1 como el caso de "claves propias de cada máquina", y distinguís los que **pierden datos** de los que solo **pierden eficacia**.

#### 🔴 Hacer stateless un endpoint con estado

**Objetivo:** tomá un endpoint propio (del proyecto del curso, de la API de soporte o de cualquier app tuya) que hoy dependa de algo que vive en el proceso, y volvelo stateless.

**Criterio de éxito:**
- El endpoint responde correctamente con `--workers 4` y con requests alternados entre workers.
- Escribís la línea "gano / pago / lo dispara" del cambio.
- Escribís qué **dependencia nueva** agregaste y qué le hace a tu disponibilidad compuesta (fórmula 1 de la Unidad 1).
- Nombrás explícitamente la alternativa que descartaste y por qué.

**Lo lograste si:** podés apagar cualquier worker a mitad de una sesión de uso y el usuario no nota nada más que, como mucho, un request reintentado.

---

### Unidad 3 — Evolucionar el diagrama y defender cada paso

**Teoría mínima.** El entregable de esta sesión no es una arquitectura: es una **secuencia de decisiones**. Cada paso del diagrama se escribe en tres campos —**gano / pago / lo dispara**— y se defiende en tres más: **supuesto, alternativa descartada, qué me haría volver atrás**. El campo que casi todos omiten es "lo dispara", y es el que convierte una buena práctica copiada en una decisión propia. Ningún escalón lleva cifras de usuarios: lleva un **síntoma observable**.

**Ejemplo resuelto.** El paso 5 de la API de soporte, escrito entero:

> **Paso 5 — tres réplicas stateless de la API detrás de un load balancer.**
>
> - **Gano:** redundancia en el tier que más se cae (deploys, crashes, OOM); capacidad casi lineal en el primer tramo; deploys sin ventana de caída.
> - **Pago:** un componente nuevo en el camino crítico (el balanceador, que multiplica mi disponibilidad y —si es uno solo— es un SPOF nuevo); 3× conexiones a PostgreSQL, contra un `max_connections` que por default está en el orden de 100 y no se cambia en caliente; y la pérdida de "mirar un solo log".
> - **Lo dispara:** dos síntomas, cualquiera de los dos alcanza: (a) el scale up llegó al techo útil del tier, o (b) un reinicio para deployar dejó de ser aceptable para el negocio.
> - **Supuesto:** el servicio ya es stateless (paso 4 hecho y verificado con el checklist).
> - **Alternativa descartada:** seguir con scale up y una ventana de mantenimiento anunciada. Más simple, pero no da redundancia: el día que la caja muera, el servicio se cae entero, y eso ya no entra en el objetivo de disponibilidad que declaramos.
> - **Qué me haría volver atrás:** si al medir con tres réplicas el throughput no subiera —porque el cuello pasó a ser la base—, quitaría una réplica y atacaría primero la capa de datos. Más réplicas contra una base saturada solo agregan contención.

**Por qué este formato y no un párrafo.** Un párrafo esconde los campos faltantes; la plantilla los expone. Si no podés llenar "lo dispara", el paso no está justificado todavía. Si no podés llenar "qué me haría volver atrás", es que estás tratando la decisión como permanente, y la arquitectura es un blanco móvil.

#### 🟢 Completar los campos que faltan

Te entregan este paso a medio escribir:

> **Paso 6 — mover la redacción del borrador del ticket a una cola con workers.**
> **Gano:** el endpoint contesta en milisegundos en vez de esperar al modelo.
> **Pago:** [falta]
> **Lo dispara:** [falta]

1. Completá "pago" con al menos **tres** costos distintos (pensá en el cliente, en la operación y en el scale in).
2. Completá "lo dispara" con un **síntoma observable y medible**, sin cifras de usuarios.
3. Agregá los tres campos de defensa: supuesto, alternativa descartada, qué te haría volver atrás.

<details><summary>Pista</summary>

Para "pago", pensá qué tiene que hacer el frontend que antes no hacía, y qué pasa si el worker se apaga a mitad del trabajo. Para "lo dispara", el síntoma vive en la distribución de latencia, no en el promedio.
</details>

**Lo lograste si:** tu "lo dispara" es algo que se puede leer en un panel, y tu "pago" menciona la idempotencia o los reintentos.

#### 🟡 Evolucionar un caso nuevo, de cero a escalado

Caso: **un buscador interno de documentación** con FastAPI. Hoy es un single server que, en cada búsqueda, (a) consulta PostgreSQL, (b) llama a una LLM API para reformular la consulta del usuario y (c) devuelve resultados. Guarda las búsquedas recientes de cada usuario en un `dict` en memoria y los PDFs subidos en `./docs/`.

Pasos:
1. Dibujá el estado inicial (Mermaid o papel).
2. Elegí y escribí un objetivo de disponibilidad.
3. Recorré los siete escalones. Para cada uno, decidí **si aplica o no a este caso** y escribí la línea de tres campos. Si un escalón no aplica, justificá por qué en una línea.
4. Marcá en el diagrama final los SPOF que quedan y los dos cuellos de botella que el scale out del web tier **no** resuelve.
5. Elegí **un** paso y escribí su defensa de tres campos.

<details><summary>Pista</summary>

Hay dos cosas en memoria o en disco local que bloquean el paso 4. Y hay un escalón que, en este caso, tiene un disparador distinto del habitual: fijate qué pasa con la cuota del proveedor cuando cada búsqueda llama al modelo.
</details>

**Lo lograste si:** tu secuencia llega a una arquitectura escalada sin saltarse el escalón 4, cada paso tiene su síntoma disparador, y los dos cuellos marcados son la base y la cuota del proveedor.

#### 🔴 La defensa de tres minutos

**Objetivo:** preparar y escribir la defensa de **tu** diagrama de evolución (el entregable de la sección 6.4) como si te lo preguntaran en una entrevista o en la puesta en común.

**Criterio de éxito:**
- Un texto de no más de 300 palabras que recorra la secuencia completa, no el estado final.
- Cada paso con su síntoma disparador.
- Al menos un paso donde digas **"acá todavía no estamos"** y por qué no corresponde todavía.
- Una respuesta preparada para estas tres preguntas: *"¿por qué no microservicios?"* (retomá el criterio de **S13**), *"¿por qué no cinco nueves?"* y *"si mañana se duplica la carga, qué toca primero?"*.

**Lo lograste si:** ninguna de las tres preguntas te obliga a improvisar, y tu respuesta a la tercera nombra un recurso medido, no un componente.

---

### Unidad 4 — Cuando el techo es del proveedor

**Teoría mínima.** En una app que llama a una LLM API, el recurso que se agota primero suele estar afuera. Los rate limits son de la **organización** (y del proyecto o workspace), se miden en RPM y en tokens por minuto de entrada y salida, se aplican por modelo y se implementan con token bucket. Tus réplicas comparten la misma cuota, así que el scale out del web tier no sube ese techo. Las palancas son otras: caching (los tokens de entrada cacheados no cuentan para el ITPM en la mayoría de los modelos de Claude), repartir entre modelos, encolar lo no interactivo y subir de tier. Y hay que distinguir **429** (me pasé yo) de **529** (está sobrecargado el proveedor).

**Ejemplo resuelto.** Cuenta de capacidad de la API de soporte, con la cuota del tier Start para Claude Sonnet 5: **1.000 RPM, 2.000.000 ITPM, 400.000 OTPM** *(tabla consultada el 12 de octubre de 2026)*. Supuestos del ejemplo: cada ticket manda 8.000 tokens de entrada (prompt del sistema + política de atención + historial) y recibe 400 de salida.

```text
A — techo por cada límite, sin caching
  requests:  1.000 RPM                              → 1.000 req/min
  entrada:   2.000.000 ITPM ÷ 8.000  =   250        →   250 req/min  ← MANDA
  salida:      400.000 OTPM ÷   400  = 1.000        → 1.000 req/min
  Techo real: 250 req/min, de punta a punta, para TODA la organización.

B — ¿y si agrego réplicas de la API?
  Techo real: 250 req/min. Sin cambios. La cuota no es de la réplica.

C — ¿y si cacheo la parte fija del prompt y logro 80 % de cache hit?
  tokens de entrada NO cacheados por request = 8.000 × 0,20 = 1.600
  entrada:   2.000.000 ITPM ÷ 1.600 = 1.250         → 1.250 req/min
  requests:  1.000 RPM                              → 1.000 req/min  ← AHORA MANDA
  Techo real: 1.000 req/min. El cuello se mudó del ITPM al RPM.
```

**Por qué esta cuenta y no otra.** Se podría estimar el techo mirando solo el RPM, que es el número más visible de la tabla: daría 1.000 y sería **cuatro veces optimista**. La cuenta correcta evalúa los tres límites y toma el mínimo, porque se alcanza el límite con el que llegue primero. Y el escenario C muestra el movimiento más característico del tema: **destrabar un cuello muda el cuello**, no lo elimina. Ahora la palanca útil cambia (repartir entre modelos, encolar, subir de tier), porque cachear más no mueve el RPM.

> ⚠️ Esa tabla de cuotas **caduca**. Cualquier cuenta de capacidad que escribas lleva la fecha de consulta al lado, igual que acá.

#### 🟢 Recalcular con otro prompt

Usá la misma cuota del ejemplo (1.000 RPM, 2.000.000 ITPM, 400.000 OTPM, consultada el 12 de octubre de 2026) y estos supuestos nuevos: el equipo decide **adjuntar el historial completo del ticket**, así que la entrada pasa a 20.000 tokens, y pide respuestas más largas: 1.200 tokens de salida.

1. Calculá el techo por cada uno de los tres límites y decí cuál manda.
2. Calculá el techo si lográs 50 % de cache hit sobre la entrada.
3. Contestá: ¿el cambio de `max_tokens` afecta tu techo de OTPM?

<details><summary>Pista</summary>

Para el punto 3, revisá qué dice la doc de rate limits sobre la relación entre `max_tokens` y el OTPM. No es lo que la intuición dice.
</details>

**Lo lograste si:** los tres techos son correctos, identificás que ahora manda la entrada por bastante más margen, y tu respuesta al punto 3 coincide con lo que dice la doc.

#### 🟡 El incidente de los 429

A las 10:05 el panel de la API de soporte muestra: errores en el 30 % de los requests al endpoint de redacción de borradores, p95 por las nubes, **CPU de las tres réplicas al 18 %**. En los logs hay 429 y algunos 529. El equipo acaba de activar autoscaling por CPU y, además, un compañero propone "subir el máximo de réplicas a 10".

1. Explicá por qué el autoscaling por CPU **no va a disparar** en este incidente.
2. Explicá por qué subir a 10 réplicas puede **empeorar** la tasa de 429 (acordate de qué cuenta contra el límite del minuto).
3. Separá los 429 de los 529: ¿qué significa cada uno y cuál de los dos te dice algo sobre *tu* configuración?
4. Proponé, en orden de implementación, **tres** medidas que sí atacan el problema, y marcá cuál es la única que además baja el costo.
5. Decí qué header mirarías para confirmar tu diagnóstico en 30 segundos.

<details><summary>Pista</summary>

El punto 2 tiene dos efectos sumados: más concurrencia contra la misma cuota, y el detalle que documenta OpenAI sobre los requests fallidos. El punto 4 empieza por la palanca que la propia doc describe como forma de subir el throughput efectivo.
</details>

**Lo lograste si:** tu respuesta al punto 3 no confunde "mi cuota" con "capacidad del proveedor", y tu orden del punto 4 no arranca por "subir de tier".

#### 🔴 Diseñar la caja que falta

**Objetivo:** diseñar (en papel y pseudocódigo, no hace falta implementarlo) el **model gateway** de la API de soporte: la pieza que aparece en el escalón 7.

**Criterio de éxito:**
- Un diagrama con la caja ubicada: qué la llama, a qué llama, y qué queda del otro lado.
- La lista de responsabilidades que le asignás, con una línea de justificación cada una. Al menos: interfaz unificada, visibilidad de cuota y política ante rate limit.
- La decisión explícita de **qué NO va a hacer** el gateway en esta etapa (acordate: reintentos, timeouts y degradación se diseñan en serio en **S16**).
- El trade-off en formato de tres campos, incluido el costo de poner un hop más en el camino crítico y lo que le hace a tu disponibilidad compuesta.
- Una respuesta a: *"¿por qué no llamar al proveedor directo desde cada réplica, como hasta ahora?"*

**Lo lograste si:** tu gateway se justifica por **visibilidad y control**, no por "es lo que se hace", y tu diagrama deja claro que el gateway **no** sube la cuota: la administra.

---

## 8. Ruta de estudio sugerida

```mermaid
flowchart TD
    V["1 · Vocabulario y medida<br/>Huyen cap. 9 + tabla del SRE Book<br/>20 min"] --> AR["2 · Aritmetica de la disponibilidad<br/>AWS Reliability Pillar<br/>15 min"]
    AR --> U1["Unidad 1 de ejercicios<br/>20 min"]
    U1 --> ST["3 · La regla del stateless<br/>12-Factor VI + Azure scale out<br/>15 min"]
    ST --> SM["4 · El caso en tu stack<br/>Starlette SessionMiddleware<br/>5 min"]
    SM --> U2["Unidad 2 de ejercicios<br/>20 min"]
    U2 --> EV["5 · Definiciones y orden canonico<br/>Google Cloud Patterns + ByteByteGo cap. 2<br/>40 min"]
    EV --> U3["Unidad 3 de ejercicios<br/>25 min"]
    U3 --> IA["6 · El techo del proveedor<br/>Anthropic rate limits y errors + OpenAI<br/>20 min"]
    IA --> GW["7 · La ultima caja<br/>Huyen cap. 10, model gateway<br/>15 min"]
    GW --> U4["Unidad 4 de ejercicios<br/>25 min"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class ST foco
```

Las dependencias del grafo son reales, no decorativas:

1. **Vocabulario primero** (Huyen cap. 9 + la tabla del SRE Book). Son veinte minutos que evitan discutir una hora sin números.
2. **La aritmética de la disponibilidad** (AWS). Sin las dos fórmulas, "redundancia" es una palabra; con ellas, es una cuenta. No se entiende el paso 5 del diagrama sin esto.
3. **La regla del stateless** (12-Factor VI y la guía de Azure). Está resaltado porque es el nodo del que depende todo lo demás: sin él, scale out es "sumar máquinas" y la sesión pierde su idea central.
4. **El caso concreto en tu stack** (Starlette): la trampa de la `secret_key` por réplica.
5. **Las definiciones y el orden canónico** (Google Cloud *Patterns* y ByteByteGo cap. 2): redundancia, stateless y los doce pasos que estructuran la pizarra. Leé solo las secciones de escalado, statelessness y redundancia de la primera.
6. **El enganche con IA** (Anthropic *Rate limits* → *Errors* → OpenAI *Rate limits*).
7. **La última caja** (Huyen cap. 10, model gateway).

> 💡 Intentá cada ejercicio **antes** de mirar su solución en la sección 12. El valor de la Unidad 3 en particular está en equivocarse: un paso mal justificado que después corregís enseña más que leer la versión correcta.

---

## 9. Checklist de autoevaluación

- [ ] Puedo explicar, sin mirar los apuntes, la diferencia entre **carga, capacidad y latencia**, y por qué escalar arregla una y no la otra.
- [ ] Puedo mostrar con un ejemplo por qué el **promedio de latencia** engaña, y decir qué percentiles reportaría en su lugar.
- [ ] Sé traducir un objetivo de disponibilidad a **tiempo caído por año** y argumentar por qué no pedir el nueve siguiente.
- [ ] Puedo calcular la disponibilidad de una cadena de **dependencias duras** y de un par de **componentes redundantes**, y sé qué condición tienen que cumplir para que la segunda fórmula valga.
- [ ] Puedo nombrar los **dos límites del scale up** y explicar cuál llega primero en la práctica.
- [ ] Puedo listar al menos cinco tipos de **estado** que hay que sacar de un servidor antes de replicarlo, y adónde va cada uno.
- [ ] Puedo explicar qué son las **sticky sessions**, por qué 12-Factor las prohíbe, y cómo se reinventan por accidente con una `secret_key` por réplica.
- [ ] Puedo explicar por qué más web servers **no** arreglan un cuello en la base, y nombrar el número de PostgreSQL que lo hace concreto.
- [ ] Puedo dibujar los **siete escalones** del diagrama de evolución y decir, para cada uno, qué gano, qué pago y qué síntoma lo dispara.
- [ ] Puedo explicar por qué diez réplicas no suben el techo de llamadas al modelo, y nombrar tres palancas que sí.

---

## 10. Preguntas de repaso

1. Tu servicio tiene p50 de 120 ms y p99 de 4 segundos, con CPU al 20 %. Tu jefe pide "más servidores". ¿Qué le contestás, y qué medirías antes de tocar la infraestructura?
2. Declarás un objetivo de 99,99 % para un servicio que depende duro de tres componentes de 99,99 % cada uno. ¿Es alcanzable? Mostrá la cuenta y decí qué cambiarías: ¿el objetivo, la arquitectura, o la naturaleza de alguna dependencia?
3. Un equipo te dice que ya está listo para escalar horizontalmente porque "la app no guarda nada en el servidor". ¿Qué cinco preguntas le hacés para verificarlo?
4. Explicá por qué el scale out, pasado cierto punto, deja de darte throughput proporcional a los recursos que agregás. Nombrá las dos fuentes de pérdida.
5. Una app de IA empieza a devolver 429 bajo carga, con la CPU tranquila. El equipo tiene autoscaling por CPU configurado. Explicá por qué el autoscaling no ayuda, qué diferencia hay si los errores fueran 529, y cuál sería tu plan en orden de prioridad.

---

## 11. Recursos adicionales

### Imprescindibles

| Recurso | Para qué | Tiempo |
|---|---|---|
| [Availability Table — Google SRE Book, Apéndice A](https://sre.google/sre-book/availability-table/) | La tabla de nueves → tiempo caído, con la nota sobre medir caídas parciales por operaciones fallidas | 5 min |
| [Availability — AWS Well-Architected, Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/availability.html) | Las dos fórmulas (dependencias duras y componentes redundantes) y el costo de cada nueve | 15 min |
| [The Twelve-Factor App — VI. Processes](https://12factor.net/processes) | La regla que hace posible el scale out, en cinco minutos y en la fuente primaria | 5 min |
| [Design to scale out — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/scale-out) | Afinidad de instancia, identificación de cuellos, scale in, contención y coherencia | 8 min |
| [Rate limits — Claude API](https://platform.claude.com/docs/en/api/rate-limits) | La cuota como límite de escalado: RPM/ITPM/OTPM, token bucket, ITPM cache-aware | 10 min |

### Recomendados

| Recurso | Para qué | Tiempo |
|---|---|---|
| [Scale From Zero To Millions Of Users — ByteByteGo, cap. 2](https://bytebytego.com/courses/system-design-interview/scale-from-zero-to-millions-of-users) | El esqueleto del diagrama: los doce pasos canónicos y el contraste stateful/stateless | 30–40 min |
| [Patterns for scalable and resilient apps — Google Cloud](https://docs.cloud.google.com/architecture/scalable-and-resilient-apps) | Definiciones de redundancia y stateless; separar stateful de stateless; SPOF | 25 min (alcanzan las secciones de escalado, statelessness y redundancia) |
| [Connection Settings — PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-connection.html) | `max_connections`: el número que explica por qué la base es el cuello tan pronto | 5 min (solo `max_connections`) |
| [SessionMiddleware — Starlette](https://starlette.dev/middleware/) | El caso del estado de sesión en tu propio stack, y la trampa de la `secret_key` | 5 min |
| [Claude API errors](https://platform.claude.com/docs/en/api/errors) | 429 vs 529 y el comportamiento de reintento del SDK | 5 min (secciones *HTTP errors* y *Long requests*) |

### Opcionales

| Recurso | Para qué | Tiempo |
|---|---|---|
| [Change the machine type of a stopped VM — Compute Engine](https://docs.cloud.google.com/compute/docs/instances/changing-machine-type-of-stopped-instance) | La factura del scale up en la doc de un proveedor: hay que detener la VM | 5 min |
| [Rate limits — OpenAI API](https://developers.openai.com/api/docs/guides/rate-limits) | La segunda fuente del mismo modelo (cuota por organización y proyecto) + backoff con jitter | 8 min |

### De la biblioteca del profesor

- **Huyen (2025), *AI Engineering*, cap. 9 — métricas de inferencia.** Latencia como distribución, percentiles, TTFT, throughput en RPM, el trade-off latencia/throughput y el goodput. *(15 min)*
- **Huyen (2025), *AI Engineering*, cap. 10 — model gateway.** La caja que cierra el diagrama de una app de IA. *(20 min)*
- **Ng (2026), *AI Engineering Skills Map: Software engineering fundamentals*, sección "Scaling and operating in production".** El marco: escalar requiere entender la carga real, y la arquitectura es un blanco móvil. *(5 min)*

---

## 12. Soluciones comentadas

### Unidad 1 — Medir antes de escalar: percentiles y aritmética de disponibilidad

#### 🟢 El outlier y el percentil

**1) Sin el outlier de 3.000 ms** (n = 9): ordenada → `90, 95, 99, 100, 100, 100, 102, 104, 110`.

```
suma = 900  →  promedio = 100 ms
p50: ceil(0,50 × 9) = 5  →  100 ms
p90: ceil(0,90 × 9) = 9  →  110 ms
p95: ceil(0,95 × 9) = 9  →  110 ms
```

**2) Con un segundo outlier de 2.500 ms** (n = 11): ordenada → `90, 95, 99, 100, 100, 100, 102, 104, 110, 2500, 3000`.

```
suma = 3900 + 2500 = 6400  →  promedio ≈ 581,8 ms
p50: ceil(0,50 × 11) = 6  →  100 ms
p90: ceil(0,90 × 11) = 10 →  2500 ms
p95: ceil(0,95 × 11) = 11 →  3000 ms
```

**3) Qué se movió.** El **promedio** es el que se mueve más en los dos escenarios: pasó de 390 a 100 al quitar un valor, y de 390 a ~582 al agregar otro. El **p50 no se mueve nunca** (100 ms en los tres casos), porque los outliers no cambian el centro de la distribución. El p90 y el p95 se mueven solo cuando la cola cambia de tamaño relativo.

**Qué reportar en un panel:** p50 **y** p95 (o p99) juntos. El p50 te dice cómo es la experiencia típica; el p95 te dice cuán mal está la cola. El promedio no te dice ninguna de las dos, y el máximo es un solo evento.

**Por qué esta elección y qué se descarta.** La alternativa habitual —"promedio y máximo"— tiene los dos defectos combinados: el promedio mezcla la cola con el centro y el máximo no distingue un problema sistemático de un timeout de red aislado. Y una nota de método: con 9, 10 u 11 muestras el p95 **es** el peor valor, así que no es un indicador estable. Para que un p95 signifique algo necesitás cientos o miles de muestras en la misma ventana.

#### 🟡 El objetivo de disponibilidad de tu diagrama

**Escenario (a) — web tier de una sola instancia:**

```
0,9999 (LB) × 0,999 (web) × 0,999 (PG) × 0,999 (LLM API) = 0,996903...  →  99,69 %
```

**Escenario (b) — tres instancias independientes de 99,9 %:**

```
web tier redundante: tasa de falla = 0,001³ = 0,000000001  →  99,9999999 %
0,9999 × 0,999999999 × 0,999 × 0,999 = 0,997901...  →  99,79 %
```

**Veredicto:** **ninguno de los dos cumple 99,95 %.** Triplicar el web tier mejoró del 99,69 % al 99,79 % —algo, no nada— pero sigue muy lejos del objetivo.

**El término que lo impide:** hay **dos** componentes únicos de 99,9 % en la cadena (PostgreSQL y la LLM API), y una cadena de dependencias duras no puede superar a su peor componente. Con dos términos de 99,9 % multiplicándose, el techo está por debajo de 99,8 %, así que 99,95 % es inalcanzable por más réplicas de web que agregues. Y la LLM API es la peor noticia de la cuenta: su disponibilidad **no la controlás**.

**Propuesta que no es "más web servers":** convertir la LLM API en una dependencia **blanda**. Si la redacción del borrador no está disponible, el endpoint puede devolver el ticket con los datos de la base y un borrador vacío, o un borrador de una plantilla. El request se atiende, degradado. Con eso la LLM API sale del producto de dependencias duras:

```
0,9999 × 0,999999999 × 0,999 = 0,998899...  →  99,89 %
```

Todavía falta: queda PostgreSQL, que ahora es el techo. El paso siguiente es redundar la capa de datos (primario + standby, tema de **S21**) o bajar el objetivo a 99,9 % o menos y declararlo.

**Tiempo caído:** 99,89 % queda **por debajo de la fila de 99,9 %** de la tabla, así que tu presupuesto de caída anual es **mayor que 8 horas 45 minutos** — y bastante más que los 4 h 22 min que correspondían a 99,95 %.

**Por qué esta solución y qué descarta.** La alternativa intuitiva era redundar más el web tier: la cuenta muestra que mejora un término que no domina. La solución elegida cambia la **naturaleza** de la dependencia en vez de su cantidad, que es la jugada más potente y más barata del repertorio: una dependencia que podés degradar sale de la multiplicación. *(El diseño concreto de esa degradación es **M07·S16**.)*

#### 🔴 La ficha de medición de tu servicio

No hay una única respuesta correcta. Esta es una ficha modelo, sobre la API de soporte, con el nivel de concreción que se espera:

```markdown
# Ficha de medición — API de soporte interno
Fecha: 2026-10-12

## Carga
- Unidad: tickets procesados por minuto (equivale a 1 request al modelo por ticket).
- Pico esperado: lunes 9:00–11:00, ~3× el promedio del día.
- Qué la mueve: cantidad de agentes en turno (no cantidad de usuarios registrados).

## Latencia
- Objetivo: p95 < 1,5 s en la última hora para `GET /tickets`;
  p95 < 6 s para el endpoint que llama al modelo (es I/O-bound por diseño).
- Se mide en el servidor y, aparte, en el navegador del agente.

## Capacidad
- Definición: la carga a la que el p95 del endpoint del modelo cruza los 6 s.
- Valor actual: desconocido → primera tarea de medición (hay que cargarlo, no estimarlo).

## Disponibilidad
- Objetivo: 99,5 % (el techo real de la cadena actual está por debajo de 99,8 %).
- Cadena de dependencias duras: LB (99,99) × web (99,9) × PostgreSQL (99,9) = 99,79 %.
- La LLM API se declara dependencia BLANDA: sin ella se devuelve el ticket sin borrador.
- Acción para subir a 99,9 %: redundar el web tier (fácil, ya es stateless) y evaluar
  standby de PostgreSQL en S21 — sin eso, 99,9 % no es alcanzable.

## Por qué no el nueve siguiente
99,99 % implica 52 min al año: exigiría multi-zona, automatización de recuperación
probada y no poder apoyarnos en ninguna dependencia menos disponible que eso.
Es una herramienta interna: el costo de esa ingeniería es mayor que el de unas horas caído.
```

**Por qué la ficha tiene esta forma.** Los dos campos que más se omiten son "capacidad" (porque exige medir, no opinar) y "por qué no el nueve siguiente" (porque exige decir no). El primero evita escalar a ciegas; el segundo es el criterio de parada del diagrama. Fijate también en dos detalles: la capacidad queda **declarada como desconocida** en vez de estimada —inventar un número ahí es peor que admitir que falta medirlo—, y el objetivo de disponibilidad se eligió **después** de hacer la cuenta de la cadena, no antes. Declarar 99,9 % con esta topología habría sido firmar algo que la arquitectura no puede cumplir.

---

### Unidad 2 — Sacar el estado del servidor

#### 🟢 Romper y arreglar el contador

**1) El síntoma.** Con `--workers 4`, refrescando `/visitas` la secuencia es algo como `1, 1, 2, 1, 2, 3, 2, …`: cada proceso lleva su propio contador y el balanceo interno decide quién te atiende. No es un bug de concurrencia: es que **hay cuatro estados distintos**, y ninguno es "el" estado.

**2) La corrección, con Postgres:**

```python
# main.py
from fastapi import Depends, FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/app")
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/visitas")
def contar(db: Session = Depends(get_db)):
    # Una sola sentencia: el incremento lo hace el motor, no Python.
    # Si lo hiciéramos como SELECT → +1 → UPDATE, dos workers podrían leer el
    # mismo valor y escribir el mismo resultado: una visita perdida (lost update).
    total = db.execute(
        text("""
            INSERT INTO contadores (nombre, total) VALUES ('visitas', 1)
            ON CONFLICT (nombre) DO UPDATE SET total = contadores.total + 1
            RETURNING total
        """)
    ).scalar_one()
    db.commit()
    return {"visitas": total}
```

Con Redis la operación equivalente es un incremento atómico que devuelve el valor nuevo en un solo viaje, lo que evita el mismo read-modify-write.

**3) Verificación.** Con `--workers 4`, refrescá diez veces: la secuencia tiene que ser `1, 2, 3, …, 10` sin saltos ni repeticiones.

**4) Por qué `global` no es el problema de fondo.** `global visitas` solo declara que el nombre se resuelve en el módulo; el problema es que **el módulo vive dentro de un proceso**. Sacar el `global` y usar una clase, un singleton o un `lru_cache` no cambia nada: cualquier estructura en memoria se replica con cada worker. El problema no es la sintaxis, es la **ubicación** del estado.

**Qué se descarta.** Dejar el contador en memoria y activar sticky sessions "para que cada usuario vea un número coherente": además de violar 12-Factor, no arregla nada —el número sería distinto según la réplica, y el panel interno necesita el total, no el total de una réplica.

#### 🟡 Auditoría de estado de un servicio

| # | Ítem | ¿Se rompe? | Cómo se rompe | Destino del estado |
|---|---|---|---|---|
| 1 | `secret_key` generada al arrancar | **Sí** | Cada réplica firma con otra clave y rechaza las cookies de las demás: el usuario pierde la sesión al rotar de réplica. **Es el caso "claves de cifrado propias de cada máquina".** | La clave a variable de entorno, **la misma en todas las réplicas** |
| 2 | Adjuntos en `./uploads/` | **Sí** | El archivo existe solo en la réplica que recibió el upload; si el GET cae en otra, 404 | Almacenamiento de objetos compartido (o la base, si son chicos) |
| 3 | `@lru_cache` del catálogo | **Degrada**, no pierde | Cada réplica tiene su copia, el hit rate baja y una invalidación no llega a todas | Aceptable si se declara; si hay que invalidar, cache compartida |
| 4 | Scheduler interno de las 02:00 | **Sí, al revés** | No pierde datos: **ejecuta de más**. Con N réplicas, N resúmenes diarios por email | Worker/scheduler aparte, o un lock compartido con dueño único |
| 5 | WebSocket del estado del ticket | **Sí** | La conexión está pegada a *una* réplica; un evento generado en otra no llega al cliente | Canal compartido para el fan-out (de **M07·S09**) |
| 6 | Rate limiter en un `dict` | **Sí** | El límite se vuelve 20×N por usuario: deja de limitar | Store compartido con operaciones atómicas y expiración |
| 7 | Historial de conversación por `ticket_id` | **Sí** | La conversación existe solo en la réplica que empezó: el request siguiente "olvida" todo | Al mismo lugar que el resto del estado de sesión, o a la base |

**Stickiness invisible: el ítem 1.** Es el más peligroso de los siete porque la app *parece* funcionar: nadie ve un error, solo usuarios que "se desloguean solos". Si alguien activa sticky sessions para tapar eso, el síntoma desaparece y la causa queda.

**Pierden datos** 1, 2, 5 y 7. **Pierden eficacia** 3 (hit rate) y 6 (deja de limitar, aunque este es grave por otro motivo: es un control de seguridad y de costo). El 4 es la categoría propia: **hace de más**.

**Por qué el orden importa.** Si tuvieras que arreglar solo tres, serían 1, 2 y 7: son los que producen errores visibles para el usuario. El 6 va inmediatamente después porque es el que te puede costar plata en la cuota del proveedor.

#### 🔴 Hacer stateless un endpoint con estado

No hay una respuesta única. Una resolución válida, sobre el ítem 7 de la auditoría (historial de conversación):

- **Qué se movió:** el `dict` por `ticket_id` pasó a una tabla con el historial, leído por `ticket_id` al entrar al endpoint y escrito al salir.
- **Gano:** cualquier réplica puede continuar cualquier conversación; el historial sobrevive a un reinicio, a un deploy y a un scale in.
- **Pago:** dos viajes a la base por request (lectura y escritura), una dependencia dura más en el camino del endpoint, y una decisión nueva que antes no existía: cuánto historial conservar y cuándo truncarlo.
- **Lo dispara:** cualquier intento de poner una segunda instancia; antes que eso, el bug "el asistente me olvida" que aparece al correr con varios workers.
- **Dependencia nueva y su efecto en la disponibilidad:** PostgreSQL ya era dependencia dura del endpoint, así que el producto de la fórmula 1 **no cambia**. Ese es, de hecho, un argumento fuerte a favor de elegir la base que ya tenés en vez de sumar Redis solo para esto: Redis habría agregado un factor nuevo a la multiplicación.
- **Alternativa descartada:** mandar el historial completo desde el cliente en cada request. Sería stateless del lado del servidor y cero dependencias nuevas, pero el cliente podría manipularlo (le estaríamos dejando editar el contexto que va al modelo) y el payload crecería sin techo.
- **Verificación:** correr con `--workers 4`, mantener una conversación alternando requests, y matar un worker a mitad. El usuario debería notar, como máximo, un request reintentado.

---

### Unidad 3 — Evolucionar el diagrama y defender cada paso

#### 🟢 Completar los campos que faltan

> **Paso 6 — mover la redacción del borrador del ticket a una cola con workers.**
>
> - **Gano:** el endpoint contesta en milisegundos en vez de esperar al modelo; el pico se absorbe en la cola en vez de en el p95; el trabajo pesado escala independientemente del web tier.
> - **Pago (tres costos distintos):**
>   1. **Para el cliente:** la respuesta pasa a ser `202 Accepted` con un id, así que el frontend necesita consultar el estado (o recibir un push). La asincronía deja de ser un detalle interno y se vuelve parte del contrato de la API.
>   2. **Para la operación:** dos componentes nuevos (la cola y los workers), con su propio despliegue, sus propios logs y su propia disponibilidad.
>   3. **Para la corrección:** entrega *at-least-once*, así que el trabajo tiene que ser **idempotente** y hay que decidir qué pasa con los reintentos y con los mensajes que fallan siempre. Y en scale in, una instancia se puede apagar a mitad de un trabajo: hace falta apagado limpio, checkpoints o que la tarea vuelva a la cola.
> - **Lo dispara:** el p95 del endpoint arrastrado por la llamada al modelo mientras el p50 está sano —es decir, la cola de la distribución la hace una operación larga dentro del request, no la falta de capacidad.
> - **Supuesto:** el agente de soporte no necesita el borrador en el mismo instante en que abre el ticket; tolera unos segundos.
> - **Alternativa descartada:** dejarlo síncrono y subir el timeout. Más simple, pero el request mantiene tomados un worker del servidor y una conexión a la base mientras espera, así que el costo de la latencia se paga en capacidad.
> - **Qué me haría volver atrás:** si el producto exigiera el borrador en la misma respuesta, volvería a síncrono y atacaría la latencia por otro lado (streaming de la respuesta del modelo, prompt más corto, modelo más rápido).

**Por qué este "lo dispara" y no otro.** "Está lento" no es un disparador: no se puede medir ni se puede dar por resuelto. "El p95 lo arrastra una operación larga mientras el p50 está sano" es un síntoma leíble en un panel y, además, descarta solo la hipótesis "falta capacidad" —si faltara capacidad, el p50 también estaría mal.

#### 🟡 Evolucionar un caso nuevo, de cero a escalado

**1) Estado inicial.** Single server con FastAPI + PostgreSQL en la misma caja, `./docs/` en disco local, búsquedas recientes en un `dict`, llamada a la LLM API por búsqueda.

**2) Objetivo de disponibilidad.** 99,5 % para arrancar, con 99,9 % como meta cuando la capa de datos tenga redundancia. Es una herramienta interna de documentación: si está caída una tarde, la gente busca a mano. Pedir 99,99 % no se justifica.

**3) Los siete escalones:**

| Paso | ¿Aplica? | Gano / pago / lo dispara |
|---|---|---|
| 1 · Single server | Punto de partida | *Gano:* simplicidad total. *Pago:* la app y la base compiten; dominio de falla único. *Lo dispara:* — |
| 2 · Separar la base | **Sí** | *Gano:* dimensionar cada tier por separado; un deploy no reinicia la base. *Pago:* un salto de red por query y una dependencia dura más que multiplica. *Lo dispara:* la indexación de documentos hace competir a la base con el web por memoria. |
| 3 · Scale up | **Sí** | *Gano:* más capacidad sin tocar código. *Pago:* ventana de mantenimiento (detener la VM; `max_connections` solo al arrancar); SPOF intacto. *Lo dispara:* CPU/memoria sostenidas al tope con las queries ya perfiladas. |
| 4 · Sacar el estado | **Sí, y es bloqueante** | Dos cosas lo bloquean: el `dict` de búsquedas recientes (va a la base o a un store compartido) y los PDFs en `./docs/` (van a almacenamiento de objetos; si no, la réplica B no encuentra el PDF que subió la A). *Gano:* cualquier instancia atiende cualquier búsqueda. *Pago:* dependencias nuevas y cambios de código. *Lo dispara:* el intento de levantar la segunda instancia. |
| 5 · N réplicas + LB | **Sí** | *Gano:* redundancia y deploys sin caída. *Pago:* el LB como caja nueva y posible SPOF; N× conexiones a la base → pooler. *Lo dispara:* el scale up topó, o un reinicio dejó de ser aceptable. |
| 6 · Cola + workers | **Sí, pero no para la búsqueda** | La búsqueda es interactiva: no se encola. Lo que sí: **la ingesta e indexación de PDFs**, que es pesada y no interactiva. *Gano:* subir un PDF devuelve rápido; la indexación no compite con las búsquedas. *Pago:* el usuario necesita ver "indexando"; idempotencia (no indexar dos veces el mismo documento). *Lo dispara:* una subida grande degradando el p95 de las búsquedas. |
| 7 · Gateway al modelo | **Sí** | *Gano:* visibilidad de la cuota, caching de las reformulaciones repetidas, reparto entre modelos. *Pago:* un hop más y un componente propio. *Lo dispara:* **429 del proveedor con la CPU tranquila**, que acá llega temprano porque **cada búsqueda llama al modelo** — la cuota se agota mucho antes que el cómputo. |

**4) SPOF y cuellos que el scale out del web tier no resuelve.** SPOF restantes: el load balancer único (→ **S15**) y PostgreSQL único (→ **S21**). Los dos cuellos: **la base** (conexiones, y la indexación compitiendo con las lecturas) y **la cuota del proveedor** (una llamada por búsqueda, con el techo fijado por el límite de tokens de entrada).

**5) Defensa del paso 4:**

> **Supuesto:** las búsquedas recientes de un usuario son un dato chico y prescindible, y los PDFs son inmutables una vez subidos.
> **Alternativa descartada:** sticky sessions + disco compartido montado en todas las réplicas. Resuelve los síntomas sin tocar código, pero mantiene la afinidad de instancia (y por lo tanto el problema de perder un servidor) y agrega una dependencia de infraestructura frágil.
> **Qué me haría volver atrás:** nada razonable. Este paso no tiene vuelta atrás útil: es la precondición de los escalones 5, 6 y 7.

**Por qué el paso 6 "aplica parcialmente" es la respuesta correcta.** El error típico es encolar todo lo que se pueda encolar. Una búsqueda interactiva en una cola empeora la experiencia sin ganar nada: no hay pico que absorber si el usuario está esperando la respuesta en pantalla. La cola es para lo que el usuario **no** está esperando.

#### 🔴 La defensa de tres minutos

Modelo de defensa (≈280 palabras), sobre la API de soporte:

> Arrancamos con todo en una caja, que para el prototipo era correcto: una sola cosa que desplegar y un solo log que mirar.
>
> El primer cambio lo disparó un síntoma concreto: la indexación y las queries competían con el web por memoria, y un deploy de la app reiniciaba la base. Separamos los tiers. Eso nos costó un salto de red por query y una dependencia dura más —que, con la fórmula de dependencias duras, nos bajó el techo de disponibilidad—, pero nos permitió dimensionar cada mitad por lo que consume.
>
> Después escalamos vertical, y lo volvería a hacer: cero cambios de código y cero complejidad nueva. Lo dejamos cuando apareció el síntoma que no se arregla con una máquina más grande: un reinicio para deployar dejó de ser aceptable. El techo de CPU no fue el problema; el punto único de falla sí.
>
> Para poner la segunda instancia tuvimos que hacer el trabajo real: sacar el estado. Sesiones a un store compartido, adjuntos a almacenamiento de objetos, el rate limiter a una operación atómica compartida y la `secret_key` a variable de entorno —esa última nos había generado "deslogueos" misteriosos—. Recién con eso pusimos tres réplicas detrás de un balanceador.
>
> **Dónde todavía no estamos:** no tenemos replicación de la base. Es nuestro SPOF conocido y el término que le pone techo a nuestra disponibilidad compuesta; está priorizado, no olvidado.
>
> **¿Por qué no microservicios?** Porque nuestro problema es de carga, no de equipos ni de ciclos de despliegue independientes, y un monolito modular nos escala igual con mucho menos costo operativo.
>
> **¿Por qué no cinco nueves?** Porque son 5 minutos al año: exige multi-región, recuperación automatizada y probada, y no poder apoyarnos en ninguna dependencia menos disponible. Es una herramienta interna.
>
> **Si se duplica la carga:** toca primero el límite de tokens de entrada del proveedor. La palanca es caching de la parte fija del prompt, no más réplicas.

**Por qué funciona esta defensa.** Tres cosas: (1) cada paso tiene su síntoma, así que no suena a receta copiada; (2) incluye un "todavía no estamos", que es lo que distingue a alguien que conoce su sistema de alguien que lo presenta; (3) la respuesta a la última pregunta nombra un **recurso medido** (el ITPM), no un componente. Decir "le metemos más réplicas" habría contradicho toda la sesión.

---

### Unidad 4 — Cuando el techo es del proveedor

#### 🟢 Recalcular con otro prompt

**1) Techo por cada límite** (entrada 20.000, salida 1.200):

```
requests:  1.000 RPM                                → 1.000 req/min
entrada:   2.000.000 ITPM ÷ 20.000 = 100            →   100 req/min  ← MANDA
salida:      400.000 OTPM ÷  1.200 ≈ 333            →   333 req/min
Techo real: 100 req/min.
```

Adjuntar el historial completo te costó **el 60 % de la capacidad** (de 250 a 100 req/min) sin cambiar una línea de infraestructura. Es el argumento más contundente de la sesión a favor de mirar el tamaño del prompt como variable de escala.

**2) Con 50 % de cache hit en la entrada:**

```
tokens de entrada no cacheados = 20.000 × 0,50 = 10.000
entrada:   2.000.000 ÷ 10.000 = 200                 →   200 req/min  ← sigue mandando
salida:      400.000 ÷  1.200 ≈ 333                 →   333 req/min
requests:  1.000 RPM                                → 1.000 req/min
Techo real: 200 req/min.
```

El caching duplicó la capacidad, y el cuello **no se mudó**: sigue siendo la entrada. Para que se mude habría que subir el cache hit bastante más, o recortar el prompt.

**3) ¿`max_tokens` afecta al OTPM?** No: la doc de rate limits dice explícitamente que **`max_tokens` no afecta al OTPM**. Lo que cuenta para el OTPM son los tokens de salida realmente generados, no el techo que pediste. La intuición dice lo contrario —"si pido más, me reservan más"—, y por eso vale la pena saberlo: bajar `max_tokens` no te compra cuota, aunque sí te protege de respuestas larguísimas inesperadas.

**Por qué el orden de los cálculos importa.** Primero los tres techos, después el mínimo. Si calculás solo el que te parece relevante, te queda el número optimista — y acá el optimista (1.000) es diez veces el real.

#### 🟡 El incidente de los 429

**1) Por qué el autoscaling por CPU no dispara.** Porque el request está **esperando**, no calculando: es I/O-bound (lo de **M07·S04**). El proceso está bloqueado en la llamada al proveedor, así que la CPU se queda en el 18 % aunque el sistema esté saturado. La métrica elegida no observa el recurso que se agotó. Para que un autoscaler sirviera acá, la métrica tendría que ser el largo de la cola de requests o la tasa de 429 — y aun así escalar no ayudaría, por el punto 2.

**2) Por qué 10 réplicas pueden empeorarlo.** Dos efectos que se suman:
- La cuota es **de la organización**, no de la réplica: diez réplicas no tienen diez cuotas, tienen la misma. Lo único que cambia es cuántas pueden pedir a la vez, lo que acelera el agotamiento del balde.
- **Los requests fallidos también cuentan** contra el límite del minuto (lo documenta OpenAI para su API). Así que los 429 generados por el exceso de concurrencia consumen cuota, lo que produce más 429: el error se auto-alimenta. Y si además hay reintentos sin jitter, todos los clientes vuelven juntos y reconstruyen el pico.

**3) 429 vs 529.** **429 `rate_limit_error`** = **tu organización** llegó a un rate limit o a su tope de gasto; indica qué límite se superó y trae `retry-after`. Es el que habla de *tu* configuración: tu tier, tu tamaño de prompt, tu concurrencia. Una subida brusca puede además disparar 429 por *acceleration limits*, y la recomendación es subir el tráfico gradualmente. **529 `overloaded_error`** = la API está temporalmente sobrecargada, lo que puede pasar con tráfico alto **de todos los usuarios**: no es tu culpa y no lo arreglás con configuración, solo con reintentos y con un plan de degradación.

**4) Tres medidas, en orden de implementación:**
1. **Prompt caching de la parte fija del prompt.** Primero porque es la única que sube el throughput efectivo sin cambiar el contrato con nadie: en la mayoría de los modelos de Claude solo los tokens de entrada **no** cacheados cuentan para el ITPM. **Es también la única que baja el costo.**
2. **Mover a una cola lo que no es interactivo** (los borradores de tickets que nadie está mirando en ese instante) y aplanar el pico; para volúmenes grandes, la API de Batches.
3. **Repartir entre modelos** (los límites se aplican por modelo, así que se pueden usar varios en paralelo hasta su límite respectivo) y, si después de todo eso el techo sigue siendo el problema, **subir de tier**.

Todo eso centralizado en un **model gateway** es lo que hace que estas tres palancas sean operables en vez de estar repartidas por el código.

**5) El header para confirmar en 30 segundos.** `anthropic-ratelimit-input-tokens-remaining`, más `anthropic-ratelimit-requests-remaining` para descartar el otro límite, y `retry-after` en las respuestas 429. Si el de tokens de entrada está en cero mientras el de requests tiene margen, el diagnóstico está cerrado: el cuello es el ITPM, no el RPM.

**Qué se descarta y por qué.** La medida que *no* está en la lista es "subir el máximo de réplicas", que era la propuesta del compañero: no toca el recurso agotado y empeora el síntoma. Tampoco está "reintentar más veces": sin jitter y sin respetar `retry-after`, reintentar es pedirle lo mismo al mismo balde vacío.

#### 🔴 Diseñar la caja que falta

Resolución modelo:

```mermaid
flowchart LR
    R["Replicas FastAPI<br/>y workers"] --> GW["Model gateway<br/>interfaz unificada"]
    GW --> M1["Modelo principal"]
    GW --> M2["Modelo alternativo"]
    GW --> OBS["Logs y metricas<br/>de cuota y costo"]

    classDef foco fill:#FEF2F4,stroke:#E6284E,stroke-width:2px
    class GW foco
```

**Responsabilidades, con justificación:**

| Responsabilidad | Por qué va acá |
|---|---|
| **Interfaz unificada** (una función por proveedor + un endpoint que despacha) | Si una API cambia, se actualiza un solo lugar en vez de N llamados repartidos por el código |
| **Visibilidad de cuota** (leer y exponer los headers de rate limit) | La cuota es de la organización: solo tiene sentido medirla donde pasa todo el tráfico, no por réplica |
| **Política ante rate limit** (rutear a un modelo alternativo o esperar) | Los límites son por modelo, así que el reparto solo se puede decidir en un punto que conozca el estado de todos |
| **Caching de prompts** | Es la palanca que sube el throughput efectivo; centralizada, se aplica a todos los callers sin tocarlos |
| **Control de acceso y costo** | Evita repartir el token de la organización entre servicios y permite atribuir gasto por caller |

**Qué NO hace en esta etapa:** política completa de reintentos con backoff y jitter, timeouts por caller, circuit breaker y degradación elegante. Todo eso se diseña en **M07·S16** y meterlo acá a medias es peor que no tenerlo: un reintento mal hecho multiplica el problema que pretende resolver.

**Trade-off:**
- **Gano:** un lugar donde ver la cuota y el costo, cachear, repartir entre modelos y loguear; un solo punto de cambio cuando una API se mueve.
- **Pago:** un hop más en el camino crítico (latencia) y una **dependencia dura nueva**, que multiplica mi disponibilidad compuesta; más un componente propio que mantener y desplegar.
- **Lo dispara:** 429 del proveedor con la CPU tranquila, o la necesidad de usar más de un modelo.

**¿Por qué no llamar al proveedor directo desde cada réplica?** Porque la información que necesitás para administrar la cuota es **global** y cada réplica solo ve su parte. Llamando directo: no sabés cuánta cuota queda en total, no podés decidir el reparto entre modelos, el caching se configura N veces, y el día que quieras cambiar de proveedor tocás N lugares. El gateway no sube la cuota —eso no lo puede hacer nadie más que el proveedor—: la **administra**, que es lo único que está de tu lado.

> ⚠️ Cuidado con el entusiasmo: un gateway es una caja nueva en el camino crítico de todos los requests al modelo. Si no está redundado, acabás de crear un SPOF para la parte de IA de tu producto. Dibujalo en el diagrama y anotalo para **S15**.
