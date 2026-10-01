import json
EN = {'cóncavo':'concave','confesar':'to confess','buscar':'to search','regresar':'to return',
'consolar':'to console','liviano':'lightweight','sueldo':'salary','nuevo':'new','iglesia':'church',
'cueva':'cave','acusar':'to accuse','tímido':'shy','doblar':'to fold','feliz':'happy',
'olvido':'forgetfulness','mote':'boiled corn','lagartija':'lizard','horrible':'horrible',
'camarada':'comrade','ladera':'hillside','diablo':'devil','venir':'to come','eructar':'to burp',
'juguete':'toy','pintar':'to paint','pezuña':'hoof','caminar':'to walk','mellizo':'twin',
'asado':'roasted','hueco':'hole','pájaro':'bird','visitar':'to visit','continuar':'to continue',
'tragar':'to swallow','tenedor':'fork','banco':'bench','orina':'urine','coser':'to sew',
'amado':'beloved','descartar':'to discard'}
E = json.load(open('evaluacion_v2.json', encoding='utf-8'))
E = [e for e in E if e['subconjunto'] != 'D_ingles']
A = [e for e in E if e['subconjunto'] == 'A_lexico_es']
D, i = [], 0
for e in A:
    es = e['consulta'].split('dice ')[1].split(' en quechua')[0]
    if es in EN:
        i += 1
        D.append({'id': f'D{i:03d}', 'subconjunto': 'D_ingles',
                  'consulta': f"how do you say {EN[es]} in Wanka Quechua?",
                  'forma_esperada': e['forma_esperada'], 'oro': e['oro']})
json.dump(E + D, open('evaluacion_v2.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('D:', len(D))
