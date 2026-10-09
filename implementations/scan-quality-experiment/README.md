> Public source snapshot: personal room/avatar/capture assets are not bundled. Original README below documents the source project; asset-included claims apply only to the original private delivery. Use your own assets and local settings. API scripts use OPENAI_API_KEY or TYPESAFE_API_KEY from your environment.

# Scan quality experiment

## Result preview



Actual experiment comparison, not a reconstructed demo video. See the measured results and limitations below.

Non-destructive offline RGB-D fusion of Ryo's 2026-10-08 3d Scanner App room capture. Outputs are point clouds, not upgraded meshes or learned Gaussian splats.

## Run

```sh
python3 -m venv --system-site-packages /tmp/openclaw/scan-quality-env
/tmp/openclaw/scan-quality-env/bin/python -m pip install numpy Pillow scipy
/tmp/openclaw/scan-quality-env/bin/python fuse_compare.py
```

Source and output paths are explicit constants at the top of the script. Source archive remains untouched. No cloud upload or GPU service is used.

## Result

Confidence=2, depth 0.2–8 m; 3-pixel sampling, every other RGB keyframe, excluding 9 held-out frames and their ±2 adjacent keyframes. Fused 1,163,429 colored input samples.

- 2 cm voxels: 499,259 points, held-out median nearest-point distance 13.03 mm, P90 46.71 mm.
- 1 cm voxels: 912,725 points, held-out median 11.78 mm, P90 46.64 mm.

These are agreement with 23,748 points from withheld noisy source depth, not independently measured physical accuracy. More output points trivially help nearest-neighbor distance; these numbers do not prove perceptual improvement. Original source mesh sees all frames and is not a fair held-out competitor.

Conventions were selected against existing source mesh vertex proximity: depth ×0.001 meters; image x,-y,-z into ARKit camera; row-major cameraPoseARFrame; no extra translation. On the validation subset median vertex distance was18.9mm; this provides internal consistency, not independent metric calibration.

## What remains for realistic improvement

The result proves original data can be recomputed. It is deliberately not branded a higher-quality result. Color was downsampled to depth resolution, so existing10K textured OBJ and generated Scaniverse SPZ are the better realism baselines. Next controlled experiment: full-resolution RGB texture reprojection with visibility/angle weighting and exposure seam handling, or held-out-view Gaussian training; retain baseline and withhold nonadjacent input views. Sparse point fusion alone does not recover missing detail or fix tracking drift.

Durable artifacts: `/path/to/local-assets`.
