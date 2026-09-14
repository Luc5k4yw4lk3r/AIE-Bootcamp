
# Evento
Link: https://valencia.aitinkerers.org/p/agents-everywhere-bots-channels-more-global-hackathon

**Sponsors**:
- OpenAI
- Openrouter
- CopilotKit
## Investigacion de sponsors
- Ultimas novedades
	-  Promocion de ultimas tecnologias
- Documentacion
- Como usar sus plataformas
- Ver si promocionaron alguna otra hackathon

## Herramientas propuestas por el evento
- **At work:** Slack, Teams, email, documents, calendars, tickets, support, or live collaboration
- **In your pocket:** messaging, mobile, notifications, and short asynchronous moments
- **On the web:** browsers and software where an agent can research, navigate, transact, or take action
- **In the room:** voice, vision, wearables, robotics, and other physical-world interfaces

### Seleccionar e investigar algunas herramientas
**Slack**
- Como integrarse
- Que apps, agentes e integraciones existen en slack actualmente
**Documents**
- Google docs
**Voice**
- Elevenlabs
**Copiar extensiones de chrome**

# Herramientas
OpenAI
- https://openai.com/codex/
- Codex CLI
	- npm i -g @openai/codex
	- Simil claude code
- Codex IDE extension
# Ideas
## Datos

## Exploracion de ideas
https://chromewebstore.google.com/
Slack marketplace de apps y agentes
https://academy.openai.com/public/collections/education-ai?linkMenu=Education&slugs=education-ai
https://academy.openai.com/public/courses/ai-for-educators-lc8j1

# Preparación de entorno de trabajo
## Pasos para armar mi entorno de trabajo
Creo mi carpeta del proyecto en workspace

Arquitectura: https://drive.google.com/file/d/11X259pKdbqgirVebSEH_743PvkRXZ5-i/view?usp=sharing

Inicializo con un prompt con claude

```
Quiero armar un template para inicializar mi entorno de trabajo:

SPEC DRIVEN DEVELOPMENT
Voy a usar spec. Tomar como referencia como se implemento aca:
https://github.com/mouredev/hello-sdd/tree/main/habits-cli/specs

OPEN KNOWLEDGE FORMAT - OKF
Quiero usar este formato para las specs
https://github.com/GoogleCloudPlatform/open-knowledge-format

N8N
Quiero instalar MCP a n8n y las skills
https://docs.n8n.io/connect/connect-to-n8n-mcp-server

claude mcp add --transport http n8n-mcp http://localhost:5678/mcp-server/http \ --header "Authorization: Bearer <TU_TOKEN_N8N_MCP>"

skills n8n
https://github.com/czlonkowski/n8n-skills

VARIABLES DE ENTORNO
Guardar todas las variables de entorno en un .env

BASE DE DATOS
Voy a usar la base de datos neon
npx neon@latest init
psql 'postgresql://USER:TU-PASS@URL/neondb?sslmode=require&channel_binding=require'

GIT
Generar .gitignore
No comitear nada por el momento
Quitar a Claude como colaborador del repo

```

## Que pasa si me piden trabajar con una tecnologia que no conozco
- Buscar la documentación de la librería o el software a usar.  Ejemplo:
```
[https://docs.copilotkit.ai/](https://docs.copilotkit.ai/)

Explicame que es esto y como se podria usar para estas: " idea1, idea2"
```
- Buscar si hay MCP o skill de dicho software para poner en Claude

# Síndrome del impostor
Como evitarlo y entender nuestro valor. 

**Somos los nuevos**: Las responsibilidades técnicas son de los que ya forman parte de industria.
**Presentacion y comunicación**:  Si somos de negocio, tenemos que solicitar que nos expliquen  para poder comunicarlo en pitch.  
**Ideas**: Si somos de negocio llevar problemas o ideas concretas para trabajar en una posible solución.  **Esto es lo mas importante de una hackathon**. 

**Roles y Organización con el equipo**
- Si nuestro compañero es fuerte en backend nosotros tomamos roles de front con v0
- Si nuestro compañero es fuerte en front nosotros podemos hacer cosas de backend con n8n
- Si es un equipo fuerte técnicamente tomar el rol de comunicación o investigación. Preguntar y entender bien el problema.

# Notas
- **Desactivar Claude Code como  como colaborador**
	- Configurar el claude.json
	- no subir el claude.md