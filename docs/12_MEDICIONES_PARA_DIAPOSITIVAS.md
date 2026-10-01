# 12 · Mediciones que necesitan las diapositivas, las figuras y el informe

> **Para quién.** El orquestador, que ejecuta las mediciones con `scripts/medir_pmv1.py`, y el usuario,
> que entrega la carpeta resultante al asistente documental.
>
> **Base.** El protocolo completo (M1–M15, formato de `mediciones.json`, metadatos obligatorios) está en
> `CONSIDERACIONES.md` §8. Este archivo dice **para qué sirve cada medición** y **qué hay que devolver**.
> Regla de siempre: lo que no se mida queda «por registrar»; ninguna cifra se rellena a mano.

---

## 1. Diapositiva → figura → medición

| # | Diapositiva (rol) | Figura o dato | Medición | Archivo de origen |
|---|---|---|---|---|
| 1 | Carátula | Nombres y roles, enlaces al repo y al video | — | Lo da el usuario |
| 2 | Antecedentes (PM) | Cifras de literatura (Wang, Merx, Swacha, Puraca) | — (fuentes ya verificadas) | — |
| 3 | Problema (PM) | Árbol de problemas; KPIs de partida | **M1** (páginas con texto, fragmentos legibles, páginas señaladas) | `mediciones.json → M1_corpus` |
| 4 | Solución (AIE) | Flujo con abstención; ejemplo «zorro → Atuq, p. 37» | **M4** (decisión por vía) + C-01 de `docs/11` §3 | `arnes_por_consulta.csv`, captura `E1-1` |
| 5 | Objetivos medibles (QA) | Tabla OE1–OE5: meta frente a resultado | **M1, M2, M3, M4, M5** | `mediciones.json` |
| 6 | Trazabilidad C1→C6 (PM) | Matriz integradora | — (`CONSIDERACIONES.md` §10.3) | — |
| 7 | Arquitectura hexagonal (ARQ) | Hexágono y diagrama de paquetes con los **nombres reales** de clases y puertos | Árbol de `backend/src` del commit medido | `GH-1`, listado de `application/ports/{in,out}` |
| 8 | Patrones (ARQ) | Repository (SQLite + PostgreSQL), Factory, DI, Strategy (UmbralConLema, TraductorTabla/Ollama), Adapter | Nombres de clase reales | Código del commit medido |
| 9 | Módulo de IA: umbral (AIE) | **Barrido de τ** (precisión, recall, F1 y FP frente a τ) con y sin regla de lema; **matriz de confusión** en τ vigente | **M3** | `barrido_umbral.csv`, `M3_umbral` |
| 10 | Evidencias (DEV) | Capturas E1 y estructura en GitHub | **Capturas** de `docs/11` §5 | `capturas/` |
| 11 | Resultados consolidados (QA) | Tabla: pruebas, cobertura, SonarQube, Newman, latencia, recall por partición, FP en C, paridad, tamaño | **M2, M3, M4, M5, M7, M8, M9, M10, M13, M14** | `mediciones.json`, `junit.xml`, `coverage.xml`, `sonar.json`, `newman.json` |
| 12 | Video (DEV) | Enlace y fotogramas | Grabación de `docs/11` §4 | Lo da el usuario |
| 13 | Cierre / limitaciones (PM) | D es techo; HU-04 no evaluada; PMV3 sin validar en dispositivo; L-1…L-9 | **M2 (D), M15** | `mediciones.json` |

Figuras del informe (C5/C6) que también dependen de mediciones:

| Figura | Medición |
|---|---|
| Ecosistema con limitaciones (C5) | M9, M10, M11 (qué herramienta encontró qué) |
| Latencia GPU frente a CPU | **M5** en las dos máquinas + `HW-1`/`HW-2` |
| Recall por partición | **M2** (A, B, D sin/tabla/Ollama, E y D′ si existen) |
| Despliegue (PC escritorio / compilación / móvil) | M6 (memoria), M13 (tamaños exportados) |
| Métricas ágiles (C4) | **M12** (commits por autor, PR, lead time) |

## 2. Lo mínimo imprescindible si falta tiempo

Si solo da tiempo a una ronda de mediciones, estas son las que sostienen la exposición. Sin ellas, las
diapositivas 5, 9 y 11 quedan con «por registrar»:

1. **M3**: barrido de τ y matriz de confusión con 0 FP en C. Es el corazón del módulo de IA.
2. **M2**: recall@1, recall@5 y MRR@10 por partición, con D declarado techo.
3. **M4**: 0 invocaciones del generador sin respaldo; 0 respuestas sin documento o página.
4. **M5**: latencia P50/P95 con Qwen3.5-4B real, en GPU y, si se puede, en CPU.
5. **M7 + M8**: pruebas y cobertura por capa.
6. Las capturas `E1-1`, `E1-2`, `E1-3`, `GH-1`, `GH-2`, `QA-1`.

## 3. Qué entregar al asistente documental

Una carpeta comprimida con:

```
docs/evidencias/<AAAA-MM-DD>_<commit>_<maquina>/      ← una por máquina (GPU y CPU)
├── mediciones.json · MEDICIONES.md
├── barrido_umbral.csv · arnes_por_consulta.csv · latencias.csv · paridad.csv · respuestas_por_lema.csv
├── junit.xml · coverage.xml · lcov.info · pip_audit.json · npm_audit.json · newman.json · sonar.json
└── capturas/*.png
docs/evidencias/<fecha>_base-integrante_<maquina>/    ← la línea base congelada (para el «antes/después»)
docs/11_CASOS_VIDEO_Y_CAPTURAS.md                     ← con el §3 rellenado
backend/src/ (solo el árbol: `tree /F backend\src > arbol_src.txt`)
```

Más tres datos que no salen del código: **nombres y roles** del equipo, **enlace del repositorio** y
**enlace del video**.

Con eso se regeneran, con cifras medidas:
- las figuras de `docs/diagramas/`: hexágono, paquetes, despliegue, secuencia, confusión, ecosistema y
  recall (hoy muestran Streamlit y τ 0,41 de la versión 1);
- `Recursos_Visuales_Exposicion.docx`;
- las diapositivas;
- el guion de exposición;
- la tabla de resultados del informe.

## 4. Comprobaciones antes de entregar

- [ ] `meta.commit` de `mediciones.json` coincide con la etiqueta `v0.1.0` (o con el commit que se va a mostrar).
- [ ] `meta.tau` y `meta.regla_lema` coinciden con lo decidido en ADR-020 y ADR-021.
- [ ] Ningún campo con un valor «a mano»: lo no medido figura como `"estado": "no_medido"` con motivo.
- [ ] Las cifras nuevas de la revisión 2 (0,48 · 92,8 % · 180/180 · 90,2 % · 70,6 % · 21,5 MB · 2,5 × 10⁻⁸)
      están **reproducidas** o, si no, la diferencia está anotada en `MEDICIONES.md`.
- [ ] Las capturas no muestran datos personales (correo, rutas con el nombre de usuario, marcadores).
