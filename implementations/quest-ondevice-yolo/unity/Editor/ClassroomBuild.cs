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
        PlayerSettings.productName="Classroom Local YOLO";PlayerSettings.bundleVersion="0.2.0";PlayerSettings.Android.bundleVersionCode=3;
        PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
        PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
        AssetDatabase.SaveAssets();Debug.Log("CLASSROOM_SCENE_READY");
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
