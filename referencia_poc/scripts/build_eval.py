"""Construye el conjunto de evaluación a partir del propio corpus, sin
formular ninguna forma lingüística que no esté documentada en él.

  A  consultas léxicas en español, redactadas de forma natural
  B  consultas equivalentes formuladas de manera independiente (inglés y
     paráfrasis), para medir robustez de fraseo e idioma (RF-04)
  C  consultas deliberadamente fuera de la cobertura del corpus (RF-08),
     verificando que el término no aparece en ningún fragmento
"""
import json, re, random, unicodedata, difflib

FRAG = [json.loads(l) for l in open('fragmentos.jsonl', encoding='utf-8')]

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

TEXTO_NORM = [norm(f['texto']) for f in FRAG]

def fragmentos_con(forma):
    f = norm(forma)
    return [FRAG[i]['id'] for i, t in enumerate(TEXTO_NORM) if re.search(r'\b' + re.escape(f) + r'\b', t)]

# ---------- entradas del diccionario castellano -> wanka ----------
pat = re.compile(r'^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ]{2,24}):\s*([^\n]{2,60})', re.M)
entradas = []
for x in FRAG:
    if not x['documento'].startswith('293274822'):
        continue
    for m in pat.finditer(x['texto']):
        es = m.group(1).strip().lower()
        qu = re.split(r'[,\.\(]', m.group(2).strip())[0].strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñüĆćŚśẂẃ' ]{4,20}", qu):
            continue
        if ' ' in qu:                       # solo formas de una palabra
            continue
        # descarta préstamos casi idénticos al castellano (coincidencia trivial)
        if difflib.SequenceMatcher(None, norm(es), norm(qu)).ratio() > 0.66:
            continue
        entradas.append({'es': es, 'qu': qu, 'pagina': x['pagina']})

vistos, unicas = set(), []
for e in entradas:
    if e['es'] in vistos:
        continue
    vistos.add(e['es']); unicas.append(e)

random.seed(20260908)
random.shuffle(unicas)

conjunto = []
for e in unicas:
    oro = fragmentos_con(e['qu'])
    if len(oro) == 0 or len(oro) > 40:       # descarta formas ausentes o ubicuas
        continue
    conjunto.append({**e, 'oro': oro})
    if len(conjunto) >= 120:
        break

A = [{'id': f'A{i+1:03d}', 'subconjunto': 'A_lexico_es',
      'consulta': f"¿cómo se dice {e['es']} en quechua wanka?",
      'forma_esperada': e['qu'], 'oro': e['oro']} for i, e in enumerate(conjunto)]

plantillas_b = [
    "how do you say {} in Wanka Quechua?",
    "necesito el término wanka para referirme a {}",
    "what is the Wanka Quechua word for {}?",
    "estoy buscando la palabra que designa {} en la variedad wanka",
]
B = [{'id': f'B{i+1:03d}', 'subconjunto': 'B_independiente',
      'consulta': plantillas_b[i % len(plantillas_b)].format(e['es']),
      'forma_esperada': e['qu'], 'oro': e['oro']} for i, e in enumerate(conjunto[:60])]

# ---------- fuera de cobertura ----------
candidatos = ['impresora tridimensional', 'criptomoneda', 'algoritmo genético',
  'satélite artificial', 'reactor nuclear', 'vacuna de ARN mensajero', 'firewall',
  'hipoteca bancaria', 'turbina eólica', 'resonancia magnética', 'submarino',
  'aeropuerto internacional', 'semiconductor', 'telescopio espacial',
  'seguro de vida', 'fibra óptica', 'motor diésel', 'panel solar',
  'radiografía dental', 'contrato de arrendamiento', 'quimioterapia',
  'placa base', 'videoconferencia', 'anestesia general', 'código de barras',
  'bolsa de valores', 'inteligencia artificial', 'planta desalinizadora',
  'certificado digital', 'endoscopia', 'peaje electrónico', 'ecografía',
  'refinería de petróleo', 'antibiótico', 'grúa portuaria', 'cajero automático',
  'tomografía', 'central hidroeléctrica', 'auditoría contable', 'microprocesador']
C = []
for c in candidatos:
    palabras = [p for p in norm(c).split() if len(p) > 4]
    if any(fragmentos_con(p) for p in palabras):
        continue                              # aparece en el corpus: no sirve
    C.append({'id': f'C{len(C)+1:03d}', 'subconjunto': 'C_fuera_de_cobertura',
              'consulta': f"¿cómo se dice {c} en quechua wanka?",
              'forma_esperada': None, 'oro': []})

todo = A + B + C
with open('evaluacion.json', 'w', encoding='utf-8') as f:
    json.dump(todo, f, ensure_ascii=False, indent=1)
print('entradas del diccionario utilizables:', len(unicas))
print('A:', len(A), ' B:', len(B), ' C:', len(C), ' total:', len(todo))
print('ejemplos A:', [(a['consulta'], a['forma_esperada'], len(a['oro'])) for a in A[:4]])
print('ejemplos C:', [c['consulta'] for c in C[:3]])
