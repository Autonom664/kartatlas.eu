# usage: python -I tools/apply_unnamed.py [--dry] research/out/unnamed/U01.json [...]   (run from pipeline/)
# Applies reviewed verdicts for unnamed/guessed OSM entries to overrides.json:
#   real            -> name, web (if a https/http site is given), kind (indoor/outdoor if stated)
#   club_or_private -> name (if given) and club=true
#   not_kart        -> kind=kids (hidden from the public atlas)
#   uncertain       -> nothing
# Existing manual overrides for name/web/kind are never replaced.
import json, sys
dry = '--dry' in sys.argv
files = [f for f in sys.argv[1:] if f != '--dry']
o = json.load(open('overrides.json', encoding='utf-8'))
count = {}
for f in files:
    for r in json.load(open(f, encoding='utf-8')):
        v = r.get('verdict'); count[v] = count.get(v, 0) + 1
        cur = o.get(r['id'], {})
        new = dict(cur)
        if v == 'real':
            if r.get('name') and 'name' not in cur: new['name'] = r['name']
            if str(r.get('website') or '').startswith('http') and 'web' not in cur: new['web'] = r['website']
            if r.get('type') in ('indoor', 'outdoor') and 'kind' not in cur: new['kind'] = r['type']
        elif v == 'club_or_private':
            if r.get('name') and 'name' not in cur: new['name'] = r['name']
            new['club'] = True
        elif v == 'not_kart' and 'kind' not in cur:
            new['kind'] = 'kids'
        if new != cur:
            print(('would set ' if dry else 'set ') + r['id'], {k: new[k] for k in new if cur.get(k) != new[k]})
            o[r['id']] = new
print(count)
# rental / own-kart findings and websites go into a research record file, so the filters and badges use them
recs = []
for f in files:
    for r in json.load(open(f, encoding='utf-8')):
        if r.get('verdict') not in ('real', 'club_or_private'): continue
        rec = {'id': r['id'], 'rental': r.get('rental') if r.get('rental') in ('yes', 'no') else None,
               'own_karts': r.get('own_karts') if r.get('own_karts') in ('yes', 'no') else None,
               'website': r.get('website') if str(r.get('website') or '').startswith('http') else None,
               'sources': r.get('sources') or [], 'checked_at': r.get('checked_at')}
        recs.append(rec)
print('rental/own records', len(recs), 'rental=no', sum(1 for x in recs if x['rental'] == 'no'), 'own=yes', sum(1 for x in recs if x['own_karts'] == 'yes'))
if not dry:
    json.dump(o, open('overrides.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(recs, open('research/out/W21_unnamed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
