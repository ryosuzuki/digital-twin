# Fixed-overview object memory with one moving target

Owner: AI agent 4 / fixed_overview_tracking, 2026-10-08. Integration target: private `ryosuzuki/spatial-memory-private-backup` `origin/main`. Existing public upstream is not modified by publication.

## Run and reproduce

From the canonical editor at `/path/to/local-assets`:

1. Retain the private `sessions/quest-215403`, `private/object-memory-spatial.json`, room alignment/refinements, and textured scan assets described in `object-room.md`.
2. Derive the moving track with Python (numpy and OpenCV):
   `python scripts/derive-bottle-world.py --audit /path/to/local-assets`
3. `node scripts/serve-object-room.mjs` and open `http://127.0.0.1:8832/object-tracked.html`.
4. `node scripts/render-object-tracked.mjs --check` checks the fixed transform, temporal gating, motion, hold-last and deterministic rewind. Omit `--check` to export the demo. `OUT` overrides the output directory.

Output directory: `/path/to/local-assets`. MP4: `room-memory-fixed-tracking.mp4`; checks, verification/frame-time map and visual screenshots are beside it. Private media/derived observations remain in Storage, not Git.

## Implemented behavior and evidence

- Fixed oblique full-room camera. Camera transform is asserted unchanged at every exported frame, including observation selection. Textured scan is clipped above 1.45 m for a dollhouse/cutaway; scan geometry remains static.
- Cached class detections accumulate while video plays. Green class/proximity bins are NOT verified instances.
- The bottle visible being picked up, carried and lowered at 63.78–67.60 s uses an existing reviewed HSV green-region track. A 3D surface point is derived from the masked recorded depth (25th percentile, valid arm's-reach range 0.15–0.95 m), calibrated intrinsics and recorded sensor pose. The prior 0.75 m authored range is NOT used.
- 31 valid samples, two rejected frames (656 and 659) for insufficient foreground depth. Display interpolates between accepted points, including those short gaps. The estimated first-to-last displacement is 1.465 m, not independent ground-truth accuracy. Amber marker, box and trail use one fixed track ID; after the interval, the last observation persists.
- Same actual Quest capture `20261002_215403`; October 8 scan has approximate ICP registration. No live inference, general re-identification, recovered object rotation/6DoF, or motion of the textured mesh is claimed. The tracked point is the green surface, not the bottle center. RGB approximately 9.6 Hz, depth approximately 5 Hz; residual jitter and asynchronous-depth errors remain.
- Record lookup answers from timestamps; not an LLM or external knowledge query. Source footage motion and representative demo frames are visually inspected separately from numerical checks.

## Exact publication allowlist

`editor/object-tracked.html`, `editor/src/object-tracked.mjs`, `editor/scripts/derive-bottle-world.py`, `editor/scripts/render-object-tracked.mjs`, `editor/docs/object-tracked.md`, plus backup-root README link. Other source files are reused unchanged. Prior object-stream/demo and unrelated showcase changes are preserved.

Scoped validation: Node syntax for the two modules; Python compile; browser behavioral checks; exact source-copy SHA-256 equality. Private assets are not present in the backup checkout, so end-to-end browser validation runs in the canonical project. Remote readback validates exact source blobs after push. No temporary branch or worktree is created; canonical private backup stays on main.

Validation results: existing 12 Node tests and 13 Python tests pass. Browser checks pass with zero page errors. Final export is 420 frames at 12 fps (35 seconds); camera invariance is asserted on all 420. Remote integration is main-integrated after exact-blob readback; media verification receipt is stored outside Git in the dated workspace artifacts.
