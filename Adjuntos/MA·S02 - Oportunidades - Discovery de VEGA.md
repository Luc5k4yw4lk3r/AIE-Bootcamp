---
tipo: proyecto
estado: en-progreso
modulo: A
tags: [proyectos, requisitos]
---

# Oportunidades — Discovery de VEGA

**Outcome de referencia:** Bajar el tiempo medio de resolución de los contactos entrantes.
**Equipo:** [Tu Equipo] · **Fecha:** 25 de agosto de 2026

## Mapa de stakeholders
|Stakeholder|Poder|Interés|Actitud|Por qué|
|---|---|---|---|---|
|**Marta Sedano**  <br>Dir. Operaciones|Alto|Alto|Partidaria|Impulsora; su bonus depende del coste por contacto. Riesgo: su métrica puede empujar a automatizar en vez de aumentar|
|**Iván Ferreras**  <br>Resp. Atención|Medio|Alto|Opositor encubierto|Dice que le preocupa la valoración de sus agentes; teme un recorte de plantilla. Sin el eje de actitud, cae junto a Marta y el mapa miente|
|**Cristina Roa**  <br>Jurídica / DPO|Alto (veto)|Medio|Neutral condicional|Su poder es de freno, no de impulso. No sabe si entra en el AI Act|
|**Diego Amat**  <br>IT Manager|Alto (veto técnico)|Bajo-medio|Opositor blando|No quiere que nada toque el CRM de producción; su equipo está saturado|
|**Agentes (42)**|Bajo formal, decisivo real|Alto|Desconocida|Nadie les preguntó nada. Su veto se ejerce el día que deciden no usar el sistema|

## Journey map 

| #   | Fase                         | Acciones                                                             | Pensamiento                                  | Emoción               | Dolor                                                                                         |
| --- | ---------------------------- | -------------------------------------------------------------------- | -------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------- |
| 1   | Recepción del contacto       | Atiende, saluda, escucha                                             | "A ver qué toca"                             | 😐 Neutral            | —                                                                                             |
| 2   | Identificación en el CRM     | Pide DNI, busca, abre contrato                                       | "Espero que los datos estén bien"            | 🙂 Leve fricción      | Pantallas lentas, datos repartidos                                                            |
| 3   | Comprensión de la pregunta   | Repregunta, mira la factura                                          | "¿Término fijo o regularización?"            | 😐 Concentración      | El cliente no sabe nombrar lo que no entiende                                                 |
| 4   | **Búsqueda en la intranet**  | Busca por palabras clave entre 4.100 docs, compara, duda de vigencia | "¿Esta circular sigue vigente?"              | 😖 **Pozo emocional** | **60% del tiempo se va aquí**: búsqueda por keyword, sin señal de vigencia, cliente esperando |
| 5   | Construcción de la respuesta | Traduce, arma la explicación                                         | "Si me equivoco con un importe, esto vuelve" | 😕 Duda               | Miedo a dar una cifra mal; sin forma de verificar rápido                                      |
| 6   | Cierre y tipificación        | Confirma, se despide, tipifica                                       | "Ya está. El siguiente"                      | 🙂 Alivio con fatiga  | Tipificación manual; en picos se hace corriendo o mal                                         |

![[Pasted image 20260827163656.png]]

---

## Oportunidades priorizadas


| #   | Oportunidad                                                                                                                                                                  | Dolor de origen (fase)               | Impacto | Esfuerzo | Cuadrante          | Notas                                                                                                                                           |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------- | -------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Al agente le cuesta localizar con rapidez la condición específica que aplica a la factura del cliente entre miles de documentos mientras atiende la llamada[cite: 1].        | Fase 4: Búsqueda en la intranet      | 5       | 3–5      | Grandes apuestas   | *El esfuerzo está en rango porque depende de si podemos extraer información de los 4.100 documentos sin fallos[cite: 1]. Se requiere un spike.* |
| 2   | El agente necesita poder verificar con total seguridad una cifra antes de comunicársela al cliente para evitar escalar un error[cite: 1].                                    | Fase 5: Construcción de la respuesta | 5       | 2–5      | Grandes apuestas   | *Esfuerzo en rango: depende de la capacidad del modelo para no alucinar números y dar trazabilidad exacta[cite: 1].*                            |
| 3   | Al agente le cuesta identificar exactamente a qué concepto de la factura se refiere el cliente cuando este usa un vocabulario no técnico y ambiguo.                          | Fase 3: Comprensión de la pregunta   | 4       | 2        | Quick win          | -                                                                                                                                               |
| 4   | Un agente con menos de seis meses de antigüedad necesita orientación paso a paso sobre dónde empezar a buscar sin tener que interrumpir a sus compañeros veteranos[cite: 1]. | Fase 4: Búsqueda en la intranet      | 4       | 3–5      | Grandes apuestas   | *Depende de cómo estructuremos las respuestas para que sirvan de guía (esfuerzo incierto)[cite: 1].*                                            |
| 5   | El agente necesita registrar el resultado del contacto sin consumir tiempo extra de escritura manual durante los días de pico (3.400 contactos)[cite: 1].                    | Fase 6: Cierre y tipificación        | 3       | 2        | Quick win          | -                                                                                                                                               |
| 6   | El agente necesita poder compartir el fragmento exacto de la condición contractual con el cliente de forma rápida para respaldar su explicación verbal.                      | Nueva (Post-Fase 5)                  | 2       | 2        | Relleno / Sumidero | *Se descarta por ahora; aporta poco a bajar el tiempo de llamada telefónica.*                                                                   |




---

## Hipótesis a testear

### H1 — Recuperación certera de condiciones de factura (Factibilidad)
- **Creemos que:** Centralizar la búsqueda sobre el corpus completo permitirá al agente encontrar la condición aplicable en la primera consulta, sin abrir múltiples archivos[cite: 1].
- **Lo sabremos si:** Sobre un set de 30 contactos reales de factura, el documento correcto aparece entre los 3 primeros resultados en al menos 24 de ellos[cite: 1].
- **Lo abandonamos si:** El documento correcto aparece en menos de 15 casos, o si el sistema se inventa (alucina) una sola condición que no exista en el documento original[cite: 1].
- **Test:** Research spike (sin tocar el CRM de producción para respetar el veto de Diego Amat)[cite: 1].
- **Timebox:** 3 días[cite: 1].

### H2 — Seguridad al afirmar un importe (Valor / Usabilidad)
- **Creemos que:** Mostrar siempre el fragmento original de texto junto a la respuesta le dará al agente la seguridad necesaria para responder sin dudar[cite: 1].
- **Lo sabremos si:** En una simulación, los agentes confían en el dato entregado sin necesidad de abrir el PDF original en el 90% de las consultas.
- **Lo abandonamos si:** Los agentes ignoran la respuesta rápida y siguen buscando a mano el documento para re-verificar el importe por miedo a equivocarse.
- **Test:** Wizard of Oz (un humano experto busca rápidamente y envía la respuesta al agente en pruebas)[cite: 1].
- **Timebox:** 2 días.

### H3 — Traducción de jerga del cliente (Valor)
- **Creemos que:** Proveer un mapeo rápido de "términos coloquiales del cliente" a "conceptos formales de Nortia" reducirá el tiempo de la fase de comprensión de la pregunta.
- **Lo sabremos si:** Al usar un glosario rápido en 20 llamadas, la fase 3 ("Comprensión") se completa en menos de un minuto.
- **Lo abandonamos si:** El agente prefiere seguir repreguntando al cliente de forma natural en lugar de usar la herramienta.
- **Test:** Encuesta de una pregunta y prototipo (papel o pantalla estática).
- **Timebox:** 1 día.


---

## Preguntas abiertas para la elicitación de MA·S03

- ¿Qué palabras usa típicamente el cliente residencial para referirse a la "regularización" o al "término fijo" cuando no entiende la factura?
- En la fase 4, ¿cómo sabe exactamente un agente veterano que una circular antigua ha sido invalidada si no hay una marca de "vigencia" explícita en la intranet?[cite: 1]
- ¿En qué momento exacto de la llamada el agente nuevo (de las primeras 7 semanas) decide rendirse y pedirle ayuda a un veterano?[cite: 1]
- ¿Cuántas pantallas distintas del CRM abre el agente simultáneamente durante la fase 2 (Identificación) y qué datos cruza entre ellas?[cite: 1]