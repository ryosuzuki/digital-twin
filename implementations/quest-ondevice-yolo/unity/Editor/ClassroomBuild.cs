using System;
using System.IO;
using Meta.XR;
using Unity.InferenceEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.UI;

public static class ClassroomBuild
{
    const string Base = "Assets/PassthroughCameraApiSamples/";
    [MenuItem("Classroom/Prepare YOLO scene")]
    public static void Prepare()
    {
        VerifyPositionGate();
        var scene = EditorSceneManager.OpenScene(Base+"CameraViewer/CameraViewer.unity");
        var old = UnityEngine.Object.FindFirstObjectByType<PassthroughCameraSamples.CameraViewer.CameraViewerManager>();
        var fields = new SerializedObject(old);
        var preview = (RawImage)fields.FindProperty("m_image").objectReferenceValue;
        var camera = (PassthroughCameraAccess)fields.FindProperty("m_cameraAccess").objectReferenceValue;
        var demo = old.gameObject.AddComponent<QuestYolo>();
        demo.cameraAccess = camera;demo.preview=preview;
        var depthPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(Base+"MultiObjectDetection/EnvironmentRaycast/Prefabs/EnvironmentRaycastPrefab.prefab");
        var depthObject = (GameObject)PrefabUtility.InstantiatePrefab(depthPrefab, scene);
        demo.environmentRaycast = depthObject.GetComponent<EnvironmentRaycastManager>();
        demo.modelAsset=AssetDatabase.LoadAssetAtPath<ModelAsset>(Base+"MultiObjectDetection/SentisInference/Model/yolov9onnx.onnx");
        demo.labelsAsset=AssetDatabase.LoadAssetAtPath<TextAsset>(Base+"MultiObjectDetection/SentisInference/Model/SentisYoloClasses.txt");
        demo.backend=Environment.GetEnvironmentVariable("YOLO_CPU")=="1"?BackendType.CPU:BackendType.GPUCompute;
        // CameraViewerManager would replace the frozen inference frame with a live texture; replace only this component.
        UnityEngine.Object.DestroyImmediate(old);
        EditorSceneManager.SaveScene(scene,"Assets/Classroom/QuestYolo.unity");
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/Classroom/QuestYolo.unity",true)};
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android,"org.openclaw.classroom.yolo");
        PlayerSettings.productName="Classroom Local YOLO";PlayerSettings.bundleVersion="0.3.1";PlayerSettings.Android.bundleVersionCode=5;
        PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
        PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
        AssetDatabase.SaveAssets();Debug.Log("CLASSROOM_SCENE_READY");
    }
    [MenuItem("Classroom/Verify position-update gate")]
    public static void VerifyPositionGate()
    {
        var gate = new QuestPositionUpdateGate();
        bool Observe(Vector3 p, float time, out Vector3 target, float updated=0, float cadence=.3f) =>
            gate.Observe(Vector3.zero,p,time,updated,.20f,.10f,3,1f,Mathf.Max(1f,3f*cadence),out target,out _);
        void Check(bool condition, string scenario) {
            if (!condition) throw new Exception("POSITION_GATE_FAILED " + scenario);
        }
        // Sub-deadband jitter must never accumulate into a relocation.
        for (int i=0;i<12;i++) Check(!Observe(new Vector3(.19f,0,0),2+i*.1f,out _),"small_jitter");
        // Two consistent observations are insufficient; an isolated outlier restarts the cluster.
        Check(!Observe(new Vector3(.4f,0,0),4,out _),"first_candidate");
        Check(!Observe(new Vector3(.41f,0,0),4.2f,out _),"second_candidate");
        Check(!Observe(new Vector3(0,.6f,0),4.4f,out _),"outlier_restarts");
        Check(!Observe(new Vector3(.42f,0,0),4.6f,out _),"return_restarts");
        Check(!Observe(new Vector3(.43f,0,0),4.8f,out _),"second_after_outlier");
        Check(Observe(new Vector3(.44f,0,0),5,out var target),"confirmed_motion");
        Check(Vector3.Distance(target,new Vector3(.43f,0,0))<.0001f,"confirmed_mean");
        // Even confirmed observations must respect cooldown and reacquire evidence afterwards.
        Check(!Observe(new Vector3(.5f,0,0),5.1f,out _,5),"cooldown");
        Check(!Observe(new Vector3(.5f,0,0),6.1f,out _,5),"after_cooldown_first");
        Check(!Observe(new Vector3(.51f,0,0),6.3f,out _,5),"after_cooldown_second");
        Check(Observe(new Vector3(.52f,0,0),6.5f,out _,5),"after_cooldown_third");
        Check(!Observe(new Vector3(float.NaN,0,0),7,out _),"invalid_depth");
        Check(!Observe(new Vector3(.4f,0,0),8,out _),"gap_first");
        Check(!Observe(new Vector3(.4f,0,0),10,out _),"observation_gap");
        Check(gate.Count==1,"gap_resets_confirmation");
        gate.Reset();
        // Slow physical-device cadence (2–4s) must still permit three consistent observations.
        Check(!Observe(new Vector3(.4f,0,0),20,out _,0,3f),"slow_first");
        Check(!Observe(new Vector3(.42f,0,0),23,out _,0,3f),"slow_second");
        Check(Observe(new Vector3(.44f,0,0),27,out target,0,4f),"slow_third_confirmed");
        Check(Vector3.Distance(target,new Vector3(.42f,0,0))<.0001f,"slow_mean");
        Check(!Observe(new Vector3(.4f,0,0),30,out _,0,3f),"slow_new_first");
        Check(!Observe(new Vector3(.4f,0,0),45,out _,0,3f),"slow_stale_gap");
        Check(gate.Count==1,"slow_stale_gap_resets");
        gate.Reset(); // Pause/focus-loss resets evidence before re-observation.
        Check(!Observe(new Vector3(.4f,0,0),46,out _,0,3f),"resume_requires_new_evidence");
        Debug.Log("POSITION_GATE_CHECKS_PASSED jitter outlier confirmation cooldown invalid_depth gap slow_cadence stale_gap pause_reset");
    }
    [MenuItem("Classroom/Build Android APK")]
    public static void Build()
    {
        Prepare();Directory.CreateDirectory("Builds");
        var report=BuildPipeline.BuildPlayer(EditorBuildSettings.scenes,"Builds/classroom-yolo.apk",BuildTarget.Android,BuildOptions.Development);
        if(report.summary.result!=BuildResult.Succeeded)throw new Exception("Android build failed: "+report.summary.result);
        Debug.Log("CLASSROOM_APK_READY Builds/classroom-yolo.apk");
    }
}
