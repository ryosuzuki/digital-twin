# digital-twin — implementation catalog

A public source-classification monorepo that organizes pinned source snapshots without modifying or deleting their original repositories. Each implementation has its own directory. These are not integrated into a shared application or made API-compatible.

## Where to start

- [spatial-home-lab](implementations/spatial-home-lab/README.md) — **Our recent Home and Lab digital twins**, kept separate from the older scan snapshots: runnable local catalog, independent per-venue gateways, availability checks, and synthetic upstreams for a fresh clone. Connect your existing private Spatial services; room assets and camera configuration are not published.

- [quest-ondevice-yolo](implementations/quest-ondevice-yolo/README.md) — On-device YOLO for Quest 3/3S: WebXR preview and native Unity first-person passthrough annotations. No external GPU required. The [illustrated tutorial](implementations/quest-ondevice-yolo/TUTORIAL.md) explains center raycasting, spatial placement, and detection versus tracking. See its VERIFICATION.md for accepted device behavior and limitations.
- [scan-realistic-viewer](implementations/scan-realistic-viewer/README.md) — View an actual Gaussian scan, without dynamic behavior. See [RUN.md](implementations/scan-realistic-viewer/RUN.md).
- [scan-spatial-ui-demo](implementations/scan-spatial-ui-demo/README.md) — Spatial UI inside a real scan. See [RUN.md](implementations/scan-spatial-ui-demo/RUN.md).
- [scan-interactive-twin](implementations/scan-interactive-twin/README.md) — Interaction and manipulation inside a room. See [RUN.md](implementations/scan-interactive-twin/RUN.md).
- [scan-interactive-room-ryo](implementations/scan-interactive-room-ryo/README.md) — Walk through a textured room mesh, grab small objects, and record actions. See [RUN.md](implementations/scan-interactive-room-ryo/RUN.md).
- [scan-quality-experiment](implementations/scan-quality-experiment/README.md) — Scan-quality comparison experiments. See [RUN.md](implementations/scan-quality-experiment/RUN.md).
- [spatial-object-memory](implementations/spatial-object-memory/README.md) — Object memory from a fixed overhead view; bottle movement and synthetic fixtures support replay. See [RUN.md](implementations/spatial-object-memory/RUN.md).
- [spatial-memory-private-backup](implementations/spatial-memory-private-backup/README.md) — Historical manual, Quest detection, room-first, stream, and tracked variants. See [RUN.md](implementations/spatial-memory-private-backup/RUN.md).

## Implementation boundaries

The imported snapshots are primarily desktop WebGL / Web-server prototypes. The added quest-ondevice-yolo implementation has separate Web and Unity variants; it does not imply the imported projects were ported to Unity or Quest. Each README records its original approach, run commands, and verification scope. Model inference and 3D generation algorithms belong to [3d-generation](https://github.com/ryosuzuki/3d-generation); the tracking platform belongs to [image-tracking](https://github.com/ryosuzuki/image-tracking). Integrated avatar-and-room demos retain their practical application boundaries despite some source duplication.

Imported-snapshot verification covers source identity, JS/Python syntax, and restoration information. Original demo videos remain linked from original READMEs. Snapshot classification did not run new device tests or AI calls. Additional implementations document their own verification separately.

## Reproducibility

`source-index.json` and each `CATEGORY-SNAPSHOT.json` record source commits, Git blobs, SHA-256 digests, and public-source checks. Run `python3 scripts/verify-snapshots.py` to verify copied source identity. Supply your own assets; see ASSETS.md.

Integration target: main-integrated. Completion owner: category consolidation worker. Authoritative paths: files added to this repository. Original repository worktrees remain untouched.

## Recordings and original assets

- [quest-spatial-studio](https://github.com/ryosuzuki/quest-spatial-studio): Quest capture, camera pose, and depth acquisition. This is a separate large recording project; this category preserves the relevant private-backup snapshot.
- [scan-digital-twin-archive](https://github.com/ryosuzuki/scan-digital-twin-archive): Private archive of original scans, videos, and restoration ZIPs. Large archives are not duplicated here.

## Authentication

API features use environment variables `OPENAI_API_KEY` (OpenAI) or `TYPESAFE_API_KEY` (formerly Jev). Personal authentication routes are excluded from public source. Personal scans are not published.
