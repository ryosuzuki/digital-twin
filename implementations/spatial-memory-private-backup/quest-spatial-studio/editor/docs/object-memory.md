# Quest Object Memory prototype

Uses the real `20261002_215403` take in the local private session, including RGB, calibrated camera pose, registered depth and the room mesh captured in the same coordinate system. The independent October 8 iPad/Polycam scan is **not** registered or used. No source recording was uploaded or committed by this task.

## Launch

From editor: `PORT=8831 node scripts/serve-living-scenarios.mjs`, then open `http://127.0.0.1:8831/object-memory.html`.

## Pipeline

1. `scripts/detect-object-memory.py`: ultralytics YOLO11n pretrained COCO, CPU inference locally on every tenth recorded frame (92 frames); 334 detections at confidence >= .38 excluding people. Dependencies were installed in `/tmp/openclaw/quest-object-venv` and weights downloaded to `/tmp/openclaw/quest-object-yolo/yolo11n.pt`; these are disposable and must be reinstalled if removed. No private media is sent to the model provider.
2. `scripts/spatialize-object-memory.py`: sample 5x5 registered-depth neighborhood at each 2D box center; median valid axial depth between .2 and 8 meters, at least five valid pixels. Backproject using intrinsics and transform via the frame's recorded camera quaternion/translation. 331 observations have valid samples. Outputs are private/object-memory-detections.json and private/object-memory-spatial.json.
3. `src/object-memory.mjs`: show actual synchronized RGB, detected boxes only on the corresponding sampled source frame; selected approximate world point is reprojected across camera motion. Room overview, clickable detections, class history, strongest-evidence search, last class observation, and persistent browser-local per-observation notes.
4. `scripts/render-object-memory.mjs`: actual browser interaction verification and 34-second scripted capture of implemented UI. Video frames retain a source frame/time map; the resulting video is not an unedited recording and no live headset inference is claimed.

## Verification and boundaries

Browser checks: selection by clicking detected laptop, note save/reload restoration, note-text search, finite 3D observations, no JS errors. Visual inspections and full MP4 decode recorded in the dated output receipt.

Detector outputs can be wrong (e.g., wall art classified as bottle). Depth is sampled at the box center, which can land on background. This produces approximate surface positions, not accurate object centroids/3D boxes. No independent physical ground-truth accuracy check. No persistent instance matching, object movement interpretation, hidden contents inference, Gemini/LLM reasoning, LEDGER code, live Quest deployment, or OpenClaw tool integration. Last observation is by category, not identity. This is an XR-Objects/LEDGER-inspired recorded-data prototype, not their full replication.

The original concurrent `showcase` files and source recordings are unchanged. Work is limited to new object-memory-specific files.
