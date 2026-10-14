# usage: python -I osm_raceways_match.py <work dir> <tracks.json>  (then review the sheet_N.png contact sheets by eye)
# Assigns fetched OSM raceway ways to the venue they belong to, merges connected ways,
# filters car circuits / motocross, writes candidates.json and a contact sheet sheet_N.png.
import json, sys, os, glob, math
import numpy as np, cv2
d, tracks = sys.argv[1], sys.argv[2]
T = json.load(open(tracks, encoding='utf-8'))
targets = {t['o']: t for t in json.load(open(os.path.join(d, 'targets.json'), encoding='utf-8'))}
def hav(a, b, c, e):
    p = math.radians; h = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(e - b) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))
ways = {}
for f in glob.glob(os.path.join(d, 'r_*.json')):
    try: els = json.load(open(f, encoding='utf-8'))['elements']
    except (ValueError, KeyError): print('skip', f); continue
    for e in els:
        if e['type'] == 'way' and e.get('geometry'): ways[e['id']] = e
BAD = {'motocross', 'bmx', 'cycling', 'horse_racing', 'rc_car', 'model_aerodrome', 'equestrian', 'speedway', 'dirt_bike'}
per = {}
for w in ways.values():
    tg = w.get('tags', {})
    if tg.get('highway') != 'raceway' or tg.get('sport') in BAD or tg.get('area') == 'yes' or 'building' in tg: continue
    pts = [(g['lat'], g['lon']) for g in w['geometry']]
    # nearest venue (any venue in the atlas) to this way
    best, bd = None, 1e9
    for t in T:
        dd = min(hav(t['la'], t['lo'], a, b) for a, b in pts[::max(1, len(pts) // 20)])
        if dd < bd: best, bd = t, dd
    if best and best['o'] in targets and bd <= 350:
        per.setdefault(best['o'], []).append({'id': w['id'], 'pts': pts, 'tags': tg})
def length(l): return sum(hav(a[0], a[1], b[0], b[1]) for a, b in zip(l, l[1:]))
def merge(lines):
    lines = [list(l) for l in lines]; changed = True
    while changed:
        changed = False
        for i in range(len(lines)):
            for j in range(len(lines)):
                if i == j: continue
                a, b = lines[i], lines[j]
                if a[-1] == b[0]: lines[i] = a + b[1:]
                elif a[-1] == b[-1]: lines[i] = a + b[::-1][1:]
                elif a[0] == b[-1]: lines[i] = b + a[1:]
                elif a[0] == b[0]: lines[i] = b[::-1] + a[1:]
                else: continue
                del lines[j]; changed = True; break
            if changed: break
    return lines
cands = []
for o, ws in per.items():
    lines = merge([w['pts'] for w in ws])
    tot = sum(length(l) for l in lines); mx = max(length(l) for l in lines)
    sports = sorted({w['tags'].get('sport', '-') for w in ws}); names = sorted({w['tags'].get('name', '') for w in ws} - {''})
    t = targets[o]
    verdict = 'ok'
    if mx > 2500: verdict = 'too long (car circuit?)'
    elif mx < 120: verdict = 'too short'
    cands.append({'o': o, 'n': t['n'], 'cc': t['cc'], 'k': t['k'], 'ways': [w['id'] for w in ws], 'sports': sports, 'names': names,
                  'lines': [[[round(a, 6), round(b, 6)] for a, b in l] for l in lines], 'total_m': round(tot), 'longest_m': round(mx), 'verdict': verdict})
cands.sort(key=lambda c: (c['verdict'] != 'ok', c['cc'], c['n'] or ''))
json.dump(cands, open(os.path.join(d, 'candidates.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ways', len(ways), 'venues with candidates', len(cands), 'ok', sum(c['verdict'] == 'ok' for c in cands))
# contact sheet: 6 x 5 tiles of 260 px
tile, cols, rows = 260, 6, 5
for s in range(0, len(cands), cols * rows):
    img = np.full((rows * tile, cols * tile, 3), 255, np.uint8)
    for k, c in enumerate(cands[s:s + cols * rows]):
        ox, oy = (k % cols) * tile, (k // cols) * tile
        la0 = c['lines'][0][0][0]; kx = 111320 * math.cos(math.radians(la0)); ky = 110540
        P = [[((p[1]) * kx, -(p[0]) * ky) for p in l] for l in c['lines']]
        xs = [x for l in P for x, _ in l]; ys = [y for l in P for _, y in l]
        sc = min((tile - 30) / max(max(xs) - min(xs), 1), (tile - 60) / max(max(ys) - min(ys), 1))
        col = (0, 140, 0) if c['verdict'] == 'ok' else (0, 0, 220)
        for l in P:
            pts = np.array([[ox + 15 + (x - min(xs)) * sc, oy + 40 + (y - min(ys)) * sc] for x, y in l], np.int32)
            cv2.polylines(img, [pts], False, col, 2)
        cv2.putText(img, f"{s + k} {c['cc']} {(c['n'] or c['o'])[:26]}", (ox + 4, oy + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1)
        cv2.putText(img, f"{c['longest_m']}m {','.join(c['sports'])[:18]} {c['verdict'][:10]}", (ox + 4, oy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (90, 90, 90), 1)
        cv2.rectangle(img, (ox, oy), (ox + tile - 1, oy + tile - 1), (200, 200, 200), 1)
    cv2.imwrite(os.path.join(d, f'sheet_{s // (cols * rows)}.png'), img)
