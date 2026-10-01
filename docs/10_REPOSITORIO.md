# 10 · Creación del repositorio entregable (PR 0 · HT-00)

> **Para quién.** El usuario, una sola vez, antes de abrir Claude Code. El resto del trabajo (PR 1 en
> adelante) lo conduce el orquestador con `PROMPT_CIERRE_PMV1.md`.
>
> **Resultado.** `github.com/omarpiero/TP_RAG_Quechua` (privado). Contiene el código del integrante **con
> su historial y su autoría**, sin el texto del corpus, más la especificación SDD y la configuración de
> Claude Code. La etiqueta `base-integrante` marca el punto de partida.

---

## 1. Por qué así

| Decisión | Motivo |
|---|---|
| Se **importa el historial** del repositorio del integrante, no se copia el código | La lista de cotejo (E2) valora el «historial de commits constante por los integrantes». Copiar los archivos borraría la autoría de quien los escribió; reescribir los commits a nombre de otros sería falsear el historial |
| Se **quita del historial** `fragmentos_v2/v3.jsonl`, `evaluacion_prosa.json` y `movil/` | Los dos primeros son el texto completo del corpus y el tercero contiene pasajes del corpus (licencias heterogéneas, ADR-015, riesgo R-07). `movil/` incluye otra copia del corpus en `assets/` y ya vive en su propio repositorio. Los archivos se **conservan en disco**, fuera de Git, porque el backend los necesita |
| Los commits pasan de 19 a 16 | Los tres que se pierden solo tocaban `movil/`. Los identificadores de commit cambian (consecuencia normal de filtrar el historial) |
| El repositorio va **fuera** de `TallerProyectos` | Claude Code carga también los `CLAUDE.md` de las carpetas padre; el de `TallerProyectos` es el de la serie documental y contiene parámetros de la versión 1 |
| Rama `main`, *push* solo con confirmación | El repositorio base usaba `master`. El script pide escribir `SI` antes de subir |

## 2. Requisitos previos (una vez)

```powershell
git --version                  # 2.36 o superior (lo exige git-filter-repo)
python --version               # 3.12
git config --global user.name  # tu nombre real: firmará el commit del PR 0 y los tuyos
git config --global user.email # el correo de tu cuenta de GitHub
gh --version                   # opcional; GitHub CLI facilita crear el repo y los PR
```

- El repositorio `omarpiero/TP_RAG_Quechua` debe existir **vacío** (sin README ni .gitignore) y ser **privado**.
  Si no existe: `gh repo create omarpiero/TP_RAG_Quechua --private` o desde github.com/new.
- **Nota para el integrante autor de la base:** su repositorio público no se toca. Conviene que lo pase a
  privado, porque versiona el texto del corpus (hallazgo m-1 de `docs/08`).

## 3. Ejecutar

Desde PowerShell, en la carpeta `SDD_RAG_Quechua` (dentro de `TallerProyectos`):

```powershell
powershell -ExecutionPolicy Bypass -File .\crear_repo.ps1
# Otra ruta de destino:
powershell -ExecutionPolicy Bypass -File .\crear_repo.ps1 -Destino D:\dev\TP_RAG_Quechua
# Solo preparar, sin subir:
powershell -ExecutionPolicy Bypass -File .\crear_repo.ps1 -SinPush
```

El script se ejecutó de prueba sobre una copia del repositorio base (sin *push*): el historial queda en
16 commits del integrante, más el commit `chore(repo)` del usuario. `backend/data/` conserva los
fragmentos en disco, ignorados por Git, y `.claude/` y `.mcp.json` quedan instalados. Antes del commit, el
script **aborta** si se fuera a versionar algún `fragmentos_*.jsonl`, `evaluacion_prosa.json`, PDF, `.env`,
`.db` o `.bin`.

## 4. Después del *push* (en github.com)

1. **Settings → Collaborators:** invitar a los cuatro integrantes (rol *Write*) y, para la revisión, al
   docente (*Read*).
2. **Settings → Branches → Add rule** para `main`: *Require a pull request before merging* (1 aprobación),
   *Require status checks* (cuando exista la CI del PR 10), *Do not allow bypassing*. En el plan gratuito, las
   reglas sobre repositorios **privados** pueden no estar disponibles. Si no lo están, la regla la cumple el
   equipo: nadie hace *push* a `main`, y `.claude/settings.json` ya prohíbe a Claude Code hacerlo.
3. **Settings → Code security:** activar *Secret scanning* y *Dependabot alerts* si el plan lo permite.
4. **Projects:** crear el tablero según `CONSIDERACIONES.md` §7.4.

## 5. Estructura que tendrá el repositorio

| Momento | Árbol |
|---|---|
| Tras el PR 0 (este script) | Igual que la base (`backend/{domain,application,infrastructure}`, `frontend/`, `docs/`) + `CLAUDE.md`, `CONSIDERACIONES.md`, `PROMPT_CIERRE_PMV1.md`, `docs/00…12`, `corpus/`, `referencia_poc/`, `.claude/`, `.mcp.json` |
| Tras el PR 1–2 (Claude Code) | La estructura objetivo de `CONSIDERACIONES.md` §4.1: `backend/src/{domain,application/{ports/{in,out},use_cases,factories},adapters/{in,out},infrastructure}` |

El movimiento a `src/` se hace con `git mv` en el PR 1 para que `git log --follow` conserve el historial
de cada archivo.

## 6. Commits de cada integrante

El script y Claude Code firman con **tu** identidad de Git. Para que el historial muestre a los cinco
integrantes, cada uno debe hacer sus propios commits desde su cuenta. La forma más práctica es que cada
uno clone el repositorio y se encargue de los PR de su rol (`CONSIDERACIONES.md` §7.1). Pueden usar Claude
Code en su equipo con el mismo `CLAUDE.md`. **Nunca** se cambia el autor de un commit para atribuirlo a
otra persona.
