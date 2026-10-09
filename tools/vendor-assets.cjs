const fs = require("node:fs");
const path = require("node:path");
const root = path.join(__dirname, "..");
const target = path.join(root, "assets");
fs.mkdirSync(target, { recursive: true });
for (const [name, file] of [["d3", "d3.min.js"], ["topojson-client", "topojson-client.min.js"]]) {
  const source = path.join(root, "node_modules", name);
  fs.copyFileSync(path.join(source, "dist", file), path.join(target, file));
  fs.copyFileSync(path.join(source, "LICENSE"), path.join(target, `${name}-LICENSE.txt`));
}
let css = "";
for (const [family, weights] of [["barlow", [400, 500, 600]], ["barlow-condensed", [600, 700]], ["ibm-plex-mono", [400, 500]]]) {
  const source = path.join(root, "node_modules", "@fontsource", family);
  for (const weight of weights) {
    const filename = `${family}-latin-${weight}-normal.woff2`;
    fs.copyFileSync(path.join(source, "files", filename), path.join(target, filename));
    const font = family.split("-").map(s => s === "ibm" ? "IBM" : s[0].toUpperCase() + s.slice(1)).join(" ");
    css += `@font-face{font-family:"${font}";font-style:normal;font-weight:${weight};font-display:swap;src:url("./${filename}") format("woff2");}\n`;
  }
  fs.copyFileSync(path.join(source, "LICENSE"), path.join(target, `${family}-LICENSE.txt`));
}
fs.writeFileSync(path.join(target, "fonts.css"), css);
console.log("Vendored pinned libraries, Latin fonts and licence notices.");
