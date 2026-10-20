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
- APK manifest readback: `org.openclaw.classroom.yolo`, version `0.1.0`, HEADSET_CAMERA permission present.
- Browser demo video: actual captured UI, 1280×900, 13.24 seconds, 331 decoded frames; input is labeled TEST IMAGE (NOT LIVE QUEST). First/middle/end frames visually inspected.

## Not verified / concrete blocker

- ADB inventory was empty on both configured home and lab build hosts. No Quest was installed, launched, stopped or recorded by this task. Existing production apps were not changed.
- Live Quest camera frames, WebXR immersive rendering, camera retention while in WebXR, native GPU/CPU inference latency, thermal behavior, controller A pause/resume and physical-world alignment remain **unverified on hardware**.
- Native camera inference is compiled code, not a completed on-headset acceptance test. The downloadable APK must not be presented as hardware-verified.
- There is no native headset demo video. The browser recording is not a substitute for one.
- WebXR is a camera-preview panel, not calibrated world-space augmentation. No measured 3D positions or anchors are produced.

## Evidence and recovery

See `artifacts.json` for exact sizes, SHA256 and retained artifact location. The DM deliverables are the same files. Runtime media and SDK/model binaries are not published in Git.

Source is preserved on main; generated materialized Unity project and built static site are retained as ZIPs. Canonical repository is synchronized only after remote readback. The isolated classroom worktree is kept as a clean reproducible working copy; no unrelated worktrees or device sessions are retired.
