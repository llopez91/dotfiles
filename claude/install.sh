#!/usr/bin/env bash
# Install personal Claude skills via symlinks
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/skills"
DEST="$HOME/.claude/skills"

mkdir -p "$DEST"

for d in "$SRC"/*/; do
    name="$(basename "$d")"
    link="$DEST/$name"
    if [ -e "$link" ] || [ -L "$link" ]; then
        rm -rf "$link"
    fi
    ln -s "${d%/}" "$link"
    echo "Linked $name -> ${d%/}"
done

echo "Skills installed in $DEST"

# El kit creativo necesita su .env para las etapas de IA.
ENV_FILE="$SRC/studio-creative/.env"
if [ ! -f "$ENV_FILE" ]; then
    cp "$SRC/studio-creative/.env.example" "$ENV_FILE"
    echo "Created $ENV_FILE - add your KIE_API_KEY"
fi
