"""Ingesta v2: segmentación adaptada al tipo documental.
Los materiales lexicográficos se segmentan por entrada; la prosa, por bloques.
"""
import json, re, hashlib, pathlib, warnings, sys
warnings.filterwarnings('ignore')
from pypdf import PdfReader
from ingest import limpiar, segmentar

LEXICOGRAFICOS = ('293274822', 'diccionario-visual')
PAT_ENTRADA = re.compile(r'^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ]{2,24}):\s*([^\n]{2,80})', re.M)

def segmentar_lexico(texto):
    """Una entrada = un fragmento. Lo no reconocido se agrupa en bloques cortos."""
    trozos, resto = [], []
    for linea in texto.split('\n'):
        m = PAT_ENTRADA.match(linea.strip())
        if m:
            trozos.append(linea.strip())
        elif linea.strip():
            resto.append(linea.strip())
    if resto:
        bloque = ' '.join(resto)
        for i in range(0, len(bloque), 300):
            t = bloque[i:i + 300]
            if len(t) > 40:
                trozos.append(t)
    return [t for t in trozos if len(t) > 8]

def main(carpeta, salida):
    filas, resumen = [], []
    for pdf in sorted(pathlib.Path(carpeta).glob('*.pdf')):
        try:
            lector = PdfReader(str(pdf))
        except Exception as e:
            print('ERROR', pdf.name, e); continue
        lexico = pdf.name.startswith(LEXICOGRAFICOS)
        con_texto = caracteres = frag_doc = 0
        for n, pagina in enumerate(lector.pages, start=1):
            try:
                texto = limpiar(pagina.extract_text() or '')
            except Exception:
                texto = ''
            if len(texto) < 60:
                continue
            con_texto += 1; caracteres += len(texto)
            trozos = segmentar_lexico(texto) if lexico else segmentar(texto)
            for j, trozo in enumerate(trozos):
                filas.append({'id': hashlib.md5(f'{pdf.name}|{n}|{j}'.encode()).hexdigest()[:12],
                              'documento': pdf.name, 'pagina': n, 'texto': trozo,
                              'tipo': 'lexicografico' if lexico else 'prosa'})
                frag_doc += 1
        resumen.append({'documento': pdf.name, 'paginas': len(lector.pages),
                        'paginas_con_texto': con_texto, 'caracteres': caracteres,
                        'fragmentos': frag_doc,
                        'tipo': 'lexicografico' if lexico else 'prosa'})
        print(f'{pdf.name[:50]:52s} {len(lector.pages):4d} pág · {con_texto:4d} con texto · {caracteres:7d} car · {frag_doc:5d} frag')
    with open(salida, 'w', encoding='utf-8') as f:
        for r in filas:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    json.dump(resumen, open('resumen_corpus.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('TOTAL fragmentos:', len(filas))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
