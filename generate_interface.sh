#!/bin/bash

# Script per generare i file Python da tutti i .proto in protoFiles/
# e copiarli nella cartella interface/

set -e

PROTO_DIR="protoFiles"
OUT_DIR="interface"

# Crea la cartella di output se non esiste
mkdir -p "$OUT_DIR"

# Cicla su tutti i file .proto in protoFiles/
for protofile in "$PROTO_DIR"/*.proto; do
  if [ -f "$protofile" ]; then
    echo "Generazione di $(basename "$protofile")..."
    protoc --proto_path="$PROTO_DIR" --python_out="$OUT_DIR" "$(basename "$protofile")"
  fi
done

echo "Generazione completata. File Python generati in $OUT_DIR/"