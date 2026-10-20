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
- APK manifest readback: `org.openclaw.classroom.yolo`, latest version `0.3.0/code4`, HEADSET_CAMERA and USE_SCENE permissions present.
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

## Quest 3 first-person passthrough acceptance — native 0.2.0/code3

- Replaces the native preview panel with compositor passthrough plus world-space lines/text only. Uses camera exposure-time pose and calibrated `ViewportPointToRay`; environment depth at the detection center supplies a surface point. The four corners intersect a camera-parallel plane through that point. No invented fixed distance and no camera-feed surface.
- Permission/scene manifest readback and in-place install succeeded. C# compile and Android ARM64/IL2CPP build succeeded. Built source SHA256 matches the published two C# files.
- Actual cold launch produced **122** new-process inference samples on GPUCompute; all report positional tracking true. Median **271.61ms**. **121/122** samples produced **3–5** depth-backed annotations; startup had one zero-hit sample. This is neither an accuracy benchmark nor XR rendering FPS.
- Actual stereo compositor recording: **4128×2208, 14.954811 seconds, 415 decoded frames**. First/middle/end inspected. Person/chair/laptop labels and outlines appear directly on the full first-person room view; no preview panel is present. Preview deliverable is the left-eye crop, resized, not a simulation.
- Missing/expired depth, lost positional tracking, pause and lost app focus suppress annotations; annotations expire after0.85s without an update. Physical A-button operation and moving-head alignment are not accepted by this stationary-device recording.
- Finite proximity override restored **enabled=true / override=DISABLED**. No tracking/boundary reset or disable was used. No unrelated application was uninstalled or force-stopped. No runtime inference server is used.
- Initial launcher-style CLI request did not start this sample and left the previous app/OS room-position dialog visible; that recording is not feature acceptance. A serial-bound direct component cold launch succeeded and the second recording/logs above belong to this sample's new PID. For automated launch, use `am start -W -n org.openclaw.classroom.yolo/com.unity3d.player.appui.AppUIGameActivity`, without adding launcher-category flags.
- APK SHA256: `61168a4cf9946c6bd8794949e3fa75912f1b2b19fbe164673c02158ee3140402`.

## Quest 3 session-anchor label acceptance — native 0.3.0/code4

- Unity C# compilation and Android ARM64/IL2CPP build passed; in-place installation of version 0.3.0/code4 passed. HEADSET_CAMERA, USE_SCENE, and USE_ANCHOR_API permissions were granted.
- Actual second cold launch, new PID10006: **57 real headset-camera inference samples**, median pipeline turnaround **271.12ms** on built-in GPUCompute. Ready native anchors progressed from 0 to 4,5,6,7.
- **7 create requests, 7 localized native anchors with UUIDs, 167 association events, 206 pose-log events, zero logged creation failures.** Counts describe this finite run, not object-detection accuracy or a general tracking benchmark.
- Developer launch option froze observations after the real-observation interval. Exactly one `observations_paused` event identified the developer timer. Final pose logs retained the same **7 native UUIDs**, `visible=True`, and fixed `inference_frame=57`, with last-seen ages 17–20.51s. This verifies session label retention after inference stopped; it is not a physical A-button test.
- Anchor roots are created once at measured detection-center depth hits. Reassociated detections update confidence/last-seen metadata, not root position. Only child text rotates. Native `Localized` and `IsTracked` gate visibility; pending/failed anchors are neither displayed nor counted ready.
- Labels are session-local. Same-class proximity association is not general moving-object identity tracking, and no anchor is saved or loaded across relaunches.
- Headset was stationary. The run does **not** quantitatively verify moving-head alignment or physically moved-object tracking. Retention logs alone do not establish either.
- First launch/take showed the OS Finding position in room dialog, lost app focus, and produced zero inferences/anchors. It is explicitly excluded from feature acceptance. The second cold-launch logs above are the accepted run.
- Actual 0.3.0 preview: **22.020s, 768×822, 738 decoded frames**. First/middle/last frames were visually inspected. People move in the room while labels remain pinned to initial locations; that is not moving-object tracking. Overlapping/duplicate class labels are a known limitation of class/proximity association.
- Maximum logged stationary anchor-coordinate delta across the 206 pose samples was **0.000361m**. This is numerical stability in a stationary tracking coordinate system, not measured physical alignment accuracy.
- Built/published source SHA256: QuestYolo.cs `02a59da3e57c1a096bdaab98705b7e5ec010ea8f12d0b630012435dea28c7a8a`; ClassroomBuild.cs `ed3876cc0a52b3e832f545ad14b1f4d62cd87285ddef390457bea0e9a4d93090`.
- APK SHA256: `a107fddf910e40ae739c7a5040e6550608d9ac92a9ddc187685c9119d200d060`. Raw/preview video and runtime/summary/analysis evidence digests are in `artifacts.json`; their media/log bytes remain outside Git.
- Version 0.2.0 planar-outline timings and media above are historical, not measurements of 0.3.0. Native 0.3.0 uses label-only native anchors, not per-inference planar box recreation.

## Still unverified

- **WebXR on the headset**, browser camera availability/retention during immersive mode and browser performance are not tested by the native acceptance above.
- Physical controller A pause/resume, real head-motion comfort, measured moving-head alignment accuracy, long-duration heat/battery behavior and USB physical-unplug operation remain unverified.
- WebXR remains a camera-preview panel. Historical native0.2.0 used an approximate corner plane; native0.3.0 instead pins label-only content at a native session anchor. Neither recovers exact object geometry or saves anchors across relaunches. Center rays can hit background; model errors and camera/depth timing can pin the wrong surface.

## Evidence and recovery

See `artifacts.json` for exact sizes, SHA256 and retained artifact location. The video and source ZIP deliverables match these artifacts. Direct APK attachment was rejected by the chat media-type restriction; the APK is retained locally. Runtime media and SDK/model binaries are not published in Git.

Source is preserved on main; generated materialized Unity project and built static site are retained as ZIPs. Canonical repository is synchronized only after remote readback. The isolated classroom worktree is kept as a clean reproducible working copy; no unrelated worktrees or device sessions are retired.
