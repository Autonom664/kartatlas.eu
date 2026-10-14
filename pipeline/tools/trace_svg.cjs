// Sample a kart-track centre line from an SVG track graphic, using headless Chromium (Playwright).
// usage: node trace_svg.cjs FILE.svg OUT_PREFIX [--index N] [--points 110]
// Lists every path with its length; samples the longest one (or --index N) in root SVG coordinates,
// including transforms. Writes OUT_PREFIX.json and OUT_PREFIX_overlay.png (traced line in red).
// For a filled "ribbon" (outer + inner edge in one path) use trace_raster.py on a rendering instead.
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const [file, out, ...rest] = process.argv.slice(2);
const opt = (k, d) => { const i = rest.indexOf(k); return i >= 0 ? Number(rest[i + 1]) : d; };
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 800, height: 800 } });
  await page.goto("file:///" + path.resolve(file).replace(/\\/g, "/"));
  const res = await page.evaluate(({ index, N }) => {
    const paths = [...document.querySelectorAll("path,polyline,polygon,line,circle,ellipse,rect")]
      .filter(e => e.getTotalLength).map((e, i) => ({ e, i, L: e.getTotalLength() }));
    const list = paths.map(p => ({ i: p.i, tag: p.e.tagName, len: Math.round(p.L), stroke: getComputedStyle(p.e).stroke, fill: getComputedStyle(p.e).fill }));
    const pick = index >= 0 ? paths.find(p => p.i === index) : paths.slice().sort((a, b) => b.L - a.L)[0];
    if (!pick) return { list };
    const m = pick.e.getCTM(), pts = [];
    for (let k = 0; k < N; k++) { const q = pick.e.getPointAtLength(pick.L * k / N); const r = new DOMPoint(q.x, q.y).matrixTransform(m); pts.push([+r.x.toFixed(1), +r.y.toFixed(1)]); }
    const a = pick.e.getPointAtLength(0), b = pick.e.getPointAtLength(pick.L);
    const closed = Math.hypot(a.x - b.x, a.y - b.y) < pick.L * 0.02;
    const svg = document.documentElement, NS = "http://www.w3.org/2000/svg", pl = document.createElementNS(NS, "polyline");
    const bb = svg.getBBox();
    pl.setAttribute("points", pts.map(p => p.join(",")).join(" ")); pl.setAttribute("fill", "none"); pl.setAttribute("stroke", "red");
    pl.setAttribute("stroke-width", String(Math.max(bb.width, bb.height) / 150)); svg.appendChild(pl);
    return { list, picked: pick.i, closed, points: pts };
  }, { index: opt("--index", -1), N: opt("--points", 110) });
  console.log(JSON.stringify({ paths: res.list, picked: res.picked, closed: res.closed }));
  if (res.points) {
    fs.writeFileSync(out + ".json", JSON.stringify({ points: res.points, closed: res.closed }));
    await page.screenshot({ path: out + "_overlay.png" });
  }
  await browser.close();
})();
