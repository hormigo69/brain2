---
description: Transcribe meeting videos using Gladia API with speaker diarization
---

# Transcribir reunión

Transcribe un video de reunión y guarda el resultado en markdown.

## Uso

```
/task-management:transcribir reunion.mov
/task-management:transcribir "/path/to/video con espacios.mov"
```

## Proceso

### 1. Validar archivo

- Si no se proporciona archivo, buscar videos en carpetas comunes:
  ```bash
  ls -lt ~/Desktop/*.{mov,mp4,m4v,webm,mkv} 2>/dev/null | head -5
  ls -lt ~/Downloads/*.{mov,mp4,m4v,webm,mkv} 2>/dev/null | head -5
  ```
- Mostrar los videos encontrados y preguntar cuál transcribir
- Si se proporciona ruta completa, verificar que existe

### 2. Verificar configuración

Comprobar que existe `~/.claude/task-management-config/gladia.env` con GLADIA_API_KEY:

```bash
cat ~/.claude/task-management-config/gladia.env 2>/dev/null | grep -q GLADIA_API_KEY
```

Si no existe, indicar cómo configurarlo:
```
Configura tu API key de Gladia:
1. Obtén una API key en https://app.gladia.io/
2. Crea el archivo:
   echo "GLADIA_API_KEY=tu_api_key" > ~/.claude/task-management-config/gladia.env
```

### 3. Preguntar datos

Usar AskUserQuestion:

1. **Tema**: texto libre (ej: "kickoff proyecto", "revisión diseño", "demo cliente")
2. **Carpeta destino** (opcional): Por defecto guarda en `{tasks_root}/transcripciones/`

### 4. Ejecutar script

```bash
python3 <<SCRIPT_PATH>>/scripts/transcribir.sh "<video>" "<output_dir>" "<tema>"
```

Donde `<<SCRIPT_PATH>>` es la ruta del plugin (usar la misma ruta que otros scripts del plugin).

### 5. Parsear resultado

El script imprime al final:
```
TRANSCRIPCION_ARCHIVO=/path/to/file.md
TRANSCRIPCION_DURACION=45
TRANSCRIPCION_FECHA=2026-01-07
TRANSCRIPCION_HORA=10:30
```

### 6. Confirmar

Mostrar resumen:
```
✓ Transcripción guardada: {archivo}
✓ Duración: {X} min
✓ Fecha: {fecha}
```

## Manejo de errores

| Error | Acción |
|-------|--------|
| Archivo no existe | "No encuentro {path}. ¿Ruta correcta?" |
| API key no configurada | Mostrar instrucciones de configuración |
| Script falla | Mostrar error del script, preguntar si reintentar |
| Audio >2h | "El audio dura {x} min. Gladia cobra por minuto. ¿Continúo?" |

## Dependencias

Requiere tener instalados:
- `ffmpeg`: `brew install ffmpeg`
- `jq`: `brew install jq`

## Formato de salida

El archivo generado tiene este formato:

```markdown
# Reunión: {tema}
- **Fecha**: YYYY-MM-DD HH:MM
- **Duración**: {X} min
- **Archivo origen**: {nombre del video}

---

## Transcripción

**Speaker 0:** Primera intervención...

**Speaker 1:** Segunda intervención...
```
