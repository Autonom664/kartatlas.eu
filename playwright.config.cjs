const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/browser",
  use: {
    baseURL: process.env.KARTATLAS_TEST_URL || "http://127.0.0.1:18082",
    browserName: "chromium",
    trace: "retain-on-failure"
  },
  reporter: "list",
  fullyParallel: true,
  workers: 2
});
