import { test } from "node:test";
import assert from "node:assert/strict";
import { decode, iou, planarRGB } from "../web/src/yolo.js";
test("RGB layout and normalization", () =>
  assert.deepEqual(
    [...planarRGB(new Uint8Array([255, 0, 128, 255]))],
    [1, 0, 128 / 255].map(Math.fround),
  ));
test("overlap and disjoint boxes", () => {
  assert.equal(iou({ x: 0, y: 0, w: 1, h: 1 }, { x: 0, y: 0, w: 1, h: 1 }), 1);
  assert.equal(iou({ x: 0, y: 0, w: 1, h: 1 }, { x: 2, y: 2, w: 1, h: 1 }), 0);
});
test("class-aware NMS, coordinate scale, threshold", () => {
  const n = 4,
    d = new Float32Array(84 * n);
  for (let i = 0; i < n; i++) {
    d[i] = 320;
    d[n + i] = 320;
    d[2 * n + i] = 160;
    d[3 * n + i] = 160;
  }
  d[4 * n] = 0.9;
  d[4 * n + 1] = 0.8;
  d[5 * n + 2] = 0.85;
  d[6 * n + 3] = 0.1;
  const r = decode(d, [1, 84, n]);
  assert.equal(r.length, 2);
  assert.equal(r[0].x, 0.375);
  assert.equal(r[1].cls, 1);
});
test("reject unsupported output contracts", () =>
  assert.throws(() => decode(new Float32Array(1), [1, 85, 1])));
