# Auditoría PR #5 · HU-09 (origen de las consultas)

- **PR / rama:** #5 `feat/HU-09-origen-consultas` (apilado sobre #4; diff propio `fix/BUG-01-datos-escribibles..aee58c5`; la rama recibió después el merge c737a76 con BUG-01, no auditado aquí)
- **Fecha:** 2026-10-29
- **Puerta de calidad (SonarQube local):** estado OK sin condiciones; el proyecto `omarpiero_rag-quechua-wanka` **no tiene ningún análisis real** (solo el evento SQ_UPGRADE). El análisis completo corresponde al bloque B9. No se ejecutó sonar-scanner.
- **Cobertura (aee58c5, sin `lento`):** global 87 % (mín. 70 %); `domain/` ≈ 94 % (21 líneas sin cubrir de 349). Cumple.
- **Pruebas:** 170 pasan, 4 omitidas (PostgreSQL) en la ejecución general; `salvaguarda` 18/18; arquitectura 6/6; Vitest 20/20. **PostgreSQL:** las 4 pruebas se ejecutaron contra `quechua_wanka_pruebas` (credencial leída con pydantic-settings, sin imprimirla) y pasan.
- **pip-audit:** sin vulnerabilidades conocidas. `npm audit`: no ejecutado (sin cambios de dependencias en el diff).
- **Ruff:** el cambio no introduce fallos de salvaguarda; ver hallazgos menores.

## Hallazgos

| # | Sev. | Archivo:línea | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Menor | `backend/scripts/generar_transacciones.py:35` | Estilo (I001) | El import de `domain.value_objects.origen_consulta` queda desordenado respecto a `infrastructure` (añadido por este PR). | `ruff check --fix`. |
| 2 | Menor | `frontend/src/componentes/PanelPrediccion.jsx:261` | react-hooks/exhaustive-deps | `useEffect(cargar, [])` usa `sinteticas`; aviso del linter (el valor inicial es `false`, sin efecto real). | Documentar con comentario o reestructurar. |
| 3 | Menor | `backend/src/application/use_cases/analizar_demanda.py` (aviso) | Honestidad del rótulo | El aviso dice «generadas por la prueba de carga» aunque las sintéticas puedan ser de `arnes` o `humo`. | Redactar «consultas de prueba (carga, arnés, humo)». |
| 4 | Menor | `backend/src/adapters/in/rest/prediccion_controller.py` | Diseño | `incluir_sinteticas` es público (cualquier cliente local puede pedir la demostración). Es seguro (siempre rotulado, no es el modo por defecto, no altera datos), pero conviene registrarlo como decisión. | Anotar en ADR-013 o dejarlo así de forma explícita. |
| 5 | Menor | `docs/evidencias/.../registro.md` | Trazabilidad | Las 65 consultas previas quedan como `usuario` sin poder distinguir pruebas manuales; está declarado en la evidencia. Aceptable; mantener el aviso en el informe. | Ninguna. |
| 6 | Menor | scripts y 19 archivos | `ruff format` / E501 | Cuatro E501 en `generar_transacciones.py` y `humo_bloque7.py`, y 2 archivos tocados sin formatear; en gran parte preexistentes. | Formatear. |

Sin bloqueantes ni mayores.

## Verificación por foco

1. **HU-09 honesta (ADR-013).** El mínimo de 100 cuenta solo `origen = usuario`: `estadisticas(incluir_sinteticas=False)` filtra por `usuario` y el caso de uso compara ese total con `minimo`. Con la base de carga (800 sintéticas) y 0 reales responde «insuficiente» y avisa. `incluir_sinteticas` por defecto es `False` en controlador, puerto, caso de uso y repositorios; con él activo y sintéticas presentes, `modo="demostracion"` y `aviso` siempre. El cliente no puede fijar `origen`: `ConsultaEntrada` solo admite `texto` (1–300); el origen sale de `Configuracion.origen_consultas` (variable de entorno del servidor, `Literal` validado) o del constructor del `Contenedor` en scripts. La CLI registra como `usuario` (humano). Los scripts de arnés/PoC no registran (`repositorio=None`).
2. **Migraciones.** SQLite: `COLUMNAS_HU09` con `ALTER TABLE … NOT NULL DEFAULT 'usuario'`, idempotente; prueba con una .db antigua (columna eliminada, fila previa) pasa. PostgreSQL: `ADD COLUMN IF NOT EXISTS`, `DROP … IF EXISTS` de firmas anteriores y recreación; `p_origen DEFAULT 'usuario'` y `COALESCE`; `p_solo_usuario DEFAULT TRUE`, por lo que las llamadas anteriores siguen funcionando. Sin inyección: todo parametrizado (`:origen`, `:solo`, `:limite`); el único SQL con f-string toma nombres y tipos de constantes del código. Riesgo menor: el `DROP` de firmas viejas elimina objetos en cada reinstalación (idempotente, aceptable).
3. **Interfaz.** Cabecera: aviso `role="status"` si `base_demostracion` (más de la mitad sintéticas). Panel: aviso de demostración cuando `modo === "demostracion"`, conteo por origen con etiquetas «(sintética)» y casilla explícita «no es demanda real». Pruebas de Vitest cubren ambos.
4. **Salvaguarda y RN-06.** El diff no toca recuperación, τ, evaluador ni generador; `consultar_corpus.py` solo añade `origen` y un reformateo. 18 pruebas `salvaguarda` en verde; RN-06 intacta (los predictores solo añaden abstenciones). No se reejecutó el arnés `@lento`/`datos`; el comportamiento no cambia por inspección del diff.
5. **SonarQube.** Ver arriba: sin análisis real; pendiente en B9.

## Estado de reglas
RN-01…RN-10: sin cambios, cumplen (RN-06 verificada). RS-01…RS-08: sin cambios; sin secretos versionados, entradas validadas, localhost, sin telemetría; el servidor MCP no se toca.

## Veredicto: **apto** para revisión humana (0 bloqueantes · 0 mayores · 6 menores)
