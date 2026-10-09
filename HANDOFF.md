# Kart Atlas: handoff for a new session

## Current status (9 October 2026)

Accessibility/security-hardening release deployed on 9 October 2026:
filters initially collapse on small/short screens; compact mobile header and
collapsed attribution prevent the list losing its height. Opening details
hides filters/attribution in all views. At 320x568 the collapsed list is 302 px;
at 390x844 details are 663 px (previously 116 px). Expanded filters still leave
a usable list, including 844x390 landscape. Heading focus, linked tab panels,
ArrowLeft/Right/Home/End navigation, polite result announcements, high-contrast
unselected presets and 44 px close targets are implemented. Sharing/comparison
feedback remains visible outside the hidden filters.
All data-driven source links use HTTP(S)-only validation; invalid links show
explicit feedback and console warnings. All 3,200 current links remain valid.
The published HTML matches the tested release exactly, with CSP and no-cache
intact. Rollback backup/image: before-accessibility-20261009 in the existing
backups directory and kart-atlas:before-accessibility-20261009. Only Kart Atlas
was rebuilt; no other project's configuration or service was modified.

The site is live at https://kartatlas.michaelbinger.dk in Docker on OVH, behind
the existing host Nginx. GitHub origin is `git@github.com:Autonom664/kartatlas.eu.git`.
See `README.md` for the current build, comparison rules, discovery features and
deployment. The user authorized changes to the previously frozen template and
pipeline to implement price/session comparisons, intent/location discovery,
mobile navigation and shareable URLs. Older scope restrictions below and in
`COPILOT_PROMPT.md` describe the earlier research phase, not the current scope.
Both domains are to serve the site; `.eu` activation awaits the user's DNS-ready
confirmation. Preserve unrelated server projects and the existing TLS vhost.

P10/P11 are completed follow-up price batches for eight previously unchecked
venues. Five have recovered published prices; Franciacorta, Fondi and Pista
Paradiso remain unverified. Original P07/P08 results are unchanged. Newer
nonempty price/layout entries are merged by the existing enrichment pipeline.
Cattolica's apparent EUR 3 package typo is retained with a warning and excluded
from comparison. Lascari's uncertain kart classes and South Milano's unverified
standard/performance distinction are explicitly excluded, not guessed.

The tested planning release adds browser-local favourites, explicit shared
shortlists, and comparison of two to four venues, keeping standard adult and
race-kart offers separate. Research P10/P11 now carries explicit inspection
dates and five verified current operator links, plus verified rental facts.
Failed checks are labelled attempts, not verified prices; older records with
no date remain undated. HTML revalidates while JSON retains one-hour caching.
Favourites are origin-specific; a shortlist link can transfer them to `.eu`.
See README for generated fields, URL format and privacy behaviour.

Planning release validation: four Python and fourteen Node tests pass.
Browser checks cover persistent favourites, shared-list merging without
overwriting saved venues, four-venue limits, separate standard/race prices,
390 px mobile scrolling, clipboard-denial feedback, Escape/focus restoration
and history navigation. Docker preview passes nginx configuration validation
and returns HTML with no-cache.

Planning release aeba2d7 deployed and verified on 9 October 2026. SSH was
intermittent on the user's away-from-home network; switching to a phone
hotspot allowed all transfers and deployment to complete. This points to a
network/source-IP-dependent issue, not bad credentials, but the exact cause
was not established. Public HTML matches the tested local file exactly and
returns Cache-Control: no-cache with CSP intact. Live browser comparison
shows Cattolica and Adventure Eefde with correct prices and check dates.
Only kart-atlas was recreated; other server containers remained running.
Rollback backup: backups/before-planning-20261009 (previous HTML, JSON and
nginx.conf). Image tag kart-atlas:before-planning-20261009 was ensured before
the build. Preserve these backups.

Paste this into a new Claude Code session opened in this folder:

---

Continue the Kart Atlas project in this folder. Read `HANDOFF.md` and your memory note "kart-track-atlas" first.

Status:
- Kart Atlas is a public map of about 1,200 go-kart venues in DE, AT, IT, CH, LI, DK, SE, NL, BE and FR. It is built from `pipeline/` into `kart-atlas.html` and `kart-atlas.json`.
- Private preview: https://claude.ai/artifact/X2VmSzyZWCyK2yFrWkx1K3. Republish by calling the Artifact tool with file_path `kart-atlas.html` and that `url`.
- Rebuild with: `cd pipeline && PYTHONIOENCODING=utf-8 python -I build.py` (it runs prep, then enrich, then injects the data into the page).
- Price research batches P01–P06 are done. P07, P08 and P09 were still running when the session ended. Check `pipeline/research/out/P07.json`, `P08.json` and `P09.json`. A file that is missing or doesn't parse means that batch didn't finish. Re-run it from `pipeline/research/in/P0x.json` with the same prompt style: WebFetch only, one venue at a time, its own `research/work_P0x/` folder, and at most 3 agents in parallel.

Next steps:
1. When P07–P09 are in: rebuild. Check the cheapest and most expensive entries in the €/min comparison and look for implausible prices. Look at the agent notes for: websites that belong to another venue, spam or casino sites, "not a kart track", and changed indoor/outdoor type. Add corrections to `pipeline/overrides.json` (keys: name, web, kind, remove, noweb, dropurl, noprice, membership, fees, club). Republish.
2. Optionally re-run venues whose notes say "Not checked" (rate limits, TLS errors), a few agents at a time.
3. When the user says the work is done: do NOT deploy anything yourself. Write a ready-to-paste prompt for GitHub Copilot. It should publish `kart-atlas.html` as `index.html` over SSH to the host 57.129.89.104 for kartatlas.michaelbinger.dk (the DNS A record exists), with a static web-server config, HTTPS via Let's Encrypt, and verification steps. Check with the user first: the SSH user, the web server software and the web root.

Rules from the user:
- The map is public. No Fredericia distances and no personal home point.
- Comparison prices are € per minute, plus € per lap where laps are stated. Only standard adult plain sessions count. Packages, offers with extras (meals, drinks, medals), special offers, kids' karts and member prices are listed but not compared. Member prices count only when "Include member prices" is on.
- Mandatory fees (licence cards, membership cards, balaclavas and so on) are shown separately in EUR.
- Many venues have both a club website and a rental website. Track lengths come from venue websites and are listed per layout. A length measured from the map is only an "≈" fallback.
- The user can confirm Danish facts. Everything else is Claude's best guess, with sources.

---

## Where things are

| Path | What |
|---|---|
| `kart-atlas.html` / `kart-atlas.json` | built page and data (do not edit by hand) |
| `pipeline/template.html` | page source (HTML/CSS/JS with `/*TRACKS*/` placeholders) |
| `pipeline/build.py` | one-step rebuild |
| `pipeline/prep.py` | OSM sites to tracks.json (classification, overrides, name guesses) |
| `pipeline/enrich.py` | merges research: details, lengths (L*), prices and fees (P*), ECB rates |
| `pipeline/overrides.json` | manual corrections keyed by OSM id (user corrections included) |
| `pipeline/research/in/`, `out/` | research batch inputs and results |
| `pipeline/osm/`, `sites_*.json` | raw OpenStreetMap data per country |

The ECB exchange rates are fetched with curl, because Python's SSL verification fails on this machine; they are cached in `pipeline/rates.json`. To test the raw page, serve the folder with `python -I -m http.server 8765` and open it in the built-in browser.
