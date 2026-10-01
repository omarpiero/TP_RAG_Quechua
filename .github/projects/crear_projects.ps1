# Crea el tablero GitHub Projects del proyecto (CONSIDERACIONES.md §7.4 · docs/13 G-05).
# Lo ejecuta el usuario, autenticado con la cuenta propietaria del repositorio:
#   gh auth login            (una vez)
#   gh auth refresh -s project
#   powershell -ExecutionPolicy Bypass -File .github\projects\crear_projects.ps1
# Las vistas Roadmap y Board no se pueden crear con gh: se añaden después en la web.

$ErrorActionPreference = 'Stop'
$Owner = 'omarpiero'
$Repo  = 'omarpiero/TP_RAG_Quechua'
$Titulo = 'TP_RAG_Quechua · Roadmap de los 3 PMV'

# 1. Proyecto y enlace con el repositorio
$proyecto = gh project create --owner $Owner --title $Titulo --format json | ConvertFrom-Json
$N = $proyecto.number
gh project link $N --owner $Owner --repo $Repo
Write-Host "Proyecto #$N creado: $($proyecto.url)"

# 2. Campos
gh project field-create $N --owner $Owner --name 'Estado' --data-type SINGLE_SELECT --single-select-options 'Backlog,Listo,En curso,En revisión,Hecho'
gh project field-create $N --owner $Owner --name 'PMV' --data-type SINGLE_SELECT --single-select-options 'PMV1,PMV2,PMV3'
gh project field-create $N --owner $Owner --name 'Sprint' --data-type SINGLE_SELECT --single-select-options 'Sprint 1,Sprint 2,Sprint 3,Sprint 4'
gh project field-create $N --owner $Owner --name 'Rol' --data-type SINGLE_SELECT --single-select-options 'PM / Scrum Master,Architect & System Designer,Lead Backend & AI Engineer,Lead Frontend & Integration,QA & DevOps'
gh project field-create $N --owner $Owner --name 'Inicio' --data-type DATE
gh project field-create $N --owner $Owner --name 'Fin' --data-type DATE
gh project field-create $N --owner $Owner --name 'Historia' --data-type TEXT
gh project field-create $N --owner $Owner --name 'Puntos' --data-type NUMBER

# 3. Identificadores de campos y opciones
$idProyecto = (gh project view $N --owner $Owner --format json | ConvertFrom-Json).id
$campos = (gh project field-list $N --owner $Owner --format json --limit 50 | ConvertFrom-Json).fields
function Campo($nombre) { $campos | Where-Object { $_.name -eq $nombre } }
function Opcion($nombre, $valor) { ((Campo $nombre).options | Where-Object { $_.name -eq $valor }).id }

function Poner($item, $nombre, $valor) {
    gh project item-edit --project-id $idProyecto --id $item --field-id (Campo $nombre).id --single-select-option-id (Opcion $nombre $valor) | Out-Null
}

# 4. Tarjetas: P0 de docs/13 §7, P1 y los PMV posteriores (estado honesto, CONSIDERACIONES §3.4)
$tarjetas = @(
    @('PR 1 · Estructura hexagonal backend/src (refactor/estructura-hexagonal)', 'HT-00 · E2', 'Architect & System Designer', 'PMV1', 'Listo'),
    @('PR 2 · Puertos de entrada, controladores por recurso y CLI (feat/puertos-entrada)', 'HT-00 · E2', 'Architect & System Designer', 'PMV1', 'Listo'),
    @('PR 3 · Reglas de respuesta: τ de configuración, UmbralConLema, pasajes, RespuestaFactory, D-1, D-6', 'HU-06', 'Lead Backend & AI Engineer', 'PMV1', 'Backlog'),
    @('PR 4 · VerificadorFormaLiteral (RN-02)', 'HU-06', 'Lead Backend & AI Engineer', 'PMV1', 'Backlog'),
    @('PR 6 · Entradas lexicográficas truncadas (D-4) y prueba de regresión', 'HU-02', 'Lead Backend & AI Engineer', 'PMV1', 'Backlog'),
    @('PR 7 · Interfaz React: UI-01…05, 07, 08, 10, 13', 'HT-04', 'Lead Frontend & Integration', 'PMV1', 'Backlog'),
    @('PR 8 · Historial en SQLite con borrado y aviso de privacidad', 'RF-11', 'Lead Backend & AI Engineer', 'PMV1', 'Backlog'),
    @('PR 9 · Prueba de arquitectura y Gherkin HU-03, HU-06, HU-07', 'HU-03 · HU-06 · HU-07', 'QA & DevOps', 'PMV1', 'Backlog'),
    @('PR 10 · CI: SonarQube, cobertura y Newman (M8, M9, M10)', 'HT-01', 'QA & DevOps', 'PMV1', 'Backlog'),
    @('PR 11 · Mediciones M1–M8, M13–M16 y M3-bis', 'HT-01', 'QA & DevOps', 'PMV1', 'Backlog'),
    @('M16 · KPI del proceso AS-IS (consulta manual, equipo)', 'C1', 'PM / Scrum Master', 'PMV1', 'Backlog'),
    @('docs/11 §3 con salidas reales + arbol_src.txt y puertos.md', 'E1 · E3', 'Architect & System Designer', 'PMV1', 'Backlog'),
    @('PR 5 · Traductor como Strategy y corrección de D-2 (P1)', 'HU-05', 'Lead Backend & AI Engineer', 'PMV1', 'Backlog'),
    @('M17 · Sesgo medible del sistema (P1)', 'C3', 'QA & DevOps', 'PMV1', 'Backlog'),
    @('PMV2 · Exportación del índice y verificación de paridad', 'RN-10', 'Lead Backend & AI Engineer', 'PMV2', 'Hecho'),
    @('PMV2 · Analítica predictiva RF-14–16', 'RF-14 · RF-15 · RF-16', 'Lead Backend & AI Engineer', 'PMV2', 'Backlog'),
    @('PMV3 · App Flutter sin conexión (espiga, sin validar en dispositivo físico)', 'PMV3', 'Lead Frontend & Integration', 'PMV3', 'Backlog')
)

foreach ($t in $tarjetas) {
    $item = (gh project item-create $N --owner $Owner --title $t[0] --format json | ConvertFrom-Json).id
    gh project item-edit --project-id $idProyecto --id $item --field-id (Campo 'Historia').id --text $t[1] | Out-Null
    Poner $item 'Rol' $t[2]
    Poner $item 'PMV' $t[3]
    Poner $item 'Estado' $t[4]
    Write-Host "  + $($t[0])"
}

Write-Host "Listo. Añade en la web las vistas Roadmap (por Inicio/Fin, agrupada por PMV) y Board (por Estado)."
