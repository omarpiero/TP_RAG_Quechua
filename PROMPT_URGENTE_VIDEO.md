# Prompt urgente — dejar el PMV1 listo para grabar el video (con .exe)

> **Uso.** Antes de pegar, ejecuta `/compact` (o abre una sesión nueva) y, si quieres ahorrar uso, `/model sonnet`.
> Cuando pida permiso para `pytest`, `npm`, `python -m PyInstaller` o `git commit`, elige «Yes, and don't ask
> again» para no frenar el trabajo. Pega el bloque completo.

```text
MODO URGENTE (autorizado por el usuario): tengo que grabar el video del PMV1 hoy. Objetivo único: dejar la app
corregida, probada y empaquetada como .exe, con el mínimo gasto de tokens.

REGLAS DE AHORRO (obligatorias)
- No releas docs completos. Usa solo: CLAUDE.md §2 y §7, docs/specs/PR-01 y PR-02 (aprobadas), docs/13 §3 y §4.1,
  docs/11 §2. Busca con rg/grep dirigido; no abras archivos de datos (fragmentos_*.jsonl, evaluacion_prosa.json).
- Salidas largas siempre recortadas (| tail -20). Nada de explicaciones entre pasos; al final de cada bloque,
  un resumen de ≤ 3 líneas.
- Delega la implementación en el subagente programador en bloques grandes (un encargo por bloque, con todo el
  contexto que necesite). El auditor revisa UNA sola vez, al final, la rama entera.
- Decisiones ya tomadas, no me las vuelvas a preguntar: specs PR-01 y PR-02 APROBADAS; ADR-021 aceptada con
  las condiciones de docs/13 §3; ADR-027 SQLite por defecto; τ = 0,48 (no cambia); el historial de Git ya está
  resuelto (main == origin/main), puedes hacer commits.

FLUJO DE TRABAJO
- Una sola rama: feat/cierre-pmv1-video, desde main. Un commit (Conventional Commits, Refs) por bloque.
- Tras cada bloque: pytest -q | tail -5 y el arnés scripts/arnes_linea_base.py comparado con
  docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/. Los bloques 1–2 deben dar CSV idénticos. Los bloques
  3+ solo pueden cambiar lo que declaran (D-1, vía de respaldo). Si aparece CUALQUIER falso positivo en C, o un
  cambio no declarado, te detienes y me avisas.
- Al terminar abres el PR con gh pr create. NO fusionas; lo fusiono yo.

BLOQUES (en este orden; si el tiempo no da, para después del 5 y avísame)
1. PR-01 tal cual su spec: mover a backend/src/{domain,application,adapters,infrastructure} con git mv;
   pyproject.toml, requirements-dev.txt, .gitattributes.
2. PR-02 tal cual su spec: 5 puertos de entrada, controladores REST por recurso dependientes solo del puerto,
   CLI mínima (consultar, indexar), LOG INFO POR CAPA (controlador → puerto de entrada → caso de uso → índice
   → evaluador → generador → repositorio), arbol_src.txt y puertos.md en docs/evidencias/.
3. Reglas (núcleo del PR-03, versión mínima):
   - τ solo desde config.py; se elimina el literal UMBRAL_CALIBRADO.
   - Regla de lema explícita, con el campo via_respaldo ∈ {similitud, lema} en la respuesta y en el DTO.
   - D-1: las consultas léxicas («cómo se dice X», «how do you say X», término suelto) no reciben pasajes de
     prosa.
   - D-6: si Ollama falla, el caso de uso devuelve el fragmento literal con el aviso «el servicio de redacción
     no está disponible», nunca un 500.
   Cada una con su prueba @salvaguarda.
4. Persistencia: SQLite por defecto (base_datos="sqlite" también fuera del .exe), GET y DELETE /api/historial,
   sin identificadores personales.
5. Interfaz React (solo esto):
   - A− / A+ / restablecer, con límites y preferencia recordada.
   - Estados de carga y de error, con reintento.
   - Validación de 1–300 caracteres.
   - Indicadores en tiempo real: barra de similitud frente a τ, latencia en ms, vía de respaldo («entrada exacta
     del diccionario» cuando es por lema) y documento + página.
   - Pasajes de prosa rotulados «no es una respuesta».
   - Todas las lecturas de la traducción.
   - Historial desde la API, con botón Borrar y aviso de privacidad.
   - Sin desbordes a 360 px.
6. Ejecutable: actualizar QuechuaWankaWeb.spec y ejecutable.py a la nueva estructura (src/).
   - Que la consola quede VISIBLE (console=True), para que el log por capas se vea en el video.
   - SQLite junto al .exe; la interfaz compilada (npm run build → backend/interfaz) va dentro del .exe.
   - Al arrancar, comprueba Ollama y avisa si no responde; abre el navegador en http://127.0.0.1:8000.
   - Construir con python -m PyInstaller QuechuaWankaWeb.spec --noconfirm y comprobar que dist/ arranca.
   - dist/, build/ y backend/interfaz/ NO se versionan.
7. Prueba de humo para el video: arranca el .exe y ejecuta contra la API los casos C-01 (zorro),
   C-02 (criptomoneda), C-03 (how do you say fox…), C-05 (pregunta de prosa P001), C-07 (vacía y > 300 car.),
   C-09 (historial tras reiniciar) y C-10 (con Ollama detenido).
   - Rellena docs/11 §3 con las salidas reales: similitud, vía, documento y página, latencia y si se invocó el
     generador.
   - Si alguno no da lo esperado, dímelo antes de que grabe.
8. Mediciones rápidas (mientras grabo):
   - Arnés M2–M4 sobre el código final.
   - M5: 30 consultas con Qwen3.5-4B real (P50/P95, en frío y en caliente, tokens/s, ollama ps).
   - pytest con cobertura por capa (M7/M8).
   - Resultado en docs/evidencias/<fecha>_<commit>_pc-rtx4060/ con mediciones.json.

FUERA DE ALCANCE AHORA (va después del video): verificador de forma literal (PR-04), truncado (PR-06), CI con
SonarQube, Newman, Gherkin completo, PR-05, M9–M17.

INFORME FINAL (≤ 10 líneas): ruta del .exe, comando de arranque, tabla de los casos C-xx (OK/falla), cifras clave
(recall A/B/D, FP en C, P50/P95), enlace al PR y qué quedó pendiente.
```

## Mientras trabaja el agente

- Haced la medición manual M16 (`docs/evidencias/m16/`). No depende del código.
- Prepara la grabación según `docs/11_CASOS_VIDEO_Y_CAPTURAS.md` §4: consola del .exe a la derecha, navegador a
  la izquierda, una consulta de calentamiento fuera de cámara y `ollama ps` mostrando GPU.
- **No grabes hasta que el paso 7 dé OK en C-01, C-02, C-03 y C-10.**
