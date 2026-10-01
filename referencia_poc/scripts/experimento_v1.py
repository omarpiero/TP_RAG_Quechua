"""Experimentos de recuperación y de umbral de abstención sobre el corpus real.
Salida: resultados_v2.json  (todas las cifras del Documento 6 proceden de aquí)
"""
import json, re, time, unicodedata, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from rank_bm25 import BM25Okapi

FRAG = [json.loads(l) for l in open('fragmentos.jsonl', encoding='utf-8')]
EVAL = json.load(open('evaluacion_v1.json', encoding='utf-8'))
IDS = [f['id'] for f in FRAG]
POS = {d: i for i, d in enumerate(IDS)}

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s)

TEXTOS = [norm(f['texto']) for f in FRAG]

# ---------- E1: BM25 léxico ----------
tok = lambda s: re.findall(r'[a-z0-9]+', s)
bm25 = BM25Okapi([tok(t) for t in TEXTOS])

# ---------- E2: TF-IDF de n-gramas de caracteres ----------
vec_c = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2, sublinear_tf=True)
M_c = normalize(vec_c.fit_transform(TEXTOS))

# ---------- E2b: TF-IDF de palabras ----------
vec_w = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1, sublinear_tf=True)
M_w = normalize(vec_w.fit_transform(TEXTOS))

RUIDO = re.compile(r'\b(en|el|la|del|de|quechua|wanka|huanca|variedad|como|se|dice|que|es|word|for|in|how|do|you|say|the|necesito|termino|para|referirme|estoy|buscando|palabra|designa|what|a)\b')

def depurar(q):
    q = RUIDO.sub(' ', q)
    return re.sub(r'[^a-z0-9 ]', ' ', q).strip()

def buscar(estrategia, consulta, k=10, depurada=False):
    q = norm(consulta)
    if depurada:
        q = depurar(q)
    if estrategia == 'bm25':
        s = np.asarray(bm25.get_scores(tok(q)), dtype=float)
        mx = s.max() if s.max() > 0 else 1.0
        s = s / mx                      # normalizado por consulta: solo para ordenar
    elif estrategia == 'char':
        s = (M_c @ normalize(vec_c.transform([q])).T).toarray().ravel()
    elif estrategia == 'palabra':
        s = (M_w @ normalize(vec_w.transform([q])).T).toarray().ravel()
    elif estrategia == 'hibrido':
        a = (M_c @ normalize(vec_c.transform([q])).T).toarray().ravel()
        b = (M_w @ normalize(vec_w.transform([q])).T).toarray().ravel()
        s = 0.5 * a + 0.5 * b
    idx = np.argpartition(-s, k)[:k]
    idx = idx[np.argsort(-s[idx])]
    return [(IDS[i], float(s[i])) for i in idx]

ESTRATEGIAS = ['bm25', 'palabra', 'char', 'hibrido']
import os
DEPURAR = os.environ.get('DEPURAR','0')=='1'
res = {'corpus': {'documentos': len(set(f['documento'] for f in FRAG)),
                  'fragmentos': len(FRAG),
                  'caracteres': sum(len(f['texto']) for f in FRAG)},
       'consultas': {'A': sum(1 for e in EVAL if e['subconjunto'] == 'A_lexico_es'),
                     'B': sum(1 for e in EVAL if e['subconjunto'] == 'B_independiente'),
                     'C': sum(1 for e in EVAL if e['subconjunto'] == 'C_fuera_de_cobertura'),
                     'D': sum(1 for e in EVAL if e['subconjunto'] == 'D_ingles')},
       'estrategias': {}}

for est in ESTRATEGIAS:
    detalle, tiempos = [], []
    for e in EVAL:
        t0 = time.perf_counter()
        top = buscar(est, e['consulta'], k=10, depurada=DEPURAR)
        tiempos.append((time.perf_counter() - t0) * 1000)
        oro = set(e['oro'])
        rank = next((i + 1 for i, (d, _) in enumerate(top) if d in oro), None)
        detalle.append({'id': e['id'], 'sub': e['subconjunto'], 'rank': rank,
                        'top1': top[0][1], 'top5': [s for _, s in top[:5]]})
    def m(sub):
        d = [x for x in detalle if x['sub'] == sub]
        if not d: return {}
        r1 = sum(1 for x in d if x['rank'] == 1) / len(d)
        r5 = sum(1 for x in d if x['rank'] and x['rank'] <= 5) / len(d)
        mrr = sum(1 / x['rank'] for x in d if x['rank']) / len(d)
        return {'n': len(d), 'recall@1': round(r1, 4), 'recall@5': round(r5, 4),
                'MRR@10': round(mrr, 4),
                'similitud_top1_media': round(float(np.mean([x['top1'] for x in d])), 4)}
    res['estrategias'][est] = {
        'A_lexico_es': m('A_lexico_es'),
        'B_independiente': m('B_independiente'),
        'C_fuera_de_cobertura': m('C_fuera_de_cobertura'),
        'D_ingles': m('D_ingles'),
        'latencia_ms': {'media': round(float(np.mean(tiempos)), 2),
                        'p95': round(float(np.percentile(tiempos, 95)), 2)},
        'detalle': detalle}

# ---------- umbral de abstención (solo estrategias con similitud acotada) ----------
def barrido(est):
    d = res['estrategias'][est]['detalle']
    pos = [x['top1'] for x in d if x['sub'] in ('A_lexico_es', 'B_independiente')]
    neg = [x['top1'] for x in d if x['sub'] == 'C_fuera_de_cobertura']
    filas = []
    for u in np.arange(0.02, 0.61, 0.01):
        vp = sum(1 for s in pos if s >= u); fn = len(pos) - vp
        fp = sum(1 for s in neg if s >= u); vn = len(neg) - fp
        prec = vp / (vp + fp) if vp + fp else 0.0
        rec = vp / (vp + fn) if vp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        filas.append({'umbral': round(float(u), 2), 'VP': vp, 'FP': fp, 'VN': vn, 'FN': fn,
                      'precision': round(prec, 4), 'recall': round(rec, 4), 'F1': round(f1, 4),
                      'abstencion_correcta': round(vn / len(neg), 4) if neg else None})
    mejor = max(filas, key=lambda r: (r['F1'], -r['FP']))
    sin_fp = [r for r in filas if r['FP'] == 0]
    return {'curva': filas, 'mejor_F1': mejor,
            'menor_umbral_sin_falsos_positivos': min(sin_fp, key=lambda r: r['umbral']) if sin_fp else None,
            'sep_media_pos': round(float(np.mean(pos)), 4),
            'nota': 'positivos = A+B (consultas con respaldo alcanzable por la estrategia); D se reporta aparte',
            'sep_media_neg': round(float(np.mean(neg)), 4)}

for est in ['char', 'palabra', 'hibrido']:
    res['estrategias'][est]['umbral'] = barrido(est)

json.dump(res, open(os.environ.get('SALIDA','resultados_v2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('CORPUS:', res['corpus'])
print('CONSULTAS:', res['consultas'])
for est in ESTRATEGIAS:
    r = res['estrategias'][est]
    print(f"\n== {est}")
    for s in ['A_lexico_es', 'B_independiente', 'D_ingles']:
        print('  ', s, r[s])
    print('   latencia', r['latencia_ms'])
    if 'umbral' in r:
        print('   mejor F1:', r['umbral']['mejor_F1'])
        print('   sin FP  :', r['umbral']['menor_umbral_sin_falsos_positivos'])
        print('   media pos/neg:', r['umbral']['sep_media_pos'], r['umbral']['sep_media_neg'])
