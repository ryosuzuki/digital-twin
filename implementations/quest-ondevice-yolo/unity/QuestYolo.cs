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
    public RawImage preview;
    public ModelAsset modelAsset;
    public TextAsset labelsAsset;
    public BackendType backend = BackendType.GPUCompute; // Headset GPU, not a remote GPU.
    [Range(1, 10)] public float detectionHz = 5;
    [Range(.05f, .95f)] public float threshold = .35f;
    Worker worker;
    Tensor<float> input;
    RenderTexture snapshot;
    Text status;
    string[] labels;
    bool paused;
    readonly List<GameObject> annotations = new();
    struct Box { public float x,y,w,h,score; public int cls; }

    IEnumerator Start()
    {
        labels = labelsAsset.text.Trim().Split('\n');
        status = NewText(preview.rectTransform, "Waiting for headset camera permission…", 32);
        status.rectTransform.anchorMin = status.rectTransform.anchorMax = new Vector2(.5f, 1);
        status.rectTransform.pivot = new Vector2(.5f, 1);
        status.rectTransform.sizeDelta = new Vector2(1280, 90);
        status.rectTransform.anchoredPosition = Vector2.zero;
        OVRPermissionsRequester.Request(new[] { OVRPermissionsRequester.Permission.PassthroughCameraAccess });
        try { worker = new Worker(ModelLoader.Load(modelAsset), backend); }
        catch (Exception e) { status.text = "Backend unavailable: " + e.Message; Debug.LogException(e); yield break; }
        input = new Tensor<float>(new TensorShape(1,3,640,640));
        snapshot = new RenderTexture(640,640,0,RenderTextureFormat.ARGB32);
        snapshot.Create();
        while (true)
        {
            if (paused || !Application.isFocused || !cameraAccess.IsPlaying)
            {
                status.text = paused ? "Paused · A to resume" : "Waiting for focus / headset camera permission";
                ClearBoxes(); yield return null; continue;
            }
            // Freeze the same frame for both inference and display, so boxes do not drift on newer frames.
            Graphics.Blit(cameraAccess.GetTexture(), snapshot);
            preview.texture = snapshot;
            var started = Time.realtimeSinceStartupAsDouble;
            TextureConverter.ToTensor(snapshot, input, new TextureTransform().SetDimensions(640,640,3));
            worker.Schedule(input);
            var awaiter = ((Tensor<float>)worker.PeekOutput()).ReadbackAndCloneAsync().GetAwaiter();
            while (!awaiter.IsCompleted) yield return null;
            using var output = awaiter.GetResult();
            var boxes = Decode(output);
            if (!paused && Application.isFocused) Draw(boxes); else ClearBoxes();
            double ms = (Time.realtimeSinceStartupAsDouble-started)*1000;
            status.text = $"LOCAL YOLO · {backend} · {ms:F0} ms · {boxes.Count} objects\nA pause/resume · backend set in Inspector";
            Debug.Log($"QUEST_YOLO backend={backend} inference_ms={ms:F2} count={boxes.Count} source=headset_camera");
            yield return new WaitForSecondsRealtime(Mathf.Max(0, 1/detectionHz-(float)(ms/1000)));
        }
    }
    void Update() { if (OVRInput.GetDown(OVRInput.RawButton.A)) paused = !paused; }
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
        ClearBoxes();var size=preview.rectTransform.rect.size;
        foreach(var b in boxes){var go=new GameObject("Detection",typeof(RectTransform));go.transform.SetParent(preview.transform,false);annotations.Add(go);
            var r=(RectTransform)go.transform;r.anchorMin=r.anchorMax=new Vector2(0,1);r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(b.x*size.x,-b.y*size.y);r.sizeDelta=new Vector2(b.w*size.x,b.h*size.y);
            Border(r,new Vector2(0,0),new Vector2(1,0),Vector2.zero,new Vector2(0,3));
            Border(r,new Vector2(0,1),new Vector2(1,1),new Vector2(0,-3),Vector2.zero);
            Border(r,new Vector2(0,0),new Vector2(0,1),Vector2.zero,new Vector2(3,0));
            Border(r,new Vector2(1,0),new Vector2(1,1),new Vector2(-3,0),Vector2.zero);
            var text=NewText(r,$"{labels[b.cls].Trim()} {b.score:P0}",32);text.rectTransform.anchorMin=text.rectTransform.anchorMax=new Vector2(0,1);text.rectTransform.pivot=new Vector2(0,1);text.rectTransform.sizeDelta=new Vector2(400,44);
        }
        status.transform.SetAsLastSibling();
    }
    static void Border(RectTransform parent,Vector2 min,Vector2 max,Vector2 offsetMin,Vector2 offsetMax)
    {
        var edge=new GameObject("Edge",typeof(RectTransform),typeof(CanvasRenderer),typeof(Image));
        edge.transform.SetParent(parent,false);var r=(RectTransform)edge.transform;
        r.anchorMin=min;r.anchorMax=max;r.offsetMin=offsetMin;r.offsetMax=offsetMax;
        edge.GetComponent<Image>().color=Color.green;edge.GetComponent<Image>().raycastTarget=false;
    }
    static Text NewText(Transform parent,string value,int fontSize){var go=new GameObject("Label",typeof(RectTransform),typeof(CanvasRenderer),typeof(Text));go.transform.SetParent(parent,false);var t=go.GetComponent<Text>();t.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");t.fontSize=fontSize;t.color=Color.green;t.text=value;t.raycastTarget=false;return t;}
    void OnDestroy(){StopAllCoroutines();if(worker!=null){worker.PeekOutput()?.CompleteAllPendingOperations();worker.Dispose();}input?.Dispose();if(snapshot!=null){snapshot.Release();Destroy(snapshot);}}
}
