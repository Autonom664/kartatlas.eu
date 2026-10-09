# usage: prep.py <scratch dir> CC [CC ...]   -> tracks.json + geo/world.min.json
import json, re, math, sys, os
base, ccs = sys.argv[1], sys.argv[2:]
# ISO numeric ids in world-atlas, used to highlight covered countries and draw neighbours
ISO = {'DE': '276', 'AT': '040', 'IT': '380', 'DK': '208', 'SE': '752', 'FR': '250', 'CH': '756', 'NL': '528', 'BE': '056', 'LI': '438'}
NAMES = {'DE': 'Germany', 'AT': 'Austria', 'IT': 'Italy', 'DK': 'Denmark', 'SE': 'Sweden', 'FR': 'France',
         'CH': 'Switzerland', 'NL': 'Netherlands', 'BE': 'Belgium', 'LI': 'Liechtenstein'}
OTHER = re.compile(r'biathlon|shapeup|rc-cart|rcr\b|automodell|modellauto|modellismo|carrera|traktor|tret|kinderquad|skate-|rollende|knax|'
                   r'fahrtraining|spiel-preis|riedblick|sportpark weyersberg|hardtschachen|verkehrs|buggy|nano-kart|offroad kids|kinder|'
                   r'jumicar|jugendcart|jugendkart|mini-lausitz|minicars|bambini|macchinine|bici kart|bike-kart|iscooter|minimoto|enfant|børne|barnbana|barn ?bil|trampbil|pedal|modelbil|radiocommand|rc ?track|rc-bane|rc-bana|rc-baan|mini-? ?auto|skelter|modelautoclub|bmx', re.I)
INDOOR = re.compile(r'battle ?kart|teamsport|indoor|halle|hall\b|palast|karthaus|powerhall|sensadrom|cartion|kart-o-mania|eco-?kart|'
                    r'kartland|e-karting|dome\b|holykart|palakart|dromokart|mokart', re.I)
CLUB = re.compile(r'\b(e\. ?v\.|msc|amc|adac|kartclub|klubb?|gokartklub|motorklub|motorsportclub|motor sportclub|club|a\.?s\.?d\.?)\b', re.I)
def hav(a, b, c, d):
    R = 6371; p = math.radians
    h = math.sin(p(c-a)/2)**2 + math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2
    return 2*R*math.asin(math.sqrt(h))
OVR = {k: v for k, v in json.load(open(base + '/overrides.json', encoding='utf-8')).items() if not k.startswith('_')}
out = []
supplemental = json.load(open(base + '/sites_supplemental.json', encoding='utf-8'))
for cc in ccs:
    sites = json.load(open(f'{base}/sites_{cc}.json', encoding='utf-8'))
    known_ids = {oid for site in sites for oid in site['osm']}
    for site in supplemental:
        if site['cc'] == cc and not known_ids.intersection(site['osm']):
            sites.append(site)
            known_ids.update(site['osm'])
    for x in sites:
        if not (34 < x['lat'] < 72 and -11 < x['lon'] < 32): continue  # drop overseas territories
        ov = next((OVR[i] for i in x['osm'] if i in OVR), {})
        if ov.get('remove'): continue
        if ov.get('name'): x['name'] = ov['name']
        if ov.get('web'): x['web'] = ov['web']
        if ov.get('noweb'): x['web'] = None
        n = x['name'] or ''
        k = x['kind']
        if OTHER.search(n) or (not n and x['len'] and x['len'] < 130): k = 'kids'
        gs = near = None
        if not n and x.get('gname'):
            if x.get('gsrc') == 'nearby': n, gs = x['gname'], x.get('gdist')
            else: near = x['gname']
        elif INDOOR.search(n) and k == 'outdoor': k = 'indoor'
        if k == 'both': k = 'indoor'
        if ov.get('kind'): k = ov['kind']
        L = x['len']
        if L and L > 2200 and x.get('geo'):  # summed overlapping variants; use the longest single line instead
            L = round(max(sum(hav(p[0], p[1], q[0], q[1]) for p, q in zip(l, l[1:])) for l in x['geo']) * 1000)
        out.append(dict(n=n or None, la=x['lat'], lo=x['lon'], k=k, len=L, c=x['city'], st=x['state'], cc=cc,
                        a=x['addr'], w=x['web'], p=x['phone'], h=x['hours'], club=bool(CLUB.search(n)) or bool(ov.get('club')), gs=gs, near=near,
                        o=x['osm'][0], g=x.get('geo')))
json.dump(out, open(base + '/tracks.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump({cc: {'name': NAMES[cc], 'id': ISO[cc]} for cc in ccs}, open(base + '/countries.json', 'w'), separators=(',', ':'))
from collections import Counter
print(Counter((t['cc'], t['k']) for t in out))
# neighbour outlines (Europe + North Africa coast), unused arcs stripped
w = json.load(open(base + '/geo/world.json', encoding='utf-8'))
keep = set(ISO.values()) | {'442', '203', '616', '826', '438', '578', '705', '191', '348', '703', '674', '336', '470', '724',
    '246', '492', '788', '012', '008', '070', '499', '688', '300', '807', '620', '372', '233', '428', '440', '112', '804', '642', '100', '020', '498'}
w['objects']['countries']['geometries'] = [g for g in w['objects']['countries']['geometries'] if g.get('id') in keep]
w['objects'].pop('land', None)
used = set()
def walk(a, f):
    return f(a) if isinstance(a, int) else [walk(x, f) for x in a]
for g in w['objects']['countries']['geometries']: walk(g['arcs'], lambda i: used.add(i if i >= 0 else ~i))
order = sorted(used); m = {o: i for i, o in enumerate(order)}
for g in w['objects']['countries']['geometries']: g['arcs'] = walk(g['arcs'], lambda i: m[i] if i >= 0 else ~m[~i])
w['arcs'] = [w['arcs'][o] for o in order]
json.dump(w, open(base + '/geo/world.min.json', 'w'), separators=(',', ':'))
for f in ('tracks.json', 'geo/world.min.json'): print(f, os.path.getsize(base + '/' + f))
