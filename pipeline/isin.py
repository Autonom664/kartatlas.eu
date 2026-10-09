# usage: isin.py sites_XX.json  -> adds state/town via Overpass is_in
import json, sys, urllib.request, urllib.parse, time
f = sys.argv[1]
s = json.load(open(f, encoding='utf-8'))
q = '[out:json][timeout:190];' + ''.join(
    f'make sep;out;is_in({x["lat"]},{x["lon"]})->.a;area.a[admin_level~"^(2|4|5|6|7|8)$"][boundary=administrative];out tags;' for x in s)
for attempt in range(5):
    try:
        req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=urllib.parse.urlencode({'data': q}).encode(),
                                     headers={'User-Agent': 'kart-map/1.0', 'Accept': 'application/json'})
        els = json.load(urllib.request.urlopen(req, timeout=200))['elements']; break
    except Exception as e:
        print('retry', e); time.sleep(20)
groups = []
for e in els:
    if e['type'] == 'sep': groups.append([])
    else: groups[-1].append(e['tags'])
assert len(groups) == len(s), (len(groups), len(s))
for site, g in zip(s, groups):
    lv = {t.get('admin_level'): t.get('name') for t in g}
    site['country'] = next((t.get('ISO3166-1') or t.get('ISO3166-1:alpha2') for t in g if t.get('admin_level') == '2'), None)
    site['state'] = lv.get('4')
    site['town'] = lv.get('8') or lv.get('7') or lv.get('6')
    if not site.get('city'): site['city'] = site['town']
json.dump(s, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
print(f, len(s), sum(1 for x in s if not x['state']))
