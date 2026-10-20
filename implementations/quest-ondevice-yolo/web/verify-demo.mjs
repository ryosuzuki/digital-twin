import { chromium } from "@playwright/test";
import fs from "node:fs/promises";
const out = process.env.YOLO_EVIDENCE;
if (!out || !process.env.YOLO_TEST_IMAGE)
  throw Error("Set YOLO_EVIDENCE and YOLO_TEST_IMAGE");
const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROME_PATH
    ? { executablePath: process.env.CHROME_PATH }
    : {}),
});
const context = await browser.newContext({
  viewport: { width: 1280, height: 900 },
  recordVideo: { dir: out, size: { width: 1280, height: 900 } },
});
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
try {
  await page.goto(process.env.YOLO_URL || "http://localhost:39461/");
  await page.getByRole("button", { name: "1 · Load model" }).click();
  await page.waitForFunction(
    () =>
      window.yoloDiagnostics?.().ready ||
      document.querySelector("#status").textContent.includes("unavailable"),
    {},
    { timeout: 60000 },
  );
  if (!(await page.evaluate(() => window.yoloDiagnostics().ready)))
    throw Error(await page.locator("#status").innerText());
  await page.locator("#file").setInputFiles(process.env.YOLO_TEST_IMAGE);
  await page.waitForFunction(
    () => window.yoloDiagnostics().samples.length >= 3,
    {},
    { timeout: 120000 },
  );
  const result = await page.evaluate(() => window.yoloDiagnostics());
  if (
    result.boxes.length < 2 ||
    !result.boxes.some((x) => x.cls === 0) ||
    !result.boxes.some((x) => x.cls === 5)
  )
    throw Error(`Expected bus/person: ${JSON.stringify(result.boxes)}`);
  await page.screenshot({ path: out + "/web-model-inference.png" });
  await fs.writeFile(
    out + "/web-model-inference.json",
    JSON.stringify(
      {
        verified:
          "desktop Chromium, public bus test image, real ONNX inference; NOT Quest",
        errors,
        ...result,
      },
      null,
      2,
    ),
  );
  await page.waitForTimeout(10000);
  await page.locator("#stop").click();
  if (await page.evaluate(() => window.yoloDiagnostics().running))
    throw Error("Stop did not stop");
  await page.locator("#start").click();
  await page.waitForFunction(
    () =>
      document
        .querySelector("#status")
        .textContent.includes("Camera unavailable"),
    {},
    { timeout: 15000 },
  );
  await page.locator("#xr").click();
  await page.waitForFunction(() =>
    document.querySelector("#status").textContent.includes("WebXR unavailable"),
  );
  if (errors.length) throw Error(errors.join("\n"));
  console.log(
    JSON.stringify({
      detections: result.boxes.length,
      classes: [...new Set(result.boxes.map((x) => x.cls))],
      samples: result.samples.map((x) => x.ms),
      pageErrors: errors,
      stop: true,
      cameraUnavailableMessage: true,
      xrUnsupportedMessage: true,
    }),
  );
} finally {
  await page.screenshot({ path: out + "/last-state.png" }).catch(() => {});
  const video = page.video();
  await context.close();
  if (video)
    await fs.copyFile(await video.path(), out + "/web-inference-demo.webm");
  await browser.close();
}
