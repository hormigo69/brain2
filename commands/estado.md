---
description: Show current status of tasks, overdue items, and upcoming week
---

# Estado actual

Muestra un resumen rápido del estado de tareas.

## Uso

```
/task-management:estado
```

## Proceso

### 1. Obtener fecha
```bash
date "+%Y-%m-%d %H:%M %A"
```

### 2. Leer archivos generados
- Leer `today.md` del tasks_root
- Leer `this-week.md` del tasks_root
- Leer `next-week.md` del tasks_root

### 3. Contar tareas
- Contar tareas en cada archivo (líneas que empiezan con `- [ ]`)
- Identificar sección "Atrasadas" y contar
- Buscar tareas recurrentes en `tasks/` (archivos con `recurrence:`)

### 4. Presentar resumen

Formato:

```
📍 Estado - {Día}, {fecha en español}

**Hoy**:
{lista de tareas de today.md, máximo 5}
{si hay más: "+ N más..."}

**Atrasadas**: {número}
{si hay, listar las primeras 3 con su due date}

**Resto de la semana**: {número} tareas

**Próxima semana**: {número} tareas

**Recurrentes activas**: {número}
{listar cada una con su recurrence y próxima fecha}
```

### 5. Sugerir acción (opcional)

Si hay atrasadas:
- "⚠️ Tienes {N} tareas atrasadas. ¿Las revisamos?"

Si no hay tareas para hoy:
- "✨ No hay tareas para hoy."

Si es lunes:
- "Es lunes. ¿Revisamos la semana?"

## Ejemplo de salida

```
📍 Estado - Domingo, 11 de enero

**Hoy**:
- [ ] [[revisar-texto-raquel-union-musicos]]
- [ ] [[validar-alterbiblio-funcionalidades-economicas]]

**Atrasadas**: 0

**Resto de la semana**: 0 tareas (semana terminada)

**Próxima semana**: 11 tareas

**Recurrentes activas**: 2
- mandar-carolina-kpi-ventas (weekly, próx: 2026-01-16)
- trimestre-autonomos (quarterly, próx: 2026-01-12)
```
