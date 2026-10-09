> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Spatial Object Memory
Local functional MVP inspired by XR-Objects and LEDGER; not a reproduction of either research implementation.

## Run
`npm install` then `node server.mjs`; open http://127.0.0.1:8824 . Loopback only.

Uses Ryo's actual 2026_10_08_12_41_21 iPad textured scan, copied unchanged; provenance in source-provenance.json. Private assets: do not publish.

Select a manual location marker, attach notes, search stored text, focus the camera on its world-space position, register new locations via raycast, and export structured JSON. Notes persist in browser localStorage. Entry shelf / Kitchen counter are manually authored demo labels, not recognized objects. Keys and tea notes are user-entered demonstration data, not claims about the real room. No automated recognition, moving-object tracking, LLM, OpenClaw runtime connection, or Quest deployment is implemented.

`node record.mjs` records actual browser interactions and checks persistence, search, unknown-item handling, surface registration, export and world-anchor invariance. Demo browser data is isolated from the ordinary user's browser.

Next integration: ingest timestamped detector results + calibrated camera pose, retain confidence/provenance, associate objects across observations, and expose read-only memory retrieval to OpenClaw. Do not infer object history from a static mesh.
