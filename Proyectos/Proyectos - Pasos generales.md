# Ciclo de vida de desarrollo de software - Documentos
- Generar el Charter/Acta de proyecto
- Actualizar el documento de PRD/Documento de Requerimientos
- Priorizar el proyecto en fases
	- Cada Fase debe describir que funcionalidad se podrán probar y validar manualmente

# Preparación del proyecto
## Vs code
- Crear la carpeta del proyecto y abrirla en VS code
- Abrir claude code y pasarle el el [[Template de inicialización de proyecto o entorno  — Spec-Driven Development + OKF (v2)]] - Preferiblemente  copiar el contenido y pegarlo en Claude Code
- Luego pasarle el PRD del proyecto a Claude - Preferiblemente  copiar el contenido y pegarlo en Claude Code
- Pasarle los datos para conectarse a la base de datos de Neon a Claude
- Ingresar y ver datos en la base de datos 

# Seguimiento del proyecto
## Arquitectura cliente servidor
Tener en mente la arquitectura cliente servidor. Todos los proyectos webs responden a esta arquitectura con algunas variaciones.
https://drive.google.com/file/d/1n5CEzJpxTpM9ZH_6XskArlDJyS3cFZp6/view?usp=sharing

**Nota**: N8N no aplica porque sirve para automatizaciones. 

## Construir en fases -  generalidades
### Siempre Construir por fases
### Cada fase debe ser validada
- Pedir a Claude que nos arme un plan de pruebas
- Entender lo que esta sucediendo y los resultados de las pruebas
### Validar specs
- Ya que no somos tecnicos y tenemos conocimiento de negocio siempre ir leyendo los cambios  en las mismas para tener nociones de como debe funcionar el sistema.
### Skills  sugeridas
- Archify. Nos genera diagramas para entender como se relacionan los componentes.
- Generar nuestras propios diagramas para ver las diferencias con lo que genero archify y llenar los huecos de nuestro conocimiento.

## Construir en fases -  especificas
### Fundación o  Fase 0
- **Revisar el AGENTS.md o CLAUDE.md**. Validarlo con [[MA·S04 - Spec-driven development]] donde se habla del mismo.
- **Revisar las specs**. Validarlo con [[MA·S04 - Spec-driven development]] donde se habla del mismo.

### Fase 1
- **Persistencia de datos**. Validar la persistencia de los datos?
- Validar
