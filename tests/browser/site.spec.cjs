const { test, expect } = require("@playwright/test");

for (const [width, height] of [[320, 568], [390, 844], [844, 390]]) {
  test(`usable list and details at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/");
    await expect(page.locator(".item").first()).toBeVisible();
    const list = await page.locator("#list").boundingBox();
    expect(list.height).toBeGreaterThan(150);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    for (const language of ["da", "de", "en"]) {
      await page.locator("#language").selectOption(language);
      await expect(page.locator("html")).toHaveAttribute("lang", language);
      expect((await page.locator("#list").boundingBox()).height).toBeGreaterThan(150);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    }
    await page.locator("#filters > summary").click();
    expect((await page.locator("#list").boundingBox()).height).toBeGreaterThan(100);
    await page.locator("#filters > summary").click();
    await page.locator(".item").first().click();
    await expect(page.locator("#detail-title")).toBeFocused();
    const detail = await page.locator("#detail").boundingBox();
    expect(detail.height).toBeGreaterThan(200);
    await page.getByRole("button", { name: "Close track details" }).click();
    await expect(page.locator(".item").first()).toBeFocused();
  });
}

test("keyboard tabs and focus restoration work", async ({ page }) => {
  await page.goto("/#venue=node%2F6859713080");
  const first = page.getByRole("tab", { name: "Overview" });
  await first.focus();
  await page.keyboard.press("End");
  await expect(page.getByRole("tab", { name: "Prices", exact: true })).toBeFocused();
  await expect(page.getByRole("tab", { name: "Prices", exact: true })).toHaveAttribute("aria-selected", "true");
  await page.keyboard.press("Home");
  await expect(first).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.locator("#detail")).toBeHidden();
});

test("language survives sharing, reload and dynamically rendered details", async ({ page }) => {
  await page.goto("/");
  await page.locator("#language").selectOption("da");
  await expect(page.locator("html")).toHaveAttribute("lang", "da");
  await expect(page.locator("#share-search")).toHaveText("Kopiér søgelink");
  await page.locator(".item").first().click();
  await expect(page.getByRole("tab", { name: "Overblik" })).toBeVisible();
  expect(new URLSearchParams(new URL(page.url()).hash.slice(1)).get("lang")).toBe("da");
  await page.reload();
  await expect(page.locator("#language")).toHaveValue("da");
  await page.locator("#language").selectOption("de");
  await expect(page.getByRole("tab", { name: "Übersicht" })).toBeVisible();
  await page.locator("#language").selectOption("en");
  await expect(page.getByRole("tab", { name: "Overview" })).toBeVisible();
  await expect(page.locator("#share-search")).toHaveText("Copy search link");
});

test("comparison keeps exact standard sessions separate from race offers", async ({ page }) => {
  await page.goto("/#compare=node%2F6859713080%2Cway%2F388280270");
  await expect(page.getByText("Session behind that €/min", { exact: true })).toBeVisible();
  await expect(page.getByText("Performance / race sessions", { exact: true })).toBeVisible();
  await expect(page.getByText("No eligible standard adult session verified", { exact: true })).toBeVisible();
  await page.keyboard.press("Escape");
  await page.goto("/#venue=node%2F13897664495");
  await expect(page.getByText(/whole party must book a family session/).first()).toBeVisible();
});

test("filters and Back restore the earlier search", async ({ page }) => {
  await page.goto("/");
  const before = await page.locator(".item").count();
  await page.locator('[data-intent="family"]').click();
  await expect(page.locator('[data-intent="family"]')).toHaveAttribute("aria-pressed", "true");
  expect(await page.locator(".item").count()).toBeLessThan(before);
  await page.goBack();
  await expect(page.locator('[data-intent=""]')).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".item")).toHaveCount(before);
});

test("only same-origin assets load; pages and sitemap have real routes and headers", async ({ page, request, baseURL }) => {
  const external = [], errors = [];
  page.on("request", req => { if (new URL(req.url()).origin !== new URL(baseURL).origin) external.push(req.url()); });
  page.on("pageerror", err => errors.push(err.message));
  const response = await page.goto("/");
  await expect(page.locator(".item").first()).toBeVisible();
  expect(response.headers()["content-security-policy"]).not.toMatch(/cdnjs|googleapis|jsdelivr|gstatic/);
  expect(external).toEqual([]);
  expect(errors).toEqual([]);
  await page.goto("/venues/node-13897664495/");
  await expect(page.locator("h1")).toContainText("Playdome");
  await expect(page.getByText(/whole party must book a family session/)).toBeVisible();
  const venue = await request.get("/venues/node-6859713080/");
  expect(venue.status()).toBe(200);
  expect(venue.headers()["cache-control"]).toContain("no-cache");
  const sitemap = await request.get("/sitemap.xml");
  const data = await request.get("/kart-atlas.json");
  expect((await sitemap.text()).match(/<loc>/g)).toHaveLength((await data.json()).length + 2);
  expect((await request.get("/venues/not-a-venue/")).status()).toBe(404);
});

test("shared URLs retain language but exclude private device coordinates", async ({ page, context }) => {
  await context.grantPermissions(["geolocation", "clipboard-read", "clipboard-write"]);
  await context.setGeolocation({ latitude: 52.123456, longitude: 12.654321 });
  await page.goto("/");
  await page.locator("#locate").click();
  await expect(page.locator("#location-status")).toContainText("Your device location (private)");
  await page.locator("#language").selectOption("da");
  await page.locator("#share-search").click();
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied).not.toMatch(/52\.123456|12\.654321|map=|town=/);
  expect(new URLSearchParams(new URL(copied).hash.slice(1)).get("lang")).toBe("da");
});

test("Pista Winner is searchable and has a working venue page and separate tariffs", async ({ page }) => {
  await page.goto("/");
  await page.locator("#q").fill("Pista Winner");
  await expect(page.locator(".item[data-id]")).toHaveCount(1);
  await page.locator(".item[data-id]").click();
  await expect(page.locator("#detail-title")).toHaveText("Pista Winner");
  await expect(page.getByText(/Session behind the lowest/)).toBeVisible();
  await page.getByRole("tab", { name: "Prices", exact: true }).click();
  await expect(page.locator("#pane-prices").getByText("Kart normale 4 tempi 270cc", { exact: false }).first()).toBeVisible();
  await expect(page.locator("#pane-prices").getByText("Kart competizione 2 tempi 125cc - 15 minuti", { exact: false })).toBeVisible();
  await page.goto("/venues/way-444163257/");
  await expect(page.locator("h1")).toHaveText("Pista Winner");
  await expect(page.getByText(/^EUR 1\.67\/min; EUR 25\.00 for 15(?:\.0)? minutes; Kart normale 4 tempi 270cc$/)).toBeVisible();
});

test("broader discovery exposes verified venues, unknown prices and recovered Swiss tariffs", async ({ page }) => {
  for (const [name, id] of [
    ["Kartsportzentrum Rottal", "way/340141838"],
    ["Pista Azzurra Jesolo", "way/130350436"],
    ["Kartcentrum Lelystad", "node/2932410866"]
  ]) {
    await page.goto("/");
    await page.locator("#q").fill(name);
    await expect(page.locator(".item[data-id]")).toHaveCount(1);
    await page.locator(".item[data-id]").click();
    await expect(page.locator("#detail-title")).toHaveText(name);
    await page.goto(`/venues/${id.replace("/", "-")}/`);
    await expect(page.locator("h1")).toHaveText(name);
  }
  await expect(page.getByText("No verified published prices in the atlas. This does not mean rental is unavailable.")).toBeVisible();
  await page.goto("/#venue=way%2F130350436");
  await page.getByRole("tab", { name: "Prices", exact: true }).click();
  await expect(page.locator("#pane-prices").getByText("RACE 200cc 4T", { exact: false }).first()).toBeVisible();
  await expect(page.locator("#pane-prices").getByText(/classification unverified/).first()).toBeVisible();
  await page.goto("/venues/way-163895648/");
  const adult = page.getByRole("row").filter({ has: page.getByRole("cell", { name: "Adult Sodi SR5", exact: true }) });
  await expect(adult).toContainText(/12(?:\.0)? min/);
  await expect(adult).toContainText(/25(?:\.0)? CHF/);
  await expect(adult).toContainText("Standard comparison");
  await expect(page.getByText(/Coming soon/).first()).toBeVisible();
});
