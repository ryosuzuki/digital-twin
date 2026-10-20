#!/usr/bin/env python3
"""Materialize the exact upstream project without rewriting its licenses or source."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
PIN='3baac1a1a53aa00af3f639425914f14238a97f84'
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args();dest=a.destination.resolve()
if dest.exists(): raise SystemExit('Destination must not exist; preserve existing projects.')
subprocess.run(['git','clone','https://github.com/oculus-samples/Unity-PassthroughCameraApiSamples.git',str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',PIN],check=True)
model=dest/'Assets/PassthroughCameraApiSamples/MultiObjectDetection/SentisInference/Model/yolov9onnx.onnx'
assert hashlib.sha256(model.read_bytes()).hexdigest()=='189ed26d273423b02243ce7f0a7795acc7da8049f879f8b73a0684d25d1138fd','Missing LFS model or wrong bytes'
# Match the engine/package set used for the verified Android build.
manifest=dest/'Packages/manifest.json'
config=json.loads(manifest.read_text())
config['dependencies'].update({'com.unity.ai.inference':'2.6.1','com.unity.xr.openxr':'1.16.1'})
manifest.write_text(json.dumps(config,indent=2)+'\n')
shutil.copyfile(ROOT/'scripts/unity-packages-lock.json',dest/'Packages/packages-lock.json')
(dest/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.4.5f1\nm_EditorVersionWithRevision: 6000.4.5f1 (cc83ebd631f8)\n')
shutil.copytree(ROOT/'unity',dest/'Assets/Classroom')
print('Ready:',dest,'Open Unity, choose Classroom > Prepare YOLO scene, then Build Android APK.')
