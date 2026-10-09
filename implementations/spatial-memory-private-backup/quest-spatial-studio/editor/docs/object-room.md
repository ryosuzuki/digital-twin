# Room-first Object Memory

Follow-up to `object-memory.md`, requested October 8: the 3D room must be the main interface, using today's high-detail scan and the real Quest capture.

## Launch

`node scripts/serve-object-room.mjs` in editor. Open http://127.0.0.1:8832/object-room.html . Uses existing source assets in `/path/to/local-assets` without copying or changing them. Source scan is 3d Scanner App capture `2026_10_08_12_41_21`, textured OBJ and texture. This is a textured mesh, **not Gaussian splatting**.

## Registration

`scripts/align-object-room.py` performs 48 yaw initializations and trimmed point-to-point rigid ICP from the first Quest GLOBAL_MESH to the October 8 scan, retaining metric scale 1. The resulting private/object-room-alignment.json transforms all displayed depth-based observations consistently. Its rotation is approximately 162 degrees about up; translation approximately [1.474,1.242,-1.062] m. Trimmed fit distance 0.0567 m; median surface-nearest distance 0.0626 m and 90th percentile 0.1438 m. These are fit residuals, **not held-out or independently measured accuracy**. Registration was visually inspected at fridge, couch and plant. Absolute physical error remains unmeasured.

## Improved object points

The original bounding-box-center depth can fall on an occluder, as happened for the couch with the foreground coffee table. `scripts/refine-room-objects.py` applies local YOLO11n-seg on the five primary evidence frames and matches segmentation boxes by IoU. It erodes masks, accepts valid registered-depth pixels, and selects the surface point nearest the coordinatewise 3D median. Refined positions for refrigerator, couch, potted plant, dining table and laptop are retained in private/object-room-refinements.json, without overwriting the earlier raw observations. Other historical observations still use earlier box-center depths. Mask-based points are approximate observed surface locations, not full 3D object volumes.

## Interaction

3D labels select a recorded observation; side panel shows its actual RGB, source timestamp/frame, detector box and (where refined) sampled surface pixel. Orbit exploration preserves world coordinates. Focus uses the transformed recorded camera location. Class history selects other evidence, not proven matching instances. Browser-local notes survive reload and can be searched. Moving objects may differ between Oct 2 and Oct 8; the room shows historical observations, not present-day inventory. The source scene is not edited to remove mesh holes.

## Demo production

`scripts/check-object-room.mjs` creates views for visual alignment inspection. `scripts/render-object-room.mjs` verifies actual marker clicks, notes/reload/search, no-match search, anchor invariance during orbit, history and evidence replay; records the real rendered UI with smoothly scripted camera moves and actual button actions. Frame map retains camera, target, observation and source label. Export is an edited replay demonstration, not real-time performance evidence.

Retained output: `/path/to/local-assets`. Original v1 video preserved separately. No live Quest deployment, complete LEDGER pipeline, verified persistent identity association, or OpenClaw API integration is claimed.
