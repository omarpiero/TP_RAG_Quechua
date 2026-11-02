#!/usr/bin/env bash
# Medicion final local (E1) sobre el commit actual: deja todo en docs/evidencias/cierre_u3/99_final_<commit>/.
# Ejecutar con Git Bash desde la raiz del repo. Credenciales solo desde backend/.env; nunca se imprimen.
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$RAIZ"
COMMIT="$(git rev-parse --short HEAD)"
O="$RAIZ/docs/evidencias/cierre_u3/99_final_$COMMIT"; mkdir -p "$O"
P="$RAIZ/backend/.venv/Scripts/python.exe"
export PYTHONIOENCODING=utf-8
export PATH="$PATH:/c/Users/user 01/AppData/Local/Programs/Ollama"
TMPQ="/c/zaptmp/qw_final"; rm -rf "$TMPQ"; mkdir -p "$TMPQ"
paso(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$O/progreso.txt"; }
pw(){ grep '^POSTGRES_PASSWORD=' "$RAIZ/backend/.env" | cut -d= -f2 | tr -d '\r\n'; }

esperar_api(){ for _ in $(seq 1 120); do curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/estado 2>/dev/null | grep -q 200 && return 0; sleep 1; done; return 1; }
parar_api(){ powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*uvicorn*infrastructure.main*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }" >/dev/null 2>&1; sleep 2; }

paso "pytest con cobertura y PostgreSQL de prueba"
( cd backend && POSTGRES_PRUEBAS_URL="postgresql+psycopg://postgres:$(pw)@localhost:5432/quechua_wanka_pruebas" \
  "$P" -m pytest -q --cov=src --cov-report=term --cov-report=json:"$O/coverage.json" --cov-report=xml:coverage.xml --junitxml="$O/junit.xml" > "$O/pytest.txt" 2>&1 )
tail -1 "$O/pytest.txt" | tee -a "$O/progreso.txt"

paso "frontend: npm ci, vitest con cobertura, build"
( cd frontend && npm ci --silent > /dev/null 2>&1; npx vitest run > "$O/vitest.txt" 2>&1; VITE_API_URL= npm run build > "$O/build.txt" 2>&1; rm -rf ../backend/interfaz; cp -r dist ../backend/interfaz )
grep -E "Tests " "$O/vitest.txt" | sed 's/\x1b\[[0-9;]*m//g' | tee -a "$O/progreso.txt"

paso "E2E Playwright (regenera capturas)"
( cd frontend && npm run test:e2e > "$O/e2e.txt" 2>&1 )
sed 's/\x1b\[[0-9;]*m//g' "$O/e2e.txt" | grep -E "passed|failed|flaky|skipped" | tail -3 | tee -a "$O/progreso.txt"

paso "arnes 248 consultas (con y sin lema, barrido)"
( cd backend && "$P" scripts/arnes_linea_base.py "$O/arnes" > "$O/arnes.txt" 2>&1 )
for f in arnes_por_consulta.csv barrido_umbral.csv; do diff --strip-trailing-cr "$O/arnes/$f" docs/evidencias/cierre_u3/00_linea_base_2980a81/arnes/$f > /dev/null && echo "$f identico a 2980a81" || echo "$f DIFIERE de 2980a81"; done | tee -a "$O/progreso.txt"

paso "modelos: reentreno en carpeta temporal y evaluar_pmv2"
( cd backend && QW_MODELOS_SALIDA="$TMPQ/modelos" "$P" scripts/entrenar_predictores.py "$O/entreno" > "$O/entrenar.txt" 2>&1; "$P" scripts/evaluar_pmv2.py "$O/pmv2" > "$O/evaluar_pmv2.txt" 2>&1 )
"$P" - "$TMPQ/modelos/metricas.json" backend/modelos/metricas.json > "$O/comparacion_metricas.txt" <<'EOF'
import json,sys
def limpio(o):
    if isinstance(o,dict): return {k:limpio(v) for k,v in o.items() if k not in("entrenado","fecha")}
    if isinstance(o,list): return [limpio(x) for x in o]
    return o
a,b=[limpio(json.load(open(p,encoding="utf-8"))) for p in sys.argv[1:3]]
print("metricas.json reproducido (sin fechas):",a==b)
EOF
cat "$O/comparacion_metricas.txt" | tee -a "$O/progreso.txt"
git -C "$RAIZ" status --porcelain -- backend/modelos | head -3 | tee -a "$O/progreso.txt"

paso "inferencia ML por consulta"
( cd backend && "$P" - > "$O/inferencia_ml.json" 2>/dev/null <<'EOF'
import json,sys,time,statistics
sys.path.insert(0,"src")
from infrastructure.contenedor import Contenedor
c=Contenedor(generador="literal") if "generador" in Contenedor.__init__.__code__.co_varnames else Contenedor()
ev=json.load(open("data/evaluacion_v2.json",encoding="utf-8"))
pred=getattr(c,"predecir_consulta",None) or getattr(c,"predecir",None)
ms=[]
for x in ev:
    t=time.perf_counter(); pred.ejecutar(x["consulta"]); ms.append((time.perf_counter()-t)*1000)
ms.sort()
print(json.dumps({"n":len(ms),"p50_ms":round(ms[len(ms)//2],2),"p95_ms":round(ms[int(len(ms)*.95)],2),"nota":"caso de uso de prediccion completo: recuperacion + rasgos + dos modelos, sin generador ni registro"}))
EOF
)
cat "$O/inferencia_ml.json" | tee -a "$O/progreso.txt"

paso "radon, bandit, pip-audit"
( cd backend && "$P" -m radon cc -a -s src > "$O/radon_cc.txt" 2>&1; "$P" -m radon mi -s src > "$O/radon_mi.txt" 2>&1; "$P" -m bandit -q -r src -f json -o "$O/bandit.json" 2>/dev/null; "$P" -m pip_audit -r requirements.txt -f json -o "$O/pip_audit.json" 2>/dev/null; "$P" -m pip_audit -r requirements-dev.txt -f json -o "$O/pip_audit_dev.json" 2>/dev/null )
tail -1 "$O/radon_cc.txt" | tee -a "$O/progreso.txt"
( cd frontend && npm audit --omit=dev --json > "$O/npm_audit.json" 2>/dev/null )

paso "Newman local contra API con base aparte"
parar_api
( cd backend && RUTA_SQLITE="C:/zaptmp/qw_final/newman.db" BASE_DATOS=sqlite GENERADOR=literal "$P" -m uvicorn infrastructure.main:app --app-dir src --host 127.0.0.1 --port 8000 > "$TMPQ/api_newman.log" 2>&1 & )
esperar_api && ( npx --yes newman@6 run docs/Asistente_Quechua_Wanka.postman_collection.json --reporters cli,json --reporter-json-export "$TMPQ/newman.json" --env-var base_url=http://127.0.0.1:8000 > "$O/newman.txt" 2>&1 )
"$P" - "$TMPQ/newman.json" > "$O/newman_resumen.json" <<'EOF'
import json,sys
r=json.load(open(sys.argv[1],encoding="utf-8"))["run"]["stats"]
print(json.dumps({k:r[k] for k in("requests","assertions")}))
EOF
cat "$O/newman_resumen.json" | tee -a "$O/progreso.txt"
parar_api

paso "data masiva SQLite 800 y PostgreSQL 1000"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/02_carga_sqlite.ps1 -Forzar -Salida "$(cygpath -w "$O/data_masiva/sqlite")" > "$O/carga_sqlite.txt" 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/03_carga_postgres.ps1 -Forzar -Salida "$(cygpath -w "$O/data_masiva/postgres")" > "$O/carga_postgres.txt" 2>&1
tail -1 "$O/carga_sqlite.txt" | tee -a "$O/progreso.txt"; tail -1 "$O/carga_postgres.txt" | tee -a "$O/progreso.txt"

paso "paridad del indice movil"
mkdir -p "$O/paridad"; ( cd backend && "$P" scripts/exportar_indice_movil.py > "$O/paridad/exportar.txt" 2>&1; "$P" scripts/validar_indice_movil.py > "$O/paridad/validar.txt" 2>&1 )
tail -3 "$O/paridad/validar.txt" | tee -a "$O/progreso.txt"

muestrear(){ # $1 archivo; muestrea VRAM cada 2 s hasta que exista $2
  while [ ! -f "$2" ]; do nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> "$1" 2>/dev/null; sleep 2; done; }

paso "M5 con Qwen en GPU y predictores"
ollama stop qwen3.5:4b >/dev/null 2>&1; sleep 3
( cd backend && RUTA_SQLITE="C:/zaptmp/qw_final/m5.db" BASE_DATOS=sqlite "$P" -m uvicorn infrastructure.main:app --app-dir src --host 127.0.0.1 --port 8000 > "$TMPQ/api_m5.log" 2>&1 & )
esperar_api; ollama stop qwen3.5:4b >/dev/null 2>&1; sleep 3
rm -f "$TMPQ/fin"; muestrear "$O/vram_gpu.txt" "$TMPQ/fin" &
( cd backend && "$P" scripts/m5_latencia.py "$O/m5_gpu" > "$O/m5_gpu.txt" 2>&1 )
ollama ps > "$O/ollama_ps_gpu.txt" 2>&1
powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*uvicorn*infrastructure.main*' } | ForEach-Object { (Get-Process -Id \$_.ProcessId).PeakWorkingSet64 } | Measure-Object -Maximum).Maximum" > "$O/ram_pico_api_bytes.txt" 2>&1
touch "$TMPQ/fin"; sleep 3; parar_api
sort -n "$O/vram_gpu.txt" | tail -1 | sed 's/^/VRAM pico MiB: /' | tee -a "$O/progreso.txt"

paso "M5 en pocos recursos: Qwen en CPU (num_gpu=0)"
printf 'FROM qwen3.5:4b\nPARAMETER num_gpu 0\n' > "$TMPQ/Modelfile"
ollama stop qwen3.5:4b >/dev/null 2>&1; ollama create qw-cpu-medicion -f "$TMPQ/Modelfile" > "$O/ollama_create_cpu.txt" 2>&1
( cd backend && RUTA_SQLITE="C:/zaptmp/qw_final/m5cpu.db" BASE_DATOS=sqlite OLLAMA_MODELO=qw-cpu-medicion "$P" -m uvicorn infrastructure.main:app --app-dir src --host 127.0.0.1 --port 8000 > "$TMPQ/api_m5cpu.log" 2>&1 & )
esperar_api; ollama stop qw-cpu-medicion >/dev/null 2>&1; sleep 3
( cd backend && "$P" scripts/m5_latencia.py "$O/m5_cpu" > "$O/m5_cpu.txt" 2>&1 )
ollama ps > "$O/ollama_ps_cpu.txt" 2>&1
parar_api; ollama stop qw-cpu-medicion >/dev/null 2>&1; ollama rm qw-cpu-medicion >/dev/null 2>&1

paso "SonarQube local"
TOK="$(powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('SONAR_TOKEN','User')" | tr -d '\r')"
TEMP="C:\\zaptmp" TMP="C:\\zaptmp" SONAR_TOKEN="$TOK" SONAR_HOST_URL="http://localhost:9000" SONAR_JAVA_PATH="C:\\Program Files\\Java\\jdk-21.0.12\\bin\\java.exe" \
  JAVA_HOME="C:\\Program Files\\Java\\jdk-21.0.12" "$RAIZ/backend/.venv/Scripts/pysonar.exe" --sonar-host-url=http://localhost:9000 --sonar-token="$TOK" --sonar-project-key=omarpiero_rag-quechua-wanka > "$TMPQ/sonar_log.txt" 2>&1
tail -2 "$TMPQ/sonar_log.txt" | cut -c1-160 | tee -a "$O/progreso.txt"
sleep 25
{ curl -s -u "$TOK:" "http://localhost:9000/api/qualitygates/project_status?projectKey=omarpiero_rag-quechua-wanka"; echo; curl -s -u "$TOK:" "http://localhost:9000/api/measures/component?component=omarpiero_rag-quechua-wanka&metricKeys=bugs,vulnerabilities,security_hotspots,code_smells,duplicated_lines_density,coverage,ncloc"; echo; } > "$O/sonar.json"
head -c 300 "$O/sonar.json" | tee -a "$O/progreso.txt"; echo

paso "agil: commits y PR"
git log --all --format='%an|%ad' --date=short > "$TMPQ/log.txt"
git shortlog -sne origin/main > "$O/git_shortlog.txt"
gh pr list --state all --limit 40 --json number,title,author,createdAt,mergedAt,state,headRefName > "$TMPQ/prs.json" 2>/dev/null
cp "$TMPQ/prs.json" "$O/prs_crudo.json"
paso "FIN"
