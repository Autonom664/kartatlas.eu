const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "kart-atlas.html"), "utf8");
const tracks = JSON.parse(fs.readFileSync(path.join(root, "kart-atlas.json"), "utf8"));
const template = fs.readFileSync(path.join(root, "pipeline", "template.html"), "utf8");

function loadFunction(name, values) {
  const match = template.match(new RegExp(`(?:async )?function ${name}\\([^]*?\\n\\}`, "m"));
  assert.ok(match, `Missing function ${name}`);
  const context = vm.createContext(values);
  vm.runInContext(match[0], context);
  return context[name];
}

test("generated script parses and all venues have unique stable IDs and coordinates", () => {
  const script = html.match(/<script>([^]*?)<\/script>/)[1];
  new vm.Script(script);
  assert.equal(new Set(tracks.map(t => t.o)).size, tracks.length);
  assert.ok(tracks.length > 1000);
  assert.ok(tracks.every(t => Number.isFinite(t.lo) && Number.isFinite(t.la)));
});

test("Magny-Cours uses the standard adult rate rather than race-kart rental", () => {
  const venue = tracks.find(t => t.o === "way/482336192");
  assert.equal(venue.ppm, 2);
  assert.equal(venue.P[0][18], true);
  assert.equal(venue.P[1][18], false);
  for (const t of tracks) {
    for (const p of t.P || []) {
      if (!p[18]) continue;
      assert.notEqual(p[1], "race");
      assert.notEqual(p[1], "junior");
      assert.notEqual(p[1], "kids");
      assert.notEqual(p[11], "package");
      assert.equal(p[14], false);
    }
  }
});

test("intent presets use positive venue evidence", () => {
  for (const intent of ["rent", "own", "race", "family", "group"]) {
    const matches = loadFunction("matchesIntent", { state: { intent } });
    assert.equal(matches({}), false, `${intent} must not assume unknown availability`);
    const examples = {
      rent: { r: "yes" }, own: { ow: "yes" }, race: { K: [[null, null, null, "race"]] },
      family: { K: [[null, null, null, "twin"]] }, group: { P: [Object.assign(Array(14).fill(null), { 0: "Grand Prix", 11: "package" })] },
    };
    assert.equal(matches(examples[intent]), true);
  }
});

test("lowest session cost is independent of lowest per-minute rate and membership is opt-in", () => {
  const offer = (cost, minutes, member, eligible = true) => {
    const p = Array(19).fill(null);
    p[2] = minutes; p[6] = cost; p[16] = member; p[18] = eligible;
    return p;
  };
  const venue = { P: [offer(58, 60, false), offer(22, 15, false), offer(10, 10, true), offer(5, 5, false, false)] };
  assert.equal(loadFunction("sessionOf", { state: { member: false } })(venue)[6], 22);
  assert.equal(loadFunction("sessionOf", { state: { member: true } })(venue)[6], 10);
});

test("private device origin and derived map viewport never enter share URLs", () => {
  for (const origin of [{ lo: 13.405, la: 52.52 }, { lo: 3, la: 46, label: "Atlas town" }]) {
    let saved;
    const state = {
      origin, sort: "distance", sel: 0, tab: "prices", cc: { DE: true },
      on: { outdoor: true }, view: "list", radius: 50, bounds: null,
    };
    const save = loadFunction("saveUrl", {
      state, TRACKS: [{ o: "way/123" }], compareIds: ["way/456"], sharedIds: ["way/789"], restoring: false, URLSearchParams,
      location: { hash: "" }, history: { pushState: (_a, _b, hash) => { saved = hash; } },
      document: { getElementById: () => ({ clientWidth: 390, clientHeight: 500 }) },
      svg: { node: () => ({}) }, d3: { zoomTransform: () => ({ invert: v => v, k: 1 }) },
      proj: { invert: () => [origin.lo, origin.la] },
    });
    save();
    const params = new URLSearchParams(saved.slice(1));
    assert.equal(params.get("venue"), "way/123");
    assert.equal(params.get("compare"), "way/456");
    assert.equal(params.get("shortlist"), "way/789");
    assert.equal(params.has("map"), !!origin.label);
    assert.equal(params.has("town"), !!origin.label);
    assert.equal(params.has("sort"), !!origin.label);
  }
});

test("source freshness is explicit, and failed checks do not claim verified prices", () => {
  const freshness = loadFunction("freshness", {});
  assert.match(freshness({ P: [[1]], Pc: "2026-10-09" }), /checked on 2026-10-09/);
  assert.match(freshness({ P: [[1]] }), /date was not recorded/);
  assert.match(freshness({ Pa: "2026-10-09" }), /No verified published prices.*Last research attempt: 2026-10-09/);
  assert.doesNotMatch(freshness({ Pa: "2026-10-09" }), /prices checked on/);
  assert.doesNotMatch(freshness({ P: [[1]], Pc: "<img>" }), /<img>/);
});

test("shortlists accept only unique existing IDs and comparisons are bounded to four", () => {
  const ids = ["way/1", "way/2", "node/3", "way/4", "way/5"];
  const validate = loadFunction("validVenueIds", { venueIds: new Set(ids), TRACKS: ids });
  assert.deepEqual(Array.from(validate(["way/1", "way/1", null, "<script>", ...ids], 4)), ids.slice(0, 4));
  assert.deepEqual(Array.from(validate({})), []);
  assert.deepEqual(Array.from(validate(ids)), ids);
});

test("family limits are evidence-based and unknown is not unavailable", () => {
  const family = loadFunction("familySummary", {});
  assert.equal(family({}), "Family options not verified.");
  assert.match(family({ K: [[null, null, null, "twin"]] }), /twin.*Age\/height limits not verified/);
  const junior = Array(19).fill(null);
  junior[0] = "Junior"; junior[1] = "junior"; junior[8] = 8; junior[10] = 130;
  assert.match(family({ P: [junior] }), /age 8\+, minimum 130 cm/);
});

test("recent verified operator replacements and source dates survive the build", () => {
  const expected = {
    "way/423697503": "https://www.pistadicattolica.it/",
    "way/388280270": "https://www.southmilanokarting.com/",
    "way/316423358": "https://www.kartodromolascari.it/",
    "node/6859713080": "https://adventureeefde.nl/",
    "node/13897664495": "https://www.playdome.nl/",
  };
  for (const [id, website] of Object.entries(expected)) {
    const t = tracks.find(t => t.o === id);
    assert.equal(t.w, website);
    assert.equal(t.ws[0][0], website);
    assert.equal(t.Pc, "2026-10-09");
    assert.equal(t.r, "yes");
    if (t.T) { assert.equal(t.Tc, "2026-10-09"); assert.ok(t.Ts); }
  }
  assert.equal(tracks.find(t => t.o === "way/388280270").ppm, null);
  for (const id of ["way/245463137", "way/59826097", "way/347258997"]) {
    const t = tracks.find(t => t.o === id);
    assert.equal(t.Pc, undefined);
    assert.equal(t.Pa, "2026-10-09");
  }
});

test("HTML revalidates while the companion dataset retains its cache policy", () => {
  const nginx = fs.readFileSync(path.join(root, "deploy", "nginx.conf"), "utf8");
  for (const location of ["/", "/index.html"]) {
    const block = nginx.split(`location = ${location} {`)[1].split("\n    }")[0];
    assert.match(block, /Cache-Control "no-cache"/);
    assert.doesNotMatch(block, /expires 1h/);
    assert.match(block, /Content-Security-Policy/);
  }
  assert.match(nginx.split("location = /kart-atlas.json {")[1], /max-age=3600/);
});

test("a fifth comparison is rejected with feedback and removal frees a place", () => {
  const status = { textContent: "" };
  let saved = 0, updated = 0;
  const toggle = loadFunction("toggleComparison", {
    venueIds: new Set(["a", "b", "c", "d", "e"]), compareIds: ["a", "b", "c", "d"],
    planner: { open: false }, document: { getElementById: () => status },
    updatePlanning: () => updated++, saveUrl: () => saved++,
  });
  toggle("e");
  assert.match(status.textContent, /up to four/);
  assert.equal(saved, 0);
  toggle("a"); toggle("e");
  assert.equal(updated, 2);
  assert.equal(saved, 2);
  assert.match(status.textContent, /4 of 4/);
});

test("favourites persist as IDs and storage failures are explicitly reported", () => {
  const status = { textContent: "" };
  const writes = [];
  let blocked = false;
  const toggle = loadFunction("toggleFavourite", {
    favouriteIds: [], venueIds: new Set(["way/1"]), planner: { open: false },
    document: { getElementById: () => status }, updatePlanning: () => {},
    localStorage: { setItem: (key, value) => { if (blocked) throw new Error("Storage denied"); writes.push([key, value]); } },
  });
  toggle("way/1");
  assert.deepEqual(writes, [["kartatlas.favourites", '["way/1"]']]);
  toggle("way/1");
  assert.equal(writes[1][1], "[]");
  blocked = true; toggle("way/1");
  assert.match(status.textContent, /Could not persist saved venues: Storage denied.*visit only/);
});

test("comparison renders standard and race offers separately and escapes source text", () => {
  const state = { member: false };
  const esc = loadFunction("esc", {});
  const sessionOf = loadFunction("sessionOf", { state });
  const offerSummary = loadFunction("offerSummary", {});
  const familySummary = loadFunction("familySummary", {});
  const freshness = loadFunction("freshness", {});
  const compare = loadFunction("comparisonTable", {
    state, esc, sessionOf, offerSummary, familySummary, freshness,
    rateSessionSummary: loadFunction("rateSessionSummary", { offerSummary, rateSessionOf: loadFunction("rateSessionOf", { state }) }),
    ppmOf: t => t.ppm, title: t => t.n, planningActions: () => "",
    feeLine: () => "", siteLinks: () => "", externalLink: loadFunction("externalLink", { URL, esc, console }),
  });
  const south = tracks.find(t => t.o === "way/388280270");
  const html = compare([{ ...south, n: '<img src=x onerror="alert(1)">' }]);
  assert.match(html, /Performance \/ race sessions/);
  assert.match(html, /No eligible standard adult session verified/);
  assert.match(html, /€60\.00/);
  assert.match(html, /&lt;img/);
  assert.doesNotMatch(html, /<img/);
});

  test("external links allow HTTP(S) only and visibly reject malformed schemes", () => {
    const warnings = [];
    const esc = loadFunction("esc", {});
    const link = loadFunction("externalLink", { URL, esc, console: { warn: (...args) => warnings.push(args) } });
    for (const url of ["javascript:alert(1)", "data:text/html,<script>", "file:///etc/passwd", "https://user:password@example.com", "https://", "", null]) {
      const rendered = link(url, "Source");
      assert.doesNotMatch(rendered, /<a /);
      assert.match(rendered, /invalid link unavailable/);
    }
    assert.equal(warnings.length, 7);
    assert.match(link("example.com/path", "Venue"), /href="https:\/\/example.com\/path"/);
    assert.match(link("http://example.com/", "<img>"), /&lt;img&gt;/);
    assert.match(link("HTTPS://example.com/", "Venue"), /href="https:\/\/example.com\/"/);
  });

  test("activating a tab updates selected state, keyboard order and panel visibility", () => {
    const tabs = ["overview", "track", "prices"].map(name => ({ dataset: { tab: name }, setAttribute(key, value) { this[key] = value; } }));
    const panes = tabs.map(t => ({ dataset: { pane: t.dataset.tab }, hidden: false }));
    const state = {};
    let saved = 0;
    const activate = loadFunction("activateTab", { state, document: { querySelectorAll: selector => selector.includes("tabpane") ? panes : tabs }, saveUrl: () => saved++ });
    activate(tabs[2]);
    assert.equal(state.tab, "prices");
    assert.deepEqual(tabs.map(t => t.tabIndex), [-1, -1, 0]);
    assert.deepEqual(panes.map(t => t.hidden), [true, true, false]);
    assert.equal(saved, 1);
  });

test("shortlist and comparison sharing omit device location, search and viewport", async () => {
  for (const mode of ["saved", "shared", "compare"]) {
    let copied;
    const share = loadFunction("sharePlan", {
      plannerMode: mode, favouriteIds: ["way/1"], sharedIds: ["way/2"], compareIds: ["way/1", "way/2"],
      window: {},
      state: { member: true, origin: { lo: 12.345, la: 54.321 } }, URL, URLSearchParams,
      location: { href: "https://kartatlas.eu/?release=1#town=Berlin&map=12.345,54.321,6&venue=way/3" },
      navigator: { clipboard: { writeText: async value => { copied = value; } } },
      document: { getElementById: () => ({ textContent: "" }) },
    });

    await share();
    const url = new URL(copied);
    const params = new URLSearchParams(url.hash.slice(1));
    assert.equal(url.search, "");
    assert.deepEqual([...params.keys()], mode === "compare" ? ["compare", "member"] : ["shortlist"]);
    assert.equal(params.get(mode === "compare" ? "compare" : "shortlist"), mode === "compare" ? "way/1,way/2" : mode === "saved" ? "way/1" : "way/2");
    assert.doesNotMatch(copied, /12\.345|54\.321/);
  }
});
test("all existing researched links remain usable under HTTP(S) validation", () => {
  const warnings = [];
  const link = loadFunction("externalLink", { URL, esc: loadFunction("esc", {}), console: { warn: message => warnings.push(message) } });
  for (const t of tracks) {
    const urls = [t.w, t.Ps, t.Ts, ...(t.src || []), ...(t.ws || []).map(w => w[0])].filter(Boolean);
    for (const url of urls) assert.match(link(url, "Source"), /<a href=/, `${t.o}: ${url}`);
  }
  assert.equal(warnings.length, 0);
});

test("generated details and results expose accessible names and focus targets", () => {
  assert.match(html, /id="stats" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(template, /id="detail-title" tabindex="-1"/);
  assert.match(template, /aria-controls="pane-\$\{x\[0\]\}"/);
  assert.match(template, /aria-labelledby="tab-\$\{x\[0\]\}"/);
  assert.match(template, /"ArrowLeft", "ArrowRight", "Home", "End"/);
  assert.match(html, /<details class="filter-panel" id="filters">/);
  assert.match(html, /<details class="foot">/);
});

test("the lowest rate explains its actual offer, independently of lowest session cost", () => {
  const state = { member: false };
  const offers = [[58, 60, false], [22, 15, false], [5, 10, true]].map(([cost, minutes, member]) => {
    const p = Array(19).fill(null);
    p[0] = "Standard"; p[2] = minutes; p[6] = cost; p[7] = cost / minutes; p[16] = member; p[18] = true;
    return p;
  });
  const venue = { P: offers };
  const rateSessionOf = loadFunction("rateSessionOf", { state });
  assert.equal(rateSessionOf(venue), offers[0]);
  const summary = loadFunction("rateSessionSummary", { rateSessionOf, offerSummary: loadFunction("offerSummary", {}) });
  assert.match(summary(venue), /€58\.00.*60 min.*€0\.97\/min/);
  state.member = true;
  assert.equal(rateSessionOf(venue), offers[2]);
});

test("family research is explicit and does not erase verified tariffs", () => {
  const matches = loadFunction("matchesIntent", { state: { intent: "family" } });
  const family = loadFunction("familySummary", {});
  for (const id of ["node/6859713080", "node/13897664495"]) {
    const t = tracks.find(t => t.o === id);
    assert.ok(t.P.length);
    assert.ok(t.FG.checked_at && t.FG.source);
    assert.equal(matches(t), true);
    assert.match(family(t), /cm/);
  }
  assert.match(tracks.find(t => t.o === "node/13897664495").FG.family.join(" "), /whole party/);
});

test("all venues have indexable pages and the sitemap uses the current domain", () => {
  const sitemap = fs.readFileSync(path.join(root, "public", "sitemap.xml"), "utf8");
  const rates = JSON.parse(fs.readFileSync(path.join(root, "pipeline", "rates_meta.json"), "utf8"));
  assert.equal((sitemap.match(/<loc>/g) || []).length, tracks.length + 2);
  for (const t of tracks) {
    const slug = t.o.replace("/", "-");
    const page = fs.readFileSync(path.join(root, "public", "venues", slug, "index.html"), "utf8");
    assert.ok(page.includes(`https://kartatlas.michaelbinger.dk/venues/${slug}/`));
    assert.ok(page.includes(`ECB rates of ${rates.date}`));
    assert.doesNotMatch(page, /<script/);
    assert.ok(sitemap.includes(`/venues/${slug}/`));
  }
});

test("deployment assets are local and CSP no longer trusts third-party CDNs", () => {
  assert.doesNotMatch(html, /https:\/\/(fonts\.googleapis|cdnjs|cdn\.jsdelivr)/);
  const nginx = fs.readFileSync(path.join(root, "deploy", "nginx.conf"), "utf8");
  assert.doesNotMatch(nginx, /cdnjs|jsdelivr|googleapis|gstatic/);
  assert.match(nginx, /try_files \$uri \$uri\/ =404/);
  for (const file of ["d3.min.js", "topojson-client.min.js", "fonts.css", "i18n.js"]) {
    assert.ok(fs.existsSync(path.join(root, "assets", file)));
  }
});

test("Pista Winner survives rebuild with separated standard, race and child prices", () => {
  const winners = tracks.filter(t => t.o === "way/444163257");
  assert.equal(winners.length, 1);
  const venue = winners[0];
  assert.equal(venue.n, "Pista Winner");
  assert.equal(venue.c, "Nizza Monferrato");
  assert.equal(venue.r, "yes");
  assert.equal(venue.k, "outdoor");
  assert.equal(venue.g, null, "OSM sports-centre boundary is not a driving layout");
  assert.equal(venue.ppm, 1.67);
  assert.equal(venue.Pc, "2026-10-09");
  assert.equal(venue.P.length, 9);
  const standard = venue.P.filter(p => p[18]);
  assert.equal(standard.length, 1);
  assert.equal(standard[0][6], 25);
  assert.equal(standard[0][2], 15);
  assert.ok(venue.P.filter(p => p[1] === "race").every(p => !p[18]));
  assert.ok(venue.P.filter(p => ["kids", "twin"].includes(p[1]) || p[11] === "package").every(p => !p[18]));
  assert.match(venue.FG.family.join(" "), /limits conflict/);
  assert.match(venue.note, /sport=motor/);
});

test("broad discovery adds only verified missing venues without fabricated layouts", () => {
  const additions = [
    ["way/340141838", "DE", "Kartsportzentrum Rottal"],
    ["way/130350436", "IT", "Pista Azzurra Jesolo"],
    ["node/2932410866", "NL", "Kartcentrum Lelystad"]
  ];
  for (const [id, cc, name] of additions) {
    const found = tracks.filter(t => t.o === id);
    assert.equal(found.length, 1);
    assert.equal(found[0].cc, cc);
    assert.equal(found[0].n, name);
    assert.equal(found[0].g, null);
    assert.equal(found[0].r, "yes");
    assert.ok(found[0].FG.source && found[0].FG.checked_at);
  }
  assert.ok(!tracks.some(t => t.o === "way/27999737"), "deleted Dutch OSM identity rejected");
  const rottal = tracks.find(t => t.o === additions[0][0]);
  assert.equal(rottal.len, 851);
  assert.equal(rottal.ppm, 1.56);
  assert.equal(rottal.P.filter(p => p[18]).length, 3);
  const jesolo = tracks.find(t => t.o === additions[1][0]);
  assert.equal(jesolo.len, 1045);
  assert.ok(jesolo.P.every(p => !p[18]), "unverified rental tiers not assumed standard or 2T");
  assert.ok(jesolo.K.every(k => !k[1] || /4T/.test(k[1])));
  assert.ok(jesolo.K.every(k => k[4] === null), "marketing tier labels are not chassis manufacturers");
  const dutch = tracks.find(t => t.o === additions[2][0]);
  assert.ok(!dutch.P?.length, "no guessed rental price");
  assert.equal(dutch.F[0][1], 1.5);
  assert.match(dutch.F[0][6], /Own helmet permitted/);
  assert.match(dutch.note, /shared-site address node/);
  assert.ok(dutch.K.every(k => k[4] === null), "duokart describes seating, not a verified brand");
});

test("rendered tariff refresh separates blocks, group durations and future fleets", () => {
  for (const id of ["way/163895648", "relation/7225161"]) {
    const t = tracks.find(t => t.o === id);
    assert.equal(t.Pc, "2026-10-09");
    assert.equal(t.P.filter(p => p[18]).length, 1);
    assert.equal(t.P.find(p => p[18])[2], 12);
    assert.equal(t.P.find(p => p[18])[4], 25);
    assert.ok(t.K.every(k => k[3] !== "electric"));
    assert.match(t.note, /Coming soon/);
  }
  const kalmar = tracks.find(t => t.o === "way/45484844");
  assert.equal(kalmar.P.length, 8);
  assert.equal(kalmar.P.filter(p => p[18]).length, 1);
  assert.ok(kalmar.P.filter(p => / x 8 /.test(p[0])).every(p => p[2] === null && !p[18]));
  assert.equal(kalmar.P.find(p => p[0] === "Formula 1")[2], 32);
  const nendeln = tracks.find(t => t.o === "way/1006250895");
  assert.equal(nendeln.k, "indoor");
  assert.equal(nendeln.P.filter(p => p[18]).length, 1);
  assert.equal(nendeln.K[0][3], "electric");
  const danish = tracks.find(t => t.o === "node/4467077725");
  assert.equal(danish.K[0][4], "Dino");
  assert.equal(danish.P.length, 5, "existing Grand Prix offers reverified and preserved");
  assert.equal(danish.F[0][5], false, "optional suit hire not mandatory");
  const french = tracks.find(t => t.o === "way/54413439");
  assert.equal(french.P.find(p => p[18])[8], 12);
  assert.equal(french.P.find(p => p[18])[10], 140);
  const belgian = tracks.find(t => t.o === "way/94522368");
  assert.ok(belgian.P.length);
  assert.equal(belgian.Pa, "2026-10-09");
  assert.notEqual(belgian.Pc, "2026-10-09", "blank price embed does not reverify old prices");
});

test("discovery research records ten countries and explicitly failed bulk scanning", () => {
  const batch = JSON.parse(fs.readFileSync(path.join(root, "pipeline", "research", "out", "discovery", "D01.json"), "utf8"));
  assert.deepEqual(batch.countries.map(c => c.cc).sort(), ["AT", "BE", "CH", "DE", "DK", "FR", "IT", "LI", "NL", "SE"]);
  assert.match(batch.bulk_osm_scan, /^Failed:/);
  assert.ok(batch.countries.every(c => c.terms.length && c.ids.length && c.outcome));
});
