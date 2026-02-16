---
description: Generate today.md, this-week.md, and next-week.md files
---

# today

Generate today.md, this-week.md, and next-week.md files from Google Tasks with calendar integration.

**Source of truth: Google Tasks** (migrated feb 2026). Do NOT use Python scripts or local .md task files.

## Process

### Step 1: Fetch Tasks from Google Tasks

**IMPORTANT: Use `date` command to get today's date. Never calculate day-of-week mentally.**

Run `date "+%Y-%m-%d %A %u"` to get today's date, day name, and day-of-week number (1=Monday).

Then fetch tasks from Google Tasks. Make 4 PARALLEL calls to `mcp__google_workspace__list_tasks`:

1. **Cloud District** — `task_list_id: "Wk1leGlhdy1kdm1kSVRuaA"`, `show_completed: false`
2. **Profesional** — `task_list_id: "elpCaENDeGxBQ21xN3BUMQ"`, `show_completed: false`
3. **Personal** — `task_list_id: "VklQWXBOSl9FeDRRZzRHUw"`, `show_completed: false`
4. **Inbox** — `task_list_id: "UUMwNExCdFd3N0o0bE9kWA"`, `show_completed: false`

### Step 2: Calculate Date Ranges

Using today's date from Step 1:

- **Today**: exact date match
- **This week**: from tomorrow through Sunday of current week
- **Next week**: Monday through Sunday of next week
- **Overdue**: any task with `due` < today

Use `date` commands to calculate the exact dates. Example:
```bash
# End of this week (Sunday)
date -v+sunday -j "+%Y-%m-%d"
# Next Monday
date -v+monday -j -v+1w "+%Y-%m-%d"
# Next Sunday
date -v+sunday -j -v+1w "+%Y-%m-%d"
```

### Step 3: Generate Files

**Read config from `~/.claude/task-management-config/config.yaml` to get `paths.tasks_root`.**

Process ALL fetched tasks and classify them by due date:

#### Task parsing rules:

- **Area mapping**:
  - Cloud District list → "Trabajo"
  - Profesional list → "Trabajo"
  - Personal list → "Personal"

- **Project extraction**: Extract from `[Proyecto]` prefix in title
  - `[Babe] Revisar presupuesto` → project "Babe", task "Revisar presupuesto"
  - `Escribir artículo LinkedIn` → no project, task as-is

- **Blocked status**: If notes contain `#esperando`, show as `(espera: REASON)` where REASON is text after `#esperando` on same line, or just `(espera)` if no reason given

- **Overdue**: If `due` < today → append `(atrasada Xd)` where X = days overdue

- **Sort order within each project/category**: Actionable tasks first, then blocked (`#esperando`) tasks last

#### Generate today.md:

Write to `{tasks_root}/today.md`:

```markdown
---
date: YYYY-MM-DD
---
# Hoy - [Día en español], DD de [mes en español]

## Trabajo
### [Proyecto]
- [ ] Tarea actionable
- [ ] Tarea bloqueada (espera: razón)

### [Otro proyecto]
- [ ] Otra tarea

## Personal
### [Categoría]
- [ ] Tarea personal

## Atrasadas
### [Proyecto]
- [ ] Tarea atrasada (atrasada 3d)
```

Rules for today.md:
- Include tasks where `due` = today (grouped by area then project)
- Include overdue tasks (`due` < today) in a separate "## Atrasadas" section at the end
- Omit empty sections (if no Personal tasks, omit "## Personal")
- Tasks without project prefix go under "### General" within their area

#### Generate this-week.md:

Write to `{tasks_root}/this-week.md`:

```markdown
---
week_start: YYYY-MM-DD
week_end: YYYY-MM-DD
---
# Esta semana - Semana del DD al DD de [mes]

## Atrasadas
- [ ] [Proyecto] Tarea (atrasada Xd)

## [Día], DD de [mes]
- [ ] [Proyecto] Tarea
- [ ] Otra tarea (espera: algo)
```

Rules for this-week.md:
- Include tasks from tomorrow through end of current week (Sunday)
- Group by day, with day headers in Spanish
- Include overdue tasks in "## Atrasadas" section at the top
- Tasks show with their `[Proyecto]` prefix in the title
- Blocked tasks show `(espera: razón)` suffix
- Skip days with no tasks
- If no tasks at all, write: `No hay tareas para el resto de la semana.`

#### Generate next-week.md:

Write to `{tasks_root}/next-week.md`:

```markdown
---
week_start: YYYY-MM-DD
week_end: YYYY-MM-DD
---
# Próxima semana - Semana del DD al DD de [mes]

## [Día], DD de [mes]
- [ ] [Proyecto] Tarea
```

Rules for next-week.md:
- Include tasks from next Monday through next Sunday
- Same format as this-week.md
- Do NOT include overdue tasks (those only go in today.md and this-week.md)
- If no tasks, write: `No hay tareas para la próxima semana.`

### Step 4: Add Calendar Events (MANDATORY)

**Read config from `~/.claude/task-management-config/config.yaml` to get:**
- `calendar.enabled` (boolean)
- `calendar.google_email` (string)

**If `calendar.enabled` is `true`, you MUST complete these steps:**

#### 4.1 Fetch Calendar Events

Use the Google Calendar MCP tool `mcp__google_workspace__get_events` with:
- `user_google_email`: value from `calendar.google_email`
- Make THREE parallel calls for efficiency:
  1. Today: `time_min` = today start, `time_max` = tomorrow start
  2. Rest of week: `time_min` = tomorrow start, `time_max` = end of week + 1 day
  3. Next week: `time_min` = next week start, `time_max` = next week end + 1 day

#### 4.2 Format Events

For each event, format as:
- All-day events: `- 📌 Event name`
- Timed events: `- HH:MM-HH:MM - Event name`

Sort events by start time within each day.

#### 4.3 Insert Calendar into today.md

**IMMEDIATELY after the `# Hoy - ...` header line, insert:**

```markdown

## Calendario
- 08:00-10:00 - Event 1
- 14:00-15:00 - Event 2

```

Use the Edit tool to insert after the header line.

#### 4.4 Insert Calendar into this-week.md and next-week.md

For EACH day section that has events, transform:

```markdown
## Lunes, 26 de enero
- [ ] [Proyecto] Tarea
```

Into:

```markdown
## Lunes, 26 de enero
### Calendario
- 09:00-10:00 - Event 1

### Tareas
- [ ] [Proyecto] Tarea
```

**IMPORTANT:**
- Only add `### Calendario` if there are events for that day
- Always add `### Tareas` header before the task list when adding calendar
- Days without events keep their current format (no changes needed)

#### 4.5 Verification

After inserting calendar, read each file to verify:
- [ ] today.md has `## Calendario` section
- [ ] this-week.md has `### Calendario` for days with events
- [ ] next-week.md has `### Calendario` for days with events

If any verification fails, fix it before completing.

### Step 5: Generate Research Digest (Optional)

**Only if `integrations.research_system` is `true` in config.yaml:**

1. Run: `/research-system:generate-research-digest`
2. Add Research section to today.md after last section

## Spanish day/month names reference

Days: lunes, martes, miércoles, jueves, viernes, sábado, domingo
Months: enero, febrero, marzo, abril, mayo, junio, julio, agosto, septiembre, octubre, noviembre, diciembre

## Example Output - today.md

```markdown
---
date: 2026-02-10
---
# Hoy - Martes, 10 de febrero

## Calendario
- 📌 Recordatorio importante
- 09:00-10:00 - Weekly team sync
- 14:00-15:00 - Client meeting

## Trabajo
### Babe
- [ ] Revisar presupuesto RFID
- [ ] Preparar presentación (espera: datos de Marta)

### Ventas
- [ ] Identificar empresas Valencia

## Personal
### Admin
- [ ] Renovar seguro coche

## Atrasadas
### Tolsa
- [ ] Enviar factura (atrasada 3d)
```

## Example Output - this-week.md

```markdown
---
week_start: 2026-02-11
week_end: 2026-02-15
---
# Esta semana - Semana del 11 al 15 de febrero

## Atrasadas
- [ ] [Tolsa] Enviar factura (atrasada 3d)

## Miércoles, 11 de febrero
### Calendario
- 10:00-11:00 - Sprint planning

### Tareas
- [ ] [Babe] Cerrar requisitos fase 2

## Viernes, 13 de febrero
- [ ] [Personal] Comprar billete tren
```

## Example Output - next-week.md

```markdown
---
week_start: 2026-02-16
week_end: 2026-02-22
---
# Próxima semana - Semana del 16 al 22 de febrero

## Lunes, 16 de febrero
### Calendario
- 09:00-10:00 - Quarterly planning kickoff

### Tareas
- [ ] [Babe] Entregar diseño final

## Miércoles, 18 de febrero
- [ ] [Ventas] Presentación interna
```
