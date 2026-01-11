# brain2 - Task Management Plugin for Claude Code

Fork mejorado del plugin [task-management](https://github.com/ttorres33/task-management) de Teresa Torres, con funcionalidades adicionales para evitar que las tareas se pierdan.

## Objetivo

Un sistema de gestión de tareas basado en markdown que se integra con Claude Code. Diseñado para:

- **Nunca perder tareas**: Las tareas vencidas aparecen en TODAS las vistas hasta que se completen
- **Visibilidad total**: Vistas diarias y semanales generadas automáticamente
- **Integración con Obsidian**: Usa wiki-links `[[tarea]]` para navegación fluida
- **Simplicidad**: Archivos markdown planos, sin base de datos

## Mejoras sobre el original

### Tareas vencidas en vistas semanales (v0.2.3)

**Problema resuelto**: En el plugin original, si una tarea con `due: 2026-01-10` no se completaba, al día siguiente desaparecía de las vistas semanales. Solo aparecía en `today.md`.

**Solución**: Ahora las tres vistas (`today.md`, `this-week.md`, `next-week.md`) muestran una sección `## Overdue` al inicio con todas las tareas vencidas:

```markdown
## Overdue
- [ ] [[tarea-olvidada]] (due: 2026-01-05)
- [ ] [[otra-tarea-vencida]] (due: 2026-01-08)

## Tuesday, January 14
- [ ] [[tarea-normal]]
```

Las tareas vencidas **nunca desaparecen** hasta que:
1. Se marquen como completadas
2. Se eliminen manualmente
3. Se cambie su fecha

## Instalación

### Desde GitHub (recomendado)

```bash
claude plugins add hormigo69/brain2
```

### Configuración inicial

Después de instalar, ejecuta el wizard de configuración:

```
/task-management:setup
```

Esto creará el archivo de configuración en `~/.claude/task-management-config/config.yaml`.

## Configuración

```yaml
paths:
  tasks_root: "/ruta/a/tu/carpeta/Tasks"

folders:
  tasks: "tasks"          # Tareas con fecha
  ideas: "ideas"          # Proyectos sin fecha
  templates: "templates"  # Plantillas
  memories: "memories"    # Material de referencia
  bugs: "bugs"           # Issues a resolver
  completed: "completed" # Archivo de completadas
  import: "import"       # Bandeja de entrada

links:
  format: "obsidian"     # "obsidian" para [[wiki-links]] o "markdown" para [texto](ruta)

integrations:
  research_system: false  # Integración con plugin research-system
```

### Formato de enlaces

| Formato | Ejemplo | Uso |
|---------|---------|-----|
| `obsidian` | `[[nombre-tarea]]` | Obsidian, Logseq, foam |
| `markdown` | `[nombre](tasks/nombre.md)` | GitHub, editores estándar |

## Comandos disponibles

### Generación de vistas

| Comando | Descripción |
|---------|-------------|
| `/task-management:today` | Genera las tres vistas + archiva tareas completadas |
| `/task-management:this-week` | Genera solo this-week.md |
| `/task-management:next-week` | Genera solo next-week.md |

### Gestión

| Comando | Descripción |
|---------|-------------|
| `/task-management:archive` | Mueve tareas completadas a `completed/` |
| `/task-management:ideas` | Lista ideas por estado |
| `/task-management:clean-imports` | Procesa archivos en `import/` |
| `/task-management:setup` | Wizard de configuración |
| `/task-management:about` | Muestra documentación |

## Estructura de carpetas

```
Tasks/
├── tasks/           # Tareas con fecha de vencimiento
│   ├── revisar-presupuesto.md
│   └── llamar-cliente.md
├── ideas/           # Proyectos sin fecha definida
│   ├── app-gastos.md
│   └── rediseño-web.md
├── templates/       # Plantillas reutilizables
│   └── weekly-review.md
├── memories/        # Material de referencia (no accionable)
│   └── notas-reunion.md
├── bugs/            # Issues a resolver
│   └── error-login.md
├── completed/       # Archivo de tareas completadas
│   └── 2026-01-tarea-vieja.md
├── import/          # Bandeja de entrada para triaje
│
├── today.md         # Vista del día (generada)
├── this-week.md     # Vista semanal (generada)
└── next-week.md     # Vista próxima semana (generada)
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

## Campos del frontmatter

| Campo | Valores | Obligatorio | Descripción |
|-------|---------|-------------|-------------|
| `type` | task, idea, template, memory, bug | Sí | Tipo de archivo |
| `due` | YYYY-MM-DD | Para tasks | Fecha de vencimiento |
| `completed` | YYYY-MM-DD | No | Fecha de completado |
| `recurrence` | weekly, biweekly, monthly, quarterly, yearly | No | Frecuencia de repetición |
| `status` | in-progress, noodling, someday | Para ideas | Estado actual |
| `tags` | [tag1, tag2] | No | Categorización |

## Flujo de trabajo típico

### Diario

1. Ejecutar `/task-management:today`
2. Revisar `today.md`:
   - **Overdue**: Tareas que debían estar hechas
   - **Due Today**: Lo que toca hoy
   - **In Progress Ideas**: Proyectos activos
3. Trabajar las tareas
4. Marcar completadas añadiendo `completed: YYYY-MM-DD`

### Semanal

1. Revisar `this-week.md` para planificar
2. Consultar `next-week.md` para anticipar
3. Ejecutar `/task-management:archive` para limpiar completadas

## Vistas generadas

### today.md

```markdown
---
date: 2026-01-11
---
# Today - Sunday, January 11

## Overdue
- [ ] [[tarea-vencida]] (due: 2026-01-05)

## Due Today
- [ ] [[revisar-presupuesto]]
- [ ] [[llamar-cliente]]

## In Progress Ideas
- [[app-gastos]]
- [[rediseño-web]]
```

### this-week.md

```markdown
---
week_start: 2026-01-05
week_end: 2026-01-11
---
# This Week - Week ending January 11

## Overdue
- [ ] [[tarea-vencida]] (due: 2026-01-05)

## Friday, January 9
- [ ] [[reunion-equipo]]

## Saturday, January 10
- [ ] [[weekly-review]]
```

### next-week.md

```markdown
---
week_start: 2026-01-12
week_end: 2026-01-18
---
# Next Week - Week of January 12

## Overdue
- [ ] [[tarea-vencida]] (due: 2026-01-05)

## Monday, January 12
- [ ] [[planificacion-sprint]]

## Wednesday, January 14
- [ ] [[presentacion-cliente]]
```

## Skills incluidos

### manage-tasks

Skill que Claude usa automáticamente al crear o modificar tareas. Asegura formato consistente.

Para activarlo, añade a tu `CLAUDE.md`:

```markdown
**Al crear o actualizar tareas:** Use the manage-tasks skill.
```

## Integración con Google Calendar

Este plugin genera vistas de tareas. Para integrar con calendario:

1. Usa el MCP de Google Workspace en Claude Code
2. Añade a tu `tasks/CLAUDE.md`:

```markdown
**DESPUÉS de ejecutar el script de generación:**
1. Consultar Google Calendar para las fechas relevantes
2. Añadir sección "## Calendario" al inicio de today.md
```

## Créditos

- **Plugin original**: [task-management](https://github.com/ttorres33/task-management) por Teresa Torres
- **Fork con mejoras**: [brain2](https://github.com/hormigo69/brain2) por Ant
- **Asistente de desarrollo**: Claude (Anthropic)

## Licencia

MIT

## Changelog

### v0.2.3 (2026-01-11)
- Añadida sección "Overdue" a `this-week.md`
- Añadida sección "Overdue" a `next-week.md`
- Las tareas vencidas ya no se pierden de las vistas semanales

### v0.2.2 (original)
- Versión base de ttorres33/task-management
