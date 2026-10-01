"""Prototipo mínimo de la PoC: consulta -> recuperación -> decisión de abstención."""
import json, re, unicodedata, numpy as np, time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

FR = [json.loads(l) for l in open('fragmentos_v2.jsonl', encoding='utf-8')]
def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s)
T = [norm(f['texto']) for f in FR]
RUIDO = re.compile(r'\b(en|el|la|del|de|quechua|wanka|huanca|variedad|como|se|dice|que|es|word|for|in|how|do|you|say|the|necesito|termino|para|referirme|estoy|buscando|palabra|designa|what|a)\b')
def depurar(q):
    return re.sub(r'[^a-z0-9 ]', ' ', RUIDO.sub(' ', norm(q))).strip()

vc = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), min_df=2, sublinear_tf=True); Mc = normalize(vc.fit_transform(T))
vw = TfidfVectorizer(analyzer='word', ngram_range=(1,2), min_df=1, sublinear_tf=True); Mw = normalize(vw.fit_transform(T))
UMBRAL = 0.41

def consultar(pregunta, k=3):
    q = depurar(pregunta)
    t0 = time.perf_counter()
    s = 0.5*(Mc @ normalize(vc.transform([q])).T).toarray().ravel() + 0.5*(Mw @ normalize(vw.transform([q])).T).toarray().ravel()
    idx = np.argsort(-s)[:k]; ms = (time.perf_counter()-t0)*1000
    top = [(FR[i], float(s[i])) for i in idx]
    return top, ms

for p in ['¿cómo se dice zorro en quechua wanka?',
          'how do you say water in Wanka Quechua?',
          '¿cómo se dice criptomoneda en quechua wanka?']:
    top, ms = consultar(p)
    f, sc = top[0]
    print('CONSULTA:', p)
    print(f'  similitud={sc:.3f}  umbral={UMBRAL}  latencia={ms:.1f} ms')
    if sc >= UMBRAL:
        print(f'  RESPONDE · fuente: {f["documento"][:40]}, pág. {f["pagina"]}')
        print('  fragmento:', f['texto'][:160].replace('\n',' '))
    else:
        print('  SE ABSTIENE: no hay respaldo documental en el corpus indexado.')
    print()
