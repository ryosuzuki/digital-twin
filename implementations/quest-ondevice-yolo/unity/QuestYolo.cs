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
    Material lineMaterial;
    Pose capturedPose;
    float lastDrawTime;
    int depthHits;
    string[] labels;
    bool paused;
    readonly List<GameObject> annotations = new();
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
        lineMaterial = new Material(Shader.Find("Sprites/Default"));
#if UNITY_ANDROID && !UNITY_EDITOR
        if (!UnityEngine.Android.Permission.HasUserAuthorizedPermission("com.oculus.permission.USE_SCENE"))
            UnityEngine.Android.Permission.RequestUserPermission("com.oculus.permission.USE_SCENE");
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
                status.text = paused ? "Paused · A to resume" : "Waiting for focus / camera / positional tracking";
                ClearBoxes(); yield return null; continue;
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
            if (!paused && Application.isFocused && OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head)) Draw(boxes); else ClearBoxes();
            double ms = (Time.realtimeSinceStartupAsDouble-started)*1000;
            status.text = $"LOCAL YOLO · {ms:F0} ms · {depthHits} spatial labels\nFirst-person passthrough · A pause/resume";
            Debug.Log($"QUEST_YOLO backend={backend} inference_ms={ms:F2} count={boxes.Count} source=headset_camera view=first_person depth_hits={depthHits} tracked={OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head)}");
            yield return new WaitForSecondsRealtime(Mathf.Max(0, 1/detectionHz-(float)(ms/1000)));
        }
    }
    void Update() {
        if (OVRInput.GetDown(OVRInput.RawButton.A)) paused = !paused;
        if (paused || !Application.isFocused || Time.realtimeSinceStartup - lastDrawTime > .85f
            || !OVRPlugin.GetNodePositionTracked(OVRPlugin.Node.Head)) ClearBoxes();
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
    void ClearBoxes(){foreach(var a in annotations)Destroy(a);annotations.Clear();}
    void Draw(List<Box> boxes)
    {
        ClearBoxes(); depthHits = 0; lastDrawTime = Time.realtimeSinceStartup;
        if (!EnvironmentRaycastManager.IsSupported || environmentRaycast == null) return;
        foreach (var b in boxes)
        {
            float left = Mathf.Clamp01(b.x), right = Mathf.Clamp01(b.x + b.w);
            float bottom = Mathf.Clamp01(1 - b.y - b.h), top = Mathf.Clamp01(1 - b.y);
            var ray = cameraAccess.ViewportPointToRay(new Vector2((left+right)/2, (bottom+top)/2), capturedPose);
            // Never invent a distance if measured environment depth is unavailable.
            if (!environmentRaycast.Raycast(ray, out var hit, 12f)) continue;
            float distance = Vector3.Distance(capturedPose.position, hit.point);
            if (distance < .25f || distance > 12) continue;
            var plane = new Plane(capturedPose.rotation * Vector3.forward, hit.point);
            var uv = new [] {new Vector2(left,top), new Vector2(right,top), new Vector2(right,bottom), new Vector2(left,bottom)};
            var corners = new Vector3[4]; bool valid = true;
            for (int i=0; i<4; i++) {
                var cornerRay = cameraAccess.ViewportPointToRay(uv[i], capturedPose);
                if (!plane.Raycast(cornerRay, out float d) || d <= 0) { valid = false; break; }
                corners[i] = cornerRay.GetPoint(d);
            }
            if (!valid) continue;
            var go = new GameObject("SpatialDetection", typeof(LineRenderer)); annotations.Add(go);
            var line = go.GetComponent<LineRenderer>(); line.sharedMaterial=lineMaterial;
            line.useWorldSpace=true; line.loop=true; line.positionCount=4; line.SetPositions(corners);
            line.startWidth=line.endWidth=Mathf.Clamp(distance*.0018f,.003f,.015f);
            line.startColor=line.endColor=Color.green;
            var labelGo = new GameObject("SpatialLabel",typeof(RectTransform),typeof(Canvas));
            labelGo.transform.SetParent(go.transform,false); labelGo.GetComponent<Canvas>().renderMode=RenderMode.WorldSpace;
            labelGo.transform.SetPositionAndRotation(corners[0],capturedPose.rotation);
            labelGo.transform.localScale=Vector3.one * Mathf.Max(.0004f,distance*.00065f);
            var text=NewText(labelGo.transform,$"{labels[b.cls].Trim()} {b.score:P0}",28);
            text.rectTransform.pivot=new Vector2(0,0);text.rectTransform.sizeDelta=new Vector2(480,44);
            depthHits++;
        }
    }
    static Text NewText(Transform parent,string value,int fontSize){var go=new GameObject("Label",typeof(RectTransform),typeof(CanvasRenderer),typeof(Text));go.transform.SetParent(parent,false);var t=go.GetComponent<Text>();t.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");t.fontSize=fontSize;t.color=Color.green;t.text=value;t.raycastTarget=false;return t;}
    void OnDestroy(){StopAllCoroutines();if(worker!=null){worker.PeekOutput()?.CompleteAllPendingOperations();worker.Dispose();}input?.Dispose();if(lineMaterial!=null)Destroy(lineMaterial);if(snapshot!=null){snapshot.Release();Destroy(snapshot);}}
}
