# Verification — 2026-10-20

Integration target: origin/main. Completion owner: current classroom implementation task.
Authoritative paths: `implementations/quest-ondevice-yolo/` and the root README entry.
Existing imported implementations remain unchanged.

## Passed

- Web: preprocessing, box coordinate scale, class-aware NMS and wrong-output-contract tests: **4 passed**.
- Production Vite build loaded from a static HTTP localhost server in a dedicated headless Chromium test, not only the dev server.
- Actual YOLO ONNX inference on the public Ultralytics bus test image: **1 bus + 3 persons**. Four initial samples ~203–225ms on desktop CPU/WASM. This is not Quest performance.
- Actual browser checks: model loading, local image inference, no page errors, Stop, missing-camera message and unsupported-WebXR message.
- npm dependency audit: **0 reported vulnerabilities** at verification time.
- Root `python3 scripts/verify-snapshots.py`: **177 preserved source hashes passed**.
- Unity **6000.4.5f1**, MRUK **85.0.0**, Unity Inference Engine **2.6.1**, OpenXR **1.16.1**: C# compiled; classroom scene generated; Android ARM64/IL2CPP development APK built successfully.
- Built source hashes match the published QuestYolo.cs / ClassroomBuild.cs bytes. Source bootstrap was independently rerun into a fresh directory; custom source, dependency overrides and package lock match.
- APK manifest readback: `org.openclaw.classroom.yolo`, version `0.1.1`, HEADSET_CAMERA permission present.
- Browser demo video: actual captured UI, 1280×900, 13.24 seconds, 331 decoded frames; input is labeled TEST IMAGE (NOT LIVE QUEST). First/middle/end frames visually inspected.

## Quest 3 actual acceptance — native 0.1.1/code2

- Actual headset camera → YOLO → on-headset GPUCompute → camera-preview bounding boxes verified on physical Quest 3 / Android14. No external inference server and no ADB reverse mapping.
- In-place install and two cold launches succeeded. **103** inference samples: median **275.27ms**, minimum **258.65ms**, maximum **623.45ms** (including startup). Detection counts varied 2–5. This is inference turnaround, NOT XR rendering FPS or a long-duration thermal benchmark.
- After force-stopping only this sample, a fresh process produced **18** additional headset-camera inference samples. Existing apps/data/calibration were preserved.
- Runtime observation caught opaque green-filled detections in0.1.0. Version0.1.1 replaces the Outline effect with four thin border images and increases text size. Actual first/middle/end frames show correctly outlined chairs. Occasional low-confidence monitor predictions remain; this is not a detection-accuracy benchmark.
- Installed base APK SHA256 equals the built/retained APK: `bdf08b5d5f8a92d146e54ae7c6fbc07f3025ef3ede7ce3fc902a2494441d0b2d`.
- Actual compositor recording: **4128×2208, 14.834889seconds,409 decoded frames**. First/middle/end personally inspected. Preview is a left-eye crop of that recording, not a rendered/simulated replacement.
- Finite proximity windows restored the prior **enabled=true / override=DISABLED** state; final STANDBY was freshly verified. No recorder was left running and no tracking/boundary settings were disabled.
- Correction to initial availability report: default-port ADB inventories were empty, but the headset was on an existing dedicated ADB endpoint. The earlier “Quest unavailable” conclusion was incomplete; the existing authorized route was reused without resetting it or changing keys.

## Still unverified

- **WebXR on the headset**, browser camera availability/retention during immersive mode and browser performance are not tested by the native acceptance above.
- Physical controller A pause/resume, real head-motion comfort, calibrated world-space alignment, long-duration heat/battery behavior and USB physical-unplug operation remain unverified.
- Native/WebXR views are camera-preview panels, not calibrated world-space augmentation. No measured 3D positions or persistent anchors are produced.

## Evidence and recovery

See `artifacts.json` for exact sizes, SHA256 and retained artifact location. The video and source ZIP deliverables match these artifacts. Direct APK attachment was rejected by the chat media-type restriction; the APK is retained locally. Runtime media and SDK/model binaries are not published in Git.

Source is preserved on main; generated materialized Unity project and built static site are retained as ZIPs. Canonical repository is synchronized only after remote readback. The isolated classroom worktree is kept as a clean reproducible working copy; no unrelated worktrees or device sessions are retired.
