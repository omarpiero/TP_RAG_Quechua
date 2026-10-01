# corpus/

Copia de trabajo del corpus documental sobre quechua wanka usado por el sistema.

| Ruta | Contenido | ¿En Git? |
|---|---|---|
| `pdf/` | Los 8 PDF (≈ 96 MB, 679 páginas, 600 con capa de texto) | **No** (`.gitignore`) — licencias heterogéneas (R-07, ADR-015) |
| `MANIFIESTO.yaml` | Por documento: título, autoría, fuente, fecha de incorporación, licencia, tipo, páginas y huella SHA-256 | Sí |

## Reglas

1. **Ningún PDF entra en el sistema sin su entrada en `MANIFIESTO.yaml`** (RNF-11, DoD-7). La ingesta
   lo rechaza.
2. **No renombrar los archivos de `pdf/`.** El nombre forma parte del identificador de fragmento
   (`md5("<archivo>|<página>|<índice>")[:12]`) al que apunta el conjunto de evaluación. Por eso el
   PDF de *Saberes y haceres* se copió como `Saberes_y_Haceres_VII_1_Quechua_Wanka.pdf`, el nombre
   con el que se indexó en la prueba de concepto; el nombre original consta en el manifiesto.
3. Para comprobar que la copia local es la correcta, la huella SHA-256 de cada archivo debe coincidir
   con la del manifiesto. La ingesta lo verifica.
4. Los campos «por registrar» (licencia, fuente, autoría) los completa **el usuario**. Ningún agente
   los rellena por suposición. Bloquean el cierre del Hito 1, no la ingesta.
5. Para añadir un documento: copiar el PDF a `pdf/`, añadir su entrada al manifiesto y ejecutar la
   reindexación (RNF-12). No se modifica código.

Origen de esta copia: `TallerProyectos/docs_idea2/corpus/` (2026-09-24).
