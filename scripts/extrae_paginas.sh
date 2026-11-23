#!/usr/bin/env bash
# PROCESO: Regenerar los textos por página que usan los agentes y el verificador de citas.
# Insumo: PDF de 15_Loan (BID/, BIRF/). Resultado: <salida>/<nombre>.txt con marcadores "=== PÁG n ===".
# Uso: bash extrae_paginas.sh <carpeta_salida> archivo1.pdf [archivo2.pdf ...]
# pdftotext: convierte el PDF a texto respetando el diseño; cada página termina con un salto de página (\f).
salida="$1"; shift; mkdir -p "$salida"
for f in "$@"; do
  n=$(basename "$f" .pdf)
  pdftotext -enc UTF-8 -layout "$f" - | awk 'BEGIN{p=1; print "=== PÁG 1 ==="} { n=split($0, parts, "\f"); for(i=1;i<=n;i++){ if(i>1){p++; print "=== PÁG " p " ==="} line=parts[i]; gsub(/[ \t]+/," ",line); if(line!=" " && line!="") print line } }' > "$salida/$n.txt"
  echo "$n: $(grep -c '=== PÁG' "$salida/$n.txt") págs"
done
