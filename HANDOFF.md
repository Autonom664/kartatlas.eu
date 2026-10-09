# Kart Atlas: handoff for a new session

## Current status (9 October 2026)

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
