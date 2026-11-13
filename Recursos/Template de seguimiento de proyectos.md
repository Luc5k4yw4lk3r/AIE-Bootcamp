# Nombre del proyecto\]: ficha de seguimiento

Nov 13, 2026 · @Luciano

Plantilla: duplicá este documento por proyecto y reemplazá lo que está entre corchetes.

## Encabezado

| Campo | Valor |
| --- | --- |
| Proyecto | \[nombre\] |
| Equipo | \[alumnos\] |
| Fase actual | \[fase del documento de requerimientos\] |
| Semáforo |  |
| Última revisión | \[fecha\] |

## Enlaces

Solo la versión vigente de cada documento.

| Recurso | Enlace |
| --- | --- |
| Acta, requerimientos y arquitectura | \[enlace\] |
| Repositorio | \[enlace\] |
| Diagrama de arquitectura | \[enlace\] |
| Deploy | \[enlace\] |
| STATUS.md del repo | \[enlace\] |
| Tablero de issues | \[enlace\] |

## Hitos

Un hito por fase. El criterio de hecho es algo que se puede mostrar en una demo.

| Fase | Criterio de hecho | Estado | Fecha objetivo |
| --- | --- | --- | --- |
| \[Fase 1\] | \[qué se puede mostrar\] |  | \[fecha\] |
| \[Fase 2\] |  |  |  |
| \[Fase 3\] |  |  |  |

## Bitácora de check-ins

Una fila por revisión, la más nueva arriba.

| Fecha | Hecho | Próximo | Bloqueos | Acuerdos | Semáforo |
| --- | --- | --- | --- | --- | --- |
| \[fecha\] | \[qué se terminó\] | \[qué sigue\] | \[qué frena\] | \[qué se acordó\] |  |
|  |  |  |  |  |  |

## Pendientes

Ordenados por dependencia: primero lo que desbloquea al resto. Si viven como issues de GitHub, alcanza con el enlace.

| Pendiente | Hito | Issue | Estado |
| --- | --- | --- | --- |
| \[tarea\] | \[fase\] | \[enlace\] |  |
|  |  |  |  |
|  |  |  |  |

## Bloqueos y riesgos

Lo que frena hoy o puede frenar la próxima fase.

| Bloqueo o riesgo | Responsable | Desde | Qué hace falta para destrabarlo |
| --- | --- | --- | --- |
| \[descripción\] | \[nombre\] | \[fecha\] | \[acción\] |
|  |  |  |  |

## Decisiones

Qué se decidió y por qué, la más nueva arriba.

| Fecha | Decisión | Por qué |
| --- | --- | --- |
| \[fecha\] | \[decisión\] | \[motivo\] |
|  |  |  |

## Recursos

- **Apps símiles:** \[enlaces a repos o productos parecidos\]
- **Skills para el proyecto:** \[lista de skills\]

## Checklist de arranque

- [ ] Inicializar el repo con el template de inicialización
- [ ] Cambiar el nombre del proyecto en el template y quitar n8n si no hace falta
- [ ] Escribir el documento de requerimientos priorizado por fases
- [ ] Pasarle a Claude el documento de inicialización y el PRD
- [ ] Crear los hitos como milestones en GitHub y cargar los pendientes como issues
- [ ] Crear `STATUS.md` en el repo y pedirle al agente que lo actualice al cerrar cada sesión
