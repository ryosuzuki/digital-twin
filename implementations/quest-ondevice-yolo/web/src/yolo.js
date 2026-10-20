export function iou(a, b) {
  const w = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)),
    h = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  return (w * h) / (a.w * a.h + b.w * b.h - w * h || 1);
}
export function decode(data, dims, threshold = 0.35, overlap = 0.45) {
  if (dims.length !== 3 || dims[0] !== 1 || dims[1] !== 84)
    throw Error(`Expected YOLO [1,84,N], got ${dims}`);
  const n = dims[2],
    out = [];
  for (let i = 0; i < n; i++) {
    let score = 0,
      cls = -1;
    for (let c = 4; c < 84; c++) {
      const s = data[c * n + i];
      if (s > score) {
        score = s;
        cls = c - 4;
      }
    }
    if (score < threshold) continue;
    const w = data[2 * n + i],
      h = data[3 * n + i];
    if (!Number.isFinite(w + h + score) || w <= 0 || h <= 0) continue;
    out.push({
      x: (data[i] - w / 2) / 640,
      y: (data[n + i] - h / 2) / 640,
      w: w / 640,
      h: h / 640,
      score,
      cls,
    });
  }
  out.sort((a, b) => b.score - a.score);
  const keep = [];
  for (const box of out) {
    if (keep.every((b) => b.cls !== box.cls || iou(b, box) < overlap))
      keep.push(box);
    if (keep.length === 40) break;
  }
  return keep;
}
export function planarRGB(rgba) {
  const n = rgba.length / 4,
    a = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    a[i] = rgba[i * 4] / 255;
    a[n + i] = rgba[i * 4 + 1] / 255;
    a[2 * n + i] = rgba[i * 4 + 2] / 255;
  }
  return a;
}
