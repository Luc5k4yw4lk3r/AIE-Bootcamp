---
tipo: tema
tags: [agentes, llm]
---

# Claude y MCPs

Material sobre Claude Code como agente de programación: qué es, cómo se le añaden capacidades con *skills* y subagentes, y cómo se conecta a herramientas externas vía MCP.

## Introducción a Claude Code

Serie oficial de Anthropic, en orden:

1. [What is Claude Code?](https://www.youtube.com/watch?v=fl1DSmwQKKY&list=PLmWCw1CzcFilebjK89WLb5cAvM8K0cLB3&index=1&pp=iAQB) — qué es y para qué sirve el agente en la terminal.
2. [What are skills?](https://www.youtube.com/watch?v=bjdBVZa66oU&list=PLmWCw1CzcFim_hkruZSlABOUOAAQ5JMyo) — cómo empaquetar instrucciones reutilizables para que el agente las cargue cuando hacen falta.
3. [Using subagents effectively](https://www.youtube.com/watch?v=n5LoKZ8Oa-A&list=PLmWCw1CzcFilWIFAY4hapAgFtGB7UlvVQ) — delegar tareas independientes a agentes secundarios.

## MCPs

**MCP** (*Model Context Protocol*) es el estándar que permite conectar un modelo a herramientas y fuentes de datos externas: una base de datos, una API, un sistema de archivos.

- [Presentación sobre MCPs (Drive)](https://drive.google.com/file/d/1hbcU0vQPeNHOEkMkzrUNJSlnA4X8X0_i/view?usp=sharing)

## Directorios de skills

Colecciones de skills ya hechas, para instalar en lugar de escribirlas desde cero:

- [skills.sh](https://www.skills.sh/)
- [agentskills.io](https://agentskills.io/home)

> [!question] Pendiente
> Probar una skill de estos directorios y anotar acá cómo fue la instalación.

## Relacionado

- [[n8n]] — la alternativa no-code para automatizar con agentes.
- [[Prompting - Curso de Andrew Ng]] — cómo escribir las instrucciones que recibe el agente.
