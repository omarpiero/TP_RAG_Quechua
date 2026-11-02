# Auditoría breve · PR #20 `fix/sonar-smells` · 2026-11-01

**Alcance:** equivalencia de regex, firma de `extraer()`, pruebas, frontend. Auditoría acotada (no se consultó SonarQube ni pip-audit/npm audit).
**Veredicto:** apto para revisión humana. Bloqueantes 0 · Mayores 0 · Menores 1.

## 1. Regex (salvaguarda)
- `PATRON_LEMA`: comparado con el de `origin/main` sobre los 3 605 fragmentos de `fragmentos_v3.jsonl` y 271 480 cadenas adversariales (espacios, tabuladores, guiones, NBSP, vacíos): 0 diferencias en span y grupo.
- `SEPARADOR_DE_FORMAS`: `[,;/]` sin espacios; el único uso (`comprobar`) hace `strip` y `_tokens` descarta espacios. Comparación exhaustiva sobre 3 257 437 cadenas (alfabeto con `, ; / \t \n . -`): 0 diferencias en la tokenización.
- `VerificadorFormaLiteral` sigue rechazando: forma truncada, lema como forma, forma de otra entrada, par cruzado y formas fusionadas sin coma; acepta la forma correcta.
- `pytest -m salvaguarda`: 65 pasan. Unit+architecture: 363 pasan, 6 omitidas.

## 2. `extraer()`
Se quitó `idioma` en `OllamaGenerador` y `GeminiGenerador`. Único llamador de producción (`GeneradorExtractivo`) y todas las pruebas ajustados; sin otros llamadores (el `extraer` de `ExtraccionDocumentalPort` es otro método). Hallazgo menor: el parámetro dejó de estar en las dos implementaciones, pero conviene confirmar que `GeneradorTextoPort` no lo declara (no lo declara `extraer`, que no es del puerto).

## 3. Pruebas
Los `assert a and b` se separaron en aserciones equivalentes; los `pytest.raises` ahora envuelven una sola llamada y las preparaciones salen del bloque. Ninguna pierde fuerza ni cambia lo comprobado. Las pruebas `salvaguarda` afectadas siguen verdes.

## 4. Frontend
`App.jsx`: extracción de `Pestanas` y `PieEstado` con las mismas ramas, textos y `data-testid`; sin cambio de comportamiento. `App.css`: reglas fusionadas; el resultado en cascada es idéntico (`.origenes__control` ya terminaba en flex con min-height 44 px). `Nube.test.jsx`: `findByText` equivale al `waitFor`. Vitest: 34 pasan.

## Hallazgos
| Sev. | Dónde | Descripción |
|---|---|---|
| Menor | `scripts/*`, ruff | 13 errores de ruff preexistentes fuera del diff del PR (no atribuibles). |

Sin RN/RS afectadas: τ no tocado, sin cambios de red/secretos.
