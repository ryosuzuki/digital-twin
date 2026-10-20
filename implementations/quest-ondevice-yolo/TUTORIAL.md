# Object detection → spatial AR

**Teaching walkthrough · native 0.3.0 session-anchor implementation · 2026-10-20**

[Standalone HTML tutorial](tutorial/index.html) · [Setup](README.md) · [Device verification](VERIFICATION.md) · [Source](unity/QuestYolo.cs)

> **Can we raycast the detected object's center into Quest depth? Yes. That is the current native implementation.**
> YOLO 2D box → calibrated center ray → environment-depth hit → world-space annotation.
> This estimates a surface position and retains a session-local native anchor. It does not establish moving-object identity or saved cross-relaunch persistence.

## 1. What you see

Native 0.3.0 displays **labels only**, centered on measured surface hits in normal first-person passthrough. There is no camera-preview panel or rectangular detection outline. The camera is inference input; Meta's compositor supplies the physical view.

![On-device recognition to anchored labels](tutorial/pipeline.svg)

Editable schematics: [pipeline.svg](tutorial/pipeline.svg) and [center-raycast.svg](tutorial/center-raycast.svg). These are diagrams, not device screenshots. Actual device media remains in the lecture distribution, not Git.

## 2. What runs where

| Layer | Unity native 0.3.0 | Web implementation |
|---|---|---|
| Input | Meta Passthrough Camera API / Quest 3–3S | Readable getUserMedia camera or local image/video |
| Detector | Pinned YOLOv9 ONNX | Same model |
| Inference | Unity Inference Engine 2.6.1 / built-in GPUCompute, optional CPU | ONNX Runtime Web 1.22.0 / WASM CPU |
| Localization | MRUK 85.0.0 / calibrated center ray into environment depth | Not implemented |
| Retention | Native OVRSpatialAnchor, session-local | Not implemented |
| Display | OpenXR 1.16.1 / label child under anchor | Three.js 0.180.0 / WebXR video-preview panel |
| Build | Unity 6000.4.5f1 / Android ARM64–IL2CPP | Vite 6.4.4 |

Initial setup downloads SDKs and weights. Runtime inference remains on Quest, without an external inference server or adb reverse. **No external GPU** means using the headset GPU, not avoiding GPUs entirely.

WebXR passthrough visibility does not imply JavaScript camera/depth access. The current Web sample is not equivalent spatial placement or anchoring; Quest Browser support/performance remains unverified.

## 3. Center raycast → session anchor → label

![Center ray and native anchor](tutorial/center-raycast.svg)

1. YOLO returns a class, score, and box in a 640×640 image, not a 3D object position.
2. Normalize the box and convert its top-origin coordinates into bottom-origin viewport coordinates.
3. Use calibrated `ViewportPointToRay(centerUV, capturedPose)` with the exposure-time camera pose.
4. Raycast into MRUK environment depth. With no hit, do not create an anchor.
5. Place a new independent root once at the measured hit; add `OVRSpatialAnchor`.
6. Wait for both `Localized` and `IsTracked`. Hide pending/failed anchors and do not count them as ready.
7. Render centered text under the native anchor. Rotate only the child text to face the viewer; never move the root from later image detections.

### Actual implementation

Excerpt from [QuestYolo.cs](unity/QuestYolo.cs), `Observe()`:

```csharp
var ray = cameraAccess.ViewportPointToRay(
    new Vector2((left+right)/2, (bottom+top)/2), capturedPose);
if (!environmentRaycast.Raycast(ray, out var hit, 12f)) continue;
// For a new object record only:
var root = new GameObject("ObjectAnchor_" + nextId);
root.transform.SetPositionAndRotation(hit.point, Quaternion.identity);
itemNew.anchor = root.AddComponent<OVRSpatialAnchor>();
```

This excerpt omits record creation and association; use the full source, not this fragment as a standalone script. The root is independent of the head. Native anchor tracking may refine its pose; the application does not drive its position from headset motion or later 2D boxes.

```csharp
// Billboard orientation only; no application-driven position change.
item.content.transform.rotation = Quaternion.LookRotation(direction, Vector3.up);
```

A native anchor pins a location, not a moving object's identity. A chair opening or gap between legs can put the center ray on background. Depth reports surfaces, not semantic ownership. Fixed labels can therefore remain at a wrong surface if the initial hit was wrong. Multiple-ray depth aggregation or segmentation could improve this, but is not implemented.

### Retention and controls

- Same-class observations are matched one-to-one to existing roots within 0.65m. Matching updates confidence and last-seen time, not root position.
- At most 20 object records. Unseen records expire after 30s; frozen observation time does not consume retention time.
- **A:** freeze/resume observations while retaining labels. **B:** clear session anchors.
- Losing app focus or head tracking hides labels but keeps records. Anchor tracking/localization must be valid before labels reappear.
- No disk save, cloud sharing, or cross-relaunch restoration. Restarting requires new detections/anchors.
- Logs include create/localized/associated/visibility/retired events, stable record IDs, native UUIDs, anchor position, headset pose, and inference frame.
- Developer-only Android float extra `classroom_demo_freeze_after` (default 0) can freeze after a real observation interval. HUD/logs explicitly identify the frozen phase; no synthetic detections are inserted.

## 4. Detection, location retention, and object tracking

| Capability | Native 0.3.0 |
|---|---|
| 2D detection | YOLO classes and boxes used internally |
| Approximate 3D localization | Calibrated center-ray depth hit |
| Stable session label | Native OVRSpatialAnchor; not recreated on every inference |
| Association | Class/proximity matching of stationary locations; can confuse nearby same-class objects |
| Moving-object tracking | Not implemented; anchor does not follow a moved object |
| Saved persistent anchor | Not implemented; no cross-relaunch save/load |
| Exact object geometry / digital twin | Not recovered by this sample |

One inference runs at a time. Requested maximum 5Hz is not guaranteed update FPS or XR rendering FPS. Native 0.2.0 historically recreated planar box outlines each inference and expired them after 0.85s; **that is not the 0.3.0 label-only anchor behavior**.

## XR-Objects: Augmented Object Intelligence

Here **XR-Objects** means [Dogan et al., UIST 2024: Augmented Object Intelligence with XR-Objects](https://xr-objects.github.io/) ([DOI](https://doi.org/10.1145/3654777.3676379)), not a generic XR GameObject.

Figure 4 and §3.3 (PDF pp.5–7) describe **object detection → depth raycast → object proxy → object-bound context menu → information, comparison, sharing, notes, and timers**. The evaluated smartphone implementation combines Unity AR Foundation / ARCore, on-device MediaPipe COCO80 detection, and a cloud PaLI MLLM. This is not evidence that all features ran locally on Quest.

| Stage | XR-Objects paper | This Quest sample |
|---|---|---|
| Find | MediaPipe detector | Local YOLO |
| Localize | ARCore depth and raycast | MRUK environment depth and center ray |
| Present | Object proxy and contextual menu | Session-anchored class labels |
| Act / reason | Information, compare, share, anchor widgets / cloud PaLI | **Not implemented:** selection, menus, per-object conversation, and cloud reasoning |

The Quest sample provides the **detection and localization foundation** for an XR-Objects-inspired interface. A possible extension places a Prefab at the center-ray hit, selects it with a controller/hand ray, and opens an object-bound menu. Native 0.3.0 does not implement or validate menus or actions; the immediate teaching goal is the anchored label itself. A `chair` label alone does not identify a product or answer questions about it.

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
4. Install on Quest 3/3S. The verified package is `org.openclaw.classroom.yolo`, version `0.3.0/code4`.
5. Grant camera and spatial-data permissions; establish positional tracking, then open **Classroom Local YOLO**.
6. Confirm centered labels over normal passthrough, without a camera-preview panel or box. A freezes observations while labels remain; B clears anchors.

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

## 6. Device evidence and historical baseline

### Current native 0.3.0: session-anchor label retention

Actual second cold launch on a stationary Quest 3 produced **57 real inference samples**, median **271.12ms** pipeline turnaround. **7 native anchors localized with UUIDs**, with 167 association events and zero logged creation failures.

After the explicitly logged developer-timer freeze, inference frame 57 stopped advancing while the same 7 UUIDs remained visible in final pose logs, at 17–20.51 seconds since last observation. The actual preview is 22.020s at 768×822 with 738 decoded frames, visually inspected at the first/middle/last frames. Overlapping/duplicate class labels remain a known limitation. This verifies label retention without repeated detections. It does not establish physical A-button input, quantitative moving-head accuracy, or moved-object tracking. The first OS position-finding take had zero inferences and is not acceptance. See [VERIFICATION.md](VERIFICATION.md) for the record.

Historical 0.2.0 numbers below are not 0.3.0 results.

### Historical native 0.2.0: planar outlines, not session anchors

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
5. **Retain:** freeze observations and compare stable native UUIDs/positions across updates. Moving-object tracking and cross-relaunch persistence remain separate tasks.

## Lecture slides and reuse

[Lecture slides — Quest implementation extension](https://docs.google.com/presentation/d/1cSDat0MuJk7qmj2TtbPbHt5IGeLQUsle8kemzN639hY/edit#slide=id.quest_lab_section)

The 13-slide Quest extension is addressed by stable `quest_lab_*` slide IDs. Other contributors may add sections and change visible slide numbers; the current live deck is not assumed to contain exactly50 slides. The outline below uses the original37-slide **reproduction template** numbering (38–50), not an authoritative live-deck position. Actual device images and Drive video remain in the lecture distribution; raw room media is not redistributed here.

| Template slide | Topic |
|---|---|
| 38 | Build it: object-aware AR — implementation section |
| 39 | Recognize objects in first person — actual demo frame |
| 40 | Demo: on-headset inference — actual device video |
| 41 | From detections to anchored labels — recognize, locate, anchor |
| 42 | Detection is not yet tracking — capability distinctions |
| 43 | How it runs on the headset — processing pipeline |
| 44 | A center hit becomes a stable label — native session anchor |
| 45 | What we used — pinned software stack |
| 46 | The center-ray step in code — source excerpt |
| 47 | Unity native versus WebXR — current capabilities |
| 48 | What the anchor-retention test shows — native 0.3.0 measurements |
| 49 | Verify the label stays put — retention and physical-motion limits |
| 50 | Try it, then change one layer — classroom exercise |

[slides.json](tutorial/slides.json) preserves template slide IDs, order, titles, and technical notes; its numbers are not live-deck positions. [compose-slides.py](tutorial/compose-slides.py) reproduces native Slides shapes/text and Drive image/video references. It contains neither media pixels nor credentials. It requires the specific course template's layout/placeholder IDs; it is not a universal empty-deck authoring tool.

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

Publication scope: implementation teaching sources and original schematic figures only. No room media, private transcripts, credentials, SDK binaries, or model weights. Integration target: `origin/main`; completion owner: Quest classroom tutorial task. Authoritative paths: this tutorial, `tutorial/`, native source under `unity/`, verification/artifact receipts, and README links. Native source now targets0.3.0 session anchors; imported snapshots remain unchanged.
