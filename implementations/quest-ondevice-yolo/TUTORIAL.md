# Object detection → spatial AR

**Teaching walkthrough · native 0.2.0 · 2026-10-20**

[Standalone HTML tutorial](tutorial/index.html) · [Setup](README.md) · [Device verification](VERIFICATION.md) · [Source](unity/QuestYolo.cs)

> **Can we raycast the detected object's center into Quest depth? Yes. That is the current native implementation.**
> YOLO 2D box → calibrated center ray → environment-depth hit → world-space annotation.
> This estimates a surface position; it does not establish temporal object identity or persistent anchors.

## 1. What you see

The native sample draws green outlines and labels such as `chair` or `person` directly over the normal first-person passthrough view. There is no rectangular camera-video panel. Camera frames are still required for inference, but do not need to be displayed as UI.

**Recognition input and passthrough display follow different paths.** The Meta compositor renders the physical view; the application adds only line and text geometry.

![Pipeline — all inference stays on the headset](tutorial/pipeline.svg)

Editable figures: [pipeline.svg](tutorial/pipeline.svg) / [center-raycast.svg](tutorial/center-raycast.svg). These are explanatory schematics, not device captures. Actual device video is distributed through the lecture slides and requester-facing deliverables. Room images, recordings, model weights, and APKs are not redistributed in this Git repository.

## 2. What runs where

| Layer | Native Unity implementation | Web implementation |
|---|---|---|
| Input | Meta Passthrough Camera API / Quest 3–3S | Readable `getUserMedia` camera or local image/video |
| Detector | Pinned YOLOv9 ONNX model | Same model |
| Inference | Unity Inference Engine 2.6.1 / built-in GPUCompute, optional CPU | ONNX Runtime Web 1.22.0 / WASM CPU |
| Spatial placement | MRUK 85.0.0 / EnvironmentRaycastManager | Not implemented in this Web sample |
| Display | Unity OpenXR 1.16.1 / world-space lines and text / compositor passthrough | Three.js 0.180.0 / preview panel inside WebXR |
| Build | Unity 6000.4.5f1 / Android ARM64–IL2CPP verified | Vite 6.4.4 |
| External GPU | Not required | Not required |
| Headset acceptance | Native 0.2.0 physically verified within the limits below | Quest Browser not physically tested |

Initial setup downloads SDKs and the model. Native runtime inference remains on the headset, without an external inference server or `adb reverse`. **No external GPU** means using Quest's built-in GPU, not avoiding GPUs entirely.

A visible WebXR passthrough background does not imply JavaScript can read its pixels or depth. A Raw Camera Access specification is not proof of Quest Browser support. The current Web sample does not provide the native sample's spatial placement.

## 3. Center raycast: from a 2D box to an approximate 3D position

![Center raycasting and approximate annotation plane](tutorial/center-raycast.svg)

1. YOLO returns `class, score, x, y, width, height` in a 640×640 image. It does not return 3D positions.
2. Normalize the box and convert the image's top-origin coordinates to Unity's bottom-origin viewport coordinates.
3. Pass its center UV to `ViewportPointToRay(uv, capturedPose)`. Do not guess a field of view or fixed distance.
4. Query environment depth with `EnvironmentRaycastManager.Raycast`. The hit point supplies an approximate world-space object location.
5. Construct a plane through that point, parallel to the exposure-time camera. Intersect the four corner rays with this plane and draw their outline.
6. Hide annotations when there is no hit, distance is out of range, or positional tracking is lost.

### Actual implementation

Excerpt from [QuestYolo.cs, Draw()](unity/QuestYolo.cs). Variable `b` is a normalized detection box.

```csharp
float left = Mathf.Clamp01(b.x), right = Mathf.Clamp01(b.x + b.w);
float bottom = Mathf.Clamp01(1 - b.y - b.h), top = Mathf.Clamp01(1 - b.y);
var ray = cameraAccess.ViewportPointToRay(
    new Vector2((left+right)/2, (bottom+top)/2), capturedPose);
if (!environmentRaycast.Raycast(ray, out var hit, 12f)) continue;
float distance = Vector3.Distance(capturedPose.position, hit.point);
if (distance < .25f || distance > 12) continue;
var plane = new Plane(capturedPose.rotation * Vector3.forward, hit.point);
```

The camera pose is captured before copying the image. Projecting an older image using the later head pose after inference would introduce additional motion-related misalignment.

```csharp
capturedPose = cameraAccess.GetCameraPose();
Graphics.Blit(cameraAccess.GetTexture(), snapshot);
```

[Full processing path](unity/QuestYolo.cs): `Start()` captures and infers → `Decode()` applies confidence threshold and class-aware NMS → `Draw()` raycasts and draws world-space geometry → `Update()` checks expiry and tracking.

### Why the center is not always the object

Chair openings, gaps between a person's legs, and overlapping objects can put the box center on background. Depth reports a surface distance along a pixel direction, not object identity or ownership. A single ray does not guarantee the geometric center or 3D dimensions of the object.

**Possible extensions, not implemented:** sample multiple rays within the box, reject depth outliers, and use a median or nearer cluster. A segmentation mask could exclude background. Object identity errors and occlusion still require separate handling.

## 4. Detection ≠ tracking ≠ anchors

| Concept | Question | Current 0.2.0 |
|---|---|---|
| 2D detection | What appears where in this image? | Implemented: YOLO classes and boxes |
| 3D localization | Where in the world should this annotation appear? | Implemented: approximate center-ray depth hit |
| Temporal object tracking | Is this the same object across time? | **Not implemented:** annotations are recreated, without persistent IDs |
| Head tracking | Where is the headset and how is it oriented? | Uses Meta positional tracking, not object identity |
| Persistent anchor | Can content return to the same location after restart? | **Not implemented:** no saving or sharing |
| Digital twin | Can objects, geometry, and state be managed over time? | Not accomplished by this sample alone |

One asynchronous inference runs at a time. Lines and labels are recreated after each result. The default requested maximum is 5Hz, but processing time can reduce the actual update rate. **A 5Hz setting guarantees neither 5 detection FPS nor XR rendering FPS.** Annotations expire after 0.85 seconds without updates.

A next-stage object record could store `trackId, class, position, confidence, lastSeen` and associate new detections with past 3D positions, classes, and 2D boxes. Tracking a moving object differs from anchoring content to a fixed location. These are proposed extensions, not accepted current features.

## XR-Objects: Augmented Object Intelligence

Here **XR-Objects** means [Dogan et al., UIST 2024: Augmented Object Intelligence with XR-Objects](https://xr-objects.github.io/) ([DOI](https://doi.org/10.1145/3654777.3676379)), not a generic XR GameObject.

Figure 4 and §3.3 (PDF pp.5–7) describe **object detection → depth raycast → object proxy → object-bound context menu → information, comparison, sharing, notes, and timers**. The evaluated smartphone implementation combines Unity AR Foundation / ARCore, on-device MediaPipe COCO80 detection, and a cloud PaLI MLLM. This is not evidence that all features ran locally on Quest.

| Stage | XR-Objects paper | This Quest sample |
|---|---|---|
| Find | MediaPipe detector | Local YOLO |
| Localize | ARCore depth and raycast | MRUK environment depth and center ray |
| Present | Object proxy and contextual menu | World-space outlines and class labels |
| Act / reason | Information, compare, share, anchor widgets / cloud PaLI | **Not implemented:** selection, menus, per-object conversation, and cloud reasoning |

The Quest sample provides the **detection and localization foundation** for an XR-Objects-inspired interface. A possible extension places a Prefab at the center-ray hit, selects it with a controller/hand ray, and opens an object-bound menu. Native 0.2.0 does not implement or validate that interaction. A `chair` label alone does not identify a product or answer questions about it.

## 5. Reproduce

### Unity — recommended for first-person AR

```bash
# Run from the digital-twin root. The destination must not already exist.
python3 implementations/quest-ondevice-yolo/scripts/prepare-unity.py /absolute/new/quest-yolo-unity
```

Install Git LFS and Unity Hub Android Build Support (SDK/NDK/OpenJDK). The bootstrap retrieves Meta upstream commit `3baac1a1a53aa00af3f639425914f14238a97f84` and verifies the model SHA256.

1. Open the generated project in **Unity 6000.4.5f1**.
2. Run **Classroom > Prepare YOLO scene**.
3. Run **Classroom > Build Android APK**.
4. Install on Quest 3/3S. The verified package is `org.openclaw.classroom.yolo`, version `0.2.0/code3`.
5. Grant camera and spatial-data permissions; establish positional tracking, then open **Classroom Local YOLO**.
6. Confirm green outlines and labels over normal passthrough, without a camera-preview panel.

[ClassroomBuild.cs](unity/Editor/ClassroomBuild.cs) defines scene, permission, and Prefab setup. [prepare-unity.py](scripts/prepare-unity.py) defines pinned retrieval. The camera API targets Quest 3/3S. Documented API minimum requirements differ from the exact versions used in this verified build.

### Web — detection introduction, not equivalent spatial placement

```bash
cd implementations/quest-ondevice-yolo/web
npm ci
npm run prepare-assets
npm test
npm run dev
```

Start on desktop: Load model → camera or local image → detections. Quest distribution needs trusted HTTPS. WebXR uses a preview panel; browser-camera access depends on actual permission and support. See the [Web setup](README.md#web).

## 6. What was actually tested

[VERIFICATION.md](VERIFICATION.md) is the primary acceptance record. On a **stationary Quest 3, native 0.2.0, 2026-10-20**:

- Real headset camera → built-in GPUCompute → first-person outlines and labels.
- 122 inference samples from a new process; median **271.61ms per update**.
- 121/122 samples produced 3–5 depth-backed annotations; one startup sample had none.
- First, middle, and last frames of the approximately 14.95-second compositor recording were inspected. Person/chair/laptop labels and outlines appear directly in the room view, without a preview panel.

**121/122 is not detection accuracy.** It counts inference samples that produced depth-backed annotations, not correct objects against ground truth. The 271.61ms measurement is a pipeline/update metric, not XR rendering FPS.

Unverified: quantitative moving-head alignment, physical A-button input, long-duration heat/battery, physical USB unplugging, and Quest Browser/WebXR behavior. The earlier camera-panel 0.1.1 median of 275.27ms is a different measurement.

## 7. Classroom exercises

1. **Detect:** compare confidence thresholds 0.35 and 0.6 on people and chairs.
2. **Localize:** find cases where the center ray hits background, such as a chair opening.
3. **Explain:** why do four 2D corners not recover the physical object's 3D geometry?
4. **Measure:** inspect `QUEST_YOLO ... inference_ms=... depth_hits=... tracked=...`; do not confuse timing with rendering FPS.
5. **Extend:** aggregate multiple depth rays. Design object-ID tracking and persistent anchors as separate tasks.

## Lecture slides and reuse

[Lecture slides — Quest implementation extension](https://docs.google.com/presentation/d/1cSDat0MuJk7qmj2TtbPbHt5IGeLQUsle8kemzN639hY/edit#slide=id.quest_lab_section)

Thirteen slides (38–50) follow the existing 37-slide deck. Actual device images and Drive video remain in the lecture distribution; raw room media is not redistributed here.

| Slide | Topic |
|---|---|
| 38 | Build it: object-aware AR — implementation section |
| 39 | Recognize objects in first person — actual demo frame |
| 40 | Demo: on-headset inference — actual device video |
| 41 | From labels to XR-Objects — object-bound interaction goal |
| 42 | Detection is not yet tracking — capability distinctions |
| 43 | How it runs on the headset — processing pipeline |
| 44 | A ray turns a pixel into a 3D point — projection geometry |
| 45 | What we used — pinned software stack |
| 46 | The center-ray step in code — source excerpt |
| 47 | Unity native versus WebXR — current capabilities |
| 48 | What the real-device test shows — measured acceptance |
| 49 | Next: make each object actionable — unimplemented extensions |
| 50 | Try it, then change one layer — classroom exercise |

[slides.json](tutorial/slides.json) preserves slide IDs, order, titles, and technical notes. [compose-slides.py](tutorial/compose-slides.py) reproduces native Slides shapes/text and Drive image/video references. It contains neither media pixels nor credentials. It requires the specific course template's layout/placeholder IDs; it is not a universal empty-deck authoring tool.

### Safe dry-run: generate without writing to Google

1. Prepare Drive image/video assets you are authorized to use. Create `media.json`: `[{"id":"IMAGE_DRIVE_ID"},{"id":"VIDEO_DRIVE_ID"}]`. The recipe does not upload assets or modify sharing.
2. Specify a fresh work directory. Dry-run uses only the standard library and requires no authentication.

```bash
python3 implementations/quest-ondevice-yolo/tutorial/compose-slides.py \
  --presentation-id YOUR_TEMPLATE_COPY_ID \
  --media-json /absolute/media.json \
  --work-dir /absolute/new/quest-slide-plan
```

This writes `manifest.json` and `requests.json` without Google API calls. To apply, use a **copy** of the original 37-slide course template and a caller-provided authenticated `google_api.py` helper implementing `Google().presentation(id)` and `Google().batch(id, requests)`. Choose a new work directory and add `--google-helper-dir /absolute/helper-directory --apply`.

Do not reapply to the completed original deck. Existing IDs and the 37-slide check stop this. Changes use multiple batches: inspect partial application after a failure instead of blindly retrying; restart on a fresh template copy. Authentication and token handling belong to the caller's helper, not this source.

## Sources

- [XR-Objects: project and paper](https://xr-objects.github.io/) — UIST 2024, DOI 10.1145/3654777.3676379, Figure 4 / §3.3, pp.5–7.
- [Pinned Meta upstream](https://github.com/oculus-samples/Unity-PassthroughCameraApiSamples/tree/3baac1a1a53aa00af3f639425914f14238a97f84)
- [Meta Passthrough Camera API](https://developers.meta.com/horizon/documentation/unity/unity-pca-overview)
- [Meta Unity inference integration](https://developers.meta.com/horizon/documentation/unity/unity-pca-sentis)
- [WebXR Raw Camera Access specification](https://immersive-web.github.io/raw-camera-access/)
- Repository sources: [Unity processing](unity/QuestYolo.cs), [scene generation](unity/Editor/ClassroomBuild.cs), [Web processing](web/src/yolo.js), [verification](VERIFICATION.md).

Publication scope: implementation teaching sources and original schematic figures only. No room media, private transcripts, credentials, SDK binaries, or model weights. Integration target: `origin/main`; completion owner: Quest classroom tutorial task. Authoritative tutorial paths: this file, `tutorial/`, and tutorial links in implementation/root README. Runtime code and imported snapshots remain unchanged.
