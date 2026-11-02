#!/usr/bin/env bash
# Mediciones contra la nube, sin modificar Neon ni Render salvo filas `humo` y la fuente temporal
# que Newman crea y borra. El token se lee de la variable de usuario TOKEN_PRUEBAS y no se imprime.
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$RAIZ/backend"
O="$RAIZ/docs/evidencias/nube/metricas_u3"; mkdir -p "$O"
P=".venv/Scripts/python.exe"; API=https://quechua-api.onrender.com
export PYTHONIOENCODING=utf-8
TOKEN_PRUEBAS="$(powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('TOKEN_PRUEBAS','User')" | tr -d '\r\n')"; export TOKEN_PRUEBAS
paso(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$O/progreso.txt"; }

paso "paridad 248 consultas contra /api/predicciones"
"$P" scripts/medir_nube_u3.py paridad "$O" 0.3 2>&1 | tail -1 | cut -c1-400 | tee -a "$O/progreso.txt"

paso "humo por endpoint (servicio despierto)"
"$P" scripts/humo_nube.py "$API" --salida "$O" > "$O/humo_consola.txt" 2>&1; tail -3 "$O/humo_consola.txt" | cut -c1-200 | tee -a "$O/progreso.txt"

paso "Gemini: 20 consultas de A con 5 s de pausa"
"$P" scripts/medir_gemini_nube.py "$API" --n 20 --espera 5 > "$O/gemini_consola.txt" 2>&1; tail -4 "$O/gemini_consola.txt" | cut -c1-240 | tee -a "$O/progreso.txt"

paso "comparacion local frente a nube (10 A + 10 C)"
"$P" scripts/medir_nube_u3.py comparar "$O" 5 2>&1 | tail -1 | tee -a "$O/progreso.txt"
rm -f "$O/_comparar_temporal.db"*

paso "Newman contra la nube con cabeceras de humo"
T=/c/zaptmp/nube_col.json
"$P" - "$RAIZ/docs/Asistente_Quechua_Wanka.postman_collection.json" "$T" <<'EOF'
import json,os,sys
c=json.load(open(sys.argv[1],encoding="utf-8"))
script=["pm.request.headers.add({key:'X-Origen-Consultas',value:'humo'});",
        "pm.request.headers.add({key:'X-Token-Pruebas',value:pm.environment.get('tp')||pm.globals.get('tp')});"]
c.setdefault("event",[]).append({"listen":"prerequest","script":{"type":"text/javascript","exec":script}})
json.dump(c,open(sys.argv[2],"w",encoding="utf-8"))
EOF
( cd "$RAIZ" && npx --yes newman@6 run "$(cygpath -w $T)" -e docs/Asistente_Quechua_Wanka.nube.postman_environment.json --global-var "tp=$TOKEN_PRUEBAS" --reporters cli,json --reporter-json-export /c/zaptmp/newman_nube.json > /c/zaptmp/newman_nube.txt 2>&1 )
grep -v "$TOKEN_PRUEBAS" /c/zaptmp/newman_nube.txt | sed 's/\x1b\[[0-9;]*m//g' > "$O/newman_nube.txt"
"$P" - /c/zaptmp/newman_nube.json > "$O/newman_nube_resumen.json" <<'EOF'
import json,sys
r=json.load(open(sys.argv[1],encoding="utf-8"))["run"]
print(json.dumps({"requests":r["stats"]["requests"],"assertions":r["stats"]["assertions"],"tiempo_medio_ms":r["timings"].get("responseAverage")}))
EOF
cat "$O/newman_nube_resumen.json" | tee -a "$O/progreso.txt"
rm -f "$T" /c/zaptmp/newman_nube.json /c/zaptmp/newman_nube.txt

paso "conteo por origen e historial"
curl -s "$API/api/analitica/demanda" -m 60 | "$P" -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:d.get(k) for k in ('conteo_por_origen','suficiente','total','modo','mensaje')},ensure_ascii=False))" > "$O/analitica_real.json" 2>&1
cat "$O/analitica_real.json" | cut -c1-300 | tee -a "$O/progreso.txt"
paso "FIN"
