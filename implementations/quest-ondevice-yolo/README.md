# On-device YOLO for Quest — WebXR / Unity classroom samples

Two implementations run the same YOLOv9 model **without an external GPU or inference server**.
They target **Quest 3 / 3S**, not camera-API support for Quest 2 / Pro.

- **Web:** ONNX Runtime Web WASM CPU inference on a readable camera or local image/video. WebXR displays the annotated preview on a panel inside the headset.
- **Unity native:** Meta Passthrough Camera API supplies headset camera frames; Unity Inference Engine runs on the built-in GPU (GPUCompute) or CPU. **First-person passthrough** receives label-only annotations at calibrated center-ray depth hits. Version 0.3.0 attaches each label to a session-local native `OVRSpatialAnchor`; later detections update observations without repositioning that anchor. No camera-preview panel or bounding rectangle is displayed.
- YOLO returns classes and 2D boxes. The native implementation raycasts each box center into environment depth and creates a native session anchor there. The text child billboards by rotation only. This is not exact 3D object geometry, moving-object tracking, saved cross-relaunch anchoring, or a complete digital twin.

## Illustrated walkthrough

[Teaching tutorial](TUTORIAL.md) · [Standalone HTML](tutorial/index.html) · [Pipeline diagram](tutorial/pipeline.svg) · [Center-raycast diagram](tutorial/center-raycast.svg)

Source excerpts explain center-ray localization, its approximations, detection versus tracking, and reproduction.

## Which implementation should I use?

Start with **Unity native** for headset-camera first-person AR. A WebXR passthrough background does not imply JavaScript can read its pixels. The Web sample checks actual `getUserMedia` permission results and reports failures. It does not invent detections or label test images as live input. Camera retention during immersive WebXR also depends on browser support.

## Web

```bash
cd implementations/quest-ondevice-yolo/web
npm ci
npm run prepare-assets
npm test
npm run dev
```

On desktop, open the localhost URL, select **Load model**, then **Start camera**. To change cameras, select another device and press Start camera again. Local images and videos also support real-model inference.

For Quest distribution, run `npm run build` and host `dist/` on **trusted HTTPS**. A LAN HTTP address cannot provide camera / WebXR access. The development server only serves JavaScript and model files; it is not an inference server. Initial model download needs internet access. Offline reopening after closing the page and PWA caching are not implemented.

1. Open the HTTPS URL in Quest Browser.
2. Load model; confirm the WASM CPU backend.
3. Start camera, grant permission, and inspect the selected camera and image.
4. If input is readable, enter WebXR. This is a preview panel, not an object-aligned label overlay.
5. Stop releases the camera. Save metrics exports inference timing.
6. Record preview saves up to 60 seconds. This is not an OS compositor recording.

If browser camera access is unavailable, use Unity. Do not assume Raw Camera Access support.

### Developer-only native retention demonstration

A cold launch may pass Android float extra `classroom_demo_freeze_after` (default 0) to freeze observations after the specified seconds following the first real inference. The HUD explicitly reports OBSERVATIONS FROZEN. This changes observation timing, never fabricates detections. Normal launches do not auto-freeze. Logs distinguish the developer timer from physical A-button input.

### Repeat Web verification

```bash
npm exec playwright install chromium
# Supply your own test image and evidence output directory.
YOLO_TEST_IMAGE=/absolute/test.jpg YOLO_EVIDENCE=/absolute/output node verify-demo.mjs
```

The verifier expects person and bus detections in the [public Ultralytics bus.jpg](https://github.com/ultralytics/assets/blob/main/im/bus.jpg). That image is not redistributed here. Set `CHROME_PATH` to a dedicated test Chrome executable if needed. The verifier does not connect to an existing user profile.

## Unity native

The bootstrap creates the classroom scene from an **exact Meta upstream commit**, without duplicating SDKs, scenes, or model binaries in this repository.

```bash
python3 implementations/quest-ondevice-yolo/scripts/prepare-unity.py /absolute/new/quest-yolo-unity
```

The destination must not exist. Install Git LFS and Unity Hub Android Build Support (SDK/NDK/OpenJDK).

1. Open the generated project in **Unity 6000.4.5f1**, the version used for the verified build. Upstream declares 6000.0.66f2; the bootstrap explicitly sets the tested version.
2. Run **Classroom > Prepare YOLO scene**.
3. Review Meta > Tools > Project Setup Tool as needed. Headset camera permission is required.
4. Run **Classroom > Build Android APK** to create `Builds/classroom-yolo.apk`.
5. Install the dedicated `org.openclaw.classroom.yolo` package. The session-anchor implementation is **0.3.0/code4**; see VERIFICATION.md for actual device acceptance. The earlier plane-outline implementation was 0.2.0/code3. Other applications are not modified.
6. On Quest, open Library > Unknown Sources > **Classroom Local YOLO**.
7. Grant camera and spatial-data permissions. Labels appear directly in normal passthrough. A freezes/resumes observations while retaining anchors; B clears them.

```bash
# Use the actual path of your Unity installation.
/path/to/Unity -batchmode -nographics -quit -projectPath /absolute/new/quest-yolo-unity \
  -buildTarget Android -executeMethod ClassroomBuild.Build -logFile /absolute/build.log
```

The default is the **built-in GPU**. For CPU, set `YOLO_CPU=1` in the build environment or change the generated QuestYolo component backend to CPU. The menu Build command also prepares the scene; use standard Build Settings if preserving Inspector edits.

- Default requested maximum: 5Hz, one inference at a time. Inference update rate and XR rendering FPS are different.
- Logs: `QUEST_YOLO backend=... inference_ms=... count=... source=headset_camera`.
- Focus or positional-tracking loss hides labels without destroying their anchors. Pending, failed, unlocalized, or untracked native anchors are not displayed or counted as ready. No depth hit means no new anchor. Unobserved objects expire after 30 seconds; freezing observations retains them until resume or clear.
- Performance depends on headset load, heat, and memory. Actual measurements are in [VERIFICATION.md](VERIFICATION.md).
- The source camera-viewer Canvas is disabled. An environment-raycast Prefab supplies depth hits using exposure-time camera pose and calibrated `ViewportPointToRay`. A root is placed once at the center hit, then receives `OVRSpatialAnchor`. Later same-class detections within the association radius update confidence/last-seen metadata, not the root position. Only child text rotates to face the viewer. Default association radius is 0.65m, maximum 20 anchors, retention 30s; proximity matching can confuse nearby same-class objects. Anchors remain session-local and are neither saved nor reloaded. Background center hits and depth errors can pin labels to the wrong surface.

## Classroom experiments

1. Detect people, chairs, bottles, or other classes from the model's 80-class vocabulary.
2. Compare thresholds 0.35 and 0.6 for false positives and missed detections.
3. Compare requested 1Hz / 5Hz detection rates with rendering behavior.
4. Freeze observations with A and check that existing anchors remain. Resume with A; clear with B. Compare CPU/GPU in a separate experiment.
5. Contrast 2D detection with a fixed session anchor from an approximate center-depth hit. Inspect stable IDs, native UUIDs, and headset pose in logs.

## Sources and licenses

- [Pinned Meta upstream](https://github.com/oculus-samples/Unity-PassthroughCameraApiSamples/tree/3baac1a1a53aa00af3f639425914f14238a97f84)
- [Meta PCA overview](https://developers.meta.com/horizon/documentation/unity/unity-pca-overview)
- [Unity inference integration](https://developers.meta.com/horizon/documentation/unity/unity-pca-sentis)
- [WebXR Raw Camera Access specification](https://immersive-web.github.io/raw-camera-access/) — a specification is not proof of Quest Browser support.
- Meta's documented baseline: Quest 3/3S, OS v74+, `horizonos.permission.HEADSET_CAMERA`, MRUK v81+.
- Pinned upstream manifest: MRUK 85.0.0, Inference Engine 2.2.1. The bootstrap explicitly selects the verified Inference Engine 2.6.1 and OpenXR 1.16.1.
- Model SHA256: `189ed26d273423b02243ce7f0a7795acc7da8049f879f8b73a0684d25d1138fd`.
- Preserve upstream SDK/scene licenses. Meta's README describes the supplied model as MIT; separately review licensing when replacing it.
- Camera images, room recordings, APKs, SDK binaries, and model weights are not stored in Git. Only source and retrieval instructions are distributed.
