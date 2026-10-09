> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Spatial Object Memory

Source for the **fixed-overview room-memory / moving-bottle prototype** shown in the October 8, 2026 demo. This is the object-memory prototype, not the avatar or live-pose demo.

**Personal recordings, room scans, detections, and depth data are not published.** A fully synthetic fixture is generated locally so you can run and inspect the same replay, marker-motion and memory UI without those private inputs. The synthetic fixture is illustrative, not evidence of tracking accuracy.

## Run

Requires Node.js 20.11+ and a modern WebGL browser.

```sh
npm ci
npm run fixture
npm start
```

Open http://127.0.0.1:8833 . Scrub the timeline to 64–68 seconds to see the amber bottle marker move. It retains the last observation after the track ends. Select a label and click “When was this seen?” for timestamp lookup. The fixed overview remains unchanged. Green labels accumulate by class/proximity, not verified object identity.

The server binds only to localhost. Three.js is installed locally; replay does not need a cloud API.

## Code map

- `object-tracked.html`: fixed overview, evidence panel and timeline UI.
- `src/object-tracked.mjs`: temporal gating, trajectory interpolation, fixed camera, last-location memory and rewind reset.
- `src/object-stream-base.mjs`: Three.js room rendering, source-frame replay, approximate room registration and evidence selection.
- `src/math.mjs`: calibrated projection, pose helpers and time-to-frame lookup.
- `scripts/derive-bottle-world.py`: offline derivation of the real demo's reviewed green-bottle surface trajectory from masks, recorded depth, camera intrinsics/pose and scan registration. Requires NumPy and OpenCV. No private input data is bundled.
- `scripts/make-fixture.mjs`: synthetic room mesh, synthetic frames, detections and trajectory; clearly separate from measured results.
- `scripts/check-demo.mjs`: browser checks for time gating, >1m marker motion, last-position retention, rewind and fixed camera.

## Bring your own capture

The historical folder name `sessions/quest-215403` is only the default loader path; replace its generated fixture with your own data.

1. Put a session manifest and image frames under `sessions/quest-215403/`. `session.json` contains `duration`, calibrated `intrinsics` (`fx,fy,cx,cy,width,height`) and time-ordered `frames` (`t,image,position,quaternion` xyzw).
2. Replace `scan/textured_output.obj` and the texture. The public loader expects `textured_output.svg`; for a real JPEG change that texture URL in `src/object-stream-base.mjs` to your own filename.
3. Supply `private/object-room-alignment.json`: 3×3 `rotation` and 3-vector `translation`, mapping capture-world into scan coordinates.
4. Supply `private/object-memory-spatial.json` with `observations`: `id,label,frame,t,confidence,depthMeters,position,box` (xyxy pixels in the historical 1280×1280 capture). The existing base UI expects observations for refrigerator, couch, potted plant, dining table and laptop; customize its `labels` list for other scenes.
5. Optional `private/object-room-refinements.json` maps observation IDs to refined `position` and optional `sourcePixel`; use `{}` without refinements.
6. Supply `private/bottle-world-track.json` with sorted `samples` (`t,frame,scanPosition,position,box`) and `endpointDisplacementMeters`. Derivation script usage:

```sh
python3 -m pip install numpy opencv-python
python3 scripts/derive-bottle-world.py --audit /path/to/local/audit
```

The derivation script expects `audit/bottle-track.json` (`frames`: `frameIndex,mask,timeSeconds,centroid,bbox` xywh), corresponding masks, and `registered-depth/000000.bin` (little-endian uint16 millimeters, 320×320). These are sensor-specific conventions; calibrate/modify them for your capture. It rejects background-depth samples and transforms valid measured points; it does not invent a fallback range.

Generated fixtures and replacement captures are gitignored. Running `npm run fixture` overwrites those local fixture paths; do not run it over your sole copy of real data.

## What the original video demonstrated

Recorded Quest RGB + camera poses + depth, a textured room scan with approximate registration, cached class detections, and one manually reviewed moving-green-bottle association interval. Its amber marker used 31 valid depth observations, with two background-depth frames rejected. The mesh remained static while the marker moved and its last observation persisted.

**Not implemented:** live inference, general re-identification, recovered bottle rotation/6DoF, moving the scan geometry, or a guarantee of an object's current location. Timestamp answers are record lookup, not an LLM. Approximate alignment and depth/RGB timing introduce uncertainty. Public synthetic trajectories are not the measured private trajectory.

## Verification

With the server running and Google Chrome installed:

```sh
npm test
```

The test uses Playwright with installed Chrome (`BROWSER_CHANNEL` may override it). For a bundled Chromium installation, adapt the launch option and run `npx playwright install chromium`.

## Origin

Extracted from the local Quest Spatial Studio object-memory extension. New clean public history contains source and synthetic-fixture generation only; the original private backup remains private. Three.js and Playwright retain their upstream licenses. No blanket license is asserted for unrelated upstream projects or private assets.
