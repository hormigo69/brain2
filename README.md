# brain2 - Task Management Plugin for Claude Code

Sistema de gestión de tareas basado en markdown para Claude Code. Fork mejorado del plugin [task-management](https://github.com/ttorres33/task-management) de Teresa Torres.

## Características

- **Nunca perder tareas**: Las tareas vencidas aparecen en TODAS las vistas hasta que se completen
- **Vistas en español**: Fechas y etiquetas generadas en español
- **Integración con Google Calendar**: Añade eventos del calendario a las vistas
- **Integración con Obsidian**: Usa wiki-links `[[tarea]]` para navegación fluida
- **Auto-configuración**: El wizard de setup crea toda la estructura automáticamente

## Instalación rápida

```bash
# 1. Instalar el plugin
claude plugins add hormigo69/brain2

# 2. Ejecutar el wizard de configuración
/task-management:setup

# 3. Generar tu primera vista
/task-management:today
```

El wizard creará automáticamente:
- Todas las carpetas necesarias
- Un archivo CLAUDE.md con instrucciones
- Una tarea de ejemplo

## Integración con Google Calendar (opcional)

Para ver eventos del calendario en tus vistas de tareas:

### 1. Instalar el MCP de Google Workspace

```bash
# Clonar el repositorio
git clone https://github.com/taylorwilsdon/google_workspace_mcp.git
cd google_workspace_mcp

# Instalar dependencias
pip install -r requirements.txt

# Configurar en Claude Code (seguir instrucciones del repo)
```

### 2. Habilitar en el setup

Durante `/task-management:setup`, responde "sí" cuando pregunte sobre Google Calendar e introduce tu email.

### 3. Resultado

Las vistas incluirán automáticamente los eventos:

```markdown
# Hoy - Lunes, 12 de enero

## Calendario
- 09:15-10:00 - Weekly Equipo
- 10:30-11:00 - Reunión cliente
- 15:00-16:00 - Revisión proyecto

## Tareas
- [ ] [[revisar-presupuesto]]
- [ ] [[llamar-proveedor]]
```

## Transcripción de reuniones (opcional)

Transcribe videos de reuniones usando la API de Gladia con identificación de hablantes.

### 1. Instalar dependencias

```bash
brew install ffmpeg jq
```

### 2. Configurar API key de Gladia

```bash
# Obtén tu API key en https://app.gladia.io/
echo "GLADIA_API_KEY=tu_api_key" > ~/.claude/task-management-config/gladia.env
```

### 3. Usar

```bash
/task-management:transcribir ~/Desktop/reunion.mov
```

### Resultado

Se genera un archivo markdown con la transcripción:

```markdown
# Reunión: kickoff proyecto
- **Fecha**: 2026-01-11 10:30
- **Duración**: 45 min
- **Archivo origen**: reunion.mov

---

## Transcripción

**Speaker 0:** Buenos días, empezamos con el kickoff...

**Speaker 1:** Perfecto, tengo preparada la presentación...
```

## Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/task-management:setup` | Wizard de configuración inicial |
| `/task-management:today` | Genera vista del día + archiva completadas |
| `/task-management:this-week` | Genera vista de la semana actual |
| `/task-management:next-week` | Genera vista de la próxima semana |
| `/task-management:archive` | Mueve tareas completadas a `completed/` |
| `/task-management:ideas` | Lista ideas por estado |
| `/task-management:transcribir` | Transcribe videos de reuniones con IA |
| `/task-management:about` | Muestra documentación |

## Estructura de carpetas

```
Tasks/
├── tasks/           # Tareas con fecha de vencimiento
├── ideas/           # Proyectos sin fecha definida
├── templates/       # Plantillas reutilizables
├── memories/        # Material de referencia
├── bugs/            # Issues a resolver
├── completed/       # Archivo de completadas
├── inbox/           # Captura rápida
│
├── today.md         # Vista del día (generada)
├── this-week.md     # Vista semanal (generada)
├── next-week.md     # Vista próxima semana (generada)
└── CLAUDE.md        # Instrucciones para Claude
```

## Formato de archivos

### Tarea con fecha

```yaml
---
type: task
due: 2026-01-15
tags: [proyecto-x, urgente]
---
# Revisar presupuesto Q1

Descripción de la tarea...
```

### Idea (sin fecha)

```yaml
---
type: idea
status: in-progress
tags: [personal, app]
---
# App para trackear gastos

Notas y desarrollo de la idea...
```

### Tarea recurrente

```yaml
---
type: task
due: 2026-01-15
recurrence: weekly
tags: [rutina]
---
# Weekly review

Las tareas recurrentes nunca se archivan.
```

## Vistas generadas (ejemplos en español)

### today.md

```markdown
---
date: 2026-01-11
---
# Hoy - Domingo, 11 de enero

## Calendario
- 10:00-11:00 - Reunión equipo
- 15:00-16:00 - Call cliente

## Atrasadas
- [ ] [[tarea-vencida]] (due: 2026-01-05)

## Tareas
- [ ] [[revisar-presupuesto]]
- [ ] [[llamar-cliente]]

## Ideas en progreso
- [[app-gastos]]
```

### this-week.md

```markdown
---
week_start: 2026-01-05
week_end: 2026-01-11
---
# Esta semana - Semana del 5 al 11 de enero

## Atrasadas
- [ ] [[tarea-vencida]] (due: 2026-01-05)

## Viernes, 9 de enero
- [ ] [[reunion-equipo]]

## Sábado, 10 de enero
- [ ] [[weekly-review]]
```

### next-week.md

```markdown
---
week_start: 2026-01-12
week_end: 2026-01-18
---
# Próxima semana - Semana del 12 al 18 de enero

## Lunes, 12 de enero
### Calendario
- 09:15-10:00 - Weekly Equipo
- 10:30-11:00 - Reunión cliente

### Tareas
- [ ] [[planificacion-sprint]]

## Miércoles, 14 de enero
### Calendario
- 10:30-16:00 - Jornada presentación

### Tareas
- [ ] [[presentacion-cliente]]
```

## Flujo de trabajo típico

### Diario

1. Ejecutar `/task-management:today`
2. Revisar `today.md`:
   - **Calendario**: Eventos del día
   - **Atrasadas**: Tareas que debían estar hechas
   - **Tareas**: Lo que toca hoy
3. Trabajar las tareas
4. Marcar completadas añadiendo `completed: YYYY-MM-DD`

### Semanal

1. Revisar `this-week.md` para planificar
2. Consultar `next-week.md` para anticipar
3. Ejecutar `/task-management:archive` para limpiar completadas

## Configuración

El archivo de configuración se encuentra en `~/.claude/task-management-config/config.yaml`:

```yaml
paths:
  tasks_root: "/ruta/a/tu/carpeta/Tasks"

folders:
  tasks: "tasks"
  ideas: "ideas"
  templates: "templates"
  memories: "memories"
  bugs: "bugs"
  completed: "completed"
  import: "import"

links:
  format: "obsidian"  # o "markdown"

integrations:
  research_system: false
  google_calendar: true
  google_email: "tu@email.com"
```

## Campos del frontmatter

| Campo | Valores | Obligatorio | Descripción |
|-------|---------|-------------|-------------|
| `type` | task, idea, template, memory, bug | Sí | Tipo de archivo |
| `due` | YYYY-MM-DD | Para tasks | Fecha de vencimiento |
| `completed` | YYYY-MM-DD | No | Fecha de completado |
| `recurrence` | weekly, biweekly, monthly, quarterly, yearly | No | Frecuencia |
| `status` | in-progress, noodling, someday | Para ideas | Estado actual |
| `tags` | [tag1, tag2] | No | Categorización |

## Skills incluidos

### manage-tasks

Skill que Claude usa automáticamente al crear o modificar tareas. Asegura formato consistente.

Se activa automáticamente si añades a tu CLAUDE.md:

```markdown
**Al crear o actualizar tareas:** Use the manage-tasks skill.
```

## Mejoras sobre el original

### v0.2.5 - Transcripción de reuniones
- Nuevo comando `/task-management:transcribir` para transcribir videos
- Usa API de Gladia con identificación de hablantes (diarización)
- Genera markdown con la transcripción formateada

### v0.2.4 - Localización español
- Fechas en formato "Lunes, 12 de enero"
- Etiquetas en español: Hoy, Esta semana, Próxima semana, Tareas, Atrasadas
- Setup mejorado con auto-creación de carpetas y CLAUDE.md

### v0.2.3 - Tareas vencidas en vistas semanales
- Las tareas vencidas aparecen en `this-week.md` y `next-week.md`
- Nunca se pierden hasta que se completen

## Créditos

### Inspiración

Este plugin nace de ver la entrevista [Claude Code Changed How I Work](https://youtu.be/uBJdwRPO1QE?si=h7hk4oqTdNROzAvq) donde Teresa Torres explica cómo usa Claude Code para gestionar tareas.

Recursos adicionales de Teresa:
- [Canal de YouTube](https://www.youtube.com/@ProductTalkVideos)
- [Newsletter Product Talk](https://www.producttalk.org/)

### Desarrollo

- **Plugin original**: [task-management](https://github.com/ttorres33/task-management) por Teresa Torres
- **Fork con mejoras**: [brain2](https://github.com/hormigo69/brain2)
- **Asistente de desarrollo**: Claude (Anthropic)

## Licencia

MIT
