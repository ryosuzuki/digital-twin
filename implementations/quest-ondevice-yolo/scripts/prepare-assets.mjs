import { createHash } from "node:crypto";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";
const root = fileURLToPath(new URL("../web/", import.meta.url));
const base =
  "https://raw.githubusercontent.com/oculus-samples/Unity-PassthroughCameraApiSamples/3baac1a1a53aa00af3f639425914f14238a97f84/Assets/PassthroughCameraApiSamples/MultiObjectDetection/SentisInference/Model/";
await mkdir(path.join(root, "public/models"), { recursive: true });
for (const [remote, local, hash] of [
  [
    "yolov9onnx.onnx",
    "yolov9.onnx",
    "189ed26d273423b02243ce7f0a7795acc7da8049f879f8b73a0684d25d1138fd",
  ],
  [
    "SentisYoloClasses.txt",
    "classes.txt",
    "634a1132eb33f8091d60f2c346ababe8b905ae08387037aed883953b7329af84",
  ],
]) {
  const res = await fetch(base + remote);
  if (!res.ok) throw Error(`${remote}: ${res.status}`);
  const data = Buffer.from(await res.arrayBuffer());
  if (createHash("sha256").update(data).digest("hex") !== hash)
    throw Error(`Hash mismatch: ${remote}`);
  await writeFile(path.join(root, "public/models", local), data);
}
console.log(
  "Pinned model and labels prepared. WASM runtime is bundled by Vite. No inference server.",
);
