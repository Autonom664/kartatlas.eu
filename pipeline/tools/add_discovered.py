# usage: python -I tools/add_discovered.py research/out/discovery/D05.json W24_D05 [--hold "name part" ...] [--dry]   (run from pipeline/)
# Adds confirmed discovery venues to sites_supplemental.json and writes their research record file research/out/<W name>.json.
# A venue is added only when it has a stable OSM reference: its own object ("osm_id") or the address/building
# object returned by geocoding ("address_osm_id"). Venues without one, or matching --hold, are listed for follow-up.
# Never adds an ID that is already a venue in the atlas or already used by another new venue.
import json, sys
args = sys.argv[1:]
dry = '--dry' in args
holds = [args[i + 1].lower() for i, a in enumerate(args) if a == '--hold']
src, wname = [a for a in args if not a.startswith('--') and a.lower() not in holds][:2]
D = json.load(open(src, encoding='utf-8'))
sup = json.load(open('sites_supplemental.json', encoding='utf-8'))
taken = {i for s in sup for i in s['osm']} | {t['o'] for t in json.load(open('tracks.json', encoding='utf-8'))}
yn = lambda v: 'yes' if v in (True, 'yes') else 'no' if v in (False, 'no') else None
recs, held = [], []
for v in D.get('new_venues', []):
    oid = v.get('osm_id') or v.get('address_osm_id')
    own = bool(v.get('osm_id'))
    if not oid or any(h in v['name'].lower() for h in holds) or oid in taken:
        held.append((v['name'], oid, 'held' if oid not in taken or not oid else 'ID already used')); continue
    taken.add(oid)
    what = 'the venue\'s own OSM object' if own else 'the address/building object at the venue address, not a karting feature'
    if oid.startswith('site/'):  # no OSM object exists: a site ID with the operator's own position
        what = 'a site ID (no OSM object exists yet); the position comes from ' + (
            'the street of the operator\'s address (approximate)' if v.get('approximate') else 'the operator\'s own map pin')
    cc = v.get('country') or D.get('countries', [None])[0]
    sup.append({'name': v['name'], 'lat': v['lat'], 'lon': v['lon'], 'kind': 'indoor' if v.get('type') == 'indoor' else 'outdoor', 'len': None,
                'city': v.get('town'), 'state': None, 'addr': v.get('address'), 'web': v.get('website'), 'phone': v.get('phone'),
                'hours': v.get('hours'), 'osm': [oid], 'geo': None, 'cc': cc, 'source': v.get('website'), 'checked_at': v.get('checked_at'),
                'note': f'Added by discovery {D.get("id") or src.split("/")[-1][:3]}; confirmed on the operator site. The stable ID is {what}; no driving geometry is inferred from it.'})
    r = {k: v.get(k) for k in ('website', 'phone', 'email', 'hours', 'karts', 'ages', 'ages_source', 'family', 'group', 'prices', 'fees',
                               'membership', 'price_source', 'tracks', 'layout_page', 'sources')}
    r.update({'id': oid, 'name': None, 'status': 'open', 'type': v.get('type') if v.get('type') in ('indoor', 'outdoor') else None,
              'rental': yn(v.get('rental')), 'own_karts': yn(v.get('own_karts')), 'checked_at': v.get('checked_at'), 'note': None})
    r['sources'] = [s for s in (r.get('sources') or []) if str(s).startswith('http')]
    if isinstance(r.get('fees'), str):  # fees given as one sentence: keep it as the membership/fee text
        r['membership'] = r.get('membership') or r['fees']; r['fees'] = []
    recs.append(r)
print('add', len(recs), '| held', len(held))
for h in held: print('  HOLD', h)
if not dry:
    json.dump(sup, open('sites_supplemental.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(recs, open(f'research/out/{wname}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
