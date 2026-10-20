> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Spatial Memory — private source backup

<!-- youtube-demos:start -->
## Watch demos on YouTube

Click the preview or a video title to play. Videos are Unlisted; original MP4 downloads remain in GitHub Releases.

[](https://youtu.be/ZYbokiDqQd0)

- [▶ 2026-10-08 Quest Object Memory](https://youtu.be/ZYbokiDqQd0)
- [▶ 2026-10-08 Room Object Memory v2](https://youtu.be/Pfv_F02ohC4)
- [▶ 2026-10-08 Room Memory Streaming](https://youtu.be/BhugEsihb9Q)
- [▶ 2026-10-08 Room Memory Fixed Tracking](https://youtu.be/NPMkpYoSQh8)

<!-- youtube-demos:end -->

## Demo preview — October 8, 2026

[](https://youtu.be/ZYbokiDqQd0)

Fixed cutaway room overview with recorded observations and a depth-backed bottle track.

[Watch the public recording on YouTube](https://youtu.be/NPMkpYoSQh8). Original private asset archives are not included in this source snapshot.

Snapshot of the October 8, 2026 prototypes. Original working projects remain under `/path/to/local-assets`.

- `spatial-object-memory`: initial manual scan-annotation prototype. See its README for setup.
- `quest-spatial-studio`: existing tracked recorder/editor source plus automatic object-memory and room-first additions. See `editor/docs/object-memory.md` and `editor/docs/object-room.md` for setup, processing, verification and limitations.
- Original Quest upstream: https://github.com/ryosuzuki/quest-spatial-studio (public; unchanged by this backup).

## Data and videos

Large private captures, scan assets, derived detections and rendered videos are not in Git. They remain in the original Storage paths referenced by the docs and scripts. In particular:
- Scan assets: `/path/to/local-assets`
- Derived private data: `/path/to/local-assets`
- Videos: `/path/to/local-assets`, including `room-demo/`

This is a source backup, not an independent backup of those media assets. Restore source to the original layout or adjust the local asset paths. Existing verification is documented in the project docs; this backup additionally checks source byte identity and JS/Python syntax. Unrelated untracked showcase work is excluded.

## Fixed overview and moving bottle revision

See [fixed-overview tracking](quest-spatial-studio/editor/docs/object-tracked.md) for the cutaway room view, one depth-backed moving bottle track, deterministic replay and demo reproduction. The amber proxy moves; the textured scan remains static.
