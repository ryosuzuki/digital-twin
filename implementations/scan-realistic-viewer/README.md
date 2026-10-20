> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Scan realistic viewer

<!-- youtube-demos:start -->
## Watch demos on YouTube

Click the preview or a video title to play. Videos are Unlisted; original MP4 downloads remain in GitHub Releases.

[](https://youtu.be/D2AYDvZM-WI)

- [▶ 2026-10-08 Real Scanned Room Walkthrough](https://youtu.be/D2AYDvZM-WI)

<!-- youtube-demos:end -->

## Demo preview — October 8, 2026

[](https://youtu.be/D2AYDvZM-WI)

Walkthrough of the original Scaniverse Gaussian room capture.

[Watch the public recording on YouTube](https://youtu.be/D2AYDvZM-WI). Original private asset archives are not included in this source snapshot.

Private local viewer of Ryo's actual Scaniverse capture, not a generated room.

## Open

```
npm ci
npm start
```

Then open http://127.0.0.1:8816 . Drag to orbit, scroll to dolly, right drag to pan. Reset restores the room viewpoint. Start walkthrough runs a scripted camera path through the real 3D Gaussian representation.

The included `public/room.spz` is copied from the original preserved scan; it is excluded from Git. No upload is performed. A distributable offline build is produced by `npm run build`. Serve `dist` with `python3 -m http.server 8816 --bind 127.0.0.1 --directory dist`.

## Source and limits

Original: `/path/to/local-assets Support/scans/user-room/model.spz`

SPZ v3, 301,106 Gaussian points, SH degree 3. Rendered with Spark 2.3.1 / Three.js. This renders the existing trained splat; it is not an offline retraining result or measured quality improvement. Gaps, blur, floaters and sparse ceiling/wall regions remain visible. No physical tracking, Quest-device validation, or automatic RoomPlan alignment is claimed. Static scene, not live digital-twin synchronization.

Video is an actual Chromium WebGL recording of the viewer using a scripted camera trajectory. No generated imagery. Verification checks load, absence of page errors, orbit input, reset and representative rendered screenshots.
