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
  const match = template.match(new RegExp(`function ${name}\\([^]*?\\n\\}`, "m"));
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
      state, TRACKS: [{ o: "way/123" }], restoring: false, URLSearchParams,
      location: { hash: "" }, history: { pushState: (_a, _b, hash) => { saved = hash; } },
      document: { getElementById: () => ({ clientWidth: 390, clientHeight: 500 }) },
      svg: { node: () => ({}) }, d3: { zoomTransform: () => ({ invert: v => v, k: 1 }) },
      proj: { invert: () => [origin.lo, origin.la] },
    });
    save();
    const params = new URLSearchParams(saved.slice(1));
    assert.equal(params.get("venue"), "way/123");
    assert.equal(params.has("map"), !!origin.label);
    assert.equal(params.has("town"), !!origin.label);
    assert.equal(params.has("sort"), !!origin.label);
  }
});
