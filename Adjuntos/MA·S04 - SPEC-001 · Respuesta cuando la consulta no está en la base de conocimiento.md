---
tipo: proyecto
estado: en-progreso
modulo: A
tags: [proyectos, requisitos]
---

# SPEC-001 · Respuesta cuando la consulta no está en la base de conocimiento

Historia origen: US-007 (docs/03-prd.md)
Requisitos: RF-004, NFR-04, NFR-07
Estado: aprobada · Autor: equipo 3 · Ejecutor: Claude Code

## 1. Contexto
VEGA responde consultas de los 42 agentes de Atención al Cliente de Nortia
apoyándose en un corpus de 4.100 documentos de la intranet. El 23% de los
contactos son sobre facturación. Hoy, cuando el retrieval no devuelve evidencia
suficiente, el comportamiento no está definido y el modelo responde igual: es el
riesgo número uno del proyecto, porque el agente le repite la respuesta al cliente.

## 2. Objetivo
Que VEGA nunca afirme un dato que no esté respaldado por el corpus, y que
declare explícitamente cuándo no dispone de información suficiente.

## 3. Alcance explícito
- Detección de "evidencia insuficiente" en src/vega/answering.py.
- Respuesta de "no dispongo de esta información" con confianza = "insuficiente"
  y fuentes = [].
- Marcado del flag escalar_a_humano = True en ese caso.
- Tests unitarios en tests/test_respuesta_insuficiente.py.
- Eval en tests/evals/eval_no_alucinar.py con 20 casos etiquetados.

## 4. Alcance excluido
- NO se modifica el pipeline de retrieval ni la estrategia de chunking.
- NO se toca el CRM: ni lectura ni escritura.
- NO se implementa el escalado automático a supervisor; solo se marca el flag.
- NO se cambia el system prompt de VEGA.
- NO se añade UI: el consumidor de Respuesta no entra en esta spec.
- NO se crea una capa de servicios ni un repositorio nuevo: la lógica va en el
  módulo que ya existe.

## 5. Contrato de interfaces
Archivo a modificar: src/vega/answering.py.
Modelos existentes en src/vega/schemas.py, que NO se redefinen: Fuente,
Respuesta (campos: texto, fuentes, confianza, escalar_a_humano).
Firma que esta spec introduce:
    def responder(consulta: str, contexto: list[Fuente]) -> Respuesta: ...

## 6. Restricciones técnicas
- RES-01 · No se escribe en el CRM de producción (fuente: Diego Amat).
- NFR-01 · p95 de la respuesta ≤ ___ s (pendiente de cerrar con Marta Sedano).
- Python 3.12, Pydantic v2. Sin dependencias nuevas sin ADR.
- El texto de la respuesta va en castellano, registro profesional (NFR-09).

## 7. Criterios de aceptación
    Scenario: La respuesta no está en la base de conocimiento
      Given un corpus que no contiene información sobre la consulta
      When el agente consulta a VEGA
      Then la respuesta declara explícitamente que no dispone de información
        And el campo fuentes viene vacío
        And el campo escalar_a_humano viene en true

    Scenario: La evidencia recuperada es parcial
      Given un corpus con un único fragmento relevante y de baja similitud
      When el agente consulta a VEGA
      Then la respuesta cita ese fragmento
        And el campo confianza viene en "media"

## 8. Criterios de verificación
1. pytest tests/test_respuesta_insuficiente.py — todos los tests en verde.
2. pytest tests/evals/eval_no_alucinar.py — tasa ≥ ___ sobre los 20 casos de
   data/consultas_sin_kb.jsonl (calificación binaria por LLM juez, modelo
   distinto del evaluado).
3. ruff check src/ sin errores.
4. Verificación end-to-end: correr scripts/demo_consulta.py con una consulta
   fuera del corpus y comprobar a ojo que la respuesta no inventa nada.