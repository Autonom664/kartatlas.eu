# Kart Atlas

A static atlas of kart venues across ten European countries.

## Build and tests

From `pipeline/`, run:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -I test_price_rules.py
python -I build.py
```

From the project root, run `node --test tests\site.test.cjs` after rebuilding.
These dependency-free tests check generated script syntax, data invariants,
the price regression, intent predicates, session costs and location privacy.

Edit `pipeline/template.html`, not the generated `kart-atlas.html`. The build
also regenerates `kart-atlas.json`. Research inputs, results and manual
corrections are preserved in `pipeline/`.

## Discovery

- Intent presets distinguish rental, family, own-kart, race rental and group
  opportunities using published fleet/session facts. Unknown availability is
  not presented as confirmed.
- Town search uses towns represented in the atlas. Centres are averages of
  venue coordinates, **not authoritative town centres**. No external geocoder
  is contacted and arbitrary postcodes are not supported.
- Device geolocation requires an explicit click and browser permission.
  Coordinates stay in page memory and are excluded from URLs. Distances are
  straight-line kilometres, not driving distances.
- Radius search, nearest sorting and search-this-map-area narrow the results.
- Mobile users can switch between List and Map; marker details open over the map.
- Share links encode filters, map position and stable OSM venue identifiers.
  Browser Back/Forward restores these states. Device coordinates and their
  map viewport are never included.

## Prices

`pipeline/price_rules.py` produces explicit comparison eligibility at index 18
of each compact offer. Race/performance karts, children, packages and extras
are never standard-adult comparisons. Special labels and unqualified
discount/block notes are excluded; separately priced alternatives in notes
do not disqualify a standard session. An optional boolean
`comparison_eligible` research field supports verified exceptions, but cannot
override the kart-class/package restrictions.

Session summaries show the lowest-priced eligible timed session, which can
differ from the session offering the lowest EUR/min. Mandatory fees remain
separate with their conditions; no complete first-visit total is claimed.
Member-only prices remain opt-in.

## Docker deployment

```powershell
docker compose -f deploy\compose.yaml build
docker compose -f deploy\compose.yaml up -d
```

The container listens on loopback port 18081 and is served through host Nginx.
The origin deployment is `/home/ubuntu/kart-atlas-deploy` on SSH alias
`dst-ovh`. Upload the generated page/data and updated deployment files, then
rebuild/recreate only this Compose project.

The live hostname is `kartatlas.michaelbinger.dk`. The bootstrap host config
also prepares `kartatlas.eu`; do **not** overwrite the active Certbot-managed
TLS vhost with the bootstrap config. Activate `.eu` only after DNS is ready
and a certificate covering that name has been issued. Both names are intended
to serve the site without a cross-domain redirect.

Security headers permit first-party geolocation only, disable camera and
microphone, restrict resources with CSP, and retain a one-hour cache lifetime.
The app still uses inline scripts/styles and pinned third-party script URLs.
