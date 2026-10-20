# Spatial Home / Lab — current twin gateway

A runnable local catalog for **our recent Home and Lab Spatial digital twins**, not the older archived scan demos. It opens the existing, separate applications through two loopback proxies and checks whether each application responds. Root-relative modules, room assets, camera snapshots, API requests and interaction POSTs are forwarded to the corresponding venue without mixing Home and Lab state.

This directory contains new integration code, **not a full public snapshot of the private Spatial application**. The application source and our actual room assets remain private. It does not reconstruct the twins or claim that a synthetic room is our lab.

## Run immediately with synthetic upstreams

Python 3.10+; no package installation or cloud API required.

```bash
cd implementations/spatial-home-lab
python3 fixture.py
```

In another terminal:

```bash
python3 gateway.py --config config.example.json
```

Open **http://127.0.0.1:39800/**. Select Home or Lab. Each clearly labeled synthetic upstream has a moving box and an interaction button. They exercise the real gateway paths; they are not recorded room or camera footage.

```bash
python3 -m unittest -v
```

## Connect the actual recent Home and Lab twins

1. Start the existing private Spatial Home and Lab web services using their existing configuration. Do not replace either app with this fixture.
2. Copy `config.example.json` to a private path **outside this checkout**.
3. Set each `upstream` to its existing loopback HTTP origin and retain the actual route (`/home.html` or `/lab.html`). Set unused `proxy_port` values and an unused `dashboard_port` if necessary.
4. Run `python3 gateway.py --config /path/to/private/home-lab-config.json`.
5. Open the dashboard. Each app loads through its own origin. Its original room, camera and registration code remains responsible for all scene behavior.

Private restoration records retain the verified service and source mapping. Never add your real config, assets, scan coordinates or camera addresses to this public repo.

## What the two current applications contain

- **Home:** its own scanned room and calibration, two physical camera tiles, 3D room workspace, separate optional recognition/diagnostic views.
- **Lab:** its own room scan, four physical camera tiles, paper identity / room-placement layers and registration controls.
- Both use the existing browser/WebGL application. This gateway is not a Unity or Quest port. Optional recognizers may require external services; no inference implementation is added here.

## Integration design and limits

A single `/home/` / `/lab/` path prefix would break existing absolute `/twin.js`, `/room.glb` and API routes. Separate listening ports preserve those namespaces without editing the current applications or embedding personal configuration in public code. The gateway binds **127.0.0.1 only**, accepts only configured loopback upstreams, blocks foreign Host/Origin headers, does not forward browser credentials, and never logs private paths. This is not an authenticated internet deployment. Do not expose the ports publicly.

The adapter forwards GET, HEAD and POST (up to 16 MiB). WebSocket upgrades, authentication-dependent applications and HTTPS upstreams are not supported. Absolute URLs embedded in a private application's code continue to use that application's original local configuration. Existing navigation that deliberately switches to another private service remains original behavior.

A green availability check means **HTTP 200 only**, not fresh cameras, valid registration, physical accuracy, or successful model inference. Upstream failures remain failures. The gateway does not start/restart devices or recognizers and does not alter calibration. Existing services can still be used directly.

## Verification

Ten dependency-free tests cover distinct Home/Lab origins, root-relative module/API forwarding, POST interaction forwarding, dashboard health, missing paths, config validation, and hostile browser origins/hosts. Live integration additionally compared served HTML and module bytes through the adapter with the original Home/Lab endpoints, plus room-file hashes; that is HTTP/source evidence, not live-pixel or measured tracking acceptance. See the private dated delivery receipt for the particular service instance. No private capture or room screenshot is bundled.
