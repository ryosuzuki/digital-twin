> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Living Scan — Interactive Digital Twin

<!-- youtube-demos:start -->
## Watch demos on YouTube

Click the preview or a video title to play. Videos are Unlisted; original MP4 downloads remain in GitHub Releases.

[](https://youtu.be/GS6aEhNLz3U)

- [▶ 2026-10-08 Interactive Scanned Digital Twin](https://youtu.be/GS6aEhNLz3U)

<!-- youtube-demos:end -->

## Demo preview — October 8, 2026

[](https://youtu.be/GS6aEhNLz3U)

First-person room navigation and manipulation of added virtual props.

[Watch / download the original demo MP4](https://github.com/ryosuzuki/scan-interactive-twin/releases/download/demo-archive-2026-10-08/interactive-twin.mp4) · [Demo files and provenance](docs/demo/README.md)

Local desktop prototype using Ryo's actual iPad 3d Scanner App room capture from 2026-10-08. The room is the original textured geometry converted to GLB, not a generated scene or enhanced reconstruction.

## Run

Node.js required. Three.js is bundled in the distributable; no external web requests or npm install are needed.

1. Unzip the complete folder.
2. In that folder run `node server.mjs`.
3. Open http://127.0.0.1:8818 in Chrome.

Alternatively, source checkout: `npm install` then `npm start`.

## Interaction

- **W / A / S / D:** walk forward / left / back / right.
- **Right mouse drag:** look around.
- **Click colored prop:** grab; move mouse to move it in 3D.
- **Q / E while holding:** rotate left / right.
- **Mouse wheel while holding:** change distance from camera.
- **Click again:** release in place.
- **Add object ahead:** create another movable prop.
- **Animate selected:** animate the most recently grabbed or added prop.
- **Stop animation:** stop all props.
- **Reset view:** return camera to the initial view (preserves placed props).

## What this demonstrates

Actual scanned room with first-person navigation, raycast selection, 3D repositioning, rotation, release and live object animation. Demo recording uses browser mouse/keyboard events, not a pre-rendered 3D mockup. Props are intentionally colored and distinguishable from captured furniture.

## Limits

Desktop mouse/keyboard only; Quest controllers/WebXR not implemented or tested in this version. The room mesh remains static: existing scanned furniture has not been segmented or animated. No physics, gravity or wall collision; users can walk through mesh surfaces. Placement is not a measured physical alignment experiment. Scan holes and baked-lighting artifacts remain. This is not Gaussian Splat rendering or newly improved scan reconstruction. The included model retains the full 10K texture (GPU may internally rescale to its supported limit).

## Provenance

`assets/room.glb`: 68,367,164 bytes; SHA256 `769d6cfdcba358445771c09b8ec1cbd0efe61736a819083d3cd5447fbef8dca3`. Derived via Blender GLB conversion from original `textured_output.obj` of capture `2026_10_08_12_41_21`. 533,450 imported triangles (50 fewer than source OBJ; source unchanged). Private room scan: no upload or publication performed.

Three.js 0.180.0 (MIT), copyright its authors. Included license retained in node_modules/three/LICENSE.
