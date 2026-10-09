# usage: name_guess.py sites_XX.json [...]
# For sites without a name, look up nearby named features (likely venue name) and the nearest place
# (for a descriptive fallback). Writes guess fields into the sites file: gname, gsrc ('nearby'|'place'), gdist.
import json, sys, re, math, time, urllib.request, urllib.parse

MOTOR = re.compile(r'kart|circuit|ring\b|pista|autodromo|bana\b|baan\b|racing|race|speed|motor|piste|rennstrecke|arena|gocart|go-cart', re.I)
SKIP_KEYS = ('highway', 'waterway', 'place', 'boundary', 'natural', 'railway', 'route', 'public_transport', 'power', 'addr:street')

def hav(a, b, c, d):
    p = math.radians
    h = math.sin(p(c-a)/2)**2 + math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2
    return 2*6371000*math.asin(math.sqrt(h))

def query(q):
    for attempt in range(6):
        try:
            req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=urllib.parse.urlencode({'data': q}).encode(),
                                         headers={'User-Agent': 'kart-map/1.0', 'Accept': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=200))['elements']
        except Exception as e:
            print('  retry', e); time.sleep(15 + 10*attempt)
    raise SystemExit('overpass failed')

def score(t, d):
    s = 0
    sp = t.get('sport', '')
    if 'karting' in sp: s += 6
    elif re.search(r'motor', sp): s += 3
    if re.search(r'kart|gocart|go-cart', t['name'], re.I): s += 4
    elif MOTOR.search(t['name']): s += 2
    if t.get('leisure') in ('sports_centre', 'stadium', 'track'): s += 1
    if t.get('club') or t.get('amenity') == 'clubhouse': s += 1
    return s - d/250

for f in sys.argv[1:]:
    sites = json.load(open(f, encoding='utf-8'))
    todo = [x for x in sites if not x['name']]
    print(f, len(todo), 'unnamed')
    for i in range(0, len(todo), 30):
        batch = todo[i:i+30]
        q = '[out:json][timeout:190];' + ''.join(
            f'make sep;out;nwr(around:450,{x["lat"]},{x["lon"]})[name];out center tags;'
            f'make sep2;out;node(around:6000,{x["lat"]},{x["lon"]})[place~"^(town|village|suburb|hamlet|city)$"];out;'
            for x in batch)
        els = query(q)
        groups, cur = [], None
        for e in els:
            if e['type'] == 'sep': groups.append([[], []]); cur = 0
            elif e['type'] == 'sep2': cur = 1
            else: groups[-1][cur].append(e)
        assert len(groups) == len(batch), (len(groups), len(batch))
        for x, (near, places) in zip(batch, groups):
            best, bs = None, 2.5
            for e in near:
                t = e.get('tags', {})
                if any(k in t for k in SKIP_KEYS) or 'name' not in t: continue
                c = e.get('center') or {'lat': e.get('lat'), 'lon': e.get('lon')}
                if c.get('lat') is None: continue
                d = hav(x['lat'], x['lon'], c['lat'], c['lon'])
                sc = score(t, d)
                if sc > bs: best, bs, bd = t, sc, d
            if best:
                x['gname'], x['gsrc'], x['gdist'] = best['name'], 'nearby', round(bd)
                if not x.get('web'): x['web'] = best.get('website') or best.get('contact:website')
                continue
            rank = {'town': 0, 'city': 0, 'suburb': 1, 'village': 1, 'hamlet': 2}
            pl = sorted(((rank[p['tags']['place']], hav(x['lat'], x['lon'], p['lat'], p['lon']), p['tags']['name'])
                         for p in places if p.get('tags', {}).get('name') and p['tags'].get('place') in rank), key=lambda r: r[1])
            # nearest village/town within 3 km, else nearest anything, else municipality
            pick = next((p for p in pl if p[0] <= 1 and p[1] < 3000), pl[0] if pl else None)
            x['gname'] = pick[2] if pick else (x.get('town') or x.get('city'))
            x['gsrc'] = 'place'
        print('  ', min(i+30, len(todo)), 'done')
    json.dump(sites, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f, 'nearby', sum(1 for x in todo if x.get('gsrc') == 'nearby'), 'place', sum(1 for x in todo if x.get('gsrc') == 'place'))
