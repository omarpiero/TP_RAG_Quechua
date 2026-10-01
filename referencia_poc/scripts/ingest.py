"""Ingesta del corpus de quechua wanka: extrae texto por página, conserva
procedencia (documento + página) y segmenta en fragmentos.
Uso: python3 ingest.py corpus fragmentos.jsonl
"""
import sys, json, re, hashlib, pathlib, warnings
warnings.filterwarnings('ignore')
from pypdf import PdfReader

def reunir_lineas_rotas(t):
    """Algunas capas de OCR devuelven un token por línea. Se detecta por la
    longitud media de línea y se recompone el texto."""
    lineas = [l for l in t.split('\n') if l.strip()]
    if len(lineas) < 15:
        return t
    media = sum(len(l.strip()) for l in lineas) / len(lineas)
    if media >= 12:
        return t
    salida = ' '.join(l.strip() for l in lineas)
    salida = re.sub(r'\s+([,.;:%\)\]\?\!])', r'\1', salida)
    salida = re.sub(r'([\(\[])\s+', r'\1', salida)
    salida = re.sub(r'\s*-\s*(?=[a-záéíóúñ])', '', salida)   # guion de corte silábico
    return salida

def limpiar(t):
    t = t.replace('\x00', ' ')
    t = reunir_lineas_rotas(t)
    t = re.sub(r'-\n(?=[a-záéíóúñ])', '', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()

def segmentar(texto, objetivo=650):
    parrafos = [p.strip() for p in re.split(r'\n\s*\n|\n(?=[A-ZÁÉÍÓÚÑ]{3,})', texto) if p.strip()]
    trozos, buf = [], ''
    for p in parrafos:
        if len(buf) + len(p) + 1 <= objetivo:
            buf = (buf + '\n' + p).strip()
        else:
            if buf:
                trozos.append(buf)
            if len(p) <= objetivo:
                buf = p
            else:
                for i in range(0, len(p), objetivo):
                    trozos.append(p[i:i + objetivo])
                buf = ''
    if buf:
        trozos.append(buf)
    return [t for t in trozos if len(t) > 40]

def main(carpeta, salida):
    filas, resumen = [], []
    for pdf in sorted(pathlib.Path(carpeta).glob('*.pdf')):
        try:
            lector = PdfReader(str(pdf))
        except Exception as e:
            print('ERROR', pdf.name, e); continue
        con_texto = 0; caracteres = 0; frag_doc = 0
        for n, pagina in enumerate(lector.pages, start=1):
            try:
                texto = limpiar(pagina.extract_text() or '')
            except Exception:
                texto = ''
            if len(texto) < 60:
                continue
            con_texto += 1; caracteres += len(texto)
            for j, trozo in enumerate(segmentar(texto)):
                filas.append({
                    'id': hashlib.md5(f'{pdf.name}|{n}|{j}'.encode()).hexdigest()[:12],
                    'documento': pdf.name,
                    'pagina': n,
                    'texto': trozo
                })
                frag_doc += 1
        resumen.append({'documento': pdf.name, 'paginas': len(lector.pages),
                        'paginas_con_texto': con_texto, 'caracteres': caracteres,
                        'fragmentos': frag_doc})
        print(f'{pdf.name[:52]:54s} {len(lector.pages):4d} pág · {con_texto:4d} con texto · {caracteres:7d} car · {frag_doc:5d} frag')
    with open(salida, 'w', encoding='utf-8') as f:
        for r in filas:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open('resumen_corpus.json', 'w', encoding='utf-8') as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print('TOTAL fragmentos:', len(filas))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
