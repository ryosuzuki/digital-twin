# Video-to-room memory replay

Launch `node scripts/serve-object-room.mjs`, then open http://127.0.0.1:8832/object-stream.html. Uses the same private capture, alignment and scan assets as object-room.md. Run `node scripts/render-object-stream.mjs --check` for scoped checks or omit --check for the demo export.

Video RGB is replayed from the measured Quest capture. Cached YOLO detections (~1 Hz) populate 3D spatial bins only when their recorded timestamp has passed. Nearby same-class observations within 0.65m are grouped to reduce overlapping labels; this is not instance tracking. Labels persist when out of camera view. Selecting a bin opens an observed frame; “When was this seen?” queries timestamps in that bin, not an LLM or web knowledge service. Scrubbing backward removes future observations.

The export shows 3x recorded replay, not live inference. Detection boxes are sample-and-hold between detection timestamps; they are not optical-flow tracked. The separate October 8 textured scan is approximately registered to the October 2 Quest geometry. No independent accuracy claim, live Quest deployment, general visual Q&A or complete LEDGER reproduction.

Output: /path/to/local-assets Verification JSON and screenshots alongside. Source is backed up to private spatial-memory-private-backup main; captures and output videos stay in Storage.

Display filter: confidence >= 0.65 and recorded depth >= 0.5 m, to reduce weak detections and near-camera artifacts. False detections can remain. Marker scale is distance-compensated for readability.
