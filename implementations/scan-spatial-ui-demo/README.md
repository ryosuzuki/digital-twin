> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Ryo’s Scan Studio

<!-- youtube-demos:start -->
## Watch demos on YouTube

Click the preview or a video title to play. Videos are Unlisted; original MP4 downloads remain in GitHub Releases.

[](https://youtu.be/y__D9akryNw)

- [▶ 2026-10-08 Spatial UI in a Scanned Room](https://youtu.be/y__D9akryNw)

<!-- youtube-demos:end -->

## Demo preview — October 8, 2026

[](https://youtu.be/y__D9akryNw)

Place and edit text and objects on the real scanned surfaces.

[Watch / download the original demo MP4](https://github.com/ryosuzuki/scan-spatial-ui-demo/releases/download/demo-archive-2026-10-08/spatial-ui-demo.mp4) · [Demo files and provenance](docs/demo/README.md)

Private editable 3D spatial-authoring demo built on Ryo’s actual iPad room scan from 2026-10-08. This is a minimal counterpart to the static scan authoring part of Ziru’s Intelligent Spatial Interface, not a fake video composite.

## Run

```sh
npm ci
npm start
```

Open http://127.0.0.1:8813 in Chrome. The retained project already has dependencies installed. The private delivery ZIP includes the exact original OBJ and JPG; originals remain unchanged in the source archive. No private scan has been published.

## Use

- Drag to orbit, right-drag to pan, wheel to zoom. Inside resets the kitchen view; Overview frames the entire scan.
- Enter text, click Pin text, then click a scanned surface. The anchor and normal come from an actual mesh ray intersection.
- Place object adds a geometric virtual object attached to the clicked surface.
- Select content, edit size, surface rotation or offset. Update selected text applies the text field to the selected text item.
- Export layout downloads JSON. Layout persists in browser localStorage; original geometry is never edited.

## Evidence and boundaries

The browser test places two text items and an object using actual UI clicks, rotates the camera, checks anchor invariance, exports the layout, reloads and verifies persistence. See the dated output verification.json and demo video. There is no live tracking, physical registration, automatic object recognition, or recorded RGB video replay. The mesh’s scan holes are visible; this prototype does not invent missing room content. The independently captured Polycam RoomPlan is deliberately not overlaid without registration. No Record3D recording was present.

Mesh: 533,500 triangles, original 10,240 × 10,240 texture. Source and hashes are in source-provenance.json. The viewer can resample the original texture to the GPU’s supported size automatically.
