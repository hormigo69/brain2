---
description: Generate today.md, this-week.md, and next-week.md files
---

# today

Generate today.md, this-week.md, and next-week.md files with inbox processing and calendar integration.

## Process

### Step 1: Process Mobile Inbox

**Check for entries in the mobile inbox file (configured in `paths.mobile_inbox` in config.yaml):**

Default location: `~/Library/Mobile Documents/com~apple~CloudDocs/inbox.md`

This file is populated by an iOS Shortcut that allows quick task capture from the phone.

1. Read the mobile inbox file from `paths.mobile_inbox`
2. If file doesn't exist or is empty, skip to Step 2
3. If entries exist, interpret each line (format: `- [ ] text [capturado: YYYY-MM-DD]`):
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

### Step 3: Add Calendar Events (MANDATORY)

**Read config from `~/.claude/task-management-config/config.yaml` to get:**
- `calendar.enabled` (boolean)
- `calendar.google_email` (string)

**If `calendar.enabled` is `true`, you MUST complete these steps:**

#### 3.1 Fetch Calendar Events

Use the Google Calendar MCP tool `mcp__google_workspace__get_events` with:
- `user_google_email`: value from `calendar.google_email`
- Make THREE parallel calls for efficiency:
  1. Today: `time_min` = today, `time_max` = tomorrow
  2. Rest of week: `time_min` = tomorrow, `time_max` = end of week + 1 day
  3. Next week: `time_min` = next week start, `time_max` = next week end + 1 day

#### 3.2 Format Events

For each event, format as:
- All-day events: `- 📌 Event name`
- Timed events: `- HH:MM-HH:MM - Event name`

Sort events by start time within each day.

#### 3.3 Insert Calendar into today.md

**IMMEDIATELY after the `# Hoy - ...` header line, insert:**

```markdown

## Calendario
- 08:00-10:00 - Event 1
- 14:00-15:00 - Event 2

```

Use the Edit tool to insert after the header line.

#### 3.4 Insert Calendar into this-week.md and next-week.md

For EACH day section that has events, transform:

```markdown
## Lunes, 26 de enero
- [ ] [[task-1]]
```

Into:

```markdown
## Lunes, 26 de enero
### Calendario
- 09:00-10:00 - Event 1

### Tareas
- [ ] [[task-1]]
```

**IMPORTANT:**
- Only add `### Calendario` if there are events for that day
- Always add `### Tareas` header before the task list when adding calendar
- Days without events keep their current format (no changes needed)

#### 3.5 Verification

After inserting calendar, read each file to verify:
- [ ] today.md has `## Calendario` section
- [ ] this-week.md has `### Calendario` for days with events
- [ ] next-week.md has `### Calendario` for days with events

If any verification fails, fix it before completing.

### Step 4: Generate Research Digest (Optional)

**Only if `integrations.research_system` is `true` in config.yaml:**

1. Run: `/research-system:generate-research-digest`
2. Add Research section to today.md after "Ideas en progreso"

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

## Trabajo

### Proyecto
- [ ] [[task-1]]

## Personal

### Admin
- [ ] [[task-2]]

## Ideas en progreso
- [[idea-1]]
```

## Example Output - this-week.md

```markdown
---
week_start: 2025-10-04
week_end: 2025-10-06
---
# Esta semana - Semana del 4 al 6 de octubre

## Atrasadas
- [ ] [[old-task]] (due: 2025-10-01)

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

## Atrasadas
- [ ] [[old-task]] (due: 2025-10-01)

## Lunes, 7 de octubre
### Calendario
- 09:00-10:00 - Quarterly planning kickoff

### Tareas
- [ ] [[quarterly-planning]]

## Miércoles, 9 de octubre
### Tareas
- [ ] [[team-sync]]
```
