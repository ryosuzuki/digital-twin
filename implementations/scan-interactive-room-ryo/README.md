> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Interactive scan twin

<!-- youtube-demos:start -->
## Watch demos on YouTube

Click the preview or a video title to play. Videos are Unlisted; original MP4 downloads remain in GitHub Releases.

[](https://youtu.be/t_sJEuC5TMw)

- [▶ 2026-10-08 Scanned Room Walk Grab and Animate](https://youtu.be/t_sJEuC5TMw)

<!-- youtube-demos:end -->

## Demo preview — October 8, 2026

[](https://youtu.be/t_sJEuC5TMw)

Navigate the room, manipulate props, record and replay their motion.

[Watch / download the original demo MP4](https://github.com/ryosuzuki/scan-interactive-room-ryo/releases/download/demo-archive-2026-10-08/interactive-room-walk-grab-animate.mp4) · [Demo files and provenance](docs/demo/README.md)

Private desktop WebGL prototype using Ryo's actual 2026-10-08 iPad 3d Scanner App room scan (533,500 triangles and original 10K texture).

## Run

```
node server.mjs
```

Open http://127.0.0.1:8827 . The server binds only to localhost. The delivery ZIP includes Three.js and the scan in `scan/`, so no package download is necessary. In the working checkout the original archived scan is read-only at `/path/to/local-assets`. No public upload.

## Use

- WASD: fixed-height walking; Shift: faster; right-drag or arrows: look. A waist-height forward ray prevents many wall crossings, but is not a complete capsule/physics collision solver.
- Click a colored prop: grab. Mouse: carry; wheel: depth; Q/R: rotate; click: release. E also toggles grab/release.
- Record object motion: start recording a prop (held / under pointer / most recently added). Pick it up and move it, then stop recording. Replay loops the actual captured positions and rotations.
- Start walking character: animate a stylized procedural figure on an authored loop in the room.
- Save scene + motion: download editable JSON with source identity, object transforms and timestamped motion samples.

## Boundaries

The room is an unchanged textured scan, including holes and captured texture limitations. Colored movable props and the walking character are added geometric assets; existing scanned furniture has not been segmented or rigged. Character motion is procedural, not motion capture or path planning. No claim of Quest controller testing, full physics, metric registration to a live room, or scan cleanup. This implements walking, grabbing, rotating, motion recording and replay within the real scanned room, rather than a static viewer.

## Verification

`node record.mjs` exercises browser mouse/keyboard controls, verifies camera translation, pickup/release, rotation, motion capture/replay and character activation, and captures video plus screenshots in the dated output directory. `verification.json` contains observed states and assertions.
