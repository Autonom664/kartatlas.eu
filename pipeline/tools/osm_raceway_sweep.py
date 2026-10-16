# usage: python -I tools/osm_raceway_sweep.py <work dir> fetch|analyse   (run from pipeline/)
# Finds kart-sized OSM raceways that are NOT near any atlas venue (e.g. tracks tagged sport=motor instead of
# sport=karting). fetch: downloads highway=raceway ways per 2x2 degree tile into <work dir>/tile_*.json (resumable).
# analyse: merges connected ways, keeps 200-1600 m tracks >1 km from every venue (incl. hidden), writes
# candidates.json and contact sheets sweep_N.png for visual review. Candidates are leads, not venues.
import json, sys, os, glob, math, subprocess, time
d, mode = sys.argv[1], sys.argv[2]
os.makedirs(d, exist_ok=True)
UA = 'KartAtlas/1.0 (kartatlas.michaelbinger.dk; research script)'
BOX = {'DE': (47.2, 5.8, 55.1, 15.1), 'AT': (46.3, 9.5, 49.1, 17.2), 'CH': (45.8, 5.9, 47.9, 10.5), 'IT': (36.6, 6.6, 47.1, 18.6),
       'FR': (42.3, -4.8, 51.1, 8.3), 'NL': (50.7, 3.3, 53.6, 7.3), 'BE': (49.5, 2.5, 51.6, 6.5), 'LU': (49.4, 5.7, 50.2, 6.6),
       'DK': (54.5, 8.0, 57.8, 15.2), 'SE': (55.3, 10.9, 69.1, 24.2), 'PL': (49.0, 14.1, 54.9, 24.2), 'CZ': (48.5, 12.0, 51.1, 18.9)}
tiles = sorted({(math.floor(la / 2) * 2, math.floor(lo / 2) * 2) for s, w, n, e in BOX.values()
                for la in range(math.floor(s), math.ceil(n)) for lo in range(math.floor(w), math.ceil(e))})
if mode == 'fetch':
    for la, lo in tiles:
        out = os.path.join(d, f'tile_{la}_{lo}.json')
        if os.path.exists(out) and os.path.getsize(out) > 50: continue
        q = f'[out:json][timeout:120];way({la},{lo},{la + 2},{lo + 2})[highway=raceway];out geom tags;'
        for a in range(3):
            for host in ('https://overpass-api.de/api/interpreter', 'https://maps.mail.ru/osm/tools/overpass/api/interpreter'):
                r = subprocess.run(['curl', '-s', '-m', '180', '-A', UA, '--data-urlencode', 'data=' + q, host, '-o', out + '.tmp', '-w', '%{http_code}'],
                                   capture_output=True, text=True)
                try:
                    if r.stdout == '200':
                        json.load(open(out + '.tmp', encoding='utf-8')); os.replace(out + '.tmp', out); break
                except ValueError: pass
            if os.path.exists(out): break
            time.sleep(30)
        print(la, lo, 'ok' if os.path.exists(out) else 'FAILED', flush=True)
        time.sleep(3)
    sys.exit()
# analyse
def hav(a, b):
    p = math.radians; h = math.sin(p(b[0] - a[0]) / 2) ** 2 + math.cos(p(a[0])) * math.cos(p(b[0])) * math.sin(p(b[1] - a[1]) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))
T = json.load(open('tracks.json', encoding='utf-8'))
grid = {}
for t in T: grid.setdefault((round(t['la'], 1), round(t['lo'], 1)), []).append(t)
def near_venue(pt):
    for dla in (-0.1, 0, 0.1):
        for dlo in (-0.1, 0, 0.1):
            for t in grid.get((round(pt[0] + dla, 1), round(pt[1] + dlo, 1)), []):
                if hav(pt, (t['la'], t['lo'])) < 1000: return t
BAD = {'motocross', 'bmx', 'cycling', 'horse_racing', 'rc_car', 'model_aerodrome', 'speedway', 'dirt_bike', 'equestrian', 'running', 'skateboard', 'karting'}
ways = {}
for f in glob.glob(os.path.join(d, 'tile_*.json')):
    for e in json.load(open(f, encoding='utf-8'))['elements']:
        tg = e.get('tags', {})
        if e['type'] == 'way' and e.get('geometry') and tg.get('sport') not in BAD and tg.get('area') != 'yes' and 'building' not in tg:
            ways[e['id']] = e
# merge connected ways (shared end nodes) into clusters
pts = {i: [(g['lat'], g['lon']) for g in w['geometry']] for i, w in ways.items()}
ends = {}
for i, p in pts.items():
    for q in (p[0], p[-1]): ends.setdefault((round(q[0], 6), round(q[1], 6)), []).append(i)
parent = {i: i for i in pts}
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
for ids in ends.values():
    for j in ids[1:]: parent[find(j)] = find(ids[0])
clusters = {}
for i in pts: clusters.setdefault(find(i), []).append(i)
cands = []
for ids in clusters.values():
    L = sum(sum(hav(a, b) for a, b in zip(pts[i], pts[i][1:])) for i in ids)
    if not 200 <= L <= 1600: continue
    allp = [q for i in ids for q in pts[i]]
    c = (sum(q[0] for q in allp) / len(allp), sum(q[1] for q in allp) / len(allp))
    if near_venue(c): continue
    tags = [ways[i].get('tags', {}) for i in ids]
    names = sorted({t.get('name') for t in tags if t.get('name')})
    if any(n and any(k in n.lower() for k in ('autodrom', 'circuit de', 'motocross', 'cross', 'rally', 'speedway', 'oval', 'drag')) for n in names) and L > 1200: continue
    cands.append({'ways': ids, 'lat': round(c[0], 6), 'lon': round(c[1], 6), 'length_m': round(L), 'names': names,
                  'sports': sorted({t.get('sport', '-') for t in tags}), 'lines': [[[round(a, 6), round(b, 6)] for a, b in pts[i]] for i in ids]})
cands.sort(key=lambda c: (-len(c['names']), c['lat']))
json.dump(cands, open(os.path.join(d, 'candidates.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('raceway ways', len(ways), 'clusters', len(clusters), 'candidates', len(cands), 'named', sum(1 for c in cands if c['names']))
import numpy as np, cv2
tile, cols, rows = 220, 7, 6
for s in range(0, len(cands), cols * rows):
    img = np.full((rows * tile, cols * tile, 3), 255, np.uint8)
    for k, c in enumerate(cands[s:s + cols * rows]):
        ox, oy = (k % cols) * tile, (k // cols) * tile
        kx = 111320 * math.cos(math.radians(c['lat'])); ky = 110540
        P = [[(p[1] * kx, -p[0] * ky) for p in l] for l in c['lines']]
        xs = [x for l in P for x, _ in l]; ys = [y for l in P for _, y in l]
        sc = min((tile - 20) / max(max(xs) - min(xs), 1), (tile - 50) / max(max(ys) - min(ys), 1))
        for l in P:
            cv2.polylines(img, [np.array([[ox + 10 + (x - min(xs)) * sc, oy + 40 + (y - min(ys)) * sc] for x, y in l], np.int32)], False, (0, 120, 0), 2)
        cv2.putText(img, f"{s + k} {c['length_m']}m {','.join(c['sports'])[:12]}", (ox + 3, oy + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)
        cv2.putText(img, (', '.join(c['names']) or '-')[:30], (ox + 3, oy + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (90, 90, 90), 1)
        cv2.rectangle(img, (ox, oy), (ox + tile - 1, oy + tile - 1), (200, 200, 200), 1)
    cv2.imwrite(os.path.join(d, f'sweep_{s // (cols * rows)}.png'), img)
