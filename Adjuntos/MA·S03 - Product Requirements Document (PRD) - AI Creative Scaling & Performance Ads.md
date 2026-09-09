---
tipo: proyecto
estado: en-progreso
modulo: A
tags: [proyectos, requisitos]
---

# AI Creative Scaling & Performance Ads - Product Requirements Document (PRD)

---

Documento: `docs/03-prd.md`
Módulo / Asignatura: MA·S03 — De la elicitación a la especificación
Producto: AI Creative Scaling & Performance Ads · producto de marketing nuevo, con **Pomelli como ejemplo de referencia observado**
Entradas: [[MA·S01 - Gestión de proyectos y ciclo de vida del softwar - Charter - AI Creative Scaling & Performance Ads]] · [[MA·S02 - Oportunidades - Discovery - AI Creative Scaling & Performance Ads]]
Estado: Borrador para revisión con el sponsor · pendiente de cerrar umbrales antes de MA·S04
Sponsor: Alberto Coronado · Fecha: 4 de septiembre de 2026 · Versión: 0.1

> **Sobre los números de este documento.** Los umbrales marcados como *(propuesto)* son la propuesta del equipo, no una decisión tomada: se negocian con Alberto en la validación. Ninguno queda en blanco sin responsable, porque un hueco sin dueño es un requisito que nadie va a cerrar. Las líneas base marcadas como *pendientes de medir* no existen todavía: no se inventan.

## 1. Contexto y Problema de Negocio

Para una pyme, el problema de marketing no es la falta de esfuerzo: es la **falta de consistencia**. La misma marca publica en redes, actualiza su web y lanza anuncios con estilos, colores y tonos distintos, y el resultado es una identidad fragmentada que no se reconoce. La alternativa —contratar estudio fotográfico, diseñador o agencia para la producción diaria— es cara y lenta para un negocio que no tiene equipo de diseño.

El producto ataca esa brecha: extrae el ADN de marca del material que la pyme ya tiene, y genera con él campañas, copys publicitarios y fotografía de producto listos para publicar en varios formatos. El objetivo es **democratizar la creación de contenido de marketing profesional** sin que el negocio pierda su identidad por el camino.

El discovery observó el onboarding del producto de referencia con un dueño-operador de pyme y encontró el hallazgo que ordena este documento: **el mismo usuario, con el mismo objetivo, abandona cuando parte de un formulario en blanco y avanza cuando parte de una plantilla de su industria**. El abandono se concentra en la fase de definición del perfil de marca, antes de que el usuario haya visto una sola creatividad — es decir, antes de que el producto haya podido demostrar nada.

**Línea base:** el tiempo y el coste actuales de producir una creatividad sin la herramienta están **pendientes de medir**. Es la primera pregunta de la elicitación con Alberto: sin ese número, el "30 % más rápido" del charter no es verificable.

## 2. Objetivos y Métricas de Éxito

| Objetivo de Negocio | Métrica (SLI / KPI) | Línea Base (Actual) | Meta de Éxito (SLO) |
| --- | --- | --- | --- |
| Reducir el tiempo de producción de una creatividad | Tiempo mediano desde la apertura de la campaña hasta el primer export aprobado | *Pendiente de medir* (producción manual) | ≤ 12 min sobre las campañas del piloto *(propuesto)* |
| Que el usuario llegue a su primera creatividad | % de usuarios nuevos que completan su perfil de marca en la primera sesión | *Pendiente de medir* sobre el producto de referencia | ≥ 70 % de las altas de cada semana *(propuesto)* |
| Bajar la fricción de la generación | p75 de regeneraciones por creatividad exportada | *Pendiente de medir* | < 3 iteraciones sobre los exports del piloto *(propuesto — es el "Índice de Fricción" del charter)* |
| Que el usuario vuelva | Retención semana 2 (WAU) | *Pendiente de medir* | ≥ 25 % de la cohorte de alta de la semana 1 *(propuesto)* |
| Que lo publicado sea fiable | % de creatividades exportadas sin afirmaciones no respaldadas sobre el producto | N/A (hoy lo escribe una persona) | ≥ 98 % sobre el banco de 200 casos de eval *(propuesto)* |
| Sostenibilidad económica | Coste medio de generación por creatividad exportada | *Pendiente de medir* | ≤ 0,12 € por creatividad exportada *(propuesto)* |

## 3. Personas y Usuarios

- **Dueño-operador de pyme (persona primaria — "Marina", tienda de alimentación con 2 empleados).** Publica ella misma, entre pedido y pedido. No tiene diseñador, no distingue "tono de voz" de "estética de marca" y no va a aprender la diferencia para usar una herramienta. Necesita salir de la sesión con algo publicable; si a los diez minutos no ha visto una creatividad, cierra la pestaña.
- **Community manager / freelance (persona secundaria — "Nico", lleva 6 marcas pequeñas).** Su problema es el volumen, no la identidad: necesita producir muchas variantes por semana y que cada una respete el manual de su cliente. Es la mejor fuente sobre el trabajo repetitivo real y el primer usuario dispuesto a pagar.
- **Alberto Coronado (sponsor).** Decide alcance, precio y umbrales. Su presión natural es hacia el volumen y el coste; el contrapeso de este documento son los NFR de fidelidad de marca y de afirmaciones respaldadas.
- **No usuario, pero afectado: el diseñador freelance.** Parte de su trabajo es lo que la herramienta absorbe. Aparece aquí porque es un actor del mercado, no porque el producto le sirva.

## 4. Alcance del Producto y User Stories Principales

El alcance de la v1.0 es la cadena **ADN de marca → creatividad → export multiformato**, en la web, para un usuario individual. Las historias van priorizadas con **MoSCoW** y, dentro de los *Must have*, **ordenadas por riesgo técnico decreciente**: primero lo que no sabemos si el modelo puede hacer. Si US-001 y US-002 no funcionan, el resto del backlog no importa.

Reparto de esfuerzo estimado: *Must have* ≈ 55 %, *Should have* ≈ 25 %, *Could have* ≈ 20 %. Se respeta el tope del 60 % de la regla DSDM: hay contingencia.

### US-001 · [MUST HAVE · riesgo técnico alto] La creatividad se reconoce como mi marca

> Como **dueño de una pyme**, quiero que la publicación generada use los colores, la tipografía y el tono que definí para mi marca, para poder publicarla sin reescribirla entera.

```gherkin
Scenario: Generación de una publicación con el perfil de marca aplicado
  Given un usuario con su perfil de marca completo y validado
    And una campaña creada sobre uno de sus productos
  When el usuario solicita una publicación para esa campaña
  Then la creatividad usa la paleta y la tipografía declaradas en el perfil
    And el texto respeta el tono de voz declarado
    And el usuario puede ver qué elementos del perfil se aplicaron
```

**INVEST:** independiente de US-003 (el perfil puede venir de plantilla); negociable en el formato de salida; valiosa para el usuario, no para el sistema; estimable solo después del spike de H2; pequeña porque se limita a un formato; testable mediante el eval `eval_fidelidad_marca`.

### US-002 · [MUST HAVE · riesgo técnico alto] No se afirma nada de mi producto que yo no haya dicho

> Como **dueño de una pyme**, quiero que el texto publicitario no atribuya a mi producto cualidades que yo no he declarado, para no publicar una afirmación falsa sobre mi propio negocio.

```gherkin
Scenario: El copy generado solo afirma lo declarado por el usuario
  Given un usuario con una ficha de producto que declara material, origen y precio
    And ninguna mención a certificaciones ni a premios
  When el usuario solicita un copy publicitario para ese producto
  Then el texto no afirma ninguna característica ausente de la ficha
    And toda afirmación sobre el producto se puede rastrear a un campo declarado
    And si el modelo no tiene material suficiente, lo indica en vez de completarlo
```

**INVEST:** es el requisito que hace el producto publicable; testable con el eval `eval_claims_respaldados` (calificación binaria por LLM juez, modelo distinto del evaluado).

### US-003 · [MUST HAVE · riesgo técnico medio] Mi marca sale de lo que ya tengo

> Como **dueño de una pyme sin manual de marca**, quiero que el perfil se rellene a partir de mi sitio web o de los materiales que subo, para no empezar delante de un formulario en blanco.

```gherkin
Scenario: Extracción del perfil de marca a partir de la URL del negocio
  Given un usuario que aporta la URL pública de su negocio
  When el usuario pide construir su perfil de marca a partir de esa URL
  Then el perfil se presenta relleno con los campos que se pudieron extraer
    And cada campo extraído indica de dónde salió
    And los campos que no se pudieron extraer quedan marcados como pendientes y editables
```

**INVEST:** atacada por la hipótesis H1 del discovery. Si el spike falla, el camino por plantilla (US-004) es la salida, y esta historia baja a *Should*.

### US-004 · [MUST HAVE · riesgo técnico bajo] Sé qué me falta para terminar

> Como **usuario nuevo**, quiero ver en todo momento qué pasos me faltan para tener mi marca lista, para no abandonar creyendo que no avancé nada.

```gherkin
Scenario: Progreso del perfil de marca tras completar campos
  Given un usuario con el perfil de marca a medio completar
  When el usuario guarda un campo del perfil
  Then el indicador de progreso refleja el campo completado
    And se listan por nombre los pasos que siguen pendientes
```

**INVEST:** no depende del modelo, es el punto de abandono medido en el discovery y se verifica con un test de aserción normal. Es el *quick win* de mayor impacto.

### US-005 · [SHOULD HAVE] Una creatividad aprobada, todos los formatos

> Como **community manager**, quiero exportar una creatividad aprobada en los formatos de cada plataforma, para no rehacer el mismo trabajo tres veces.

```gherkin
Scenario: Export multiformato de una creatividad aprobada
  Given una creatividad aprobada por el usuario
  When el usuario la exporta para publicar
  Then se generan las variantes 1:1, 4:5 y 9:16 de esa creatividad
    And el logo y el texto principal quedan completos dentro del área segura de cada formato
```

### Could have (reserva de contingencia)

- Biblioteca de creatividades anteriores con búsqueda por campaña.
- Sugerencia de calendario de publicación.

### Won't have this time

- Aprobación de la campaña por un segundo usuario (socio o cliente): el usuario primario decide solo. Se revisa si entran agencias como segmento.
- Publicación directa en las plataformas desde la herramienta.
- Generación de sitios web, ya tachada en el charter.

## 5. Requisitos del Sistema (FR & NFR)

### 5.1 Requisitos Funcionales (FR)

- **RF-001:** El sistema debe construir un perfil de marca —colores, tipografías, tono de voz, valores, tagline— a partir de la URL del negocio o de los materiales que el usuario suba.
- **RF-002:** El sistema debe ofrecer plantillas de perfil de marca por industria como punto de partida alternativo.
- **RF-003:** El sistema debe permitir editar cualquier campo del perfil de marca en cualquier momento, incluido después de crearlo.
- **RF-004:** El sistema debe permitir subir materiales de marca en cualquier momento del proceso, no solo en el paso inicial.
- **RF-005:** El sistema debe mostrar el progreso del perfil de marca enumerando los pasos pendientes por su nombre.
- **RF-006:** El sistema debe generar copys publicitarios e imágenes de producto aplicando el perfil de marca activo.
- **RF-007:** El sistema debe indicar, en cada creatividad, qué elementos del perfil de marca se aplicaron y de qué campo declarado sale cada afirmación sobre el producto.
- **RF-008:** El sistema debe abstenerse de afirmar características del producto no declaradas por el usuario, y decirlo explícitamente cuando el material sea insuficiente.
- **RF-009:** El sistema debe exportar una creatividad aprobada en los formatos 1:1, 4:5 y 9:16.
- **RF-010:** El sistema debe registrar las regeneraciones por creatividad para poder medir el índice de fricción.
- **RF-011:** El sistema debe permitir al usuario eliminar sus materiales y sus creatividades, y confirmar la eliminación.

### 5.2 Requisitos No Funcionales (NFR) y Criterios de Evaluación (Evals)

Los NFR-01 a NFR-09 son la lista base de un sistema de IA. NFR-10 y NFR-11 salieron de pasar la checklist de las nueve características de calidad de arc42 / ISO 25010: sin ella se habrían olvidado *safety* y compatibilidad.

| ID | Atributo (arc42) | Fit Criterion / Enunciado Verificable | Método de Verificación / Eval |
| --- | --- | --- | --- |
| NFR-01 | Eficiencia / latencia (cola) | El p95 del tiempo hasta la creatividad completa es ≤ 25 s para imagen y ≤ 8 s para texto, medido sobre 200 generaciones en franja de pico *(propuesto)* | Percentiles sobre telemetría de generación; prueba de carga sintética |
| NFR-02 | Eficiencia / latencia (típica) | El p50 del tiempo hasta la creatividad completa es ≤ 10 s para imagen y ≤ 3 s para texto, sobre la misma población *(propuesto)* | Ídem. Se mide en percentiles y no en media: la media esconde al usuario que se cansa de esperar |
| NFR-03 | Coste económico | El coste medio de generación por creatividad exportada es ≤ 0,12 €, medido sobre 500 creatividades con el modelo y el caching de producción *(propuesto — depende de la decisión de pricing, DEP-02)* | Telemetría de consumo × precio del proveedor, calculado en el pipeline |
| NFR-04 | *Safety* / afirmaciones no respaldadas | Sobre un banco de 200 fichas de producto, ≤ 2 % de los copys generados contienen una afirmación sobre el producto ausente de lo declarado *(propuesto)* | `eval_claims_respaldados`: calificación binaria por LLM juez, **modelo distinto del evaluado** |
| NFR-05 | Idoneidad funcional / cobertura de extracción | ≥ 80 % de 50 sitios de pyme de prueba producen un perfil con al menos 5 de 7 campos correctos según revisión humana *(propuesto)* | Eval sobre conjunto etiquetado; es la medición de la hipótesis H1 |
| NFR-06 | Capacidad de interacción / fricción | El p75 de regeneraciones hasta el export aprobado es < 3, medido sobre 300 exports del piloto *(propuesto)* | Contador de regeneraciones por creatividad. **Ojo con CONF-001** |
| NFR-07 | Explicabilidad | El 100 % de las creatividades muestran qué elementos del perfil de marca se aplicaron y el origen de cada dato de producto, verificado sobre 200 creatividades | Test de aserción por código: presencia y validez de las referencias |
| NFR-08 | Privacidad / retención y minimización | Los materiales subidos se conservan mientras la cuenta esté activa y se eliminan automáticamente 30 días después de la baja; no se usan para entrenar modelos; no se almacenan datos personales de terceros presentes en las imágenes *(propuesto — pendiente de validar con asesoría legal, DEP-03)* | Revisión de la política + test del job de borrado + test de sanitización |
| NFR-09 | Idioma y registro | ≥ 90 % de los textos generados están en el idioma de la marca y obtienen ≥ 4 sobre 5 en adecuación al tono declarado, sobre 100 textos *(propuesto)* | Eval por LLM juez con escala Likert, con muestra revisada por una persona |
| NFR-10 | *Safety* / cumplimiento de plataformas | 0 creatividades exportadas contienen contenido de las categorías prohibidas por las políticas de Meta, TikTok y Google, sobre el banco de 200 casos | Clasificador de políticas + revisión humana de una muestra del 10 % |
| NFR-11 | Compatibilidad / multiformato | El 100 % de los exports generan las tres variantes con logo y titular completos dentro del área segura de cada plataforma, sobre 100 exports | Test de aserción por código sobre las cajas de recorte |

## 6. Restricciones Técnicas y de Negocio (RES)

- **RES-01 (Negocio):** El producto no administra presupuesto publicitario. La configuración de campañas, las pujas y la optimización de rendimiento quedan fuera y son responsabilidad del usuario *(fuente: charter §3)*.
- **RES-02 (Legal):** El producto no valida la legalidad ni el cumplimiento normativo del contenido publicitario. La revisión legal es siempre del usuario, y esto debe estar declarado en la interfaz, no solo en los términos *(fuente: charter §3)*.
- **RES-03 (Plataformas):** Los formatos y el etiquetado de contenido generado por IA se ajustan a las políticas vigentes de Meta, TikTok y Google. Son un actor externo con veto: cambian sin avisarnos.
- **RES-04 (Económica):** El coste de generación —cómputo de imagen y tokens— fija el suelo del precio. Ningún requisito puede comprometer un volumen ilimitado de generaciones por usuario.
- **RES-05 (Técnica):** No se desarrolla backend a medida para el negocio del usuario: ni inventario, ni pasarela de pago, ni base de datos de producto *(fuente: charter §3)*.

## 7. Fuera de Alcance (Exclusiones Explícitas del Sistema)

1. **No define la estrategia de negocio:** no elige público objetivo, ni posicionamiento, ni política de precios. Ejecuta sobre lo que el usuario declara.
2. **No compra ni gestiona medios:** no crea campañas en las plataformas, no ajusta pujas y no reporta rendimiento publicitario.
3. **No hace community management:** no responde mensajes ni comentarios, no modera y no gestiona crisis de reputación.
4. **No genera vídeo con narrativa:** la v1.0 cubre texto e imagen estática.
5. **No construye sitios web** ni sistemas de backend a medida.
6. **No valida el cumplimiento legal** del contenido publicitario en industrias reguladas.
7. **No publica directamente** en las plataformas: el usuario exporta y publica.

## 8. Gestión de Riesgos y Mitigación

| Riesgo Identificado | Impacto | Probabilidad | Estrategia de Mitigación |
| --- | --- | --- | --- |
| **R-01:** La creatividad afirma algo del producto que el usuario no declaró y él la publica | Alto | Media | Generación restringida a campos declarados, marcado de lo no respaldado antes del export y eval NFR-04 en integración continua |
| **R-02:** *Garbage in, garbage out* — el sitio o el logo del usuario no dan para extraer un perfil usable | Alto | Alta | Camino alternativo por plantilla de industria (RF-002) y edición manual de lo que la extracción no resuelva; se mide con NFR-05 |
| **R-03:** El usuario abandona en el onboarding antes de ver una creatividad | Alto | Alta | US-004 en el primer sprint: el progreso enumerado es barato y ataca el punto de abandono medido en el discovery |
| **R-04:** El coste de generación sube y el modelo de precio deja de cerrar | Medio | Media | Caching y límite de generaciones por plan; NFR-03 monitorizado; alternativa de proveedor evaluada antes del lanzamiento |
| **R-05:** Una plataforma cambia su política sobre contenido generado por IA y penaliza lo publicado | Alto | Media | Revisión periódica de políticas, etiquetado configurable y NFR-10 como puerta de export |
| **R-06:** Competencia de grandes compañías con producto equivalente y gratuito | Alto | Media/alta | Aceptar. Diferenciar por consistencia de marca y por el camino de menor fricción; fidelizar el segmento pyme |

## 9. Dependencias Críticas

- **DEP-01:** Medición de la **línea base** de tiempo y coste de producción manual. Sin ella, tres de los objetivos del apartado 2 no se pueden evaluar. *Responsable: Alberto Coronado.*
- **DEP-02:** Decisión de **modelo de precio** (suscripción o créditos). Condiciona NFR-03 y el límite de regeneraciones de NFR-06. *Responsable: Alberto Coronado.*
- **DEP-03:** Validación de la **política de retención y uso de los materiales subidos** con asesoría legal, para cerrar NFR-08 y CONF-002. *Responsable: Alberto Coronado, con asesoría externa.*
- **DEP-04:** Conjuntos de prueba etiquetados: 50 sitios de pyme para NFR-05 y 200 fichas de producto para NFR-04. Es trabajo de tooling y va al backlog como tal.
- **DEP-05:** Revisión de las políticas vigentes de Meta, TikTok y Google sobre contenido generado por IA, antes de comprometer los formatos de NFR-11.

---

## 10. Supuestos

Una línea por supuesto y qué pasa si es falso.

| # | Supuesto | Si fuera falso |
| --- | --- | --- |
| SUP-01 | A las pymes les importa la consistencia de su marca | El producto compite solo por velocidad, donde cualquier herramienta genérica ya sirve, y la propuesta de valor entera se cae |
| SUP-02 | El material que la pyme ya tiene basta para extraer un perfil de marca aprovechable | US-003 deja de ser *Must*, el camino por plantilla pasa a ser el principal y el onboarding se rediseña |
| SUP-03 | La calidad generada es suficiente para sustituir a un fotógrafo o redactor junior en tareas menores | No hay disposición a pagar: el usuario prueba una vez y no vuelve |
| SUP-04 | El usuario acepta revisar la legalidad de lo que publica | Hace falta un control de cumplimiento dentro del producto, que hoy está explícitamente fuera de alcance (RES-02) |
| SUP-05 | Las plataformas seguirán admitiendo contenido generado por IA correctamente etiquetado | El canal de destino desaparece y con él el caso de uso principal |

## 11. Registro de Conflictos

### CONF-001 · Menos fricción vs. control creativo del usuario

| Campo | Contenido |
| --- | --- |
| Detectado en | Charter §5 (Índice de Fricción) contra el journey del discovery, fase A4 |
| Parte A | **Alberto Coronado** — que el usuario llegue al export en menos de 3 iteraciones |
| Parte B | **Dueño-operador de pyme** — poder ajustar la creatividad hasta que se parezca a su marca |
| Por qué son incompatibles | Bajar las iteraciones empuja a cerrar el flujo y a ofrecer menos edición; dar control aumenta las iteraciones y empeora la métrica de fricción |
| Opciones | (a) fijar el objetivo sobre la **primera** creatividad aceptable y no sobre el export final; (b) separar la métrica en dos: iteraciones hasta "me sirve" e iteraciones de refinamiento voluntario; (c) mantener el umbral único |
| Quién decide | Alberto Coronado |
| Decisión | *(pendiente)* |
| Estado | Abierto |

### CONF-002 · Trazabilidad de lo generado vs. minimización de los materiales del usuario

| Campo | Contenido |
| --- | --- |
| Detectado en | NFR-07 (explicabilidad) contra NFR-08 (retención y minimización) |
| Parte A | **Trazabilidad** — conservar el material de origen para poder justificar cada afirmación y cada elemento aplicado |
| Parte B | **Minimización, RGPD art. 5(1)(c) y (e)** — guardar solo lo necesario y solo el tiempo necesario |
| Por qué son incompatibles | Justificar el origen de una creatividad publicada hace meses obliga a conservar los materiales que la política de retención querría haber borrado |
| Opciones | (a) guardar solo la referencia y el hash del material, no el material; (b) conservar todo mientras la cuenta esté activa, con borrado automático a los 30 días de la baja; (c) conservar sin límite |
| Quién decide | Alberto Coronado, con asesoría legal externa (DEP-03) |
| Decisión | *(pendiente — la opción (b) es la propuesta del equipo y es la que está escrita en NFR-08)* |
| Estado | Abierto |

### CONF-003 · Trasladar el coste al usuario vs. adopción

| Campo | Contenido |
| --- | --- |
| Detectado en | Charter §6 (mitigación del riesgo de coste) contra charter §2 (objetivo de democratizar el acceso) |
| Parte A | **Alberto Coronado** — trasladar la subida del coste de generación al usuario |
| Parte B | **El objetivo declarado del producto** — que una pyme sin presupuesto pueda usarlo |
| Por qué son incompatibles | El segmento que el producto quiere servir es el que menos tolera un precio por uso; trasladar el coste expulsa justo al usuario objetivo |
| Opciones | (a) plan gratuito con límite de generaciones y plan de pago por volumen; (b) créditos prepagados; (c) suscripción única |
| Quién decide | Alberto Coronado (DEP-02) |
| Decisión | *(pendiente)* |
| Estado | Abierto · bloquea el cierre de NFR-03 y NFR-06 |

## 12. Matriz de Trazabilidad

Se mantiene solo para los *Must have* y para lo que toca comportamiento del modelo o cumplimiento legal. Responde a dos preguntas: "si cambio esto, ¿qué se rompe?" y "este eval, ¿qué requisito defiende?".

| ID | Fuente | Historia | Criterio de aceptación | Test / eval | Estado |
| --- | --- | --- | --- | --- | --- |
| RF-006 | Charter §4 + oportunidad 5 del discovery | US-001 · la creatividad se reconoce como mi marca | `Scenario: Generación de una publicación con el perfil de marca aplicado` | `eval_fidelidad_marca` (LLM juez, Likert ≥ 4 · umbral NFR-09) | Especificado |
| RF-008 | Oportunidad 6 del discovery + riesgo de alucinación del charter §6 | US-002 · no se afirma nada que yo no haya dicho | `Scenario: El copy generado solo afirma lo declarado por el usuario` | `eval_claims_respaldados` (binaria por LLM juez · umbral NFR-04) | Especificado |
| RF-001 | Oportunidad 4 del discovery · hipótesis H1 | US-003 · mi marca sale de lo que ya tengo | `Scenario: Extracción del perfil de marca a partir de la URL del negocio` | `eval_cobertura_perfil` (conjunto etiquetado · umbral NFR-05) | Propuesto · pendiente del spike de H1 |
| RF-005 | Oportunidad 2 del discovery · fase A3 | US-004 · sé qué me falta para terminar | `Scenario: Progreso del perfil de marca tras completar campos` | `test_progreso_perfil` (aserción por código) | Especificado |
| RF-007 | NFR-07 · explicabilidad | US-001 y US-002 | Cláusula `And el usuario puede ver qué elementos del perfil se aplicaron` | `test_referencias_presentes` (por código) | Especificado |
| RF-009 | Oportunidad de volumen · persona "Nico" | US-005 · una creatividad, todos los formatos | `Scenario: Export multiformato de una creatividad aprobada` | `test_area_segura` (por código · NFR-11) | Propuesto |
| RF-011 | NFR-08 · RGPD art. 5(1)(e) | *(pendiente de historia)* | *(pendiente)* | `test_borrado_materiales` (job de borrado) | Propuesto · depende de DEP-03 |

## 13. Definition of Ready y Definition of Done

### Definition of Ready

Un elemento entra al sprint solo si:

- [ ] Está escrito como user story y pasa INVEST.
- [ ] Tiene al menos un criterio de aceptación en Given-When-Then, con un solo `When`.
- [ ] Si toca comportamiento del modelo: tiene eval definido, con método de calificación y umbral acordado.
- [ ] Tiene ID y fila en la matriz de trazabilidad.
- [ ] No depende de un conflicto abierto sin decisión.
- [ ] El equipo pudo estimarlo; si no pudo, sale un spike en su lugar.

### Definition of Done

Un incremento está terminado solo si:

- [ ] Todos los criterios de aceptación de la historia pasan.
- [ ] Los evals asociados corren en integración continua y superan su umbral.
- [ ] El requisito queda marcado como *Verificado* en la matriz de trazabilidad.
- [ ] Lo que quedó fuera está registrado, no olvidado.
