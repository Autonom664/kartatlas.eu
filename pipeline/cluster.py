import json, math, sys, re
src, out = sys.argv[1], sys.argv[2]
els = json.load(open(src, encoding='utf-8'))['elements']
def hav(a, b):
    R = 6371000
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))
items = []
for e in els:
    t = e.get('tags', {})
    if e['type'] == 'node':
        pts = [(e['lat'], e['lon'])]
    elif e['type'] == 'way':
        pts = [(p['lat'], p['lon']) for p in e.get('geometry', []) if p]
    else:
        pts = [(p['lat'], p['lon']) for m in e.get('members', []) for p in (m.get('geometry') or []) if p]
        if not pts and 'bounds' in e:
            b = e['bounds']; pts = [(b['minlat'], b['minlon']), (b['maxlat'], b['maxlon'])]
    if not pts: continue
    c = (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
    length = 0
    if e['type'] == 'way' and t.get('highway') == 'raceway' and t.get('area') != 'yes':
        length = sum(hav(pts[i], pts[i+1]) for i in range(len(pts)-1))
    lay = None
    if e['type'] == 'way' and (t.get('highway') == 'raceway' or t.get('leisure') == 'track') and len(pts) > 2:
        lay = pts
    items.append(dict(id=f"{e['type']}/{e['id']}", c=c, t=t, length=length, lay=lay))
def simplify(pts, tol=1.5):
    # Douglas-Peucker in metres (local equirectangular)
    if len(pts) < 3: return pts
    la0 = math.radians(pts[0][0]); kx = 111320*math.cos(la0); ky = 110540
    xy = [(p[1]*kx, p[0]*ky) for p in pts]
    keep = [False]*len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts)-1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = xy[i], xy[j]; dx, dy = x2-x1, y2-y1; L = math.hypot(dx, dy) or 1e-9
        best, bi = 0, -1
        for m in range(i+1, j):
            d = abs(dy*(xy[m][0]-x1) - dx*(xy[m][1]-y1))/L if L > 1e-6 else math.hypot(xy[m][0]-x1, xy[m][1]-y1)
            if d > best: best, bi = d, m
        if best > tol: keep[bi] = True; stack += [(i, bi), (bi, j)]
    return [p for p, k in zip(pts, keep) if k]
# single-link clustering at 350 m
n = len(items); parent = list(range(n))
def f(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
for i in range(n):
    for j in range(i+1, n):
        if abs(items[i]['c'][0]-items[j]['c'][0]) < 0.01 and hav(items[i]['c'], items[j]['c']) < 350:
            parent[f(i)] = f(j)
groups = {}
for i in range(n): groups.setdefault(f(i), []).append(items[i])
sites = []
for g in groups.values():
    def score(it):
        t = it['t']; s = 0
        if 'name' in t: s += 10
        if t.get('leisure') in ('sports_centre', 'track'): s += 3
        s += sum(1 for k in t if k.startswith(('addr:', 'website', 'contact:', 'phone')))
        return s
    g.sort(key=score, reverse=True)
    tags = {}
    for it in g:
        for k, v in it['t'].items(): tags.setdefault(k, v)
    names = [it['t']['name'] for it in g if 'name' in it['t']]
    name = names[0] if names else None
    lat = sum(it['c'][0] for it in g)/len(g); lon = sum(it['c'][1] for it in g)/len(g)
    track_len = sum(it['length'] for it in g)
    blob = ' '.join([name or ''] + names).lower()
    explicit = any(it['t'].get('indoor') == 'yes' or it['t'].get('covered') == 'yes' for it in g)
    bld = any('building' in it['t'] for it in g)
    outname = bool(re.search(r'kartodromo|circuit|pista|ring|raceway|outdoor|freiluft|open.?air', blob))
    indoor = explicit or bool(re.search(r'indoor|halle|hall|coperto', blob)) or (bld and not outname and track_len < 500)
    outdoor = any(it['t'].get('indoor') == 'no' or it['t'].get('outdoor') == 'yes' for it in g) or bool(re.search(r'outdoor|freiluft|open.?air', blob))
    if indoor and not outdoor: kind = 'indoor'
    elif indoor and outdoor: kind = 'both'
    else: kind = 'outdoor'
    web = tags.get('website') or tags.get('contact:website') or tags.get('url')
    city = tags.get('addr:city')
    addr = ' '.join(x for x in [tags.get('addr:street'), tags.get('addr:housenumber')] if x)
    if tags.get('addr:postcode') or city:
        addr = (addr + ', ' if addr else '') + ' '.join(x for x in [tags.get('addr:postcode'), city] if x)
    sites.append(dict(name=name, lat=round(lat, 5), lon=round(lon, 5), kind=kind,
        len=round(track_len) if track_len > 60 else None, city=city, addr=addr or None,
        web=web, phone=tags.get('phone') or tags.get('contact:phone'),
        hours=tags.get('opening_hours'), operator=tags.get('operator'),
        surface=tags.get('surface'), osm=[it['id'] for it in g],
        geo=[[[round(p[0], 6), round(p[1], 6)] for p in simplify(it['lay'])] for it in g if it['lay']] or None))
cc = sys.argv[3]
for s_ in sites: s_["cc"] = cc
sites.sort(key=lambda s: (-s["lat"]))
json.dump(sites, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
from collections import Counter
print(len(sites), Counter(s['kind'] for s in sites), sum(1 for s in sites if s['name']), sum(1 for s in sites if s['city']))
