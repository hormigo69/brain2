#!/bin/bash
# transcribir.sh - Extrae audio de video y transcribe con Gladia API
# Uso: ./transcribir.sh <video> <output_dir> <tema>

set -e

# Argumentos
VIDEO_PATH="$1"
OUTPUT_DIR="$2"
TEMA="$3"

# Configuración
CONFIG_DIR="$HOME/.claude/task-management-config"
ENV_FILE="$CONFIG_DIR/gladia.env"

# Cargar API key
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: No existe $ENV_FILE"
    echo "Crea el archivo con: GLADIA_API_KEY=tu_api_key"
    exit 1
fi

source "$ENV_FILE"

if [[ -z "$GLADIA_API_KEY" ]]; then
    echo "ERROR: GLADIA_API_KEY no está definida en $ENV_FILE"
    exit 1
fi

# Validar argumentos
if [[ -z "$VIDEO_PATH" || -z "$OUTPUT_DIR" || -z "$TEMA" ]]; then
    echo "Uso: $0 <video> <output_dir> <tema>"
    exit 1
fi

if [[ ! -f "$VIDEO_PATH" ]]; then
    echo "ERROR: No existe el archivo: $VIDEO_PATH"
    exit 1
fi

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

# Archivo temporal para audio
TEMP_AUDIO="/tmp/transcribir_audio_$$.mp3"
trap "rm -f $TEMP_AUDIO" EXIT

# Obtener duración del video
echo "Analizando video..."
DURATION_SECONDS=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_PATH" 2>/dev/null | cut -d. -f1)
DURATION_MINUTES=$((DURATION_SECONDS / 60))
echo "Duración: ${DURATION_MINUTES} minutos"

# Extraer audio
echo "Extrayendo audio..."
ffmpeg -i "$VIDEO_PATH" -vn -acodec libmp3lame -q:a 4 "$TEMP_AUDIO" -y -loglevel error

if [[ ! -f "$TEMP_AUDIO" ]]; then
    echo "ERROR: Falló la extracción de audio"
    exit 1
fi

echo "Audio extraído: $(du -h "$TEMP_AUDIO" | cut -f1)"

# Subir a Gladia
echo "Subiendo a Gladia..."
UPLOAD_RESPONSE=$(curl -s -X POST "https://api.gladia.io/v2/upload" \
    -H "x-gladia-key: $GLADIA_API_KEY" \
    -F "audio=@$TEMP_AUDIO")

AUDIO_URL=$(echo "$UPLOAD_RESPONSE" | jq -r '.audio_url // empty')

if [[ -z "$AUDIO_URL" ]]; then
    echo "ERROR: Falló la subida a Gladia"
    echo "$UPLOAD_RESPONSE" | jq .
    exit 1
fi

# Solicitar transcripción con diarización
echo "Solicitando transcripción con diarización..."
TRANSCRIPTION_RESPONSE=$(curl -s -X POST "https://api.gladia.io/v2/transcription" \
    -H "x-gladia-key: $GLADIA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"audio_url\": \"$AUDIO_URL\", \"diarization\": true}")

RESULT_URL=$(echo "$TRANSCRIPTION_RESPONSE" | jq -r '.result_url // empty')

if [[ -z "$RESULT_URL" ]]; then
    echo "ERROR: Falló al iniciar transcripción"
    echo "$TRANSCRIPTION_RESPONSE" | jq .
    exit 1
fi

# Esperar resultado
echo "Transcribiendo (esto puede tardar)..."
while true; do
    RESULT=$(curl -s "$RESULT_URL" -H "x-gladia-key: $GLADIA_API_KEY")
    STATUS=$(echo "$RESULT" | jq -r '.status // empty')

    if [[ "$STATUS" == "done" ]]; then
        break
    elif [[ "$STATUS" == "error" ]]; then
        echo "ERROR: La transcripción falló"
        echo "$RESULT" | jq .
        exit 1
    fi

    echo "  Estado: $STATUS..."
    sleep 5
done

# Extraer texto con diarización
UTTERANCES=$(echo "$RESULT" | jq -r '.result.transcription.utterances // empty')

if [[ -n "$UTTERANCES" && "$UTTERANCES" != "null" ]]; then
    # Formato con speakers
    TRANSCRIPTION=$(echo "$RESULT" | jq -r '.result.transcription.utterances[] | "**Speaker \(.speaker):** \(.text)"' | sed 's/$/\n/')
else
    # Formato sin diarización (fallback)
    TRANSCRIPTION=$(echo "$RESULT" | jq -r '.result.transcription.full_transcript // empty')
fi

if [[ -z "$TRANSCRIPTION" ]]; then
    echo "ERROR: No se obtuvo transcripción"
    exit 1
fi

# Generar nombre de archivo
DATE=$(date "+%Y-%m-%d")
TIME=$(date "+%H:%M")
SLUG=$(echo "$TEMA" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
OUTPUT_FILE="$OUTPUT_DIR/${DATE}-${SLUG}.md"
VIDEO_BASENAME=$(basename "$VIDEO_PATH")

# Guardar transcripción
cat > "$OUTPUT_FILE" << EOF
# Reunión: $TEMA
- **Fecha**: $DATE $TIME
- **Duración**: ${DURATION_MINUTES} min
- **Archivo origen**: $VIDEO_BASENAME

---

## Transcripción

$TRANSCRIPTION
EOF

echo "---"
echo "TRANSCRIPCION_ARCHIVO=$OUTPUT_FILE"
echo "TRANSCRIPCION_DURACION=$DURATION_MINUTES"
echo "TRANSCRIPCION_FECHA=$DATE"
echo "TRANSCRIPCION_HORA=$TIME"
