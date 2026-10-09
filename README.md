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

## Favourites and comparison

Open a venue to save it or add it to a comparison. The header opens saved
venues, shared shortlists and side-by-side comparison of up to four venues.
Comparison keeps standard adult sessions separate from performance/race
offers, and shows family evidence, source links, track lengths and fee
conditions. Missing facts are labelled unverified, never assumed unavailable.
The existing membership option also applies to comparisons.

Favourites use `localStorage` under `kartatlas.favourites`, containing only
stable venue IDs. No account, coordinates or external storage is involved.
Storage failures are reported and leave a usable in-memory list for the
current visit. Saved lists are browser/origin-specific: the future `.eu` domain
will not automatically inherit favourites from `.dk`; copy a shortlist link,
change its hostname to `.eu` after activation, and use Save all to transfer them.

Shortlist links use `#shortlist=`; comparison links use `#compare=` with at
most four IDs and the optional membership setting. Opening a shared shortlist
does not overwrite local favourites. Visitors explicitly save shared venues.
Only intentional list/comparison sharing exposes the corresponding venue IDs;
device coordinates and map bounds are omitted from these links.

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

Research can record `checked_at` (ISO date) for the actual source inspection,
`source` for layouts, and verified `website`/`website_note`, `name`, `rental` and
`own_karts` corrections. These fields are merged from the selected price
research record; nonempty earlier prices/layouts survive empty retries.
Generated `Pc`/`Tc` identify price/layout check dates; `Pa` records the latest
explicitly dated price research attempt, even when a retry found no prices.
A failed attempt does not change the check date of retained earlier prices.
Earlier records without explicit dates display "date not recorded", rather
than borrowing the build or exchange-rate date. Verified replacement operator
links supersede stale venue links while separate club links are retained.

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
microphone, and restrict resources with CSP. HTML uses `Cache-Control: no-cache`
so browsers revalidate it on each visit; the companion JSON retains its
one-hour cache lifetime.
The app still uses inline scripts/styles and pinned third-party script URLs.
