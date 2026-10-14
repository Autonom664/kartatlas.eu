# usage: python -I osm_raceways_fetch.py <work dir with targets.json> <tracks.json>
# Queries Overpass for raceway/karting ways near venues without an outline, chunked and paced.
import json, sys, subprocess, time, os
d, tracks = sys.argv[1], sys.argv[2]
targets = json.load(open(os.path.join(d, 'targets.json'), encoding='utf-8'))
UA = 'KartAtlas/1.0 (kartatlas.michaelbinger.dk; research script)'
for i in range(0, len(targets), 25):
    out = os.path.join(d, f'r_{i:04d}.json')
    if os.path.exists(out) and os.path.getsize(out) > 100:
        continue
    chunk = targets[i:i + 25]
    q = '[out:json][timeout:90];(' + ''.join(
        f'way(around:350,{t["la"]},{t["lo"]})[highway=raceway];way(around:350,{t["la"]},{t["lo"]})[sport=karting];'
        for t in chunk) + ');out geom tags;'
    qf = os.path.join(d, 'q.txt')
    open(qf, 'w').write(q)
    for attempt in range(3):
        r = subprocess.run(['curl', '-s', '-m', '150', '-A', UA, '-H', 'Accept: application/json',
                            '--data-urlencode', 'data@' + qf, 'https://overpass-api.de/api/interpreter',
                            '-o', out, '-w', '%{http_code}'], capture_output=True, text=True)
        ok = r.stdout == '200'
        if ok:
            try:
                json.load(open(out, encoding='utf-8')); break
            except ValueError:
                ok = False
        print('retry', i, r.stdout, flush=True); time.sleep(30)
    print(i, r.stdout, flush=True)
    time.sleep(3)
