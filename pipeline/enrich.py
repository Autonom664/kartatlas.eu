# Merge web research (research/out/*.json) into tracks.json. usage: enrich.py <pipeline dir>
import json, re, glob, sys, os
base = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from price_rules import comparison_eligible, normalize_offer
BRANDS = [(r'sodi', 'Sodi'), (r'rimo', 'RiMO'), (r'\bbiz\b', 'BIZ'), (r'\bcrg\b', 'CRG'), (r'\botk\b|tony ?kart|kosmic|exprit|redspeed', 'OTK (Tony Kart group)'),
          (r'birel', 'Birel ART'), (r'praga', 'Praga'), (r'\bopc\b', 'OPC'), (r'\bdino\b', 'Dino'), (r'\bmar\b|mar karts?', 'MAR'),
          (r'kart republic|\bkr\b', 'Kart Republic'), (r'\bparolin\b', 'Parolin'), (r'\bintrepid\b', 'Intrepid'), (r'energy', 'Energy Corse'),
          (r'\bgillard\b', 'Gillard'), (r'\bpcr\b', 'PCR'), (r'\btb ?kart', 'TB Kart'), (r'swiss ?hutless', 'Swiss Hutless'),
          (r'\bmaranello\b', 'Maranello'), (r'\bzanardi\b', 'Zanardi'), (r'\bfa ?kart', 'FA Kart'), (r'\bpraga\b', 'Praga'),
          (r'\bblitz\b', 'Blitz'), (r'\bbwt\b|bwt', 'BWT'), (r'\bsuperkart\b', 'Superkart'), (r'\bsonik\b', 'Sonik'), (r'\bgopro\b', 'GoPro')]
ENGINES = [(r'gx ?270', 'Honda GX270'), (r'gx ?390', 'Honda GX390'), (r'gx ?200|gx ?160|gx ?120', 'Honda GX200 or smaller'), (r'gx ?690|igx', 'Honda GX/iGX twin'),
           (r'rotax', 'Rotax'), (r'iame|x ?30\b|parilla', 'IAME'), (r'\btm\b', 'TM'), (r'vortex', 'Vortex'),
           (r'electri|e-?kart|\bev\b|kw\b', 'Electric'), (r'subaru|robin', 'Subaru / Robin'), (r'briggs|b&s', 'Briggs & Stratton'),
           (r'loncin|lifan|kohler|kawasaki|yamaha|predator|zongshen', None), (r'honda', 'Honda (other)')]
def norm(val, table, raw_fallback=True):
    if not val: return None
    cc = re.search(r'(\d{2,3})\s*cc', val, re.I)
    for pat, name in table:
        m = re.search(pat, val, re.I)
        if m: return name or m.group(0).title()
    if cc and table is ENGINES: return cc.group(1) + ' cc (make not stated)'
    return val.split()[0].title() if raw_fallback else None
def hp(v):
    if v is None: return None
    v = str(v).strip()
    return v or None
OVR = json.load(open(base + '/overrides.json', encoding='utf-8'))
# KART_SKIP=W08,W09 leaves unreviewed or in-progress research batches out of a release build
SKIP = {b.strip() + '.json' for b in os.environ.get('KART_SKIP', '').split(',') if b.strip()}
res = {}
for f in sorted(glob.glob(base + '/research/out/*.json'), key=lambda f: ('_user' in os.path.basename(f), os.path.basename(f)[0] in 'REWG', f)):  # user-confirmed facts win
    if os.path.basename(f) in SKIP: continue
    if os.path.basename(f)[0] in 'LP': continue  # length / price files, handled below
    try:
        rows = json.load(open(f, encoding='utf-8'))
    except ValueError:
        print('skipped (being written):', f); continue
    for r in rows:
        old = res.get(r['id'])
        if old:  # later files (follow-ups) only fill or improve fields
            m = dict(old)
            for k, v in r.items():
                if v in (None, [], '', 'unknown'): continue
                m[k] = v
            r = m
        res[r['id']] = r
tracks = json.load(open(base + '/tracks.json', encoding='utf-8'))
used = 0
for t in tracks:
    r = res.get(t['o'])
    if not r: continue
    used += 1
    if OVR.get(t['o'], {}).get('noweb'): r = {**r, 'website': None, 'websites': []}
    if r.get('name'):
        t['n'] = r['name']; t['gs'] = None; t['near'] = None
    if r.get('website'): t['w'] = r['website']
    elif re.search(r'for sale|for-sale|placeholder|casino|no longer resolves|does not resolve|parked|unrelated|hijack|suspicious|domain-sale|sale page|domain sale|does not resolve|no longer exists', r.get('note') or '', re.I): t['w'] = None
    if r.get('phone'): t['p'] = r['phone']
    if r.get('hours'): t['h'] = r['hours']
    if r.get('address'): t['a'] = r['address']
    if isinstance(r.get('layout_page'), str) and r['layout_page'].startswith('https://'): t['Lu'] = r['layout_page']
    ld = r.get('layout_diagram')
    if isinstance(ld, dict) and isinstance(ld.get('points'), list) and len(ld['points']) >= 3 and str(ld.get('source', '')).startswith('https://'):
        t['Ld'] = {'p': [[round(float(a), 1), round(float(b), 1)] for a, b in ld['points']], 'z': bool(ld.get('closed')), 's': ld['source']}
    ag = {k: r['ages'][k] for k in ('kids_min_age', 'kids_min_height_cm', 'adult_min_age', 'adult_min_height_cm', 'twin_passenger_min_age') if isinstance(r.get('ages'), dict) and isinstance(r['ages'].get(k), (int, float))}
    if ag: t['ag'] = ag
    t['e'] = r.get('email')
    t['r'] = r.get('rental') if r.get('rental') in ('yes', 'no') else None
    t['ow'] = r.get('own_karts') if r.get('own_karts') in ('yes', 'no') else None
    t['cl'] = r.get('status') == 'closed' or None
    if r.get('type') in ('indoor', 'outdoor') and t['k'] != 'kids': t['k'] = r['type']
    K = []
    for k in r.get('karts') or []:
        ch, en = k.get('chassis'), k.get('engine')
        K.append([ch, en, hp(k.get('hp')), k.get('class'), norm(ch, BRANDS), norm(en, ENGINES)])
    t['K'] = K or None
    t['src'] = (r.get('sources') or [])[:3] or None
    t['note'] = r.get('note')
    ws, seen = [], set()
    for w in r.get('websites') or []:
        u = (w.get('url') or '').strip()
        if u and u.rstrip('/').lower() not in seen:
            seen.add(u.rstrip('/').lower()); ws.append([u, w.get('role') or 'other', w.get('name')])
    t['ws'] = ws or None
# reviewed OSM raceway lines near venues that had no karting-tagged outline (research/geometry/)
import math
def _m(a, b):
    p = math.radians; h = math.sin(p(b[0] - a[0]) / 2) ** 2 + math.cos(p(a[0])) * math.cos(p(b[0])) * math.sin(p(b[1] - a[1]) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))
for f in sorted(glob.glob(base + '/research/geometry/*.json')):
    geo = json.load(open(f, encoding='utf-8'))
    for t in tracks:
        x = geo.get(t['o'])
        if x and not t.get('g'):
            t['g'] = x['lines']
            t['lm'] = t.get('lm') or round(max(sum(_m(p, q) for p, q in zip(l, l[1:])) for l in x['lines']))
# track-map search results (research/out/maps/M*.json): only layout links and traced diagrams
for f in sorted(glob.glob(base + '/research/out/maps/*.json')):
    if os.path.basename(f) in SKIP: continue
    try:
        maps = json.load(open(f, encoding='utf-8'))
    except ValueError:
        print('skipped (being written):', f); continue
    for r in maps:
        t = next((x for x in tracks if x['o'] == r['id']), None)
        if not t: continue
        if isinstance(r.get('layout_page'), str) and r['layout_page'].startswith('https://') and not t.get('Lu'): t['Lu'] = r['layout_page']
        ld = r.get('layout_diagram')
        if not t.get('g') and not t.get('Ld') and isinstance(ld, dict) and len(ld.get('points') or []) >= 3 and str(ld.get('source', '')).startswith('https://'):
            t['Ld'] = {'p': [[round(float(a), 1), round(float(b), 1)] for a, b in ld['points']], 'z': bool(ld.get('closed')), 's': ld.get('source_page') or ld['source']}
# official layouts and lengths from venue websites (research/out/L*.json)
lens = {}
for f in sorted(glob.glob(base + '/research/out/L*.json')) + sorted(glob.glob(base + '/research/out/P*.json')) + sorted(glob.glob(base + '/research/out/W*.json')) + sorted(glob.glob(base + '/research/out/G*.json')):
    if os.path.basename(f) in SKIP: continue
    try:
        for r in json.load(open(f, encoding='utf-8')):
            if r.get('tracks') or r['id'] not in lens: lens[r['id']] = r
    except ValueError:
        print('skipped (being written):', f)
for t in tracks:
    t['lm'] = t.get('len')  # length measured from the map
    r = lens.get(t['o'])
    T = []
    for k in (r or {}).get('tracks') or []:
        try: L = int(round(float(k.get('length_m'))))
        except (TypeError, ValueError): continue
        if 40 <= L <= 6000: T.append([k.get('name'), L, k.get('width_m'), k.get('use')])
    if T:
        t['T'] = T; t['Ts'] = r.get('source'); t['Tn'] = r.get('note')
        t['Tc'] = r.get('checked_at')
        t['len'] = max(x[1] for x in T)
# prices from venue websites (research/out/P*.json), converted with ECB reference rates
import urllib.request, xml.etree.ElementTree as ET
RATES_FILE = base + '/rates.json'
try:
    import subprocess
    xml = subprocess.run(['curl', '-s', '-m', '30', 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'], capture_output=True, check=True).stdout
    root = ET.fromstring(xml)
    cube = [c for c in root.iter() if c.get('time')][0]
    rates = {'date': cube.get('time'), 'EUR': 1.0}
    rates.update({c.get('currency'): float(c.get('rate')) for c in cube})
    json.dump(rates, open(RATES_FILE, 'w'))
except Exception as e:
    print('ECB fetch failed, using cached rates:', e)
    rates = json.load(open(RATES_FILE)) if os.path.exists(RATES_FILE) else {'date': None, 'EUR': 1.0}
prices, attempts = {}, {}
for f in sorted(glob.glob(base + '/research/out/P*.json')) + sorted(glob.glob(base + '/research/out/W*.json')) + sorted(glob.glob(base + '/research/out/G*.json')):
    if os.path.basename(f) in SKIP: continue
    try:
        for r in json.load(open(f, encoding='utf-8')):
            if r.get('checked_at') and (r.get('prices') or os.path.basename(f)[0] == 'P'): attempts[r['id']] = r['checked_at']
            if r.get('prices') or r['id'] not in prices: prices[r['id']] = r
    except ValueError:
        print('skipped (being written):', f)
def num(v):
    try: return float(str(v).replace(',', '.'))
    except (TypeError, ValueError): return None
for t in tracks:
    r = prices.get(t['o'])
    if r and r.get('website'):
        t['w'] = r['website']
        t['ws'] = [[r['website'], 'venue', None]] + [w for w in (t.get('ws') or []) if w[1] == 'club' and w[0] != r['website']]
        t['note'] = r.get('website_note') or t.get('note')
        if r.get('name'):
            t['n'] = r['name']; t['gs'] = None; t['near'] = None
    if r:
        for field, key in [('rental', 'r'), ('own_karts', 'ow')]:
            if r.get(field) in ('yes', 'no'):
                t[key] = r[field]
    t['Pa'] = attempts.get(t['o'])
    if OVR.get(t['o'], {}).get('noprice'): r = None
    P = []
    for q in (r or {}).get('prices') or []:
        if not isinstance(q, dict): continue  # malformed research entry
        shown, shown_note = q.get('label'), q.get('note')  # visitors see the operator's own wording
        q = normalize_offer(q)
        amt, cur = num(q.get('price')), (q.get('currency') or 'EUR').upper()
        if amt is None or amt <= 0 or cur not in rates: continue
        eur = round(amt / rates[cur], 2)
        mins = num(q.get('minutes'))
        typ = q.get('type') or ('session' if mins else 'package')
        laps = num(q.get('laps'))
        extras = bool(q.get('extras')) or typ == 'package'
        txt = ' '.join(str(q.get(k) or '') for k in ('note', 'label'))
        # explicit flag from research wins; otherwise only clear members-only wording counts
        member = q.get('member') if q.get('member') is not None else bool(
            re.search(r'\(member\)|^member price|members only|members-only|club trial|medlemspris|mitgliederpreis|prix adh', txt, re.I)
            and not re.search(r'non-member|non member|nicht.?mitglied', txt, re.I))
        ppm = round(eur / mins, 2) if mins and not extras and typ in ('session', 'per_minute') else None
        ppl = round(eur / laps, 2) if laps and not extras and typ in ('session', 'laps') else None
        P.append([shown, q.get('class'), mins, laps, amt, cur, eur, ppm,
                  q.get('min_age'), q.get('max_age'), q.get('min_height_cm'), typ, q.get('day'), shown_note, extras, ppl, member,
                  not comparison_eligible(q), comparison_eligible(q)])
    if P:
        t['P'] = P; t['Ps'] = r.get('price_source'); t['Pn'] = r.get('note')
        t['Pc'] = r.get('checked_at')
        def standard(x):
            return x[18]
        def best(idx, members):
            rows = [x for x in P if x[idx] and (members or not x[16]) and standard(x)]
            adult = [x[idx] for x in rows]
            return min(adult) if adult else None
        t['ppm'], t['ppl'] = best(7, False), best(15, False)
        mm, ml = best(7, True), best(15, True)
        t['ppmM'] = mm if mm is not None and (t['ppm'] is None or mm < t['ppm']) else None
        t['pplM'] = ml if ml is not None and (t['ppl'] is None or ml < t['ppl']) else None
        t['mem'] = r.get('membership') or OVR.get(t['o'], {}).get('membership')
for t in tracks:
    r = prices.get(t['o']) or {}
    if OVR.get(t['o'], {}).get('noprice'): r = {}
    F = []
    for fz in r.get('fees') or []:
        if not isinstance(fz, dict): continue  # malformed research entry
        amt, cur = num(fz.get('amount')), (fz.get('currency') or 'EUR').upper()
        if cur not in rates: continue
        if amt is None and not fz.get('mandatory'): continue  # unpriced optional extras add nothing
        F.append([fz.get('name'), amt, cur, round(amt / rates[cur], 2) if amt is not None else None, fz.get('period'), bool(fz.get('mandatory')), fz.get('note')])
    ov = OVR.get(t['o'], {})
    for fz in ov.get('fees') or []:
        amt, cur = num(fz.get('amount')), (fz.get('currency') or 'EUR').upper()
        if amt is not None and cur in rates:
            F.append([fz.get('name'), amt, cur, round(amt / rates[cur], 2), fz.get('period'), bool(fz.get('mandatory')), fz.get('note')])
    if F: t['F'] = F
    if not t.get('mem') and (r.get('membership') or ov.get('membership')): t['mem'] = r.get('membership') or ov.get('membership')
RATES_DATE = rates.get('date')
family = {}
for f in sorted(glob.glob(base + '/research/out/family/*.json')):
    for r in json.load(open(f, encoding='utf-8')):
        family[r['id']] = r
for t in tracks:
    if t['o'] in family:
        t['FG'] = family[t['o']]
    else:
        r = res.get(t['o']) or {}
        facts = lambda v: [v] if isinstance(v, str) else v if isinstance(v, list) else []  # one sentence or a list; flags ignored
        fam = [x for x in facts(r.get('family')) if isinstance(x, str) and x.strip()]
        grp = [x for x in facts(r.get('group')) if isinstance(x, str) and x.strip()]
        if fam or grp:
            t['FG'] = {'id': t['o'], 'checked_at': r.get('checked_at'), 'source': r.get('ages_source') or (r.get('sources') or [None])[0], 'family': fam, 'group': grp}
json.dump({'date': RATES_DATE, 'used': sorted({x[5] for t in tracks for x in (t.get('P') or [])})}, open(base + '/rates_meta.json', 'w'))
for t in tracks:
    d = OVR.get(t['o'], {}).get('dropurl')
    if d:
        if t.get('w') and d in t['w']: t['w'] = None
        if t.get('ws'): t['ws'] = [w for w in t['ws'] if d not in w[0]] or None
    if OVR.get(t['o'], {}).get('noweb'):
        t['w'] = None; t['ws'] = None
    if OVR.get(t['o'], {}).get('closed'): t['cl'] = True
    on = OVR.get(t['o'], {}).get('name')
    if on:  # a manual name correction always wins over research
        t['n'] = on; t['gs'] = None; t['near'] = None
    ow = OVR.get(t['o'], {}).get('web')
    if ow:  # a manual website correction always wins over research
        t['w'] = ow
        t['ws'] = [[ow, 'venue', None]] + [w for w in (t.get('ws') or []) if w[1] == 'club' and w[0].rstrip('/') != ow.rstrip('/')]
json.dump(tracks, open(base + '/tracks.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('enriched', used, 'of', len(tracks), '| rental yes', sum(1 for t in tracks if t.get('r') == 'yes'),
      '| with fleet', sum(1 for t in tracks if t.get('K')), '| closed', sum(1 for t in tracks if t.get('cl')))
