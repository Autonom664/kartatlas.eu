# Kart Atlas

A static atlas of kart venues across ten European countries.

## Build and tests

From `pipeline/`, run:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -I test_price_rules.py
python -I test_venue_pages.py
python -I test_supplemental_sites.py
python -I build.py
```

From the project root, run `node --test tests\site.test.cjs` after rebuilding.
These dependency-free tests check generated script syntax, data invariants,
the price regression, intent predicates, session costs and location privacy.

Edit `pipeline/template.html`, not the generated `kart-atlas.html`. The build
also regenerates `kart-atlas.json`. Research inputs, results and manual
corrections are preserved in `pipeline/`.

`public/` contains reproducibly generated venue pages, directory, sitemap and
robots file; it is not checked into Git. Build it before building Docker.
The canonical origin defaults to the live `.dk` hostname. Set `SITE_URL` to
the new HTTPS origin only after its DNS/certificate are ready.

Local JS/font assets and licence notices are checked in under `assets/`.
To reproduce them after dependency changes, use `npm ci` then `npm run assets`.
Fontsource font files use the Latin subset, covering Danish/German characters.
The app makes no third-party asset requests; operator/maps links still leave
the site when explicitly followed.

Browser regression tests use Playwright against the actual Nginx image:

```powershell
docker build -f deploy\Dockerfile -t kart-atlas:test .
docker run -d --name kart-atlas-test -p 127.0.0.1:18082:80 kart-atlas:test
npm run test:browser
docker stop kart-atlas-test
docker rm kart-atlas-test
```

If Chromium is missing, run `npx playwright install chromium` once. Set
`KARTATLAS_TEST_URL` to test another origin. The tests exercise mobile layouts
in all three interface languages, keyboard focus/tabs, comparisons, family
facts, history, sharing privacy, routes, headers and same-origin assets.

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
- Search/filters collapse initially on small or short screens. Opening a venue
  hides filters and attribution to give details the available rail height;
  closing restores them. Attribution remains accessible in a disclosure.
- Keyboard selection focuses the venue heading. Tabs support arrow keys,
  Home/End and linked panels; result counts are announced politely.
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

Details and comparisons also identify the actual offer, amount and duration
behind the lowest EUR/min. Static venue pages distinguish package driving
components from total visit duration and state the ECB conversion date.

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

## Family facts and interface languages

Official family/group research is stored separately in
`pipeline/research/out/family/FG*.json` and merged as `FG`, without replacing
existing tariffs or general research. FG01 covers Adventure Eefde and
Playdome: ages/heights, mixed family sessions, group formats and source dates.
Unknown driver limits and group minima are explicitly left unverified.

Verified venues missed by the initial `sport=karting` OSM extract live in
`pipeline/sites_supplemental.json`. Preparation merges them by country,
skipping entries whose OSM IDs already occur in the regular extract so later
refreshes do not duplicate venues. Do not use a sports-centre boundary as
driving geometry. Pista Winner (`way/444163257`, OSM `sport=motor`) was added
with official fleet/tariff research R12/P12 and family/group facts FG02.
Its linked tariff image has a 2023 path; conflicting age requirements and
tariff freshness are explicitly disclosed, not guessed.

The next discovery batch, R13/P13/FG03, applies local search terms across all
ten countries (Kartbahn/Leihkart, kartodromo/noleggio kart, gokartbane,
gokartbana/hyrkart, kartbaan/kartverhuur and location karting). Outcomes and
limitations are recorded in `pipeline/research/out/discovery/D01.json`;
nested discovery reports are not general venue-enrichment records.
Bulk Overpass queries failed, so this is **not an exhaustive OSM scan**.
Official rendered pages, tabs and images are inspected before importing facts;
search-generated prices, towns and OSM IDs are only leads.

This batch adds Rottal, Jesolo and Lelystad, with coordinate-based duplicate
checks. Lelystad uses the verified OSM address node at its shared motorsport
site, explicitly not a dedicated karting tag or driving layout; a deleted
search-suggested way was rejected. Research refreshes Greinbach, Gokart World,
Kalmar, Nendeln, Lyss, Fagnes and Haute Saintonge. Lyss electric karts marked
Coming soon are not listed as available; its two pre-existing stable entries
remain, without adding a third. Unverified Jesolo rental-tier classification
is excluded from standard comparisons; both advertised engines are 4T, not
assumed 2T from the word RACE. Multi-heat blocks and event visit times do not
become continuous session durations. Lelystad rental prices remain unknown;
Fagnes' blank tariff embed preserves earlier prices without renewing `Pc`.

English, Danish and German are available for core navigation, controls and
comparison labels. The language preference is local to the browser and also
included as `#lang=da` / `#lang=de` in shared links and history. Venue names,
tariff wording and research notes retain their source language; static venue
pages and remaining long-form data explanations are currently English.
There is no automatic translation of operator facts.

`npm run health` checks the live atlas, a venue route, sitemap, security
headers and trusted TLS certificate expiry (failure below 21 days). It exits
nonzero with an explicit error on failure. This is an on-demand checker,
**not scheduled monitoring or active alert delivery**. The `.eu` activation,
correction inbox and email alerts are deferred until the user confirms the
domain/mailbox; no nonfunctional correction form is published.

## Docker deployment

```powershell
docker compose -f deploy\compose.yaml build
docker compose -f deploy\compose.yaml up -d
```

The container listens on loopback port 18081 and is served through host Nginx.
The origin deployment is `/home/ubuntu/kart-atlas-deploy` on SSH alias
`dst-ovh`. Upload the generated page/data, `public/`, `assets/`, `.dockerignore`
and updated deployment files, then
rebuild/recreate only this Compose project.

Windows-created tar archives can mark generated directories read-only on
Linux. Before replacing an existing release, ensure the task-owned `public/`
and `assets/` directories are owner-writable; restore owner access after
extraction too. Scope permission changes only to those deployment directories.
Keep an image and source-archive rollback before replacing the live service;
do not change other projects or the host TLS vhost.

The live hostname is `kartatlas.michaelbinger.dk`. The bootstrap host config
also prepares `kartatlas.eu`; do **not** overwrite the active Certbot-managed
TLS vhost with the bootstrap config. Activate `.eu` only after DNS is ready
and a certificate covering that name has been issued. Both names are intended
to serve the site without a cross-domain redirect.

Security headers permit first-party geolocation only, disable camera and
microphone, and restrict resources with CSP. HTML uses `Cache-Control: no-cache`
so browsers revalidate it on each visit; the companion JSON retains its
one-hour cache lifetime.
The app still uses inline scripts/styles; script, stylesheet and font origins
are restricted to self, with no CDN/font-host allowlist.
All data-driven website/source links pass a shared HTTP(S)-only validator.
Invalid or credential-bearing links are shown as unavailable and logged,
not rendered as clickable links.
