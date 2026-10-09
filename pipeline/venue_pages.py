import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit


def external_link(value: str | None, label: str) -> str:
    if not value:
        return ""
    url = value.strip() if re.match(r"^[a-z][a-z\d+.-]*:", value.strip(), re.I) else "https://" + value.strip()
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password:
        raise ValueError(f"Invalid researched source URL: {value}")
    return f'<a href="{html.escape(url, quote=True)}" rel="noopener">{html.escape(label)}</a>'


def generate(base: Path, origin: str) -> None:
    parts = urlsplit(origin)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.path not in ("", "/") or parts.query or parts.fragment:
        raise ValueError("SITE_URL must be an HTTPS origin")
    origin = origin.rstrip("/")
    tracks = json.loads((base / "tracks.json").read_text(encoding="utf-8"))
    countries = json.loads((base / "countries.json").read_text(encoding="utf-8"))
    rates = json.loads((base / "rates_meta.json").read_text(encoding="utf-8"))
    public = base.parent / "public"
    pages = public / "venues"
    pages.mkdir(parents=True, exist_ok=True)
    links = []
    for t in tracks:
        oid = t["o"]
        if not re.fullmatch(r"(way|node|relation)/\d+", oid):
            raise ValueError(f"Unexpected venue ID: {oid}")
        path = f"/venues/{oid.replace('/', '-')}/"
        target = pages / oid.replace("/", "-")
        target.mkdir(exist_ok=True)
        name = t.get("n") or ("Kart track near " + t["near"] if t.get("near") else "Unnamed kart track")
        place = ", ".join(filter(None, [t.get("c"), countries[t["cc"]]["name"]]))
        desc = f"{name} in {place}. Published karting information, session prices, sources and family/group requirements."
        prices = t.get("P") or []
        eligible = [p for p in prices if p[18] and not p[16]]
        timed = [p for p in eligible if p[2]]
        cheapest = min(timed, key=lambda p: (p[6], p[2])) if timed else None
        rate = min((p for p in eligible if p[7] is not None), key=lambda p: (p[7], p[6]), default=None)
        session = lambda p: f"EUR {p[6]:.2f} for {p[2]} minutes" if p[2] else f"EUR {p[6]:.2f}"
        details = [
            ("Location", place), ("Address", t.get("a")), ("Phone", t.get("p")),
            ("Rental", {"yes": "Confirmed", "no": "Reported unavailable"}.get(t.get("r"), "Not verified")),
            ("Own karts", {"yes": "Confirmed", "no": "Reported unavailable"}.get(t.get("ow"), "Not verified")),
            ("Status", "Reported closed" if t.get("cl") else "Confirm opening with the operator"),
            ("Lowest standard session", session(cheapest) if cheapest else "No eligible public adult session verified"),
            ("Lowest standard EUR/min", f"EUR {rate[7]:.2f}/min; {session(rate)}; {rate[0] or rate[1]}" if rate else "Not verified"),
            ("Price source checked", t.get("Pc") or "Date not recorded"),
        ]
        facts = "".join(f"<dt>{html.escape(k)}</dt><dd>{html.escape(str(v))}</dd>" for k, v in details if v)
        rows = "".join(
            f"<tr><td>{html.escape(p[0] or p[1] or 'Session')}</td><td>{html.escape(p[1] or 'Unclassified')}</td>"
            f"<td>{html.escape(str(p[2])) + ' min' if p[2] else str(p[3]) + ' laps' if p[3] else 'See conditions'}</td>"
            f"<td>EUR {p[6]:.2f}" + (f" ({html.escape(str(p[4]))} {html.escape(p[5])})" if p[5] != "EUR" else "") + "</td>"
            f"<td>{'Standard comparison' if p[18] and not p[16] else 'Not a public standard comparison'}"
            f"{'; members only' if p[16] else ''}"
            f"{'; package/group offer: minutes may be a driving component, not total visit time' if p[11] == 'package' or p[14] else ''}"
            f"{'; minimum age ' + str(p[8]) if p[8] is not None else ''}"
            f"{'; maximum age ' + str(p[9]) if p[9] is not None else ''}"
            f"{'; minimum height ' + str(p[10]) + ' cm' if p[10] else ''}"
            f"{'; ' + html.escape(p[12]) if p[12] else ''}<br>{html.escape(p[13] or '')}</td></tr>"
            for p in prices
        )
        fees = "".join(f"<li>{html.escape(f[0] or 'Fee')}: EUR {f[3]:.2f}; "
                       f"{'mandatory' if f[5] else 'optional'}; {html.escape(f[4] or '')}. {html.escape(f[6] or '')}</li>"
                       for f in (t.get("F") or []))
        layouts = "".join(f"<li>{html.escape(l[0] or 'Track')}: {l[1]} m</li>" for l in (t.get("T") or []))
        family = t.get("FG") or {}
        fg = "".join(f"<h3>{label}</h3><ul>" + "".join(f"<li>{html.escape(f)}</li>" for f in family.get(key, [])) + "</ul>"
                     for key, label in [("family", "Family"), ("group", "Groups")] if family.get(key))
        if fg:
            fg += f"<p>Checked {html.escape(family['checked_at'])}. {external_link(family.get('source'), 'Official family/group source')}</p>"
        source_links = " · ".join(filter(None, [
            external_link(t.get("w"), "Operator website"), external_link(t.get("Ps"), "Price source"),
            external_link(t.get("Ts"), "Track source"),
        ]))
        page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)} - Kart Atlas</title><meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{origin}{path}"><link rel="stylesheet" href="/assets/venue.css"></head>
<body><main><nav><a href="/">Explore Kart Atlas</a> · <a href="/venues/">All venues</a></nav>
<h1>{html.escape(name)}</h1><p>{html.escape(place)}</p>
<p><a href="/#venue={quote(oid, safe='')}">Open on interactive map</a></p>
<dl>{facts}</dl><p>Lowest session cost and lowest price per minute can refer to different sessions.
Packages, race karts and member-only prices are not public standard adult comparisons. Fees are separate.
Confirm current prices, availability and suitability with the operator before travelling.</p>
<h2>Published prices</h2>{'<div class="scroll"><table><thead><tr><th>Offer</th><th>Class</th><th>Stated driving time</th><th>Price</th><th>Conditions</th></tr></thead><tbody>' + rows + '</tbody></table></div>' if rows else '<p>No verified published prices in the atlas. This does not mean rental is unavailable.</p>'}
<p>Non-euro prices are approximate conversions using ECB rates of {html.escape(rates['date'])}.
Confirm the original currency price with the operator. Package minutes can describe a driving component, not the total visit.</p>
<h2>Fees and membership</h2>{'<ul>' + fees + '</ul>' if fees else '<p>No fee amounts verified; do not assume there are no fees.</p>'}
<p>{html.escape(t.get('mem') or '')}</p><h2>Track</h2>{'<ul>' + layouts + '</ul>' if layouts else '<p>Official layout lengths not verified.</p>'}
<h2>Family and group visits</h2>{fg or '<p>Detailed family and group requirements not verified. Ask the operator.</p>'}
<h2>Sources</h2><p>{source_links or 'No official website verified.'}</p>
<footer>Venue names and tariff wording retain their source language. Data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>, ODbL.
No booking or correction submission is collected by this page.</footer></main></body></html>"""
        (target / "index.html").write_text(page, encoding="utf-8")
        links.append((path, name, place))
    index = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>European karting venues - Kart Atlas</title><link rel="stylesheet" href="/assets/venue.css"></head><body><main><a href="/">Interactive atlas</a><h1>European karting venues</h1><ul>'
    index += "".join(f'<li><a href="{p}">{html.escape(n)}</a> — {html.escape(c)}</li>' for p, n, c in sorted(links, key=lambda row: row[1].casefold()))
    (pages / "index.html").write_text(index + "</ul></main></body></html>", encoding="utf-8")
    urls = ["/", "/venues/"] + [p for p, _, _ in links]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    sitemap += "".join(f"<url><loc>{html.escape(origin + p)}</loc></url>" for p in urls) + "</urlset>"
    (public / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (public / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n", encoding="utf-8")
    current = {p.split("/")[2] for p, _, _ in links}
    for directory in pages.iterdir():
        if directory.is_dir() and re.fullmatch(r"(way|node|relation)-\d+", directory.name) and directory.name not in current:
            (directory / "index.html").unlink()
            directory.rmdir()
    print("generated", len(links), "venue pages for", origin)


if __name__ == "__main__":
    generate(Path(sys.argv[1]), os.environ.get("SITE_URL", "https://kartatlas.michaelbinger.dk"))
