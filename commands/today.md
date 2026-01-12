---
description: Generate today.md, this-week.md, and next-week.md files
---

# today

Generate today.md, this-week.md, and next-week.md files with inbox processing and calendar integration.

## Process

### Step 1: Process Inbox

**Check for entries in `${TASKS_ROOT}/inbox/inbox.md`:**

1. Read the inbox file
2. If empty, skip to Step 2
3. If entries exist, interpret each line:
   - Detect dates (hoy, mañana, viernes, próxima semana, etc.)
   - Detect type (task vs idea - "idea:" prefix or "sin fecha" = idea)
   - Infer tags from context

4. Show summary table to user:
```
┌─────────────────────────────────────────────────────────────┐
│ INBOX: N entradas encontradas                               │
├─────────────────────────────────────────────────────────────┤
│ 1. "Título interpretado"                                    │
│    → Tarea | due: YYYY-MM-DD | tags: [x, y]                 │
│                                                             │
│ 2. "Otra entrada"                                           │
│    → Idea | status: someday | tags: [z]                     │
└─────────────────────────────────────────────────────────────┘
```

5. Ask user: "¿Proceso estas entradas? (sí/no/editar)"
6. Check if any entries already exist as files in tasks/ or ideas/ - remove duplicates from inbox
7. With approval, create files and clear processed entries from inbox

**Date interpretation rules:**
- No temporal hint → Idea (no date)
- "urgente"/"hoy" → today
- "mañana" → tomorrow
- "esta semana" → Friday
- "próxima semana" → next Monday
- "viernes", "para el 15" → specific date
- Ambiguous → Ask user

### Step 2: Generate Daily Task Files

Run the generate-daily-files.py script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate-daily-files.py
```

This script will:
1. Normalize dates in all task files
2. Calculate current week and next week dates
3. Archive completed tasks (move to completed/ folder)
4. Grep for tasks by specific dates
5. Generate all three files (today.md, this-week.md, next-week.md)

### Step 3: Add Calendar Events

**Only if `calendar.enabled` is `true` in `~/.claude/task-management-config/config.yaml`:**

1. Use the Google Calendar MCP tool to fetch events:
   - For today.md: fetch events for today
   - For this-week.md: fetch events for rest of week
   - For next-week.md: fetch events for next week

2. Add "## Calendario" section to today.md (after frontmatter, before tasks):
```markdown
## Calendario
- 📌 All-day event name
- 09:00-10:00 - Event name
- 14:00-15:30 - Another event
```

3. For this-week.md and next-week.md, add "### Calendario" subsection under each day heading, before "### Tareas"

### Step 4: Generate Research Digest (Optional)

**Only if `integrations.research_system` is `true` in `~/.claude/task-management-config/config.yaml`:**

1. Run the research digest slash command:
   ```
   SlashCommand: /research-system:generate-research-digest
   ```

2. Add a Research section to today.md (after "In Progress Ideas" section) using the `links.format` setting from config.

## Example Output - today.md

```markdown
---
date: 2025-10-03
---
# Hoy - Jueves, 3 de octubre

## Calendario
- 📌 Recordatorio importante
- 09:00-10:00 - Weekly team sync
- 14:00-15:00 - Client meeting

## Atrasadas
- [ ] [[old-task]] (due: 2025-09-30)

## Tareas
- [ ] [[give-dog-flea-medicine]]
- [ ] [[schedule-grooming-loosa]]

## Ideas en progreso
- [[next-ai-project]]
```

## Example Output - this-week.md

```markdown
---
week_start: 2025-10-04
week_end: 2025-10-06
---
# Esta semana - Semana del 4 al 6 de octubre

## Viernes, 4 de octubre
### Calendario
- 10:00-11:00 - Sprint planning

### Tareas
- [ ] [[client-meeting]]

## Sábado, 5 de octubre
### Tareas
- [ ] [[weekly-review]]
```

## Example Output - next-week.md

```markdown
---
week_start: 2025-10-07
week_end: 2025-10-13
---
# Próxima semana - Semana del 7 al 13 de octubre

## Lunes, 7 de octubre
### Calendario
- 09:00-10:00 - Quarterly planning kickoff

### Tareas
- [ ] [[quarterly-planning]]

## Miércoles, 9 de octubre
### Tareas
- [ ] [[team-sync]]
```
