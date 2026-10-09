const https = require("node:https");

const origin = process.env.SITE_URL || "https://kartatlas.michaelbinger.dk";
const url = new URL(origin);
if (url.protocol !== "https:" || url.username || url.password || url.pathname !== "/" || url.search || url.hash) {
  throw new Error("SITE_URL must be an HTTPS origin without credentials");
}

async function check(path) {
  await new Promise((resolve, reject) => {
    const req = https.get(new URL(path, url), { timeout: 15000 }, res => {
      const certificate = res.socket.getPeerCertificate();
      const days = Math.floor((Date.parse(certificate.valid_to) - Date.now()) / 86400000);
      res.resume();
      if (res.statusCode !== 200) return reject(new Error(`${path}: HTTP ${res.statusCode}`));
      if (!Number.isFinite(days) || days < 21) return reject(new Error(`Certificate expires in ${days} days`));
      if (!res.headers["content-security-policy"] || res.headers["x-content-type-options"] !== "nosniff") {
        return reject(new Error(`${path}: expected security headers missing`));
      }
      res.on("end", () => { console.log(`OK ${url.origin}${path}; certificate valid for ${days} days`); resolve(); });
      res.on("error", reject);
    });
    req.on("timeout", () => req.destroy(new Error(`${path}: request timed out`)));
    req.on("error", reject);
  });
}

Promise.all(["/", "/venues/node-6859713080/", "/sitemap.xml"].map(check)).catch(error => {
  console.error(`HEALTH CHECK FAILED: ${error.message}`);
  process.exitCode = 1;
});
