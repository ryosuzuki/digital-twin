// Teaching extension; upstream SDK/model remains under its original license.
using System;
using System.Collections;
using System.Collections.Generic;
using Meta.XR;
using Unity.InferenceEngine;
using UnityEngine;
using UnityEngine.UI;

public sealed class QuestYolo : MonoBehaviour
{
    public PassthroughCameraAccess cameraAccess;
    public RawImage preview; // Legacy scene reference; never displays the camera.
    public EnvironmentRaycastManager environmentRaycast;
    public ModelAsset modelAsset;
    public TextAsset labelsAsset;
    public BackendType backend = BackendType.GPUCompute; // Headset GPU, not a remote GPU.
    [Range(1, 10)] public float detectionHz = 5;
    [Range(.05f, .95f)] public float threshold = .35f;
    Worker worker;
    Tensor<float> input;
    RenderTexture snapshot;
    Text status;
    Pose capturedPose;
    int depthHits;
    string[] labels;
    bool paused;
    [Range(.1f, 2f)] public float associationRadius = .65f;
    [Range(5, 120)] public float retentionSeconds = 30;
    const int MaxAnchors = 20;
    readonly List<SpatialObject> objects = new();
    int nextId = 1;
    int inferenceFrame;
    float lastTelemetry;
    float pauseStarted;
    float demoFreezeAfter;
    float firstInferenceAt = -1f;
    bool demoFreezeTriggered;
    sealed class SpatialObject
    {
        public int id, cls;
        public float score, lastSeen, requestedAt;
        public Vector3 requestedPosition;
        public GameObject root, content;
        public OVRSpatialAnchor anchor;
        public Text label;
        public bool localizedReported, failed, visible;
    }
    struct Box { public float x,y,w,h,score; public int cls; }

    IEnumerator Start()
    {
        labels = labelsAsset.text.Trim().Split('\n');
        // No camera-texture surface: the compositor supplies the first-person passthrough.
        foreach (var canvas in preview.GetComponentsInParent<Canvas>()) canvas.enabled = false;
        var hud = new GameObject("FirstPersonStatus", typeof(RectTransform), typeof(Canvas));
        hud.GetComponent<Canvas>().renderMode = RenderMode.WorldSpace;
        hud.transform.SetParent(Camera.main.transform, false);
        hud.transform.localPosition = new Vector3(0, -.32f, 1.1f);
        hud.transform.localScale = Vector3.one * .0007f;
        status = NewText(hud.transform, "Waiting for camera / environment depth…", 22);
        status.alignment = TextAnchor.MiddleCenter;
        status.rectTransform.sizeDelta = new Vector2(1000, 90);
#if UNITY_ANDROID && !UNITY_EDITOR
        if (!UnityEngine.Android.Permission.HasUserAuthorizedPermission("com.oculus.permission.USE_SCENE"))
            UnityEngine.Android.Permission.RequestUserPermission("com.oculus.permission.USE_SCENE");
#endif
        // Optional developer demonstration: real observations first, then freeze inference, never fake detections.
#if UNITY_ANDROID && !UNITY_EDITOR
        try {
            using var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            using var activity = player.GetStatic<AndroidJavaObject>("currentActivity");
            using var intent = activity.Call<AndroidJavaObject>("getIntent");
            demoFreezeAfter = Mathf.Max(0, intent.Call<float>("getFloatExtra", "classroom_demo_freeze_after", 0f));
        } catch (Exception e) { Debug.LogWarning("QUEST_ANCHOR demo_intent_unavailable=" + e.Message); }
#endif
        OVRPermissionsRequester.Request(new[] { OVRPermissionsRequester.Permission.PassthroughCameraAccess });
        try { worker = new Worker(ModelLoader.Load(modelAsset), backend); }
        catch (Exception e) { status.text = "Backend unavailable: " + e.Message; Debug.LogException(e); yield break; }
        input = new Tensor<float>(new TensorShape(1,3,640,640));
        snapshot = new RenderTexture(640,640,0,RenderTextureFormat.ARGB32);
        snapshot.Create();
        while (true)
        {
            if (paused || !Application.isFocused || !cameraAccess.IsPlaying || !OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head))
            {
                status.text = paused ? $"OBSERVATIONS FROZEN · {ReadyCount()} tracked anchors · A resume / B clear" : "Waiting for focus / camera / positional tracking";
                yield return null; continue;
            }
            // Cache the exposure-time camera pose, not the head pose after inference.
            capturedPose = cameraAccess.GetCameraPose();
            Graphics.Blit(cameraAccess.GetTexture(), snapshot);

            var started = Time.realtimeSinceStartupAsDouble;
            TextureConverter.ToTensor(snapshot, input, new TextureTransform().SetDimensions(640,640,3));
            worker.Schedule(input);
            var awaiter = ((Tensor<float>)worker.PeekOutput()).ReadbackAndCloneAsync().GetAwaiter();
            while (!awaiter.IsCompleted) yield return null;
            using var output = awaiter.GetResult();
            var boxes = Decode(output);
            if (!paused && Application.isFocused && OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head)) Observe(boxes);
            double ms = (Time.realtimeSinceStartupAsDouble-started)*1000;
            inferenceFrame++;
            status.text = $"LOCAL YOLO · {ms:F0} ms · {ReadyCount()} tracked anchors · {depthHits} depth hits\nCenter-hit labels · A freeze/resume · B clear";
            Debug.Log($"QUEST_YOLO backend={backend} inference_ms={ms:F2} count={boxes.Count} source=headset_camera view=anchored_labels frame={inferenceFrame} anchors={ReadyCount()} depth_hits={depthHits} tracked={OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head)}");
            yield return new WaitForSecondsRealtime(Mathf.Max(0, 1/detectionHz-(float)(ms/1000)));
        }
    }
    bool HeadTracked() => OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head);
    int ReadyCount()
    {
        int count = 0;
        foreach (var item in objects)
            if (!item.failed && item.root != null && item.anchor != null && item.anchor.Localized && item.anchor.IsTracked) count++;
        return count;
    }
    void Update()
    {
        float now = Time.realtimeSinceStartup;
        if (OVRInput.GetDown(OVRInput.RawButton.A)) SetPaused(!paused, "button_a");
        if (inferenceFrame > 0 && firstInferenceAt < 0) firstInferenceAt = now;
        if (demoFreezeAfter > 0 && !demoFreezeTriggered && firstInferenceAt >= 0 && now-firstInferenceAt >= demoFreezeAfter)
        {
            demoFreezeTriggered = true;
            SetPaused(true, "developer_demo_timer");
        }
        if (OVRInput.GetDown(OVRInput.RawButton.B)) ClearAnchors("user_clear");
        bool worldVisible = Application.isFocused && HeadTracked();
        for (int i = objects.Count - 1; i >= 0; i--)
        {
            var item = objects[i];
            if (item.root == null) { objects.RemoveAt(i); continue; }
            if (!item.failed && !item.localizedReported &&
                (item.anchor == null || now - item.requestedAt > 10f))
            {
                item.failed = true;
                Debug.LogWarning($"QUEST_ANCHOR event=create_failed id={item.id} class={item.cls} pending_s={now-item.requestedAt:F2}");
            }
            bool ready = !item.failed && item.anchor != null && item.anchor.Localized && item.anchor.IsTracked;
            if (ready && !item.localizedReported)
            {
                item.localizedReported = true;
                Debug.Log($"QUEST_ANCHOR event=localized id={item.id} uuid={item.anchor.Uuid} position={V(item.root.transform.position)}");
            }
            bool show = ready && worldVisible;
            if (item.visible != show)
            {
                item.visible = show; item.content.SetActive(show);
                Debug.Log($"QUEST_ANCHOR event=visibility id={item.id} visible={show} localized={(item.anchor != null && item.anchor.Localized)} anchor_tracked={(item.anchor != null && item.anchor.IsTracked)} head_tracked={HeadTracked()}");
            }
            // Rotate only the child text. The anchor root position is never driven by the head or new detections.
            if (show && Camera.main != null)
            {
                var direction = item.content.transform.position - Camera.main.transform.position;
                if (direction.sqrMagnitude > .0001f)
                    item.content.transform.rotation = Quaternion.LookRotation(direction, Vector3.up);
            }
            if ((item.failed && now-item.requestedAt > 15f) || (!paused && now-item.lastSeen > retentionSeconds))
            {
                Debug.Log($"QUEST_ANCHOR event=retired id={item.id} reason={(item.failed ? "create_failed" : "not_seen_timeout")}");
                Destroy(item.root); objects.RemoveAt(i);
            }
        }
        if (paused && status != null) status.text = $"OBSERVATIONS FROZEN · {ReadyCount()} tracked anchors\nLabels stay in place · A resume · B clear";
        if (now - lastTelemetry > 1f)
        {
            lastTelemetry = now;
            var head = Camera.main != null ? Camera.main.transform : transform;
            foreach (var item in objects)
                Debug.Log($"QUEST_ANCHOR event=pose id={item.id} uuid={(item.anchor != null ? item.anchor.Uuid.ToString() : "none")} position={V(item.root.transform.position)} requested={V(item.requestedPosition)} localized={(item.anchor != null && item.anchor.Localized)} anchor_tracked={(item.anchor != null && item.anchor.IsTracked)} visible={item.visible} age_s={now-item.lastSeen:F2} head_position={V(head.position)} head_rotation={V(head.eulerAngles)} head_tracked={HeadTracked()} inference_frame={inferenceFrame}");
        }
    }
    void SetPaused(bool value, string reason)
    {
        if (paused == value) return;
        float now = Time.realtimeSinceStartup;
        paused = value;
        if (paused) pauseStarted = now;
        else foreach (var item in objects) item.lastSeen += now-pauseStarted;
        Debug.Log($"QUEST_ANCHOR event=observations_paused paused={paused} reason={reason} anchors={ReadyCount()} inference_frame={inferenceFrame}");
    }
    static string V(Vector3 p) => FormattableString.Invariant($"({p.x:F4},{p.y:F4},{p.z:F4})");
    void ClearAnchors(string reason)
    {
        foreach (var item in objects) if (item.root != null) Destroy(item.root);
        objects.Clear();
        Debug.Log($"QUEST_ANCHOR event=cleared reason={reason}");
    }
    List<Box> Decode(Tensor<float> t)
    {
        if (t.shape.rank != 3 || t.shape[1] != 84) throw new InvalidOperationException("Expected [1,84,N] YOLO output");
        var candidates = new List<Box>();
        for (int i=0;i<t.shape[2];i++) {
            float score=0; int cls=0;
            for(int c=4;c<84;c++) if(t[0,c,i]>score){score=t[0,c,i];cls=c-4;}
            if(score<threshold)continue;
            float w=t[0,2,i]/640,h=t[0,3,i]/640;
            if(w<=0||h<=0||float.IsNaN(w+h+score))continue;
            candidates.Add(new Box{x=t[0,0,i]/640-w/2,y=t[0,1,i]/640-h/2,w=w,h=h,score=score,cls=cls});
        }
        candidates.Sort((a,b)=>b.score.CompareTo(a.score)); var keep=new List<Box>();
        foreach(var a in candidates){bool suppress=false;foreach(var b in keep)if(a.cls==b.cls&&IoU(a,b)>.45f){suppress=true;break;}if(!suppress)keep.Add(a);if(keep.Count==40)break;}
        return keep;
    }
    static float IoU(Box a,Box b){float area=Mathf.Max(0,Mathf.Min(a.x+a.w,b.x+b.w)-Mathf.Max(a.x,b.x))*Mathf.Max(0,Mathf.Min(a.y+a.h,b.y+b.h)-Mathf.Max(a.y,b.y));return area/Mathf.Max(1e-6f,a.w*a.h+b.w*b.h-area);}
    void Observe(List<Box> boxes)
    {
        depthHits = 0;
        if (!EnvironmentRaycastManager.IsSupported || environmentRaycast == null) return;
        var matched = new HashSet<int>();
        foreach (var b in boxes)
        {
            float left = Mathf.Clamp01(b.x), right = Mathf.Clamp01(b.x + b.w);
            float bottom = Mathf.Clamp01(1 - b.y - b.h), top = Mathf.Clamp01(1 - b.y);
            var ray = cameraAccess.ViewportPointToRay(new Vector2((left+right)/2, (bottom+top)/2), capturedPose);
            if (!environmentRaycast.Raycast(ray, out var hit, 12f)) continue;
            float distance = Vector3.Distance(capturedPose.position, hit.point);
            if (distance < .25f || distance > 12) continue;
            depthHits++;
            SpatialObject nearest = null;
            float bestDistance = associationRadius;
            foreach (var item in objects)
            {
                if (item.cls != b.cls || item.failed || matched.Contains(item.id) || item.root == null) continue;
                float delta = Vector3.Distance(item.root.transform.position, hit.point);
                if (delta < bestDistance) { nearest = item; bestDistance = delta; }
            }
            if (nearest != null)
            {
                nearest.lastSeen = Time.realtimeSinceStartup; nearest.score = b.score;
                matched.Add(nearest.id);
                nearest.label.text = $"{labels[b.cls].Trim()} #{nearest.id} {b.score:P0}";
                Debug.Log($"QUEST_ANCHOR event=associated id={nearest.id} observed={V(hit.point)} anchor_position={V(nearest.root.transform.position)} delta_m={bestDistance:F3} frame={inferenceFrame+1}");
                continue; // Never reposition an existing anchor from a later 2D observation.
            }
            if (objects.Count >= MaxAnchors) continue;
            var root = new GameObject("ObjectAnchor_" + nextId);
            root.transform.SetPositionAndRotation(hit.point, Quaternion.identity);
            var itemNew = new SpatialObject {
                id = nextId++, cls = b.cls, score = b.score,
                lastSeen = Time.realtimeSinceStartup, requestedAt = Time.realtimeSinceStartup,
                requestedPosition = hit.point, root = root
            };
            var content = new GameObject("CenterHitLabel", typeof(RectTransform), typeof(Canvas));
            content.transform.SetParent(root.transform, false);
            content.GetComponent<Canvas>().renderMode = RenderMode.WorldSpace;
            content.transform.localPosition = Vector3.zero;
            content.transform.localScale = Vector3.one * Mathf.Max(.0006f, distance*.00065f);
            var text = NewText(content.transform, $"{labels[b.cls].Trim()} #{itemNew.id} {b.score:P0}", 30);
            text.alignment = TextAnchor.MiddleCenter;
            text.rectTransform.pivot = new Vector2(.5f,.5f);
            text.rectTransform.sizeDelta = new Vector2(600,64);
            itemNew.content = content; itemNew.label = text;
            content.SetActive(false); // Pending/failed native anchors are not rendered or counted as localized.
            objects.Add(itemNew); matched.Add(itemNew.id);
            itemNew.anchor = root.AddComponent<OVRSpatialAnchor>();
            Debug.Log($"QUEST_ANCHOR event=create_requested id={itemNew.id} class={b.cls} position={V(hit.point)} frame={inferenceFrame+1}");
        }
    }
    static Text NewText(Transform parent,string value,int fontSize){var go=new GameObject("Label",typeof(RectTransform),typeof(CanvasRenderer),typeof(Text));go.transform.SetParent(parent,false);var t=go.GetComponent<Text>();t.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");t.fontSize=fontSize;t.color=Color.green;t.text=value;t.raycastTarget=false;return t;}
    void OnDestroy(){StopAllCoroutines();if(worker!=null){worker.PeekOutput()?.CompleteAllPendingOperations();worker.Dispose();}input?.Dispose();ClearAnchors("destroy");if(snapshot!=null){snapshot.Release();Destroy(snapshot);}}
}
