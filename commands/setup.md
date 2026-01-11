---
description: Configure task management plugin paths
---

# Setup Wizard

Configure the task-management plugin for your system.

## Process

### Step 1: Get Tasks Root Path

Ask the user for their tasks root directory path. This is the folder containing their task files and subfolders.

Example: `/Users/username/Documents/Tasks` or `/Users/username/Vaults/Work/Tasks`

### Step 2: Confirm Folder Structure

Show the user the default folder names and ask if they want to customize:

```yaml
folders:
  tasks: "tasks"           # Items with due dates
  ideas: "ideas"           # Projects without due dates
  templates: "templates"   # Reusable task templates
  memories: "memories"     # Reference items (not actionable)
  bugs: "bugs"             # Issues to fix
  completed: "completed"   # Archived one-time tasks
  import: "import"         # Staging area for triage
```

Most users will use the defaults.

### Step 3: Ask Link Format

Ask the user which link format they prefer:
- **obsidian** - Wiki-style links: `[[task-name]]`
- **markdown** - Standard markdown: `[task-name](tasks/task-name.md)`

Default to "obsidian" if user is unsure.

### Step 4: Check for Research System Plugin

Check if the research-system plugin is installed:

```bash
ls ~/.claude/plugins/research-system 2>/dev/null || ls -d ~/*/cc-plugins/research-system 2>/dev/null || echo "not found"
```

If found, ask the user if they want to enable the research-system integration (adds research digest to /today output).

### Step 5: Ask about Google Calendar Integration

Ask the user if they want to integrate with Google Calendar. If yes:
1. Ask for their Google email address
2. Inform them they need to install the Google Workspace MCP:
   - Repository: https://github.com/taylorwilsdon/google_workspace_mcp
   - This enables Gmail, Calendar, and Drive access from Claude Code

### Step 6: Validate Path

Verify the tasks root path exists:

```bash
ls -la "<tasks_root_path>"
```

If it doesn't exist, ask if the user wants to create it.

### Step 7: Create Config Directory

```bash
mkdir -p ~/.claude/task-management-config
```

### Step 8: Write Config File

Create `~/.claude/task-management-config/config.yaml` with the user's settings:

```yaml
paths:
  tasks_root: "<user's path>"

folders:
  tasks: "tasks"
  ideas: "ideas"
  templates: "templates"
  memories: "memories"
  bugs: "bugs"
  completed: "completed"
  import: "import"

links:
  format: "<obsidian or markdown>"

integrations:
  research_system: <true or false>
  google_calendar: <true or false>
  google_email: "<user's email if provided>"
```

### Step 9: Verify Setup

Confirm the config was written:

```bash
cat ~/.claude/task-management-config/config.yaml
```

### Step 10: Create All Folders

Create ALL folders automatically (don't ask, just create them):

```bash
mkdir -p "<tasks_root>/tasks"
mkdir -p "<tasks_root>/ideas"
mkdir -p "<tasks_root>/templates"
mkdir -p "<tasks_root>/memories"
mkdir -p "<tasks_root>/bugs"
mkdir -p "<tasks_root>/completed"
mkdir -p "<tasks_root>/import"
mkdir -p "<tasks_root>/inbox"
```

### Step 11: Create CLAUDE.md

Create a CLAUDE.md file in the tasks root with basic instructions:

```markdown
# Tasks - Sistema de gestion de tareas

## Comandos disponibles

- `/task-management:today` - Genera vista del dia + archiva tareas completadas
- `/task-management:this-week` - Genera vista de la semana
- `/task-management:next-week` - Genera vista de proxima semana
- `/task-management:archive` - Archiva tareas completadas
- `/task-management:ideas` - Lista ideas por estado

## Al crear o actualizar tareas

Use the manage-tasks skill.

## Estructura de carpetas

| Carpeta | Proposito |
|---------|-----------|
| `tasks/` | Tareas con fecha de vencimiento |
| `ideas/` | Proyectos sin fecha definida |
| `templates/` | Plantillas reutilizables |
| `memories/` | Material de referencia (no accionable) |
| `bugs/` | Issues a resolver |
| `completed/` | Tareas archivadas |
| `inbox/` | Captura rapida |

## Formato de tareas

```yaml
---
type: task
due: YYYY-MM-DD
tags: [tag1, tag2]
---
# Titulo de la tarea

Descripcion...
```
```

If Google Calendar integration is enabled, add this section to CLAUDE.md:

```markdown
## Integracion con Google Calendar

**Email:** <user's email>

**DESPUES de ejecutar el script de generacion:**
1. Consultar Google Calendar para las fechas relevantes
2. Añadir seccion "## Calendario" al inicio del archivo generado
3. Formato: `- HH:MM-HH:MM - Nombre del evento`
```

### Step 12: Create Example Task

Create an example task file to help the user get started:

```bash
# Create example task
cat > "<tasks_root>/tasks/ejemplo-tarea.md" << 'EOF'
---
type: task
due: <tomorrow's date in YYYY-MM-DD>
tags: [ejemplo]
---
# Tarea de ejemplo

Esta es una tarea de ejemplo. Puedes:
- Editarla o eliminarla
- Usarla como referencia para crear nuevas tareas

Para completarla, añade `completed: YYYY-MM-DD` al frontmatter.
EOF
```

## Example Output

```
=== Task Management Setup Complete! ===

Configuracion guardada en: ~/.claude/task-management-config/config.yaml

Directorio raiz: /Users/username/Documents/Tasks
Formato de enlaces: obsidian
Integracion Google Calendar: habilitada

Carpetas creadas:
  - tasks/
  - ideas/
  - templates/
  - memories/
  - bugs/
  - completed/
  - import/
  - inbox/

Archivos creados:
  - CLAUDE.md (instrucciones para Claude)
  - tasks/ejemplo-tarea.md (tarea de ejemplo)

=== Siguientes pasos ===

1. Si habilitaste Google Calendar, instala el MCP:
   https://github.com/taylorwilsdon/google_workspace_mcp

2. Ejecuta tu primer comando:
   /task-management:today

3. Crea tareas nuevas en tasks/ con el formato YAML mostrado

Para mas informacion: /task-management:about
```
