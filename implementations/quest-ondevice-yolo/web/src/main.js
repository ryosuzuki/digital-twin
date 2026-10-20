import * as ort from "onnxruntime-web/wasm";
import wasmURL from "../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.wasm?url";
import mjsURL from "../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.mjs?url";
import * as THREE from "three";
import { decode, planarRGB } from "./yolo.js";
const $ = (id) => document.getElementById(id),
  canvas = $("preview"),
  ctx = canvas.getContext("2d"),
  video = $("video");
const frozen = document.createElement("canvas");
frozen.width = frozen.height = 640;
let hasFrame = false;
const prep = document.createElement("canvas");
prep.width = prep.height = 640;
const pc = prep.getContext("2d", { willReadFrequently: true });
ort.env.wasm.wasmPaths = { wasm: wasmURL, mjs: mjsURL };
ort.env.wasm.numThreads = 1;
let epoch = 0;
let session,
  labels = [],
  stream,
  source,
  sourceLabel = "",
  busy = false,
  running = false,
  last = 0,
  boxes = [],
  samples = [],
  objectURL,
  recorder,
  xrSession;
const status = (s) => ($("status").textContent = s);
function draw() {
  if (!source) return;
  ctx.drawImage(hasFrame ? frozen : source, 0, 0, canvas.width, canvas.height);
  ctx.lineWidth = 3;
  ctx.font = "18px system-ui";
  for (const b of boxes) {
    const x = b.x * canvas.width,
      y = b.y * canvas.height;
    ctx.strokeStyle = "#71ffbb";
    ctx.strokeRect(x, y, b.w * canvas.width, b.h * canvas.height);
    ctx.fillStyle = "#10251ee8";
    ctx.fillRect(x, y, 210, 26);
    ctx.fillStyle = "#b0ffd6";
    ctx.fillText(
      `${labels[b.cls]} ${(b.score * 100).toFixed(0)}%`,
      x + 5,
      y + 19,
    );
  }
  ctx.fillStyle = "#07101bdb";
  ctx.fillRect(0, canvas.height - 35, canvas.width, 35);
  ctx.fillStyle = "white";
  ctx.fillText(
    `${sourceLabel} • local YOLO • ${samples.at(-1)?.ms.toFixed(0) ?? "—"} ms`,
    12,
    canvas.height - 12,
  );
}
async function infer() {
  if (!session || !source || busy) return;
  busy = true;
  const generation = epoch;
  try {
    pc.drawImage(source, 0, 0, 640, 640);
    const start = performance.now(),
      input = new ort.Tensor(
        "float32",
        planarRGB(pc.getImageData(0, 0, 640, 640).data),
        [1, 3, 640, 640],
      );
    let result;
    try {
      result = await session.run({ [session.inputNames[0]]: input });
      const output = result[session.outputNames[0]];
      if (generation !== epoch) return;
      boxes = decode(output.data, output.dims);
      frozen.getContext("2d").drawImage(prep, 0, 0);
      hasFrame = true;
    } finally {
      input.dispose();
      if (result) Object.values(result).forEach((x) => x.dispose());
    }
    const ms = performance.now() - start;
    samples.push({
      ms,
      at: new Date().toISOString(),
      detections: boxes.length,
      source: sourceLabel,
    });
    if (samples.length > 10000) samples.shift();
    $("latency").textContent = `${ms.toFixed(0)} ms`;
    $("count").textContent = `${boxes.length} detections`;
    draw();
  } catch (e) {
    running = false;
    status(`Inference stopped: ${e.message}`);
  } finally {
    busy = false;
  }
}
function loop(t) {
  if (running && source) {
    draw();
    if (t - last >= 200) {
      last = t;
      void infer();
    }
  }
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
$("load").onclick = async () => {
  if (session) return;
  try {
    status("Loading local model…");
    labels = (await (await fetch("models/classes.txt")).text())
      .trim()
      .split("\n");
    session = await ort.InferenceSession.create("models/yolov9.onnx", {
      executionProviders: ["wasm"],
    });
    status(
      "Model ready · WASM CPU · no external GPU. Choose camera or a test file.",
    );
  } catch (e) {
    status(
      `Model unavailable: ${e.message}. Run npm run prepare-assets first.`,
    );
  }
};
function stop() {
  epoch++;
  running = false;
  stream?.getTracks().forEach((t) => t.stop());
  stream = null;
  video.pause();
  video.srcObject = null;
  video.removeAttribute("src");
  source = null;
  boxes = [];
  hasFrame = false;
  if (objectURL) {
    URL.revokeObjectURL(objectURL);
    objectURL = null;
  }
  $("source").textContent = "STOPPED";
}
$("stop").onclick = () => {
  stop();
  status("Camera and inference stopped.");
};
$("start").onclick = async () => {
  stop();
  try {
    if (!navigator.mediaDevices)
      throw Error("Camera requires HTTPS (or localhost).");
    const deviceId = $("camera").value;
    stream = await navigator.mediaDevices.getUserMedia({
      video: deviceId
        ? { deviceId: { exact: deviceId } }
        : { facingMode: { ideal: "environment" } },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();
    source = video;
    sourceLabel = "LIVE CAMERA";
    $("source").textContent = sourceLabel;
    running = true;
    status(
      "Live local camera detection. Permission does not prove this is a Quest headset camera: check selected device.",
    );
    const devices = await navigator.mediaDevices.enumerateDevices();
    $("camera").replaceChildren(
      new Option("Default camera", ""),
      ...devices
        .filter((x) => x.kind === "videoinput")
        .map((x) => new Option(x.label || x.deviceId, x.deviceId)),
    );
    $("camera").value = stream.getVideoTracks()[0].getSettings().deviceId || "";
  } catch (e) {
    status(
      `Camera unavailable: ${e.name ?? ""} ${e.message}. Passthrough visibility is not camera pixel access. Native Quest sample is the reliable alternative.`,
    );
  }
};
$("file").onchange = async (e) => {
  stop();
  const f = e.target.files[0];
  if (!f) return;
  objectURL = URL.createObjectURL(f);
  if (f.type.startsWith("video/")) {
    video.src = objectURL;
    video.loop = true;
    await video.play();
    source = video;
    sourceLabel = "LOCAL VIDEO (NOT LIVE QUEST)";
  } else {
    const img = new Image();
    img.src = objectURL;
    await img.decode();
    source = img;
    sourceLabel = "TEST IMAGE (NOT LIVE QUEST)";
  }
  $("source").textContent = sourceLabel;
  running = true;
  status(
    "Local test input: real model inference, not a live headset demonstration.",
  );
  await infer();
};
$("metrics").onclick = () =>
  download(
    new Blob(
      [
        JSON.stringify(
          {
            runtime: "onnxruntime-web WASM CPU",
            headsetVerified: false,
            samples,
          },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    ),
    "yolo-metrics.json",
  );
function download(blob, name) {
  const u = URL.createObjectURL(blob),
    a = document.createElement("a");
  a.href = u;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(u), 5000);
}
$("record").onclick = () => {
  if (recorder?.state === "recording") {
    recorder.stop();
    return;
  }
  if (!canvas.captureStream || !window.MediaRecorder) {
    status("Preview recording unavailable in this browser.");
    return;
  }
  const chunks = [],
    s = canvas.captureStream(20);
  recorder = new MediaRecorder(s);
  recorder.ondataavailable = (e) => chunks.push(e.data);
  recorder.onstop = () => {
    download(
      new Blob(chunks, { type: recorder.mimeType }),
      "yolo-preview.webm",
    );
    s.getTracks().forEach((t) => t.stop());
    $("record").textContent = "Record preview";
  };
  recorder.start();
  $("record").textContent = "Stop recording";
  setTimeout(() => {
    if (recorder.state === "recording") recorder.stop();
  }, 60000);
};
$("xr").onclick = async () => {
  try {
    if (
      !navigator.xr ||
      !(await navigator.xr.isSessionSupported("immersive-ar"))
    )
      throw Error("immersive-ar unavailable");
    if (!source)
      throw Error("Start a readable camera or local test file first");
    xrSession = await navigator.xr.requestSession("immersive-ar", {
      optionalFeatures: ["local-floor"],
    });
    const renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.xr.enabled = true;
    $("xr-root").append(renderer.domElement);
    const scene = new THREE.Scene(),
      camera = new THREE.PerspectiveCamera(),
      texture = new THREE.CanvasTexture(canvas);
    const board = new THREE.Mesh(
      new THREE.PlaneGeometry(1.2, 0.75),
      new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide }),
    );
    board.position.set(0, 0, -1.3);
    camera.add(board);
    scene.add(camera);
    await renderer.xr.setSession(xrSession);
    renderer.setAnimationLoop(() => {
      texture.needsUpdate = true;
      renderer.render(scene, camera);
    });
    xrSession.addEventListener(
      "end",
      () => {
        renderer.setAnimationLoop(null);
        board.geometry.dispose();
        board.material.dispose();
        texture.dispose();
        renderer.dispose();
        renderer.domElement.remove();
      },
      { once: true },
    );
    status(
      "WebXR preview panel active. This is not a world-aligned detection overlay. Camera availability during XR is browser-dependent.",
    );
  } catch (e) {
    if (xrSession) await xrSession.end().catch(() => {});
    status(`WebXR unavailable: ${e.message}`);
  }
};
window.addEventListener("pagehide", stop);
// Read-only diagnostics for classroom automation; no synthetic detection path.
window.yoloDiagnostics = () => ({
  ready: !!session,
  busy,
  running,
  source: sourceLabel,
  boxes,
  samples: samples.slice(-20),
});
