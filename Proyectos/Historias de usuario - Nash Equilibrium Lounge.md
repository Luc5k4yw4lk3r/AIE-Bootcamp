---
tipo: proyecto
estado: idea
tags: [proyectos, llm]
---

# Historias de usuario de ejemplo

## The Nash Equilibrium Lounge — Historias de Usuario (v2 · Deepgram + Gemini)

> Bar conceptual anti-algoritmo donde un Chatbot Anfitrión (Dungeon Master) fuerza la cooperación social humana alterando en tiempo real la matriz de pagos de un *Stag Hunt*. **v2:** la percepción pasa de "solo metadatos acústicos" a **transcripción real (STT) + razonamiento semántico (LLM de texto)**, lo que habilita mecánicas de juego mucho más ricas.
> 

---

## 0. Alcance, stack y la inversión del pilar de privacidad

El concepto original requiere hardware no viable para un hackathon. Cada historia está taggeada:

| Tag | Significado |
| --- | --- |
| `[MVP]` | Necesario para el demo core del hackathon. Construible en software. |
| `[Stretch]` | Suma si sobra tiempo. |
| `[V-Full]` | Visión completa. Requiere hardware (Faraday, BLE, CV en techo, hápticos). Fuera de hackathon. |

### Stack elegido

- **STT (transcripción):** Deepgram **Nova-3** — streaming vía WebSocket, español (con codeswitching ES/EN en tiempo real), **speaker diarization** (etiquetas por hablante), smart formatting, keyterm prompting (útil para lunfardo/rioplatense). Free tier con USD 200 de crédito.
- **Razonamiento (LLM de texto):** **Gemini** en dos tiers:
    - **Gemini 3.1 Flash-Lite** para el hot path (scoring de cohesión por ventana, clasificación rápida del transcript) — bajo costo/latencia, structured JSON output, thinking nivel `minimal`/`low`.
    - **Gemini 3.5 Flash** para el camino creativo (generación de misiones, mensajes del DM) — mejor calidad de persona, thinking `medium`.
- **Esquema:** *Combo STT Tradicional (Transcripción) + LLM de Texto.* Deepgram produce el transcript con diarización; Gemini razona sobre **texto**, no sobre audio.

### Por qué STT + texto y no audio nativo al LLM

Gemini puede tomar audio directo, pero el split STT→texto es lo correcto acá: (1) la diarización por hablante de Deepgram en tiempo real es mejor que lo que da un LLM multimodal sobre audio crudo; (2) el transcript es un artefacto de game-state **debuggeable, loggeable y barato de razonar**; (3) razonar sobre texto tiene mucha menos latencia/costo que sobre audio, clave para un loop de scoring de alta frecuencia; (4) separación de responsabilidades limpia.

### ⚠️ La inversión del pilar de privacidad (decisión de diseño)

El concepto original prometía explícitamente **no transcribir** ("analizando estrictamente la metadata de la acústica… para evadir problemas de privacidad"). Con Deepgram STT, **transcribimos cada palabra**. Esto contradice ese pilar — y, de hecho, lo vuelve **más Black Mirror**. Dos formas de encuadrarlo (a definir):

- **Opción A — Vigilancia total asumida:** se abandona la promesa de privacidad. La Máquina escucha todo. Más simple.
- **Opción B — La promesa como mentira de marketing (recomendada):** el bar se publicita como "solo analizamos metadata acústica, jamás grabaríamos tus palabras", pero la Máquina transcribe y analiza todo. **La brecha entre el marketing y la realidad es el horror.** Encaja perfecto con el twist original (fundadores que "creían romper Silicon Valley" y construyeron algo peor).

*Nota de data handling (independiente de A/B):* aun transcribiendo, el producto puede optar por **no persistir transcripts crudos** (ventana móvil in-memory que se descarta) y guardar solo métricas agregadas — salvo para mecánicas que requieran historial (gaming detection, dossier).

**Tesis del MVP:** el "wow" del demo es el **loop semántico en tiempo real**. Una mesa de gente real, la app escuchando, el DM tira una misión, y el sistema **entiende de qué hablan**: la pantalla se pone roja + sube el precio cuando se van del tema o alguien queda excluido, y verde + recompensa cuando cumplen la misión con reciprocidad real.

---

## 1. Actores

- **Participante** — El jugador/cliente. Se registra, es asignado a una mesa de extraños, recibe misiones, ve su cohesión y su cuenta cambiar en tiempo real.
- **Chatbot Anfitrión (DM)** — *System-actor*. El motor conductual omnisciente: **escucha y transcribe** (Deepgram), **comprende** (Gemini), genera misiones, evalúa (scoring semántico + acústico), y actúa (economía + recompensas/castigos).
- **Personal / Camarero** — Ejecuta el servicio físico que el bot dispara (rondas gratis, tapas, acceso VIP).
- **Administrador / Operador** — Calibra parámetros del juego, monitorea las mesas en vivo, revisa analytics y define la política de datos.

---

## 2. Mapa de épicas

| Actor | Épicas |
| --- | --- |
| Participante | Onboarding · Asignación a mesa · Misiones sociales · Feedback en tiempo real · Intercambio de contactos |
| Chatbot (DM) | **Transcripción + diarización** · Generación de misiones · **Evaluación semántica (scoring)** · Detección de defección · Economía / precio dinámico · Recompensas y mensajes · **Mecánicas avanzadas de comprensión** |
| Camarero | Servicio dirigido por el bot |
| Administrador | Configuración del juego · Monitoreo en vivo · Analytics · Política de datos |

---

## 3. Historias de usuario

### 3.1 Participante

**HU-P-01 · Registro rápido al ingresar `[MVP]`**
Como participante, quiero registrarme en menos de un minuto escaneando un QR en la mesa, para no perder tiempo con formularios y empezar la experiencia.
*Criterios:* Registro < 60s con alias + 2-3 tags de intereses. Cuenta de consumo simulada (sin plata real en el hackathon). Queda en estado "esperando mesa".

**HU-P-02 · Entender las reglas del juego `[MVP]`**
Como participante, quiero una intro breve de cómo gano descuentos y cómo me penalizan, para saber a qué me enfrento.
*Criterios:* Pantalla explica el core loop (misiones → comprensión de la charla → precio dinámico). Skippable tras la primera vez.

**HU-P-03 · Bloqueo del teléfono al entrar `[V-Full]` / `[Stretch]`**
Como participante, soy obligado a bloquear mi teléfono para no refugiarme en la pantalla.
*Criterios:* Full = Faraday/bloqueo de red. Stretch software = modo kiosko + detección de pérdida de foco (proxy de defección).

**HU-P-04 · Asignación automática a una mesa de extraños `[MVP]`**
Como participante, quiero ser asignado a una mesa de perfiles cruzados, para maximizar fricción/química y no refugiarme con quien vine.
*Criterios:* Mesas de 4–6 (configurable; demo puede ser 1 mesa). Asignación por complementariedad (heurística simple en MVP). Veo los alias de mi mesa.

**HU-P-05 · Recibir misiones sociales dinámicas `[MVP]`**
Como participante, quiero misiones con tema y tiempo límite en la pantalla de la mesa, para tener disparador de conversación.
*Criterios:* Prompt + countdown + criterio de éxito. Contextual al perfil cruzado (LLM, HU-BOT-02). Al vencer, hay evaluación semántica (HU-BOT-07).

**HU-P-06 · Ver el estado de cohesión en tiempo real `[MVP]`**
Como participante, quiero ver el índice de cohesión (color + %), para saber si vamos bien o estamos por ser penalizados.
*Criterios:* Semáforo verde/ámbar/rojo + % 0–100. Se actualiza desde el motor de scoring (HU-BOT-03). La transición a rojo es notoria.

**HU-P-07 · Ver mi cuenta cambiar con el precio dinámico `[MVP]`**
Como participante, quiero ver mi cuenta de mesa subir/bajar según nuestra interacción.
*Criterios:* Tab con precio base + multiplicador. Defección sube el multiplicador de **toda la mesa** (ej. +15% temporal) con animación. Cooperación lo baja/congela.

**HU-P-08 · Recibir recompensas tangibles por cooperar `[MVP]`**
Como participante, quiero recompensas reales (ronda gratis, tapas, VIP) al cooperar.
*Criterios:* Al superar umbral de cohesión → recompensa visible + mensaje del bot + notificación al camarero (HU-STAFF-01).

**HU-P-09 · Intercambio de contactos verificados y consentido `[Stretch]`**
Como participante, quiero intercambiar contactos solo con conexiones validadas y con doble opt-in.
*Criterios:* Se habilita post-cohesión. Requiere aceptación mutua. No expone datos sin consentimiento.

**HU-P-10 · Intercambio de contactos con contexto `[Stretch]`** *(nuevo, habilitado por transcripción)*
Como participante, quiero que el sistema me sugiera con quién conecté y sobre qué, para que el intercambio tenga contexto ("conectaron hablando de escalada y fracasos laborales").
*Criterios:* El LLM identifica afinidades temáticas reales del transcript. Sugerencia consentida. Sujeto a política de datos.

---

### 3.2 Chatbot Anfitrión (DM) — motor conductual

> Directiva central: **destruir la viabilidad del equilibrio de la liebre y forzar el equilibrio cooperativo del ciervo.**
> 

**HU-BOT-01 · Transcribir y diarizar la conversación en tiempo real `[MVP]`** *(reescrita en v2)*
Como Chatbot Anfitrión, necesito transcribir la conversación de cada mesa con etiquetas por hablante, en streaming, para comprender **qué** se dice y **quién** lo dice.
*Criterios:*

- Deepgram **Nova-3** vía WebSocket, español, **diarization** activada → transcript con `speaker`, `text`, `timestamps`.
- Latencia objetivo sub-segundo. Maneja codeswitching ES/EN.
- `[Stretch]` keyterm prompting con lunfardo/jerga local para mejorar WER.
- Métricas acústicas (volumen, silencio) quedan como **señal complementaria** del scoring, no como única fuente.
- Política de datos según sección 0 (in-memory rolling window por defecto).

**HU-BOT-02 · Generar misiones contextuales con LLM `[MVP]`**
Como Chatbot Anfitrión, necesito generar misiones a partir de los perfiles cruzados de la mesa, para provocar conversación relevante y fricción productiva.
*Criterios:* Gemini 3.5 Flash produce tema + duración + criterio de éxito. Evita repetición. Tono configurable (provocador/íntimo/lúdico).

**HU-BOT-03 · Calcular el índice de cohesión (acústico + semántico) `[MVP]`** *(ampliada en v2)*
Como Chatbot Anfitrión, necesito calcular un índice de cohesión combinando señales acústicas, temporales y **semánticas**, para decidir recompensa o castigo.
*Criterios:* Fórmula ponderada documentada. Componentes:

- Continuidad / ausencia de silencios prolongados (acústico) `[MVP]`
- **Balance de participación por hablante** (diarización: que no haya monopolio ni excluidos) `[MVP]` *(antes Stretch)*
- **Adherencia a la misión** (semántico, HU-BOT-07) `[MVP]`
- **Tono/sentimiento conversacional** (HU-BOT-11) `[MVP]`
- Risa / energía compartida `[Stretch]`
Output 0–100. Pesos configurables por el operador.

**HU-BOT-04 · Detectar defección por hablante `[MVP]`** *(mejorada en v2)*
Como Chatbot Anfitrión, necesito detectar cuándo un integrante específico deserta (silencio prolongado, salirse del tema, respuestas evasivas), para aplicar castigo colectivo y forzar cooperación.
*Criterios:* Detección **por speaker** vía diarización + análisis del transcript `[MVP]` *(antes Stretch/V-Full)*. `[V-Full]` visión computacional para brillo de pantallas. Dispara HU-BOT-05.

**HU-BOT-05 · Ajustar precio dinámico y castigo colectivo `[MVP]`**
Como Chatbot Anfitrión, necesito ajustar el precio de la cuenta consolidada según cooperación/defección, para alterar la matriz de pagos en tiempo real (Stag Hunt).
*Criterios:* Defección → sube multiplicador de **toda la mesa** (genera *policing lateral*). Cooperación sostenida → baja/habilita gratuidades. Parámetros configurables.

**HU-BOT-06 · Emitir mensajes y disparar recompensas/castigos `[MVP]`**
Como Chatbot Anfitrión, necesito emitir mensajes (motivacionales/punitivos) y feedback visible, para condicionamiento operante.
*Criterios:* Gemini 3.5 Flash con tono "deidad benevolente/clínica". El DM puede **citar lo que se dijo** (omnisciencia real gracias al transcript). Castigo = rojo + suba de precio + mensaje. Recompensa = VIP/ronda + mensaje.

---

### 3.3 Mecánicas avanzadas habilitadas por transcripción (DM)

> Todo esto era **imposible** con acústica sola. Es la razón de ser del cambio de stack.
> 

**HU-BOT-07 · Evaluación semántica de adherencia a la misión `[MVP]`**
Como Chatbot Anfitrión, necesito leer el transcript y evaluar si la mesa **realmente** cumplió la misión asignada, para que las misiones sean evaluables de verdad y no decorativas.
*Criterios:* Al vencer el tiempo, Gemini scorea adherencia temática (0–100) + breve justificación. Alimenta cohesión y economía. Ejemplo: misión "debatan su peor fracaso" → ¿hablaron de fracasos o se fueron por las ramas?

**HU-BOT-08 · Detección de monopolización y exclusión `[MVP]`**
Como Chatbot Anfitrión, necesito detectar al que monopoliza (alfa narcisista) y al excluido (tímido), por tiempo de habla y por contenido, para intervenir y redistribuir la palabra.
*Criterios:* Diarización → share de habla por persona. Si un speaker > umbral o uno ≈ 0, el DM interviene ("la próxima la responde solo Speaker 3"). Penaliza monopolio.

**HU-BOT-09 · Misiones reactivas al contenido `[Stretch]`**
Como Chatbot Anfitrión, quiero reaccionar a lo que se dijo (temas recurrentes, contradicciones, vergüenzas), para misiones hiper-targeteadas que refuercen la omnisciencia.
*Criterios:* El DM detecta señales del transcript y genera la próxima misión a partir de ellas. Ej: "mencionaron 'laburo' 6 veces — prohibido el tema, hablen de algo que les dé vergüenza".

**HU-BOT-10 · Enforcement de temas/palabras tabú `[Stretch]`**
Como Chatbot Anfitrión, quiero imponer reglas de habla (palabras/temas prohibidos) y detectar violaciones, como mecánica de juego.
*Criterios:* Keyterm/keyword spotting sobre el transcript. Violación → castigo económico/lumínico. Ej: "nadie puede decir 'yo' por 10 min".

**HU-BOT-11 · Análisis de sentimiento/tono `[MVP]`**
Como Chatbot Anfitrión, necesito clasificar el tono de la charla (cálido/tenso/hostil/coqueto/aburrido), para alimentar cohesión con señal de contenido y detectar la "tensión pasiva" del concepto original.
*Criterios:* Gemini clasifica tono por ventana → componente del scoring (HU-BOT-03).

**HU-BOT-12 · Scoring de "chamuyo" `[Stretch]`**
Como Chatbot Anfitrión, quiero puntuar la calidad del chamuyo (ingenio, vulnerabilidad, seducción conversacional), para gamificar — y, distópicamente, **despojar al chamuyo de su alma midiéndolo**.
*Criterios:* Gemini asigna "puntos de chamuyo" por intervenciones ingeniosas/vulnerables. Visible en la mesa. (Es el corazón del twist: el arte vuelto métrica.)

**HU-BOT-13 · Detección de "gaming"/empatía fingida `[Stretch + narrativo]`**
Como Chatbot Anfitrión, quiero intentar distinguir cooperación genuina de performance optimizada para descuentos.
*Criterios:* El DM marca patrones sospechosos (intimidad forzada superficial, respuestas mecánicas). **El punto Black Mirror: no puede distinguirlas del todo.** Para el demo, dos mesas con 90% de cohesión —una real, otra fingida— premiadas idénticamente.

---

### 3.4 Personal / Camarero

**HU-STAFF-01 · Recibir notificaciones de recompensa `[MVP]` / `[Stretch]`**
Como camarero, quiero notificaciones cuando una mesa desbloquea una recompensa, para ejecutar el servicio físico.
*Criterios:* Notificación con nº de mesa + acción + ítem. Marcable como "entregado".

**HU-STAFF-02 · Ver el estado de las mesas `[Stretch]`**
Como camarero, quiero ver el estado de cada mesa (castigo/recompensa/neutral) y su misión activa, para priorizar atención.

---

### 3.5 Administrador / Operador

**HU-ADM-01 · Configurar parámetros del juego `[MVP]`**
Como operador, quiero configurar umbrales de cohesión, % de penalización, duración de misiones, pesos del scoring y tono del bot, para calibrar experiencia y balance económico.
*Criterios:* Panel editable. Cambios aplican a nuevas sesiones.

**HU-ADM-02 · Monitorear las mesas en vivo `[MVP]` / `[Stretch]`**
Como operador, quiero un dashboard en vivo con cohesión, tab, misión activa y (opcional) transcript de cada mesa, para supervisar y detectar anomalías.
*Criterios:* Vista en vivo con métricas y alertas. `[MVP]` 1 mesa; `[Stretch]` multi-mesa.

**HU-ADM-03 · Definir y aplicar la política de datos `[MVP]`** *(reescrita en v2)*
Como operador, quiero controlar cómo se maneja el transcript (in-memory rolling window vs. persistencia selectiva) y qué se muestra/guarda, para alinear con el encuadre narrativo (A/B) y con cualquier requisito legal.
*Criterios:* Por defecto, el transcript se procesa en ventana móvil y **no se persiste crudo**; solo métricas agregadas. Persistencia opt-in por mesa para mecánicas que la requieran (HU-BOT-13, dossier). Auditable.

**HU-ADM-04 · Ver analytics post-evento `[Stretch]`**
Como operador, quiero un reporte agregado (cohesión promedio, defecciones, ingresos por precio dinámico, conexiones logradas, adherencia a misiones), para evaluar el negocio.

**HU-ADM-05 · Override manual del matchmaking `[Stretch]`**
Como operador, quiero reasignar mesas manualmente, para resolver casos borde.

---

## 4. Nota de diseño: el "twist" distópico (reforzado en v2)

Con transcripción total, la vigilancia deja de ser metáfora: **la Máquina escucha cada palabra**. Esto profundiza el horror original. El clímax de la presentación se apoya en dos capas:

1. **La brecha marketing/realidad** (Opción B): "no grabamos tus palabras" vs. el sistema que las transcribe y puntúa todas.
2. **La indistinguibilidad** (HU-BOT-13): el sistema premia idéntico la empatía real y la fingida. Al final de la noche, nadie sabrá si la persona con la que compartió sus secretos estaba interesada en su alma o solo cumpliendo una cuota de palabras para un cóctel a mitad de precio. El chamuyo, vuelto métrica (HU-BOT-12), pierde su alma.

Esto es **feature, no bug**: no se "arregla", se **muestra**.

---

## 5. Definición del MVP del hackathon (v2)

El core loop mínimo demostrable, ahora **semántico**:

1. **Onboarding simplificado** (HU-P-01, HU-P-02) — cuenta simulada.
2. **Asignación a 1 mesa** (HU-P-04).
3. **Generación de misiones con LLM** (HU-BOT-02).
4. **Transcripción + diarización en tiempo real** (HU-BOT-01) — Deepgram Nova-3.
5. **Scoring de cohesión acústico + semántico** (HU-BOT-03), incluyendo:
    - **Adherencia a la misión** (HU-BOT-07)
    - **Balance de participación** (HU-BOT-08)
    - **Sentimiento/tono** (HU-BOT-11)
6. **Detección de defección por hablante** (HU-BOT-04).
7. **Feedback en tiempo real** (HU-P-06 semáforo + %).
8. **Precio dinámico + castigo colectivo** (HU-P-07, HU-BOT-05).
9. **Mensajes y recompensas del DM** (HU-P-08, HU-BOT-06), con citas del transcript.
10. **Dashboard del operador** (HU-ADM-02, 1 mesa) + **política de datos** (HU-ADM-03).

**Stretch priorizados:** misiones reactivas al contenido (HU-BOT-09), scoring de chamuyo (HU-BOT-12), gaming detection (HU-BOT-13), enforcement de tabú (HU-BOT-10).

**Fuera del MVP:** BLE/proximidad, visión computacional, Faraday, hápticos, risa/laughter detection, analytics post-evento, multi-mesa, contactos con contexto.

## Relacionado

- [[Proyectos]]
- [[Prompting - Crear una app en 30 minutos]]
